#define MyAppName "Campus AI Workspace"
#define MyShortcutName "Campus AI Workspace"
#define MyAppVersion "0.5.1"
#define MyAppPublisher "SiriZhao"
#define MyAppURL "https://github.com/SiriZhao/examforge-ai"
#define MyAppExeName "CampusAIWorkspace.exe"
#define MyUserDataDir "{localappdata}\CampusAIWorkspace"

[Setup]
AppId={{D92F62E9-DBBA-43D2-856A-8F1B3C8BB7A7}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Campus AI Workspace AI study SaaS desktop client
VersionInfoCopyright=Copyright 2026 SiriZhao
DefaultDirName={localappdata}\Programs\Campus AI Workspace
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist\installer
OutputBaseFilename=CampusAIWorkspaceSetup-0.5.1
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=examforge.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts"; Flags: unchecked

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyShortcutName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    MsgBox(
      'Campus AI Workspace has been uninstalled.' + #13#10 + #13#10 +
      'Local uploads, exports, logs, and caches may remain in:' + #13#10 +
      ExpandConstant('{#MyUserDataDir}') + #13#10 + #13#10 +
      'Delete that folder manually if you no longer need the data.',
      mbInformation,
      MB_OK
    );
  end;
end;
