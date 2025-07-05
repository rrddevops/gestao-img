#!/usr/bin/env python3
"""
Script simples para testar o webhook com CPFs do banco
"""

import requests
import time

# CPFs do banco para teste
CPFS = [
    "88888888888", "77777777777", "66666666666", "55555555555", "44444444444",
    "33333333333", "22222222227", "22222222226", "22222222225", "22222222224",
    "22222222223", "22222222222", "22222222221", "11111111119", "11111111118",
    "11111111117", "11111111116", "11111111115", "11111111114", "11111111113",
    "11111111112", "11111111111", "99999999999", "00000000000"
]

def testar_webhook():
    print("🚀 TESTE RÁPIDO DO WEBHOOK")
    print("=" * 50)
    print(f"📋 Total de CPFs: {len(CPFS)}")
    print("=" * 50)
    
    sucessos = 0
    erros = 0
    
    for i, cpf in enumerate(CPFS, 1):
        print(f"[{i}/{len(CPFS)}] Agendando: {cpf}")
        
        try:
            response = requests.post("http://localhost:5002/webhook", 
                                   json={'cpf': cpf}, 
                                   timeout=5)
            
            if response.status_code == 200:
                print(f"   ✅ Sucesso")
                sucessos += 1
            else:
                print(f"   ❌ Erro: {response.status_code}")
                erros += 1
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            erros += 1
        
        # Delay de 1 segundo entre agendamentos
        if i < len(CPFS):
            time.sleep(1)
    
    print("\n" + "=" * 50)
    print("📊 RESUMO")
    print("=" * 50)
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Erros: {erros}")
    print("=" * 50)
    
    if sucessos > 0:
        print("🎉 Teste concluído!")
        print("📺 Acesse as visualizações: http://localhost:8083, 8084, 8085, etc.")

if __name__ == "__main__":
    testar_webhook() 