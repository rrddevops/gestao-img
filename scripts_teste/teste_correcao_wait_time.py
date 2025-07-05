#!/usr/bin/env python3
"""
Script para testar se a correção do wait_time funcionou.
Agenda um CPF e verifica se os wait_time estão corretos no banco.
"""

import requests
import json
from datetime import datetime

# Configuração
WEBHOOK_URL = "http://localhost:5002/webhook"
TEST_CPF = "99999999999"  # CPF de teste

def agendar_cpf():
    """Agenda um CPF e mostra os horários esperados"""
    try:
        print(f"🔄 Agendando CPF {TEST_CPF}...")
        data = {'cpf': TEST_CPF}
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ CPF {TEST_CPF} agendado com sucesso!")
            
            # Mostra informações do agendamento
            entry_time = result.get('entry_time', 'N/A')
            wait_time = result.get('wait_time', 'N/A')
            
            print(f"\n📋 INFORMAÇÕES DO AGENDAMENTO:")
            print(f"• CPF: {TEST_CPF}")
            print(f"• Horário de entrada: {entry_time}")
            print(f"• Tempo de espera (primeira visualização): {wait_time}")
            
            return True
        else:
            print(f"❌ Erro ao agendar CPF {TEST_CPF}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def verificar_configuracao():
    """Verifica a configuração das visualizações"""
    try:
        print(f"\n📊 Verificando configuração das visualizações...")
        response = requests.get("http://localhost:8083/config", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            viz_config = data.get('visualization_config', {})
            
            print(f"✅ Configuração obtida com sucesso!")
            print(f"📋 CONFIGURAÇÃO DAS VISUALIZAÇÕES:")
            
            for viz_name, config in sorted(viz_config.items()):
                delay = config.get('delay_seconds', 0)
                display = config.get('display_seconds', 0)
                port = config.get('port', 0)
                print(f"• {viz_name} (porta {port}): delay={delay}s, display={display}s")
            
            return viz_config
        else:
            print(f"❌ Erro ao obter configuração: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao verificar configuração: {e}")
        return None

def verificar_agendamentos():
    """Verifica os agendamentos no banco"""
    try:
        print(f"\n📊 Verificando agendamentos no banco...")
        response = requests.get("http://localhost:8083/schedule-details", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            entries = data.get('schedule_entries', [])
            
            # Filtra apenas os agendamentos do CPF de teste
            test_entries = [entry for entry in entries if entry.get('cpf') == TEST_CPF]
            
            if test_entries:
                print(f"✅ Encontrados {len(test_entries)} agendamentos para CPF {TEST_CPF}")
                print(f"📋 AGENDAMENTOS NO BANCO:")
                
                for entry in test_entries:
                    viz_name = entry.get('visualization_name', 'N/A')
                    entry_time = entry.get('entry_time', 'N/A')
                    wait_time = entry.get('wait_time', 'N/A')
                    display_time = entry.get('display_time', 'N/A')
                    display_datetime = entry.get('display_datetime', 'N/A')
                    
                    print(f"• {viz_name}: entry={entry_time}, wait={wait_time}, display={display_time} ({display_datetime})")
                
                return test_entries
            else:
                print(f"⚠️  Nenhum agendamento encontrado para CPF {TEST_CPF}")
                return []
        else:
            print(f"❌ Erro ao obter agendamentos: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao verificar agendamentos: {e}")
        return None

def main():
    print("🔧 TESTE DA CORREÇÃO DO WAIT_TIME")
    print("=" * 60)
    
    # 1. Verifica configuração
    viz_config = verificar_configuracao()
    if not viz_config:
        print("❌ Não foi possível obter a configuração. Abortando teste.")
        return
    
    # 2. Agenda CPF
    if not agendar_cpf():
        print("❌ Falha no agendamento. Abortando teste.")
        return
    
    # 3. Verifica agendamentos
    entries = verificar_agendamentos()
    if entries is None:
        print("❌ Falha ao verificar agendamentos. Abortando teste.")
        return
    
    # 4. Análise dos resultados
    print(f"\n🎯 ANÁLISE DOS RESULTADOS:")
    
    if entries:
        print(f"✅ Agendamentos criados com sucesso!")
        
        # Verifica se os wait_time estão corretos
        for entry in entries:
            viz_name = entry.get('visualization_name', '')
            wait_time = entry.get('wait_time', '')
            expected_delay = viz_config.get(viz_name, {}).get('delay_seconds', 0)
            
            # Converte wait_time para segundos para comparação
            try:
                wait_parts = wait_time.split(':')
                wait_seconds = int(wait_parts[0]) * 3600 + int(wait_parts[1]) * 60 + int(wait_parts[2])
                
                if wait_seconds == expected_delay:
                    print(f"✅ {viz_name}: wait_time={wait_time} (correto)")
                else:
                    print(f"❌ {viz_name}: wait_time={wait_time} (esperado: {expected_delay}s)")
            except:
                print(f"⚠️  {viz_name}: wait_time={wait_time} (formato inválido)")
        
        print(f"\n📺 URLs DAS VISUALIZAÇÕES:")
        for viz_name, config in sorted(viz_config.items()):
            port = config.get('port', 0)
            print(f"• {viz_name}: http://localhost:{port}/view/")
        
        print(f"\n⏰ Aguarde alguns segundos e verifique se as imagens aparecem nas visualizações!")
    else:
        print(f"❌ Nenhum agendamento foi criado")

if __name__ == "__main__":
    main() 