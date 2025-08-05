# AcademiaDePolițe MCP Server - Python 3.9 Compatible

MCP Server pentru AcademiaDePolițe.com compatibil cu Python 3.9 - implementează protocolul Model Context Protocol manual.

## Instalare pe Server

1. **Upload fișierele pe server:**
```bash
scp server_py39.py requirements_py39.txt README_py39.md user@server:/path/to/api/llm/claude-mcp/
```

2. **Pe server - testează că funcționează:**
```bash
# NU sunt dependențe de instalat! Folosește doar librării standard Python
cd /path/to/api/llm/claude-mcp/
python3.9 test_py39.py  # Test local
python3.9 server_py39.py  # Pornește serverul
```

## Configurare Claude Desktop

### 1. Obține JWT Token
Intră în contul tău pe AcademiaDePolițe.com → Setări → API Access și copiază tokenul JWT.

### 2. Configurează Claude Desktop
Adaugă în `~/.config/claude-desktop/config.json`:

```json
{
  "mcp": {
    "servers": {
      "academiadepolitie": {
        "command": "/home/adpcomilearnings/venv-spacy/bin/python",
        "args": ["server_py39.py"],
        "cwd": "/home/adpcomilearnings/public_html/api/llm/claude-mcp",
        "env": {
          "ACADEMIADEPOLITIE_JWT_TOKEN": "PUNE_TOKENUL_TAU_JWT_AICI"
        }
      }
    }
  }
}
```

**IMPORTANT:** Înlocuiește `PUNE_TOKENUL_TAU_JWT_AICI` cu tokenul tău JWT real de la AcademiaDePolițe.com

## Tools Disponibile

### `get_student_data(user_id, ...)`
Tool principal modular identic cu versiunea oficială MCP. Toți parametrii sunt aceiași:

- `user_id` (int, obligatoriu) - ID-ul utilizatorului
- `user_profile` (bool) - Include profilul utilizatorului  
- `activitati_recente` (int, 1-10) - Numărul de activități de returnat
- `profil_comportamental` (bool) - Include analiza comportamentală (necesită `materie`)
- `progres_teorie` (bool) - Include progresul la teorie
- `analiza_lacunelor` (bool) - Include analiza lacunelor
- `utilizatori_compatibili` (int, 1-10) - Numărul de utilizatori compatibili pentru peer matching
- `materie` (int, opțional) - ID materie pentru filtrare
- `only` (str, opțional) - Filtrare activități
- `focus` (str, opțional) - Pentru utilizatori_compatibili - filtrare geografică/temporală
- `instructiuni_llm` (bool) - Transformă recomandările în instrucțiuni pentru LLM
- `all_modules` (bool) - Include toate modulele

## Resources Disponibile

- `user://profile/{user_id}` - Profilul utilizatorului
- `user://data/{user_id}` - Toate datele utilizatorului (complet)

## Testare

### Test Local:
```bash
cd /home/adpcomilearnings/public_html/api/llm/claude-mcp/
/home/adpcomilearnings/venv-spacy/bin/python test_py39.py
```

### Test cu Claude Desktop:
Restart Claude Desktop și testează cu:
- "Arată-mi profilul pentru user_id 4001"
- "Găsește-mi 3 utilizatori compatibili din același județ"
- "Vreau ultimele activități cu instrucțiuni LLM"

## Avantaje față de versiunea oficială MCP

✅ **Compatibil cu Python 3.9** (fără necesitatea Python 3.10+)  
✅ **Fără dependențe externe** (doar librării standard)  
✅ **Mai rapid de instalat** (fără pip install)  
✅ **Mai puțin spațiu** (fără node_modules/venv mare)  
✅ **100% compatibil** cu Claude Desktop  
✅ **Aceiași funcționalitate** ca versiunea oficială  

## Diferențe față de versiunea oficială

- Implementează protocolul JSON-RPC manual (în loc de FastMCP framework)
- Folosește `urllib` în loc de `httpx`
- Folosește tipuri native în loc de `pydantic`
- Menține 100% compatibilitatea cu Claude Desktop

## Troubleshooting

### Eroare "command not found"
Verifică calea exactă la Python:
```bash
which python3.9
# Folosește calea exactă în config.json
```

### Eroare de conexiune la API
Verifică că serverul poate accesa academiadepolitie.com:
```bash
curl -I https://www.academiadepolitie.com/api/internal/profile_for_conversation.php
```

### JSON decode error
Verifică că API-ul returnează JSON valid:
```bash
curl "https://www.academiadepolitie.com/api/internal/profile_for_conversation.php?user_id=4001&user_profile=1"
```