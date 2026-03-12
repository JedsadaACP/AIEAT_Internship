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
Name: "install_ollama"; Description: "Install Ollama AI Engine + Typhoon 2.5 Model (~2.5 GB download, requires internet)"; GroupDescription: "AI Engine (Optional):"; Flags: unchecked

[Files]
; Main application (everything PyInstaller compiled)
Source: "dist\AIEAT\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Schema (for fresh database creation)
Source: "data\schema.sql"; DestDir: "{app}\data"; Flags: ignoreversion
; Config files (loaded at runtime by Python)
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
; --- Ollama Installation (only if user checked the box) ---
; Step 1: Download and install Ollama silently
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -Command ""Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile '$env:TEMP\OllamaSetup.exe'; Start-Process -FilePath '$env:TEMP\OllamaSetup.exe' -ArgumentList '/S' -Wait"""; StatusMsg: "Downloading and installing Ollama AI Engine..."; Tasks: install_ollama; Flags: runhidden waituntilterminated

; Step 2: Pull the Typhoon 2.5 model (shows CMD window with download progress)
Filename: "cmd.exe"; Parameters: "/K ""%LOCALAPPDATA%\Programs\Ollama\ollama.exe pull scb10x/typhoon2.5-qwen3-4b:latest && echo. && echo Model installed successfully! Press any key to close. && pause"""; StatusMsg: "Downloading Typhoon AI Model (this may take several minutes)..."; Tasks: install_ollama; Flags: waituntilterminated

; --- Always: Launch the app ---
Filename: "{app}\AIEAT.exe"; Description: "Launch AIEAT News Dashboard"; Flags: nowait postinstall skipifsilent