; Script per creare il wizard di installazione di Disk Analyzer
[Setup]
AppName=Disk Analyzer
AppVersion=1.0
DefaultDirName={autopf}\Disk Analyzer
DefaultGroupName=Disk Analyzer
OutputDir=.
OutputBaseFilename=DiskAnalyzer_Installer
Compression=lzma
SolidCompression=yes
SetupIconFile=img/logo.ico
UninstallDisplayIcon={app}\DiskAnalyzer.exe
Uninstallable=yes
UninstallDisplayName="Uninstall Disk Analyzer"

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Dirs]
Name: "{app}\img";

[Files]
Source: "dist\Disk Analyzer.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "img\logo.ico"; DestDir: "{app}\img"; Flags: onlyifdoesntexist

[Icons]
Name: "{group}\Disk Analyzer"; Filename: "{app}\Disk Analyzer.exe"; IconFilename: "{app}\img\logo.ico"
Name: "{commondesktop}\Disk Analyzer"; Filename: "{app}\Disk Analyzer.exe"; Tasks: desktopicon
Name: "{group}\Uninstall Disk Analyzer"; Filename: "DiskAnalyzer_Uninstall.exe"

[Tasks]
Name: "desktopicon"; Description: "Crea un'icona sul desktop"; GroupDescription: "Icone aggiuntive:"

[Run]
Filename: "{app}\Disk Analyzer.exe"; Description: "Avvia Disk Analyzer"; Flags: nowait postinstall

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
procedure InitializeWizard;
begin
  WizardForm.Caption := 'Install Disk Analyzer!';
end;
