#!/usr/bin/env python3
"""
Test script pentru MCP server cu toți parametrii
"""

import asyncio
import json
from server import get_student_data

async def test_tools():
    """Testează get_student_data cu toți parametrii"""
    print("🧪 Testez MCP Server pentru AcademiaDePoliție cu parametrii completi...")
    
    # Test 1: Profil de bază
    print("\n1. Test profil utilizator...")
    try:
        profile = await get_student_data(4001, user_profile=True)
        print(f"✅ Profile: {json.dumps(profile, indent=2, ensure_ascii=False)[:300]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Activități recente
    print("\n2. Test activități recente...")
    try:
        activities = await get_student_data(4001, activitati_recente=3)
        print(f"✅ Activities: {json.dumps(activities, indent=2, ensure_ascii=False)[:300]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Utilizatori compatibili (NOU)
    print("\n3. Test utilizatori compatibili...")
    try:
        compatibili = await get_student_data(4001, utilizatori_compatibili=3, focus="toate", materie=1)
        print(f"✅ Compatibili: {json.dumps(compatibili, indent=2, ensure_ascii=False)[:300]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Instrucțiuni LLM (NOU)
    print("\n4. Test instrucțiuni LLM...")
    try:
        llm_instructions = await get_student_data(4001, activitati_recente=2, instructiuni_llm=True, materie=1)
        print(f"✅ LLM Instructions: {json.dumps(llm_instructions, indent=2, ensure_ascii=False)[:300]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Toate modulele
    print("\n5. Test toate modulele...")
    try:
        all_data = await get_student_data(4001, all_modules=True, materie=1)
        print(f"✅ All modules: {json.dumps(all_data, indent=2, ensure_ascii=False)[:300]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Combinație complexă
    print("\n6. Test combinație complexă...")
    try:
        complex_data = await get_student_data(
            4001, 
            user_profile=True, 
            activitati_recente=2, 
            utilizatori_compatibili=2, 
            focus="judet", 
            instructiuni_llm=True,
            materie=1
        )
        print(f"✅ Complex: {json.dumps(complex_data, indent=2, ensure_ascii=False)[:300]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Test complet cu toți parametrii!")

if __name__ == "__main__":
    asyncio.run(test_tools())