#!/usr/bin/env python3
"""
Test pentru MCP server Python 3.9 compatibil
"""

import asyncio
import json
from server_py39 import get_student_data

async def test_all_features():
    """Testează toate funcționalitățile serverului"""
    print("🧪 Testez MCP Server Python 3.9 pentru AcademiaDePoliție...")
    
    tests = [
        {
            "name": "Profil utilizator",
            "args": {"user_id": 4001, "user_profile": True}
        },
        {
            "name": "Activități recente",
            "args": {"user_id": 4001, "activitati_recente": 3}
        },
        {
            "name": "Utilizatori compatibili",
            "args": {"user_id": 4001, "utilizatori_compatibili": 3, "focus": "toate", "materie": 1}
        },
        {
            "name": "Instrucțiuni LLM",
            "args": {"user_id": 4001, "activitati_recente": 2, "instructiuni_llm": True, "materie": 1}
        },
        {
            "name": "Toate modulele",
            "args": {"user_id": 4001, "all_modules": True, "materie": 1}
        },
        {
            "name": "Combinație complexă",
            "args": {
                "user_id": 4001,
                "user_profile": True,
                "activitati_recente": 2,
                "utilizatori_compatibili": 2,
                "focus": "judet",
                "instructiuni_llm": True,
                "materie": 1
            }
        }
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n{i}. Test {test['name']}...")
        try:
            result = await get_student_data(**test['args'])
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                # Afișează un preview scurt al rezultatului
                result_str = json.dumps(result, indent=2, ensure_ascii=False)
                preview = result_str[:400] + "..." if len(result_str) > 400 else result_str
                print(f"✅ Success: {preview}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n🎉 Teste complete!")

if __name__ == "__main__":
    asyncio.run(test_all_features())