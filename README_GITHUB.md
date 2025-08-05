# AcademiaDePolițe MCP Server

Integrare oficială pentru [AcademiaDePolițe.com](https://www.academiadepolitie.com) cu Claude Desktop prin Model Context Protocol (MCP).

## 🚀 Instalare rapidă

### Windows
1. Descarcă [AcademiaDePolitie_MCP_Setup.exe](../../releases/latest)
2. Rulează installer-ul
3. Introdu JWT token din contul tău
4. Restart Claude Desktop

### macOS
1. Descarcă [AcademiaDePolitie_MCP_Installer.app.zip](../../releases/latest)
2. Dezarhivează și rulează aplicația
3. Introdu JWT token din contul tău
4. Restart Claude Desktop

### Linux
1. Descarcă [AcademiaDePolitie_MCP_Installer_Linux](../../releases/latest)
2. `chmod +x AcademiaDePolitie_MCP_Installer_Linux`
3. `./AcademiaDePolitie_MCP_Installer_Linux`
4. Introdu JWT token și restart Claude Desktop

## 📝 Obținerea JWT Token

1. Conectează-te pe [AcademiaDePolițe.com](https://www.academiadepolitie.com)
2. Mergi la **Setări** → **API Access**
3. Copiază token-ul JWT (începe cu `eyJ...`)

## 🎯 Ce poți face

După instalare, în Claude Desktop poți folosi comenzi precum:

- **"Arată-mi profilul meu"** - Vezi detalii despre cont și progres
- **"Care sunt ultimele mele activități?"** - Vezi activitatea recentă
- **"Analizează-mi lacunele la Matematică"** - Analiza detaliată pe materie
- **"Găsește 3 colegi pentru studiu în grup"** - Peer matching inteligent
- **"Vreau recomandări personalizate"** - Sugestii bazate pe performanță

## 🛠️ Instalare manuală (dezvoltatori)

```bash
# Clonează repository
git clone https://github.com/academiadepolitie/mcp-server.git
cd mcp-server

# Instalează dependențe
pip install -r requirements.txt

# Configurează Claude Desktop
# Adaugă în ~/.config/claude-desktop/config.json:
{
  "mcp": {
    "servers": {
      "academiadepolitie": {
        "command": "python",
        "args": ["path/to/server_py39.py"],
        "env": {
          "ACADEMIADEPOLITIE_JWT_TOKEN": "your-jwt-token"
        }
      }
    }
  }
}
```

## 📖 Documentație API

Serverul MCP expune următoarele funcționalități:

### Tool principal: `get_student_data`

Parametri disponibili:
- `user_id` - ID utilizator (obligatoriu)
- `user_profile` - Include profilul complet
- `activitati_recente` - Număr activități (1-10)
- `profil_comportamental` - Analiză comportamentală
- `progres_teorie` - Progres la teorie
- `analiza_lacunelor` - Lacune identificate
- `utilizatori_compatibili` - Găsește colegi compatibili
- `materie` - Filtrare pe materie
- `focus` - Filtrare geografică (județ/an)
- `instructiuni_llm` - Format optimizat pentru AI

## 🔒 Securitate

- Token-ul JWT este stocat local și criptat
- Comunicarea se face prin HTTPS
- Nu se stochează date personale în MCP server

## 🐛 Probleme cunoscute

- Claude Desktop trebuie restartat după instalare
- Pe macOS poate fi necesară permisiunea din Security Settings

## 📞 Suport

- Email: api@academiadepolitie.com
- Forum: [forum.academiadepolitie.com](https://forum.academiadepolitie.com)
- Issues: [GitHub Issues](../../issues)

## 📄 Licență

Copyright © 2024 AcademiaDePolițe.com. Toate drepturile rezervate.