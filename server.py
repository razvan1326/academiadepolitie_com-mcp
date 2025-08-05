#!/usr/bin/env python3
"""
MCP Server pentru AcademiaDePolițe.com
Conform documentației oficiale Model Context Protocol
"""

import asyncio
import json
import sys
import httpx
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from mcp.types import Resource, Tool, TextContent
from pydantic import BaseModel

# Inițializare MCP server
mcp = FastMCP("academiadepolitie")

# Configurare API intern
INTERNAL_API_BASE = "https://www.academiadepolitie.com/api/internal"
DEFAULT_HEADERS = {
    "User-Agent": "MCP-Server/1.0",
    "Content-Type": "application/json"
}

class UserProfileRequest(BaseModel):
    user_id: int
    materie: Optional[int] = None

class GapsAnalysisRequest(BaseModel):
    user_id: int
    materie: Optional[int] = None

class PerformanceRequest(BaseModel):
    user_id: int
    materie: Optional[int] = None

async def call_internal_api(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Cheamă API-ul intern cu parametrii specificați"""
    async with httpx.AsyncClient() as client:
        try:
            url = f"{INTERNAL_API_BASE}/profile_for_conversation.php"
            response = await client.get(url, params=params, headers=DEFAULT_HEADERS, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"API call failed: {str(e)}"}

@mcp.tool()
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
        activitati_recente: Numărul de activități recente de returnat (1-10). 
                           Exemplu: 1=ultima activitate, 5=ultimele 5 activități, 10=ultimele 10 activități
        profil_comportamental: Include profilul comportamental (necesită materie)
        progres_teorie: Include progresul la teorie (True/False)
        analiza_lacunelor: Include analiza lacunelor (True/False)
        utilizatori_compatibili: Numărul de utilizatori compatibili (1-10) pentru peer matching și colaborare
        materie: ID-ul materiei pentru filtrare (opțional)
        only: Filtrare pe tip activitate: 'a_simulat_examenul', 'are_lacune_de_clarificat', 
              'a_citit_materia', 's_a_testat_pe_lectie_capitol', 'a_notat_la_lectii', 
              'are_provocari_sustinute', 'este_in_eroare_la'
        focus: Pentru utilizatori_compatibili - filtrare geografică/temporală: 'toate', 'judet', 'an_admitere', 'judet_si_an'
        instructiuni_llm: Transformă recomandările în instrucțiuni pentru LLM (True/False)
        all_modules: Include toate modulele disponibile (True/False)
    
    Returns:
        Datele studentului conform modulelor solicitate
        
    Examples:
        - get_student_data(4001, user_profile=True) → doar profilul
        - get_student_data(4001, activitati_recente=1) → ultima activitate
        - get_student_data(4001, activitati_recente=5, only="a_simulat_examenul") → ultimele 5 simulări
        - get_student_data(4001, utilizatori_compatibili=3, focus="judet") → 3 utilizatori compatibili din același județ
        - get_student_data(4001, activitati_recente=3, instructiuni_llm=True) → activități cu instrucțiuni LLM
        - get_student_data(4001, all_modules=True) → toate datele
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
    
    result = await call_internal_api("modular", params)
    
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

# Tool-urile de mai sus sunt înlocuite cu get_student_data modular

@mcp.resource("user://profile/{user_id}")
async def get_user_profile_resource(user_id: int) -> str:
    """Resource pentru profilul utilizatorului"""
    result = await get_student_data(user_id, user_profile=True)
    return json.dumps(result, indent=2, ensure_ascii=False)

@mcp.resource("user://data/{user_id}")
async def get_user_complete_data_resource(user_id: int) -> str:
    """Resource pentru toate datele utilizatorului"""
    result = await get_student_data(user_id, all_modules=True)
    return json.dumps(result, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # Rulează serverul MCP prin stdio
    mcp.run()