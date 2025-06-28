#!/usr/bin/env python3
"""
Exemplo de uso do novo sistema de agendamento baseado em datetime
"""

import requests
import json
from datetime import datetime, timedelta
import time

# Configuração
WEBHOOK_URL = "http://localhost:5002/schedule"
STATUS_URL = "http://localhost:5002/schedule-status"

def schedule_person(cpf, entry_time, wait_time):
    """
    Agenda uma pessoa para exibição
    
    Args:
        cpf (str): CPF da pessoa
        entry_time (str): Horário de entrada (HH:MM:SS)
        wait_time (str): Tempo de espera (HH:MM:SS)
    
    Returns:
        dict: Resposta da API
    """
    payload = {
        'cpf': cpf,
        'entry_time': entry_time,
        'wait_time': wait_time
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        return response.json(), response.status_code
    except Exception as e:
        return {'error': str(e)}, 500

def get_schedule_status():
    """Obtém o status atual dos agendamentos"""
    try:
        response = requests.get(STATUS_URL, timeout=5)
        return response.json(), response.status_code
    except Exception as e:
        return {'error': str(e)}, 500

def calculate_display_times(entry_time, wait_time):
    """
    Calcula os horários de exibição para todas as visualizações
    
    Args:
        entry_time (str): Horário de entrada (HH:MM:SS)
        wait_time (str): Tempo de espera (HH:MM:SS)
    
    Returns:
        dict: Horários de exibição por visualização
    """
    entry_dt = datetime.strptime(entry_time, '%H:%M:%S')
    wait_dt = datetime.strptime(wait_time, '%H:%M:%S')
    
    # Calcula primeira exibição
    first_display = entry_dt + timedelta(
        hours=wait_dt.hour,
        minutes=wait_dt.minute,
        seconds=wait_dt.second
    )
    
    # Calcula demais exibições (a cada 10 segundos)
    display_times = {}
    for i in range(6):
        display_time = first_display + timedelta(seconds=i*10)
        display_times[f'visualization{i+1}'] = display_time.strftime('%H:%M:%S')
    
    return display_times

def example_scenario_1():
    """Cenário 1: Fila simples com 3 pessoas"""
    print("=== CENÁRIO 1: Fila Simples ===")
    print("Pessoas entrando em sequência com 30s de espera\n")
    
    # Dados das pessoas
    people = [
        {"cpf": "11111111111", "entry_time": "20:00:00", "wait_time": "00:00:30"},
        {"cpf": "22222222222", "entry_time": "20:00:15", "wait_time": "00:00:30"},
        {"cpf": "33333333333", "entry_time": "20:00:30", "wait_time": "00:00:30"},
    ]
    
    for person in people:
        print(f"Agendando: CPF {person['cpf']}")
        print(f"  Entrada: {person['entry_time']}")
        print(f"  Espera: {person['wait_time']}")
        
        # Calcula horários esperados
        display_times = calculate_display_times(person['entry_time'], person['wait_time'])
        print("  Horários de exibição:")
        for viz, time in display_times.items():
            print(f"    {viz}: {time}")
        
        # Faz o agendamento
        result, status = schedule_person(person['cpf'], person['entry_time'], person['wait_time'])
        
        if status == 200:
            print("  ✅ Agendado com sucesso\n")
        else:
            print(f"  ❌ Erro: {result.get('error', 'Erro desconhecido')}\n")

def example_scenario_2():
    """Cenário 2: Diferentes tempos de espera"""
    print("=== CENÁRIO 2: Diferentes Tempos de Espera ===")
    print("Pessoas com diferentes tempos de espera\n")
    
    # Dados das pessoas
    people = [
        {"cpf": "44444444444", "entry_time": "20:01:00", "wait_time": "00:00:15"},  # 15s
        {"cpf": "55555555555", "entry_time": "20:01:00", "wait_time": "00:00:30"},  # 30s
        {"cpf": "66666666666", "entry_time": "20:01:00", "wait_time": "00:01:00"},  # 1min
    ]
    
    for person in people:
        print(f"Agendando: CPF {person['cpf']}")
        print(f"  Entrada: {person['entry_time']}")
        print(f"  Espera: {person['wait_time']}")
        
        # Calcula horários esperados
        display_times = calculate_display_times(person['entry_time'], person['wait_time'])
        print("  Primeira exibição:")
        print(f"    visualization1: {display_times['visualization1']}")
        
        # Faz o agendamento
        result, status = schedule_person(person['cpf'], person['entry_time'], person['wait_time'])
        
        if status == 200:
            print("  ✅ Agendado com sucesso\n")
        else:
            print(f"  ❌ Erro: {result.get('error', 'Erro desconhecido')}\n")

def example_scenario_3():
    """Cenário 3: Fila grande com ordenação cronológica"""
    print("=== CENÁRIO 3: Fila Grande ===")
    print("Múltiplas pessoas com ordenação cronológica\n")
    
    # Gera dados de teste
    base_time = datetime.strptime("20:02:00", '%H:%M:%S')
    people = []
    
    for i in range(5):
        entry_time = base_time + timedelta(minutes=i*2)  # A cada 2 minutos
        person = {
            "cpf": f"7777777777{i}",
            "entry_time": entry_time.strftime('%H:%M:%S'),
            "wait_time": "00:00:30"
        }
        people.append(person)
    
    print("Agendando 5 pessoas:")
    for person in people:
        print(f"  CPF {person['cpf']}: entrada {person['entry_time']}")
        
        # Faz o agendamento
        result, status = schedule_person(person['cpf'], person['entry_time'], person['wait_time'])
        
        if status != 200:
            print(f"    ❌ Erro: {result.get('error', 'Erro desconhecido')}")
    
    print("\n✅ Todas as pessoas agendadas!")

def monitor_system():
    """Monitora o sistema em tempo real"""
    print("\n=== MONITORAMENTO DO SISTEMA ===")
    
    for i in range(5):  # Monitora por 5 iterações
        print(f"\n--- Verificação {i+1} ---")
        
        status, code = get_schedule_status()
        
        if code == 200:
            print(f"Total de jobs: {status.get('total_jobs', 0)}")
            
            current_images = status.get('current_images', {})
            print("Imagens atualmente exibidas:")
            for viz, cpf in current_images.items():
                if cpf:
                    print(f"  {viz}: {cpf}")
                else:
                    print(f"  {viz}: Nenhuma")
            
            scheduled_jobs = status.get('scheduled_jobs', {})
            if scheduled_jobs:
                print("Próximos agendamentos:")
                for cpf, viz_schedule in list(scheduled_jobs.items())[:3]:  # Mostra apenas 3
                    print(f"  CPF {cpf}:")
                    for viz, job_info in viz_schedule.items():
                        scheduled_time = job_info.get('scheduled_time', 'N/A')
                        print(f"    {viz}: {scheduled_time}")
        else:
            print(f"❌ Erro ao obter status: {status.get('error', 'Erro desconhecido')}")
        
        time.sleep(2)  # Aguarda 2 segundos

def main():
    """Função principal"""
    print("🚀 Exemplo de Uso do Sistema de Agendamento")
    print("=" * 60)
    
    # Executa os cenários
    example_scenario_1()
    example_scenario_2()
    example_scenario_3()
    
    # Monitora o sistema
    monitor_system()
    
    print("\n✅ Exemplos concluídos!")
    print("\nPara testar manualmente:")
    print("1. Acesse http://localhost:5002/ para ver a interface")
    print("2. Use o script test_scheduler.py para testes rápidos")
    print("3. Monitore as visualizações em tempo real")

if __name__ == "__main__":
    main() 