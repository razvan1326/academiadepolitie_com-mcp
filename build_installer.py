#!/usr/bin/env python3
"""
Build script pentru crearea installer-ului .exe/.app
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def build_installer():
    """Construiește installer-ul pentru platforma curentă"""
    
    system = platform.system()
    
    print("=" * 60)
    print(f"  Build Installer AcademiaDePolițe MCP - {system}")
    print("=" * 60)
    
    # Verifică PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller nu este instalat!")
        print("Instalează cu: pip install pyinstaller")
        return False
    
    # Parametri comuni
    base_args = [
        'pyinstaller',
        '--onefile',           # Un singur fișier executabil
        '--windowed',          # Fără consolă (GUI)
        '--clean',             # Curăță build-ul anterior
        '--noconfirm',         # Nu cere confirmare
        '--name', 'Academiadepolitie_com_MCP_Installer',
    ]
    
    # Parametri specifici per platformă
    if system == "Windows":
        icon_path = "icon.ico"  # Poți adăuga o icoană custom
        output_name = "Academiadepolitie_com_MCP_Setup.exe"
        base_args.extend([
            '--icon', icon_path if Path(icon_path).exists() else 'NONE',
            '--version-file', 'version_info.txt' if Path('version_info.txt').exists() else None,
            '--add-data', 'README.md;.' if Path('README.md').exists() else None,
        ])
    
    elif system == "Darwin":  # macOS
        icon_path = "icon.icns"
        output_name = "Academiadepolitie_com_MCP_Installer.app"
        base_args.extend([
            '--icon', icon_path if Path(icon_path).exists() else 'NONE',
            '--osx-bundle-identifier', 'com.academiadepolitie.mcp-installer',
        ])
    
    else:  # Linux
        output_name = "Academiadepolitie_com_MCP_Installer"
        
    # Filtrează None values
    base_args = [arg for arg in base_args if arg is not None]
    
    # Adaugă script-ul principal
    base_args.append('installer_standalone.py')
    
    print("🔨 Construiesc cu parametrii:")
    print(" ".join(base_args))
    print()
    
    # Rulează PyInstaller
    try:
        result = subprocess.run(base_args, check=True)
        print("\n✅ Build complet!")
        print(f"Executabil creat în: dist/{output_name}")
        
        # Dimensiune fișier
        if system == "Windows":
            exe_path = Path('dist') / 'Academiadepolitie_com_MCP_Installer.exe'
        else:
            exe_path = Path('dist') / 'Academiadepolitie_com_MCP_Installer'
            
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"Dimensiune: {size_mb:.1f} MB")
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Eroare la build: {e}")
        return False

def create_version_info():
    """Creează fișier version info pentru Windows"""
    version_info = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'AcademiaDePolițe.com'),
        StringStruct(u'FileDescription', u'MCP Installer pentru Claude Desktop'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'mcp_installer'),
        StringStruct(u'LegalCopyright', u'© 2024 AcademiaDePolițe.com'),
        StringStruct(u'OriginalFilename', u'AcademiaDePolitie_MCP_Setup.exe'),
        StringStruct(u'ProductName', u'AcademiaDePolițe MCP'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    print("✅ Version info creat")

def create_readme():
    """Creează README pentru distribuție"""
    readme = '''# AcademiaDePolițe MCP Installer

Installer automat pentru integrarea AcademiaDePolițe.com cu Claude Desktop.

## Ce face acest installer:

1. Salvează serverul MCP pe calculatorul tău
2. Configurează automat Claude Desktop
3. Salvează token-ul JWT securizat

## Utilizare:

1. Rulează installer-ul
2. Introdu JWT token-ul din contul tău AcademiaDePolițe.com
3. Click pe Instalează
4. Restart Claude Desktop

## Suport:

Pentru ajutor, vizitează: https://www.academiadepolitie.com/cont_elev_setari

© 2024 AcademiaDePolițe.com
'''
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme)
    print("✅ README creat")

if __name__ == "__main__":
    # Pregătește fișierele auxiliare
    if platform.system() == "Windows":
        create_version_info()
    create_readme()
    
    # Build
    success = build_installer()
    
    # Cleanup
    for temp_file in ['version_info.txt', 'README.md']:
        if Path(temp_file).exists():
            os.remove(temp_file)
    
    sys.exit(0 if success else 1)