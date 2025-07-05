#!/usr/bin/env python3
"""
Teste para verificar os ajustes finais:
1. Não mostrar CPF na tela
2. Manter última imagem quando não há novos eventos
"""

import requests
import json
import time
from datetime import datetime
import pytz

# Configurações
WEBHOOK_URL = "http://localhost:8000/webhook/"
EVENTOS_URL = "http://localhost:8000/webhook/eventos"
STATUS_URL = "http://localhost:8000/webhook/status"
TIMEZONE_BRASILIA = pytz.timezone('America/Sao_Paulo')

def obter_hora_brasilia():
    return datetime.now(TIMEZONE_BRASILIA)

def verificar_status_sistema():
    """Verifica se o sistema está rodando"""
    try:
        response = requests.get(STATUS_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Sistema está rodando")
            return True
        else:
            print(f"❌ Sistema não está respondendo: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar status: {str(e)}")
        return False

def enviar_webhook(cpf):
    """Envia webhook para um CPF"""
    try:
        payload = {"cpf": cpf}
        response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook enviado para CPF {cpf}: {result['message']}")
            return True
        else:
            print(f"❌ Erro ao enviar webhook para CPF {cpf}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão para CPF {cpf}: {str(e)}")
        return False

def listar_eventos():
    """Lista todos os eventos"""
    try:
        response = requests.get(EVENTOS_URL, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erro ao listar eventos: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro de conexão ao listar eventos: {str(e)}")
        return []

def limpar_eventos():
    """Limpa todos os eventos do sistema"""
    try:
        response = requests.delete(f"{WEBHOOK_URL}eventos", timeout=5)
        if response.status_code == 200:
            print("✅ Todos os eventos foram limpos")
            return True
        else:
            print(f"❌ Erro ao limpar eventos: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao limpar eventos: {str(e)}")
        return False

def verificar_visualizacao_html():
    """Verifica se o HTML da visualização não mostra CPF"""
    print("\n🔍 VERIFICANDO HTML DA VISUALIZAÇÃO:")
    print("-" * 50)
    
    try:
        # Verificar se a página de visualização está acessível
        response = requests.get("http://localhost:8000/visualization1", timeout=5)
        if response.status_code == 200:
            html_content = response.text
            
            # Verificar se não há elementos de CPF
            if "cpf-display" in html_content:
                print("❌ Elemento 'cpf-display' ainda presente no HTML")
                return False
            elif "CPF:" in html_content:
                print("❌ Texto 'CPF:' ainda presente no HTML")
                return False
            else:
                print("✅ CPF removido do HTML da visualização")
                return True
        else:
            print(f"❌ Erro ao acessar visualização: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar HTML: {str(e)}")
        return False

def testar_manter_ultima_imagem():
    """Testa se a última imagem é mantida quando não há novos eventos"""
    print("\n🖼️ TESTANDO MANTER ÚLTIMA IMAGEM:")
    print("-" * 50)
    
    # 1. Limpar eventos
    if not limpar_eventos():
        return False
    
    # 2. Enviar um webhook para criar eventos
    print("📤 Enviando webhook para criar eventos...")
    if not enviar_webhook("11111111111"):
        return False
    
    # 3. Aguardar processamento
    print("⏳ Aguardando 3 segundos para processamento...")
    time.sleep(3)
    
    # 4. Verificar eventos criados
    eventos = listar_eventos()
    if not eventos:
        print("❌ Nenhum evento foi criado")
        return False
    
    print(f"✅ {len(eventos)} eventos criados")
    
    # 5. Aguardar mais tempo para verificar se a última imagem é mantida
    print("⏳ Aguardando 35 segundos para verificar manutenção da última imagem...")
    time.sleep(35)
    
    # 6. Verificar se ainda há eventos (não devem ter sido removidos)
    eventos_depois = listar_eventos()
    if len(eventos_depois) == len(eventos):
        print("✅ Última imagem mantida - eventos não foram removidos")
        return True
    else:
        print(f"❌ Eventos foram removidos: {len(eventos)} -> {len(eventos_depois)}")
        return False

def main():
    """Função principal do teste"""
    print("🧪 TESTE DOS AJUSTES FINAIS")
    print("="*60)
    print(f"⏰ Hora atual (Brasília): {obter_hora_brasilia().strftime('%H:%M:%S')}")
    
    # 1. Verificar se o sistema está rodando
    print(f"\n1️⃣ Verificando status do sistema...")
    if not verificar_status_sistema():
        return False
    
    # 2. Verificar se o CPF foi removido do HTML
    print(f"\n2️⃣ Verificando remoção do CPF do HTML...")
    if not verificar_visualizacao_html():
        print("⚠️  CPF ainda está sendo exibido na visualização")
        return False
    
    # 3. Testar manutenção da última imagem
    print(f"\n3️⃣ Testando manutenção da última imagem...")
    if not testar_manter_ultima_imagem():
        print("⚠️  Última imagem não está sendo mantida corretamente")
        return False
    
    print(f"\n" + "="*60)
    print("🎉 TODOS OS AJUSTES ESTÃO FUNCIONANDO!")
    print("✅ CPF removido da visualização")
    print("✅ Última imagem é mantida quando não há novos eventos")
    print("✅ Sistema funcionando corretamente")
    print("="*60)
    
    return True

if __name__ == "__main__":
    try:
        resultado = main()
        if not resultado:
            print("\n❌ TESTE FALHOU - Verificar problemas")
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {str(e)}") 