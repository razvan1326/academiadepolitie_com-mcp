# Cum să construiești installer-ul

## Pentru Windows (.exe)

1. **Instalează PyInstaller:**
```bash
pip install pyinstaller
```

2. **Build:**
```bash
python build_installer.py
```

3. **Rezultat:**
- `dist/AcademiaDePolitie_MCP_Setup.exe` (~30-40MB)

## Pentru macOS (.app)

1. **Instalează PyInstaller:**
```bash
pip3 install pyinstaller
```

2. **Build:**
```bash
python3 build_installer.py
```

3. **Rezultat:**
- `dist/AcademiaDePolitie_MCP_Installer.app`

## Pentru distribuție

Upload fișierul `.exe` sau `.app` pe server și oferă link de download utilizatorilor:

```
https://www.academiadepolitie.com/download/AcademiaDePolitie_MCP_Setup.exe
```

## Ce conține installer-ul:

✅ Python runtime embedded  
✅ Server MCP (server_py39.py)  
✅ GUI pentru configurare JWT  
✅ Auto-configurare Claude Desktop  
✅ Nu necesită Python instalat pe PC-ul utilizatorului  

## Utilizare finală:

1. Utilizatorul descarcă și rulează `.exe`
2. Introduce JWT token  
3. Click Instalează  
4. Restart Claude Desktop  
5. Gata! MCP funcționează  