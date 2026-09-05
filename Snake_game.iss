#define MyAppName "Snake Game"
#define MyAppVersion "1.0.0.0"
#define MyAppPublisher "Muhammad Husnain Raza"
#define MyAppExeName "Snake Game.exe"

[Setup]
AppId={{8BF91184-4F96-4EC0-990D-F79ABC27F613}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\valid_icon.ico
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
OutputBaseFilename=Snake Game Setup
SetupIconFile=valid_icon.ico
SolidCompression=yes
WizardStyle=modern dynamic

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Snake Game\Snake Game.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Snake Game\background_music.wav"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Snake Game\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "valid_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\valid_icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\valid_icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
