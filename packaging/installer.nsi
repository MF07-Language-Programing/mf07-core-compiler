; NSIS installer script for CorpLang
!define PRODUCT_NAME "CorpLang"
!define PRODUCT_VERSION "0.1.0"
!define PRODUCT_PUBLISHER "MF07"

OutFile "corplang-installer.exe"
InstallDir "$PROGRAMFILES64\CorpLang"
SetCompressor lzma

Page directory
Page instfiles

Section "Install"
  SetOutPath "$INSTDIR"
  File /r "dist\mf.exe"
  ; copy into installation dir
  ; create a wrapper or add to PATH
  WriteUninstaller "$INSTDIR\uninstall.exe"
  ; create an environment variable PATH update (per-machine)
  ReadRegStr $0 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path"
  StrCpy $1 "$0;${INSTDIR}"
  WriteRegExpandStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path" "$1"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\mf.exe"
  Delete "$INSTDIR\uninstall.exe"
  RMDir "$INSTDIR"
  ; Note: PATH removal left as manual step
SectionEnd
