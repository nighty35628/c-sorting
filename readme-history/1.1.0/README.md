[绠€浣撲腑鏂嘳(#c-sorting) | [English](#c-sorting-en)

# C-SORTING

**C-SORTING** 鏄竴娆惧熀浜?PyQt6 寮€鍙戠殑鐜颁唬鍖栨櫤鑳界収鐗囧垎绫诲伐鍏凤紝閲囩敤鏋佺畝涓讳箟璁捐锛屾棬鍦ㄥ府鍔╃敤鎴峰揩閫熸暣鐞嗘潅涔辩殑鐓х墖搴撱€?

## 馃専 鏍稿績鍔熻兘

- **鏋佺畝 UI**锛氶噰鐢ㄦ祦鐣呯殑 PyQt6 鍔ㄧ敾銆佷晶杈规爮瀵艰埅鍜屽渾瑙掑崱鐗囧竷灞€銆?
- **鏅鸿兘鍒嗙被**锛?
  - **鏀寔澶氱鏍煎紡**锛氫笉浠呮敮鎸佺収鐗囷紙JPG, PNG, HEIC, WebP, BMP 绛夛級锛岃繕鏀寔瑙嗛鏂囦欢锛圡P4, MOV, AVI, MKV 绛夛級銆?
  - **鎸夋棩鏈?*锛氱簿纭埌澶╋紙YYYY-MM-DD锛夈€?
  - **鎸夋湀浠?*锛氬皢濯掍綋鎸夋湀褰掓。锛圷YYY-MM锛夈€?
  - **鎸夊湴鐐?*锛氳鍙?EXIF GPS 淇℃伅锛岄噰鐢?**鍐呯疆绂荤嚎鍩庡競鏁版嵁搴?*锛?37 涓湴绾ц鏀垮尯鍧愭爣锛夎嚜鍔ㄨ瘑鍒渶杩戠殑鍩庡競鍚嶃€?
  - **濯掍綋鍒嗘嫞**锛氳嚜鍔ㄥ皢鐓х墖鍜岃棰戝垎娴佽嚦涓嶅悓鐨勭洰鏍囨枃浠跺す銆?
- **涓€у寲璁剧疆**锛氬唴缃?10 绉嶉厤鑹叉柟妗堬紝鏀寔涓€閿垏鎹?*娣辫壊妯″紡**銆?
- **浜や簰浼樺寲**锛氬鐞嗗畬鎴愬悗鍙洿鎺ョ偣鍑诲璇濇涓殑鈥滄墦寮€鏂囦欢澶光€濇寜閽煡鐪嬬粨鏋溿€?
- **鍘嗗彶璁板綍**锛氳嚜鍔ㄨ褰曞鐞嗕换鍔★紝鏂逛究涓€閿墦寮€鐩爣鏂囦欢澶广€?
- **澶氳瑷€**锛氬畬鏁存敮鎸佺畝浣撲腑鏂囦笌鑻辨枃銆?
- **鏃犳崯鏁寸悊**锛氭敮鎸佲€滀繚鐣欏師鏂囦欢锛堝鍒讹級鈥濇垨鈥滅Щ鍔ㄦ枃浠垛€濇ā寮忋€?
- **楂樻€ц兘**锛氶噰鐢ㄥ紓姝ュ绾跨▼澶勭悊锛屽ぇ鎵归噺鐓х墖鏁寸悊鏃剁晫闈笉鍗￠】銆?

## 馃殌 蹇€熷紑濮?

1. 鍏嬮殕椤圭洰鍚庯紝鍦ㄦ牴鐩綍涓嬪垱寤哄苟婵€娲昏櫄鎷熺幆澧冿細
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
2. 瀹夎渚濊禆锛?
```powershell
pip install -r requirements.txt
```
3. 鍚姩绋嬪簭锛?
```powershell
python src/main.py
```

## 馃洜锔?椤圭洰缁撴瀯

- `src/`锛氭簮浠ｇ爜
  - `gui/app.py`锛氱幇浠ｅ寲鐨?PyQt6 鐣岄潰閫昏緫銆佷富棰樺紩鎿庝笌缈昏瘧绯荤粺銆?
  - `sorter.py`锛氭牳蹇冨垎绫荤畻娉曪紙鏃ユ湡/鏈堜唤/鍩庡競鍒嗘瀽锛夈€?
  - `exif_utils.py`锛氱収鐗?EXIF 鍏冩暟鎹В鏋愶紙鏃堕棿銆丟PS锛夈€?
  - `geocode.py`锛氬湴鐞嗙紪鐮佹湇鍔★紝鍐呯疆 337 涓腑鍥藉湴绾ц鏀垮尯鍧愭爣鐨勭绾挎煡璇㈤€昏緫銆?
  - `models/`锛氶鐣?AI 璇嗗埆鎺ュ彛锛堝浜鸿劯/鐗╀綋璇嗗埆锛夈€?
- `readme-history/`锛氬瓨鏀惧巻鍙茬増鏈殑 README 鏂囦欢銆?
- `assets/`锛氱▼搴忓浘鏍囦笌鍐呴儴璧勬簮銆?
- `config.json`锛氱敤鎴烽厤缃寔涔呭寲锛堜富棰樿壊銆佽瑷€銆佹繁鑹叉ā寮忥級銆?
- `history.json`锛氬鐞嗗巻鍙叉暟鎹€?

## 馃摑 娉ㄦ剰浜嬮」

- **绂荤嚎鏀寔**锛氬緱鐩婁簬鍐呯疆鐨勮交閲忕骇鍩庡競鍧愭爣鏁版嵁搴擄紝鍦扮悊浣嶇疆鍒嗙被鐜板湪瀹屽叏鏀寔绂荤嚎杩愯锛屾棤闇€浜掕仈缃戙€?
- **閰嶇疆鏂囦欢**锛氱▼搴忎細鍦ㄦ墍鍦ㄧ洰褰曚笅鑷姩鐢熸垚 `config.json` 鍜?`history.json` 浠ヤ繚瀛樻偍鐨勫亸濂藉拰鍘嗗彶璁板綍銆?

## 馃攧 鐗堟湰鏇存柊

- **v1.1.0** (2026-02-20): 2026 骞村害澶х増鏈€?
  - **澧炲己鏍煎紡鏀寔**锛氭敮鎸?WebP, GIF, BMP, JFIF 绛夋洿澶氬浘鐗囨牸寮忋€?
  - **澧炲姞瑙嗛鍒嗙被**锛氭敮鎸?MP4, MOV, AVI, MKV 绛変富娴佽棰戝垎绫汇€?
  - **濯掍綋鍒嗘嫞閫昏緫**锛氳嚜鍔ㄦ寜濯掍綋绫诲瀷锛堢収鐗?瑙嗛锛夊垎閫佷笉鍚岀殑椤剁骇鏂囦欢澶广€?
  - **UI 浜や簰鏀硅繘**锛氫换鍔＄粨鏉熷悗鏀寔鍦ㄥ脊绐楀唴涓€閿墦寮€鏂囦欢澶癸紝缁熶竴浜嗘寜閽瑙夐鏍笺€?
- **v1.0.8**: 閲嶆瀯鍦扮悊鍒嗙被閫昏緫銆備粠鑵捐鍦板浘 API 杩佺Щ鑷?*鍐呯疆鏈湴鍩庡競鏁版嵁搴?*鏂规锛屽疄鐜?100% 绂荤嚎杩愯锛屾樉钁楁彁鍗囬殣绉佹€т笌澶勭悊閫熷害銆?

## 璁稿彲璇?
MIT

---

# C-SORTING <a id="c-sorting-en"></a>

**C-SORTING** is a modern intelligent photo sorting tool developed based on PyQt6, featuring a minimalist design aimed at helping users quickly organize cluttered photo libraries.

## 馃専 Core Features

- **Minimalist UI**: Utilizes smooth PyQt6 animations, sidebar navigation, and rounded corner card layouts.
- **Smart Sorting**:
  - **By Date**: Precision to the day (YYYY-MM-DD).
  - **By Month**: Archives photos by month (YYYY-MM).
  - **By Location**: Reads EXIF GPS information and identifies the nearest city using a **built-in offline city database** (337 prefecture-level cities).
- **Personalized Settings**: Built-in 10 color schemes, supporting one-click switching to **Dark Mode**.
- **History**: Automatically records processing tasks for easy one-click opening of target folders.
- **Multi-language**: Full support for Simplified Chinese and English.
- **Lossless Organization**: Supports "Keep original files (Copy)" or "Move files" modes.
- **High Performance**: Uses asynchronous multi-threaded processing, ensuring the interface remains responsive during bulk photo organization.

## 馃殌 Quick Start

1. After cloning the project, create and activate a virtual environment in the root directory:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
2. Install dependencies:
```powershell
pip install -r requirements.txt
```
3. Start the program:
```powershell
python src/main.py
```

## 馃洜锔?Project Structure

- `src/`: Source Code
  - `gui/app.py`: Modern PyQt6 interface logic, theme engine, and translation system.
  - `sorter.py`: Core sorting algorithm (Date/Month/City analysis).
  - `exif_utils.py`: Photo EXIF metadata parsing (Time, GPS).
  - `geocode.py`: Geocoding service with a **built-in offline database** of 337 Chinese prefecture-level administrative regions.
  - `models/`: Reserved for AI recognition interfaces (e.g., face/object recognition).
- `readme-history/`: Archive of historical README files.
- `assets/`: Program icons and internal resources.
- `config.json`: User configuration persistence (Theme color, language, dark mode).
- `history.json`: Processing history data.

## 馃摑 Notes

- **Offline Support**: Thanks to the built-in lightweight city database, location-based sorting now fully supports offline operation, with no internet required.
- **Configuration Files**: The program automatically generates `config.json` and `history.json` in its directory to save your preferences and history.

## 馃攧 Updates

- **v1.0.8**: Major refactor of geocoding logic. Migrated from Tencent Maps API to a **built-in offline city database**, enabling 100% offline operation with improved privacy and speed.

## License
MIT


