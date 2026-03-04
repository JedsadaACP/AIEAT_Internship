; AIEAT Installer - Inno Setup 6
[Setup]
AppName=AIEAT News Dashboard
AppVersion=1.0.0
AppPublisher=AIEAT Team
DefaultDirName={autopf}\AIEAT
DefaultGroupName=AIEAT
OutputDir=installer_output
OutputBaseFilename=AIEAT_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequiredOverridesAllowed=dialog
DisableDirPage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
; Main application
Source: "dist\AIEAT\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Schema
Source: "data\schema.sql"; DestDir: "{app}\data"; Flags: ignoreversion
; Config files
Source: "app\config\scraper_config.json"; DestDir: "{app}\app\config"; Flags: ignoreversion
Source: "app\config\llm_scoring_config.json"; DestDir: "{app}\app\config"; Flags: ignoreversion
Source: "app\config\llm_translation_config.json"; DestDir: "{app}\app\config"; Flags: ignoreversion
Source: "app\config\paywall_signals.json"; DestDir: "{app}\app\config"; Flags: ignoreversion
; README
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Dirs]
Name: "{app}\data"; Permissions: users-modify
Name: "{app}\logs"; Permissions: users-modify

[Icons]
Name: "{group}\AIEAT News Dashboard"; Filename: "{app}\AIEAT.exe"
Name: "{group}\Uninstall AIEAT"; Filename: "{uninstallexe}"
Name: "{userdesktop}\AIEAT News Dashboard"; Filename: "{app}\AIEAT.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\AIEAT.exe"; Description: "Launch AIEAT News Dashboard"; Flags: nowait postinstall skipifsilent
