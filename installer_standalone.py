#!/usr/bin/env python3
"""
Installer standalone pentru AcademiaDePolițe MCP
Se va compila într-un singur .exe/.app cu PyInstaller
"""

import os
import sys
import json
import platform
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import threading
import base64

# Server MCP embedded (va fi inclus în .exe)
SERVER_PY39_CODE = '''#!/usr/bin/env python3
"""
MCP Server pentru AcademiaDePolițe.com - Embedded Version
"""

import asyncio
import json
import sys
import urllib.request
import urllib.parse
import urllib.error
from typing import Any, Dict, List, Optional, Union

# Configurare API intern
INTERNAL_API_BASE = "https://www.academiadepolitie.com/api/internal"
DEFAULT_HEADERS = {
    "User-Agent": "MCP-Server/1.0",
    "Content-Type": "application/json"
}

# Token JWT - va fi setat din variabila de mediu
JWT_TOKEN = None

class MCPServer:
    def __init__(self):
        self.tools = {}
        self.resources = {}
        
    def register_tool(self, name: str, description: str, parameters: Dict[str, Any], handler):
        """Înregistrează un tool MCP"""
        self.tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": {
                "type": "object",
                "properties": parameters.get("properties", {}),
                "required": parameters.get("required", [])
            },
            "handler": handler
        }
    
    def register_resource(self, uri: str, name: str, description: str, handler):
        """Înregistrează un resource MCP"""
        self.resources[uri] = {
            "uri": uri,
            "name": name,
            "description": description,
            "handler": handler
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Procesează cereri MCP"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": True},
                            "resources": {"subscribe": True, "listChanged": True}
                        },
                        "serverInfo": {
                            "name": "academiadepolitie",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": tool_name,
                                "description": tool_info["description"],
                                "inputSchema": tool_info["inputSchema"]
                            }
                            for tool_name, tool_info in self.tools.items()
                        ]
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name in self.tools:
                    result = await self.tools[tool_name]["handler"](**arguments)
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result, indent=2, ensure_ascii=False)
                                }
                            ]
                        }
                    }
                else:
                    raise Exception(f"Tool necunoscut: {tool_name}")
            
            elif method == "resources/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "resources": [
                            {
                                "uri": resource_info["uri"],
                                "name": resource_info["name"],
                                "description": resource_info["description"]
                            }
                            for resource_info in self.resources.values()
                        ]
                    }
                }
            
            elif method == "resources/read":
                uri = params.get("uri")
                if uri in self.resources:
                    content = await self.resources[uri]["handler"]()
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "contents": [
                                {
                                    "uri": uri,
                                    "mimeType": "application/json",
                                    "text": content
                                }
                            ]
                        }
                    }
                else:
                    raise Exception(f"Resource necunoscut: {uri}")
            
            else:
                raise Exception(f"Metodă necunoscută: {method}")
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }

async def call_internal_api(params: Dict[str, Any]) -> Dict[str, Any]:
    """Cheamă API-ul intern cu parametrii specificați"""
    try:
        # Adaugă tokenul JWT dacă există
        headers = DEFAULT_HEADERS.copy()
        if JWT_TOKEN:
            headers["Authorization"] = f"Bearer {JWT_TOKEN}"
        
        url = f"{INTERNAL_API_BASE}/profile_for_conversation.php"
        query_string = urllib.parse.urlencode(params)
        full_url = f"{url}?{query_string}"
        
        req = urllib.request.Request(full_url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
    except Exception as e:
        return {"error": f"API call failed: {str(e)}"}

async def get_student_data(
    user_id: int,
    user_profile: bool = False,
    activitati_recente: Optional[int] = None,
    profil_comportamental: bool = False,
    progres_teorie: bool = False,
    analiza_lacunelor: bool = False,
    utilizatori_compatibili: Optional[int] = None,
    materie: Optional[int] = None,
    only: Optional[str] = None,
    focus: Optional[str] = None,
    instructiuni_llm: bool = False,
    all_modules: bool = False
) -> Dict[str, Any]:
    """
    Obține datele studentului conform API-ului modular intern
    """
    # Construiește parametrii conform API-ului intern
    params = {"user_id": user_id}
    
    if all_modules:
        params["all"] = 1
    else:
        if user_profile:
            params["user_profile"] = 1
        if activitati_recente is not None:
            params["activitati_recente"] = min(max(activitati_recente, 1), 10)
        if profil_comportamental:
            params["profil_comportamental"] = 1
        if progres_teorie:
            params["progres_teorie"] = 1
        if analiza_lacunelor:
            params["analiza_lacunelor"] = 1
        if utilizatori_compatibili is not None:
            params["utilizatori_compatibili"] = min(max(utilizatori_compatibili, 1), 10)
        if instructiuni_llm:
            params["instructiuni_llm"] = 1
    
    if materie:
        params["materie"] = materie
    
    if focus:
        # Validează valorile permise pentru 'focus'
        valid_focus_values = ["toate", "judet", "an_admitere", "judet_si_an"]
        if focus in valid_focus_values:
            params["focus"] = focus
    
    if only:
        # Validează valorile permise pentru 'only'
        valid_only_values = [
            "a_citit_materia",
            "a_simulat_examenul", 
            "s_a_testat_pe_lectie_capitol",
            "are_lacune_de_clarificat",
            "a_notat_la_lectii",
            "are_provocari_sustinute",
            "este_in_eroare_la"
        ]
        if only in valid_only_values:
            params["only"] = only
    
    result = await call_internal_api(params)
    
    if "error" in result:
        return {"error": result["error"]}
    
    return {
        "tool": "get_student_data",
        "user_id": user_id,
        "modules_requested": {
            "user_profile": user_profile,
            "activitati_recente": activitati_recente,
            "profil_comportamental": profil_comportamental,
            "progres_teorie": progres_teorie,
            "analiza_lacunelor": analiza_lacunelor,
            "utilizatori_compatibili": utilizatori_compatibili,
            "instructiuni_llm": instructiuni_llm,
            "all_modules": all_modules
        },
        "filters": {
            "materie": materie,
            "only": only,
            "focus": focus
        },
        "data": result,
        "metadata": result.get("metadata", {})
    }

async def get_user_profile_resource(user_id: int) -> str:
    """Resource pentru profilul utilizatorului"""
    result = await get_student_data(user_id, user_profile=True)
    return json.dumps(result, indent=2, ensure_ascii=False)

async def get_user_complete_data_resource(user_id: int) -> str:
    """Resource pentru toate datele utilizatorului"""
    result = await get_student_data(user_id, all_modules=True)
    return json.dumps(result, indent=2, ensure_ascii=False)

async def main():
    """Funcția principală care rulează serverul MCP"""
    global JWT_TOKEN
    
    # Citește JWT token din variabila de mediu
    import os
    JWT_TOKEN = os.environ.get('ACADEMIADEPOLITIE_JWT_TOKEN')
    
    if not JWT_TOKEN:
        print("⚠️  ATENȚIE: JWT_TOKEN nu este setat! API-ul nu va funcționa corect.", file=sys.stderr)
        print("Setează variabila de mediu ACADEMIADEPOLITIE_JWT_TOKEN cu tokenul tău JWT", file=sys.stderr)
    
    server = MCPServer()
    
    # Înregistrează tool-ul principal
    server.register_tool(
        "get_student_data",
        "Obține datele studentului conform API-ului modular intern AcademiaDePoliție",
        {
            "properties": {
                "user_id": {"type": "integer", "description": "ID-ul utilizatorului (obligatoriu)"},
                "user_profile": {"type": "boolean", "description": "Include profilul utilizatorului"},
                "activitati_recente": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Numărul de activități recente"},
                "profil_comportamental": {"type": "boolean", "description": "Include profilul comportamental"},
                "progres_teorie": {"type": "boolean", "description": "Include progresul la teorie"},
                "analiza_lacunelor": {"type": "boolean", "description": "Include analiza lacunelor"},
                "utilizatori_compatibili": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Numărul de utilizatori compatibili"},
                "materie": {"type": "integer", "description": "ID-ul materiei pentru filtrare"},
                "only": {"type": "string", "description": "Filtrare pe tip activitate"},
                "focus": {"type": "string", "enum": ["toate", "judet", "an_admitere", "judet_si_an"], "description": "Filtrare geografică/temporală"},
                "instructiuni_llm": {"type": "boolean", "description": "Transformă recomandările în instrucțiuni LLM"},
                "all_modules": {"type": "boolean", "description": "Include toate modulele"}
            },
            "required": ["user_id"]
        },
        get_student_data
    )
    
    # Înregistrează resources
    server.register_resource(
        "user://profile/{user_id}",
        "User Profile",
        "Profilul utilizatorului",
        lambda: get_user_profile_resource(4001)  # Default user pentru demo
    )
    
    server.register_resource(
        "user://data/{user_id}",
        "User Complete Data", 
        "Toate datele utilizatorului",
        lambda: get_user_complete_data_resource(4001)  # Default user pentru demo
    )
    
    # Citește cereri JSON-RPC de la stdin și răspunde la stdout
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            request = json.loads(line.strip())
            response = await server.handle_request(request)
            
            print(json.dumps(response), flush=True)
            
        except json.JSONDecodeError:
            continue
        except KeyboardInterrupt:
            break
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Server error: {str(e)}"
                }
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    asyncio.run(main())
'''

class MCPInstallerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AcademiaDePolițe MCP Installer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Variabile
        self.jwt_token = tk.StringVar()
        self.status_text = tk.StringVar(value="Pregătit pentru instalare")
        
        # Detectare sistem
        self.system = platform.system()
        self.home = Path.home()
        self.install_dir = self.home / ".academiadepolitie-mcp"
        
        # Config paths
        self.config_paths = {
            "Windows": [
                self.home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json",
                self.home / "AppData" / "Local" / "Claude" / "claude_desktop_config.json"
            ],
            "Darwin": [
                self.home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
                self.home / ".config" / "claude-desktop" / "config.json"
            ],
            "Linux": [
                self.home / ".config" / "claude-desktop" / "config.json",
                self.home / ".config" / "Claude" / "claude_desktop_config.json"
            ]
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Creează interfața grafică"""
        # Header
        header_frame = ttk.Frame(self.root, padding="20")
        header_frame.pack(fill=tk.X)
        
        logo_label = ttk.Label(header_frame, 
                              text="🎓 AcademiaDePolițe MCP", 
                              font=('Arial', 20, 'bold'))
        logo_label.pack()
        
        subtitle = ttk.Label(header_frame, 
                           text="Instalare automată pentru Claude Desktop",
                           font=('Arial', 12))
        subtitle.pack()
        
        # Separator
        ttk.Separator(self.root, orient='horizontal').pack(fill=tk.X, padx=20)
        
        # Main content
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instructions = ttk.LabelFrame(main_frame, text="Instrucțiuni", padding="10")
        instructions.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(instructions, text="1. Intră în contul tău pe academiadepolitie.com", 
                 wraplength=500).pack(anchor=tk.W)
        ttk.Label(instructions, text="2. Mergi la Setări → API Access", 
                 wraplength=500).pack(anchor=tk.W)
        ttk.Label(instructions, text="3. Copiază JWT Token (începe cu 'eyJ...')", 
                 wraplength=500).pack(anchor=tk.W)
        ttk.Label(instructions, text="4. Lipește token-ul mai jos și apasă Instalează", 
                 wraplength=500).pack(anchor=tk.W)
        
        # Token input
        token_frame = ttk.LabelFrame(main_frame, text="JWT Token", padding="10")
        token_frame.pack(fill=tk.X, pady=(0, 20))
        
        token_entry = ttk.Entry(token_frame, textvariable=self.jwt_token, width=60, show="*")
        token_entry.pack(fill=tk.X)
        
        # Show/Hide token
        def toggle_token():
            if token_entry['show'] == '*':
                token_entry['show'] = ''
                show_btn.config(text='Ascunde')
            else:
                token_entry['show'] = '*'
                show_btn.config(text='Arată')
                
        show_btn = ttk.Button(token_frame, text="Arată", command=toggle_token, width=10)
        show_btn.pack(pady=(5, 0))
        
        # Install button
        install_btn = ttk.Button(main_frame, 
                               text="🚀 Instalează", 
                               command=self.install,
                               style='Accent.TButton')
        install_btn.pack(pady=10)
        
        # Progress
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Status
        status_label = ttk.Label(main_frame, textvariable=self.status_text)
        status_label.pack()
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log instalare", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=60)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def log(self, message):
        """Adaugă mesaj în log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def update_status(self, message):
        """Actualizează status"""
        self.status_text.set(message)
        self.root.update()
        
    def install(self):
        """Rulează instalarea"""
        # Validare token
        token = self.jwt_token.get().strip()
        if not token or not token.startswith("eyJ") or len(token) < 50:
            messagebox.showerror("Token Invalid", 
                               "Token-ul trebuie să înceapă cu 'eyJ' și să aibă minim 50 caractere")
            return
            
        # Dezactivează butonul
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.config(state='disabled')
                
        # Start progress
        self.progress.start()
        
        # Rulează instalarea în thread separat
        thread = threading.Thread(target=self.run_installation, args=(token,))
        thread.daemon = True
        thread.start()
        
    def run_installation(self, token):
        """Procesul de instalare"""
        try:
            self.log("🚀 Start instalare...")
            self.update_status("Creez directoare...")
            
            # 1. Creează directorul
            self.install_dir.mkdir(parents=True, exist_ok=True)
            self.log(f"✅ Director creat: {self.install_dir}")
            
            # 2. Salvează server script
            self.update_status("Salvez server MCP...")
            server_path = self.install_dir / "server.py"
            with open(server_path, 'w', encoding='utf-8') as f:
                f.write(SERVER_PY39_CODE)
            self.log(f"✅ Server salvat: {server_path}")
            
            # 3. Găsește Python
            self.update_status("Verific Python...")
            python_cmd = sys.executable
            self.log(f"✅ Python găsit: {python_cmd}")
            
            # 4. Găsește/creează config
            self.update_status("Configurez Claude Desktop...")
            config_path = self.find_or_create_config()
            self.log(f"✅ Config găsit: {config_path}")
            
            # 5. Actualizează config
            self.update_config(config_path, python_cmd, str(server_path), token)
            self.log("✅ Configurație actualizată")
            
            # 6. Creează shortcut desktop (Windows)
            if self.system == "Windows":
                self.create_desktop_shortcut()
                
            # Success
            self.progress.stop()
            self.update_status("✅ Instalare completă!")
            self.log("\n" + "="*50)
            self.log("🎉 INSTALARE COMPLETĂ!")
            self.log("="*50)
            self.log("\nPași următori:")
            self.log("1. Închide această fereastră")
            self.log("2. Restart Claude Desktop")
            self.log("3. Vei vedea 'academiadepolitie' în lista MCP")
            self.log("\nPoți folosi comenzi precum:")
            self.log('- "Arată-mi profilul meu"')
            self.log('- "Care sunt ultimele mele activități?"')
            
            messagebox.showinfo("Succes", 
                              "Instalare completă!\n\nRestart Claude Desktop pentru a activa MCP.")
            
        except Exception as e:
            self.progress.stop()
            self.update_status(f"❌ Eroare: {str(e)}")
            self.log(f"\n❌ EROARE: {str(e)}")
            messagebox.showerror("Eroare Instalare", f"A apărut o eroare:\n\n{str(e)}")
            
    def find_or_create_config(self):
        """Găsește sau creează config file"""
        # Caută în toate locațiile
        for path in self.config_paths.get(self.system, []):
            if path.exists():
                return path
                
        # Creează în locația default
        if self.system == "Windows":
            config_path = self.config_paths["Windows"][0]
        elif self.system == "Darwin":
            config_path = self.config_paths["Darwin"][0]
        else:
            config_path = self.config_paths["Linux"][0]
            
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump({"mcp": {"servers": {}}}, f, indent=2)
            
        return config_path
        
    def update_config(self, config_path, python_cmd, server_path, token):
        """Actualizează configurația"""
        # Citește config existent
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except:
            config = {}
            
        # Asigură structura
        if "mcp" not in config:
            config["mcp"] = {}
        if "servers" not in config["mcp"]:
            config["mcp"]["servers"] = {}
            
        # Adaugă serverul
        config["mcp"]["servers"]["academiadepolitie"] = {
            "command": python_cmd,
            "args": [server_path],
            "env": {
                "ACADEMIADEPOLITIE_JWT_TOKEN": token
            }
        }
        
        # Salvează
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
    def create_desktop_shortcut(self):
        """Creează shortcut pe desktop (Windows)"""
        try:
            desktop = self.home / "Desktop"
            if desktop.exists():
                shortcut = desktop / "AcademiaDePolițe MCP Settings.url"
                with open(shortcut, 'w') as f:
                    f.write("[InternetShortcut]\n")
                    f.write("URL=https://www.academiadepolitie.com/cont_elev_setari\n")
                self.log(f"✅ Shortcut creat pe Desktop")
        except:
            pass  # Nu e critic
            
    def run(self):
        """Pornește GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    # Dacă rulează cu --console, folosește versiunea text
    if len(sys.argv) > 1 and sys.argv[1] == "--console":
        # Versiune text pentru debugging
        print("Folosește versiunea GUI pentru instalare")
        sys.exit(1)
    else:
        # GUI
        app = MCPInstallerGUI()
        app.run()