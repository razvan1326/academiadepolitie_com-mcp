#!/usr/bin/env python3
"""
MCP Server pentru AcademiaDePolițe.com - Compatibil Python 3.9
Implementează protocolul Model Context Protocol manual
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

# Token JWT - va fi setat din variabila de mediu sau config
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
    
    Args:
        user_id: ID-ul utilizatorului (obligatoriu)
        user_profile: Include profilul utilizatorului (True/False)
        activitati_recente: Numărul de activități recente de returnat (1-10)
        profil_comportamental: Include profilul comportamental (necesită materie)
        progres_teorie: Include progresul la teorie (True/False)
        analiza_lacunelor: Include analiza lacunelor (True/False)
        utilizatori_compatibili: Numărul de utilizatori compatibili (1-10)
        materie: ID-ul materiei pentru filtrare (opțional)
        only: Filtrare pe tip activitate
        focus: Pentru utilizatori_compatibili - filtrare geografică/temporală
        instructiuni_llm: Transformă recomandările în instrucțiuni pentru LLM
        all_modules: Include toate modulele disponibile (True/False)
    
    Returns:
        Datele studentului conform modulelor solicitate
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