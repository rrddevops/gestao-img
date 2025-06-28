#!/usr/bin/env python3
"""
Script para verificar se o docker-compose.yml está configurado corretamente
para a nova estrutura de agendamento baseado em datetime
"""

import yaml
import sys

def verify_docker_compose():
    """Verifica se o docker-compose.yml está configurado corretamente"""
    print("🔍 Verificando configuração do docker-compose.yml")
    print("=" * 50)
    
    try:
        with open('docker-compose.yml', 'r') as file:
            config = yaml.safe_load(file)
    except Exception as e:
        print(f"❌ Erro ao ler docker-compose.yml: {e}")
        return False
    
    # Verifica se todos os serviços necessários existem
    required_services = [
        'postgres', 'app1-cadastro', 'app2-webhook',
        'visualization1', 'visualization2', 'visualization3',
        'visualization4', 'visualization5', 'visualization6'
    ]
    
    print("📋 Verificando serviços...")
    for service in required_services:
        if service in config['services']:
            print(f"  ✅ {service}")
        else:
            print(f"  ❌ {service} - FALTANDO")
            return False
    
    # Verifica configuração das visualizações
    print("\n📊 Verificando configuração das visualizações...")
    
    expected_delays = {
        'visualization1': 0,
        'visualization2': 10,
        'visualization3': 20,
        'visualization4': 30,
        'visualization5': 40,
        'visualization6': 50
    }
    
    expected_ports = {
        'visualization1': 8083,
        'visualization2': 8084,
        'visualization3': 8085,
        'visualization4': 8086,
        'visualization5': 8087,
        'visualization6': 8088
    }
    
    all_correct = True
    
    for viz_name, expected_delay in expected_delays.items():
        service = config['services'][viz_name]
        
        # Verifica delay
        delay_found = None
        for env_var in service.get('environment', []):
            if env_var.startswith('DELAY='):
                delay_found = int(env_var.split('=')[1])
                break
        
        if delay_found == expected_delay:
            print(f"  ✅ {viz_name}: DELAY={delay_found}")
        else:
            print(f"  ❌ {viz_name}: DELAY={delay_found} (esperado: {expected_delay})")
            all_correct = False
        
        # Verifica porta
        expected_port = expected_ports[viz_name]
        port_found = None
        for port_mapping in service.get('ports', []):
            if isinstance(port_mapping, str):
                external_port = int(port_mapping.split(':')[0])
                if external_port == expected_port:
                    port_found = expected_port
                    break
        
        if port_found == expected_port:
            print(f"         Porta: {expected_port}:5003 ✅")
        else:
            print(f"         Porta: {port_found} (esperado: {expected_port}:5003) ❌")
            all_correct = False
    
    # Verifica configuração do banco de dados
    print("\n🗄️ Verificando configuração do banco de dados...")
    postgres_service = config['services']['postgres']
    
    required_env_vars = ['POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD']
    for env_var in required_env_vars:
        if env_var in postgres_service.get('environment', {}):
            print(f"  ✅ {env_var}")
        else:
            print(f"  ❌ {env_var} - FALTANDO")
            all_correct = False
    
    # Verifica configuração dos apps
    print("\n🔧 Verificando configuração dos apps...")
    app_services = ['app1-cadastro', 'app2-webhook']
    
    for app_service in app_services:
        service = config['services'][app_service]
        required_env_vars = ['POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_HOST']
        
        print(f"  {app_service}:")
        for env_var in required_env_vars:
            env_found = False
            for env in service.get('environment', []):
                if env.startswith(f'{env_var}='):
                    env_found = True
                    break
            
            if env_found:
                print(f"    ✅ {env_var}")
            else:
                print(f"    ❌ {env_var} - FALTANDO")
                all_correct = False
    
    # Verifica rede
    print("\n🌐 Verificando configuração de rede...")
    if 'networks' in config and 'app-network' in config['networks']:
        print("  ✅ Rede app-network configurada")
    else:
        print("  ❌ Rede app-network não configurada")
        all_correct = False
    
    # Verifica volumes
    print("\n💾 Verificando volumes...")
    if 'volumes' in config and 'postgres_data' in config['volumes']:
        print("  ✅ Volume postgres_data configurado")
    else:
        print("  ⚠️  Volume postgres_data não configurado (opcional)")
    
    # Resultado final
    print("\n" + "=" * 50)
    if all_correct:
        print("✅ docker-compose.yml está configurado corretamente!")
        print("\n📋 Resumo da configuração:")
        print("   - 6 visualizações com delays de 0, 10, 20, 30, 40, 50 segundos")
        print("   - Portas 8083-8088 mapeadas corretamente")
        print("   - Banco PostgreSQL configurado")
        print("   - Apps conectados ao banco")
        print("   - Rede interna configurada")
        
        print("\n🚀 Para iniciar o sistema:")
        print("   docker-compose up -d --build")
        
        print("\n🧪 Para testar:")
        print("   python start_system.py")
        
        return True
    else:
        print("❌ docker-compose.yml tem problemas de configuração!")
        print("   Verifique os itens marcados com ❌ acima")
        return False

def show_expected_config():
    """Mostra a configuração esperada"""
    print("\n📖 Configuração esperada:")
    print("=" * 50)
    
    print("""
Visualizações:
  visualization1:
    ports: "8083:5003"
    environment: DELAY=0
  
  visualization2:
    ports: "8084:5003"
    environment: DELAY=10
  
  visualization3:
    ports: "8085:5003"
    environment: DELAY=20
  
  visualization4:
    ports: "8086:5003"
    environment: DELAY=30
  
  visualization5:
    ports: "8087:5003"
    environment: DELAY=40
  
  visualization6:
    ports: "8088:5003"
    environment: DELAY=50

Banco de dados:
  postgres:
    environment:
      POSTGRES_DB: gestao_img
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres

Apps:
  app1-cadastro, app2-webhook:
    environment:
      POSTGRES_DB: gestao_img
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_HOST: postgres
""")

def main():
    """Função principal"""
    print("🔍 Verificador de Configuração do Docker Compose")
    print("Sistema de Agendamento Baseado em DateTime")
    print("=" * 60)
    
    if not verify_docker_compose():
        print("\n❌ Problemas encontrados na configuração!")
        show_expected_config()
        sys.exit(1)
    
    print("\n🎉 Configuração verificada com sucesso!")

if __name__ == "__main__":
    main() 