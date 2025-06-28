#!/usr/bin/env python3
"""
Script para testar o sistema completo de gerenciamento de imagens
Inclui upload de imagem e agendamento de exibição
"""

import requests
import json
import os
import time
from datetime import datetime, timedelta

# Configuração
UPLOAD_URL = "http://localhost:5001/upload"
SCHEDULE_URL = "http://localhost:5002/schedule"
STATUS_URL = "http://localhost:5002/schedule-status"

def create_test_image():
    """Cria uma imagem de teste simples"""
    from PIL import Image, ImageDraw, ImageFont
    
    # Cria uma imagem 300x200 com texto
    img = Image.new('RGB', (300, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Adiciona texto
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 80), "Imagem de Teste", fill='black', font=font)
    draw.text((50, 110), f"Gerada em: {datetime.now().strftime('%H:%M:%S')}", fill='blue', font=font)
    
    # Salva a imagem
    filename = "test_image.jpg"
    img.save(filename, "JPEG")
    return filename

def upload_image(cpf, image_path):
    """Faz upload de uma imagem"""
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {'cpf': cpf}
            
            response = requests.post(UPLOAD_URL, files=files, data=data, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Imagem do CPF {cpf} enviada com sucesso")
                return True
            else:
                print(f"❌ Erro ao enviar imagem: {response.status_code}")
                print(f"Resposta: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao fazer upload: {e}")
        return False

def schedule_display(cpf, entry_time, wait_time):
    """Agenda a exibição de uma imagem"""
    payload = {
        'cpf': cpf,
        'entry_time': entry_time,
        'wait_time': wait_time
    }
    
    try:
        response = requests.post(SCHEDULE_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Agendamento realizado para CPF {cpf}")
            print(f"   Entrada: {entry_time}, Espera: {wait_time}")
            return True
        else:
            print(f"❌ Erro no agendamento: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao agendar: {e}")
        return False

def check_status():
    """Verifica o status do sistema"""
    try:
        response = requests.get(STATUS_URL, timeout=5)
        
        if response.status_code == 200:
            status = response.json()
            print(f"\n📊 Status do Sistema:")
            print(f"   Total de jobs: {status.get('total_jobs', 0)}")
            
            current_images = status.get('current_images', {})
            active_count = sum(1 for cpf in current_images.values() if cpf)
            print(f"   Visualizações ativas: {active_count}/6")
            
            return status
        else:
            print(f"❌ Erro ao obter status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao verificar status: {e}")
        return None

def test_complete_flow():
    """Testa o fluxo completo do sistema"""
    print("🚀 Teste Completo do Sistema de Gerenciamento de Imagens")
    print("=" * 70)
    
    # 1. Criar imagem de teste
    print("\n1️⃣ Criando imagem de teste...")
    try:
        image_path = create_test_image()
        print(f"✅ Imagem criada: {image_path}")
    except ImportError:
        print("⚠️  PIL não disponível, usando imagem existente...")
        image_path = "test_image.jpg"
        if not os.path.exists(image_path):
            print("❌ Nenhuma imagem de teste encontrada")
            return
    except Exception as e:
        print(f"❌ Erro ao criar imagem: {e}")
        return
    
    # 2. Upload de múltiplas imagens
    print("\n2️⃣ Fazendo upload de imagens...")
    test_cpfs = [
        "11111111111",
        "22222222222", 
        "33333333333",
        "44444444444",
        "55555555555"
    ]
    
    for cpf in test_cpfs:
        if upload_image(cpf, image_path):
            time.sleep(0.5)  # Pequena pausa entre uploads
    
    # 3. Agendamento de exibições
    print("\n3️⃣ Agendando exibições...")
    
    # Calcula horários baseados no tempo atual
    now = datetime.now()
    base_time = now.replace(second=0, microsecond=0) + timedelta(minutes=1)  # Próximo minuto
    
    schedules = [
        {"cpf": "11111111111", "entry_time": (base_time).strftime('%H:%M:%S'), "wait_time": "00:00:30"},
        {"cpf": "22222222222", "entry_time": (base_time + timedelta(minutes=1)).strftime('%H:%M:%S'), "wait_time": "00:00:30"},
        {"cpf": "33333333333", "entry_time": (base_time + timedelta(minutes=2)).strftime('%H:%M:%S'), "wait_time": "00:00:30"},
        {"cpf": "44444444444", "entry_time": (base_time + timedelta(minutes=3)).strftime('%H:%M:%S'), "wait_time": "00:00:30"},
        {"cpf": "55555555555", "entry_time": (base_time + timedelta(minutes=4)).strftime('%H:%M:%S'), "wait_time": "00:00:30"},
    ]
    
    for schedule in schedules:
        if schedule_display(schedule['cpf'], schedule['entry_time'], schedule['wait_time']):
            time.sleep(0.5)  # Pequena pausa entre agendamentos
    
    # 4. Verificar status inicial
    print("\n4️⃣ Verificando status inicial...")
    initial_status = check_status()
    
    # 5. Monitoramento em tempo real
    print("\n5️⃣ Monitorando sistema em tempo real...")
    print("   Aguardando início das exibições...")
    
    for i in range(10):  # Monitora por 10 iterações
        time.sleep(3)  # Aguarda 3 segundos
        
        status = check_status()
        if status:
            current_images = status.get('current_images', {})
            active_count = sum(1 for cpf in current_images.values() if cpf)
            
            if active_count > 0:
                print(f"   ⏰ Iteração {i+1}: {active_count} visualizações ativas")
                for viz, cpf in current_images.items():
                    if cpf:
                        print(f"      {viz}: CPF {cpf}")
            else:
                print(f"   ⏰ Iteração {i+1}: Aguardando exibições...")
    
    # 6. Limpeza
    print("\n6️⃣ Limpeza...")
    try:
        if os.path.exists(image_path):
            os.remove(image_path)
            print(f"✅ Arquivo temporário removido: {image_path}")
    except Exception as e:
        print(f"⚠️  Erro ao remover arquivo temporário: {e}")
    
    # 7. Status final
    print("\n7️⃣ Status final...")
    final_status = check_status()
    
    print("\n✅ Teste completo finalizado!")
    print("\n📋 Resumo:")
    print(f"   - Imagens enviadas: {len(test_cpfs)}")
    print(f"   - Agendamentos realizados: {len(schedules)}")
    print(f"   - Jobs ativos: {final_status.get('total_jobs', 0) if final_status else 'N/A'}")
    
    print("\n🌐 Para visualizar as imagens, acesse:")
    for i in range(6):
        port = 8083 + i
        print(f"   - http://localhost:{port}/view/ (Visualization{i+1})")

def main():
    """Função principal"""
    try:
        test_complete_flow()
    except KeyboardInterrupt:
        print("\n\n⏹️  Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")

if __name__ == "__main__":
    main() 