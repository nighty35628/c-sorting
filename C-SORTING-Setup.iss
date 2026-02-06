; C-SORTING 安装程序脚本 (Inno Setup)

[Setup]
AppId={{C-SORTING-BY-NIGHTY}}
AppName=C-SORTING
AppVersion=1.0.0
AppPublisher=Nighty
DefaultDirName={autopf}\C-SORTING
DefaultGroupName=C-SORTING
AllowNoIcons=yes
; 设定生成的安装包位置和名字
OutputDir=setup
OutputBaseFilename=C-SORTING-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=assets\app_icon.ico

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; 这里的 Source 路径必须指向刚才 PyInstaller 生成的目录
Source: "dist\C-SORTING\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\C-SORTING"; Filename: "{app}\C-SORTING.exe"
Name: "{commondesktop}\C-SORTING"; Filename: "{app}\C-SORTING.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\C-SORTING.exe"; Description: "{cm:LaunchProgram,C-SORTING}"; Flags: nowait postinstall skipifsilent
