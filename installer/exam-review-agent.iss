#define MyAppName "ExamForge AI"
#define MyShortcutName "ExamForge AI 期末复习资料生成器"
#define MyAppVersion "0.3.2"
#define MyAppPublisher "SiriZhao"
#define MyAppURL "https://github.com/SiriZhao"
#define MyAppExeName "ExamForgeAI.exe"
#define MyUserDataDir "{localappdata}\ExamForgeAI"

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
VersionInfoDescription=期末复习资料生成器
VersionInfoCopyright=© 2026 SiriZhao
DefaultDirName={localappdata}\Programs\ExamForge AI
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist\installer
OutputBaseFilename=ExamForgeAISetup-0.3.2
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=examforge.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加快捷方式："; Flags: unchecked

[Messages]
ButtonNext=下一步
ButtonBack=上一步
ButtonInstall=安装
ButtonFinish=完成
ButtonCancel=取消
ButtonBrowse=浏览
ButtonWizardBrowse=浏览
SetupAppTitle=ExamForge AI 安装程序
SetupWindowTitle=ExamForge AI 安装程序
WelcomeLabel1=欢迎安装 [name]
WelcomeLabel2=安装向导会把 ExamForge AI 期末复习资料生成器安装到你的电脑。%n%n软件会在本地启动服务，上传文件、导出文件和日志会保存在用户目录中。
FinishedLabel=安装完成后，你可以立即启动 ExamForge AI。
SelectDirDesc=请选择安装目录。
SelectDirLabel3=安装程序会把 ExamForge AI 安装到以下文件夹。
SelectTasksDesc=请选择需要执行的附加任务。
SelectTasksLabel2=选择安装程序在安装 ExamForge AI 时要执行的附加任务，然后点击“下一步”。
ReadyLabel1=安装程序已准备好安装 ExamForge AI。
FinishedHeadingLabel=ExamForge AI 安装完成

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyShortcutName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "启动 {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    MsgBox(
      'ExamForge AI 已卸载。' + #13#10 + #13#10 +
      '本地上传文件、导出文件和日志已保留在：' + #13#10 +
      ExpandConstant('{#MyUserDataDir}') + #13#10 + #13#10 +
      '如果不再需要这些数据，可以手动删除该文件夹。',
      mbInformation,
      MB_OK
    );
  end;
end;
