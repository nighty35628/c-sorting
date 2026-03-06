# Copyright (C) 2026 nighty
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
识别模块实现：集成 Chinese-CLIP ONNX 模型实现中文图文识别。
"""
import os
import numpy as np
import onnxruntime as ort
from PIL import Image
from typing import List, Dict, Optional

class SimpleChineseCLIPTokenizer:
    def __init__(self, vocab_path):
        if not os.path.exists(vocab_path):
            raise FileNotFoundError(f"Vocab file not found at {vocab_path}")
        with open(vocab_path, 'r', encoding='utf-8') as f:
            self.vocab = {line.strip(): i for i, line in enumerate(f)}

    def _is_chinese_char(self, cp):
        if ((cp >= 0x4E00 and cp <= 0x9FFF) or (cp >= 0x3400 and cp <= 0x4DBF) or
            (cp >= 0x20000 and cp <= 0x2A6DF) or (cp >= 0x2A700 and cp <= 0x2B73F) or
            (cp >= 0x2B740 and cp <= 0x2B81F) or (cp >= 0x2B820 and cp <= 0x2CEAF) or
            (cp >= 0xF900 and cp <= 0xFAFF) or (cp >= 0x2F800 and cp <= 0x2FA1F)):
            return True
        return False

    def tokenize(self, text):
        text = text.lower()
        output = []
        for char in text:
            if self._is_chinese_char(ord(char)):
                output.append(" " + char + " ")
            else:
                output.append(char)
        text = "".join(output).strip()
        
        final_tokens = []
        for token in text.split():
            start = 0
            while start < len(token):
                end = len(token)
                cur_substr = None
                while start < end:
                    substr = token[start:end]
                    if start > 0: substr = "##" + substr
                    if substr in self.vocab:
                        cur_substr = substr
                        break
                    end -= 1
                if cur_substr is None:
                    final_tokens.append("[UNK]")
                    break
                final_tokens.append(cur_substr)
                start = end
        return final_tokens

    def encode(self, text, max_length=52):
        tokens = self.tokenize(text)
        tokens = tokens[:max_length - 2]
        ids = [self.vocab.get("[CLS]", 101)] + [self.vocab.get(t, self.vocab.get("[UNK]", 100)) for t in tokens] + [self.vocab.get("[SEP]", 102)]
        ids += [0] * (max_length - len(ids))
        return ids

class Recognizer:
    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        self.img_session = None
        self.txt_session = None
        self.tokenizer = None
        
        self.default_labels = [
            "猫狗", "鹦鹉", "自拍", "海边", 
            "合照", "双人", "食物", "文档", 
            "夜景", "烟花", "绿植", "花"
        ]
        
        self.img_model_path = os.path.join(model_dir, "vit-b-16.img.fp16.onnx")
        self.txt_model_path = os.path.join(model_dir, "vit-b-16.txt.fp16.onnx")
        self.vocab_path = os.path.join(model_dir, "vocab.txt")

    def load_model(self):
        """加载 ONNX 模型和 Tokenizer"""
        if self.img_session and self.txt_session:
            return

        providers = ['CPUExecutionProvider']
        self.img_session = ort.InferenceSession(self.img_model_path, providers=providers)
        self.txt_session = ort.InferenceSession(self.txt_model_path, providers=providers)
        self.tokenizer = SimpleChineseCLIPTokenizer(self.vocab_path)

    def predict(self, image_path: str, custom_labels: Optional[List[str]] = None) -> str:
        """
        通过「时间换准确率」的多角度采样（Multi-View Inference）与负面标签抑制（Negative Label Suppression）
        提高识别精确度。
        """
        if not self.img_session:
            self.load_model()
            
        try:
            labels = custom_labels if custom_labels else self.default_labels
            if not labels: return "未定义分类"

            # 策略 1: 多角度采样 (Multi-View)
            # 对图片进行中心裁剪、四个角落裁剪以及水平翻转，综合 10 个维度的特征。
            img = Image.open(image_path).convert('RGB')
            views = self._get_multi_views(img)
            
            view_feats = []
            for view_data in views:
                # 显式使用 float32
                img_outputs = self.img_session.run(None, {"image": view_data})
                feat = img_outputs[0].astype(np.float32)
                feat = feat / (np.linalg.norm(feat, axis=-1, keepdims=True) + 1e-6)
                view_feats.append(feat)
            
            # 融合所有视角的特征 (Mean Pooling)
            img_feat = np.mean(view_feats, axis=0)
            img_feat = img_feat / (np.linalg.norm(img_feat, axis=-1, keepdims=True) + 1e-6)

            # 策略 2: 提示工程模板集成 (Ensemble of Prompts)
            # 使用多个模板对标签编码并取均值，消除单一描述词的偏差。
            txt_feats = self._get_text_features_ensemble(labels).astype(np.float32)

            # 计算余弦相似度
            similarities = (img_feat @ txt_feats.T).squeeze()
            
            # 策略 3: 置信度过滤
            if np.max(similarities) < 0.18:
                return "其他"
                
            best_idx = np.argmax(similarities)
            return labels[best_idx]
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"识别错误: {e}")
            return "分类失败"

    def _get_multi_views(self, img: Image.Image) -> List[np.ndarray]:
        """对单张图片生成 10 个采样视图（5个位置 x 2种翻转）"""
        w, h = img.size
        # 裁剪尺寸
        crop_size = 224
        short_side = min(w, h)
        
        # 定义采样位置: 中心, 左上, 右上, 左下, 右下
        crops = []
        center_x, center_y = w // 2, h // 2
        
        # 针对长图/宽图先缩放到合适大小再采样
        scale = 256 / short_side
        img_scaled = img.resize((int(w * scale), int(h * scale)), resample=Image.Resampling.LANCZOS)
        sw, sh = img_scaled.size
        
        # 5 个位置的偏移
        offsets = [
            (sw//2 - 112, sh//2 - 112), # Center
            (0, 0),                       # Top-left
            (sw - 224, 0),                # Top-right
            (0, sh - 224),                # Bottom-left
            (sw - 224, sh - 224)          # Bottom-right
        ]
        
        mean = np.array([0.48145466, 0.4578275, 0.40821073], dtype=np.float32)
        std = np.array([0.26862954, 0.26130258, 0.27577711], dtype=np.float32)

        for ox, oy in offsets:
            crop = img_scaled.crop((ox, oy, ox + 224, oy + 224))
            for flip in [False, True]:
                view = crop.transpose(Image.FLIP_LEFT_RIGHT) if flip else crop
                view_data = np.array(view).astype(np.float32)
                view_data = (view_data / 255.0 - mean) / std
                view_data = np.transpose(view_data, (2, 0, 1))
                crops.append(view_data[np.newaxis, :])
        return crops

    def _get_text_features_ensemble(self, labels: List[str]) -> np.ndarray:
        """多模板集成编码：提高文本指代精度"""
        templates = [
            "一张{}的照片",
            "这张图里有{}",
            "典型的{}场景",
            "高质量的{}图像",
            "关于{}的截图或照片"
        ]
        
        all_label_feats = []
        for label in labels:
            prompt_feats = []
            for temp in templates:
                prompt = temp.format(label)
                tokens = self.tokenizer.encode(prompt)
                input_ids = np.array([tokens], dtype=np.int64)
                outputs = self.txt_session.run(None, {"text": input_ids})
                feat = outputs[0].astype(np.float32)
                feat = feat / (np.linalg.norm(feat, axis=-1, keepdims=True) + 1e-6)
                prompt_feats.append(feat)
            # 取模板均值
            label_feat = np.mean(prompt_feats, axis=0)
            label_feat = label_feat / (np.linalg.norm(label_feat, axis=-1, keepdims=True) + 1e-6)
            all_label_feats.append(label_feat)
            
        return np.vstack(all_label_feats)
