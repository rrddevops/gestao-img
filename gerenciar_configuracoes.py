#!/usr/bin/env python3
"""
Script para gerenciar as configurações das visualizações
"""

import requests
import json
import sys

def mostrar_configuracoes():
    """Mostra todas as configurações atuais"""
    print("=== CONFIGURAÇÕES ATUAIS ===")
    
    try:
        # Busca configurações de todos os servidores
        servers = [
            {"name": "visualization1", "url": "http://localhost:8083"},
            {"name": "visualization2", "url": "http://localhost:8084"},
            {"name": "visualization3", "url": "http://localhost:8085"},
            {"name": "visualization4", "url": "http://localhost:8086"},
            {"name": "visualization5", "url": "http://localhost:8087"},
            {"name": "visualization6", "url": "http://localhost:8088"}
        ]
        
        for server in servers:
            try:
                response = requests.get(f"{server['url']}/config/all", timeout=5)
                if response.status_code == 200:
                    configs = response.json()
                    print(f"\n{server['name']} ({server['url']}):")
                    for config in configs:
                        print(f"  - {config['visualization_name']}: delay={config['delay_seconds']}s, display={config['display_seconds']}s, port={config['port']}, ativo={config['is_active']}")
                else:
                    print(f"{server['name']}: Erro {response.status_code}")
            except Exception as e:
                print(f"{server['name']}: Erro de conexão - {e}")
                
    except Exception as e:
        print(f"Erro ao buscar configurações: {e}")

def atualizar_configuracao(visualization_name, delay_seconds, display_seconds):
    """Atualiza a configuração de uma visualização específica"""
    print(f"=== ATUALIZANDO CONFIGURAÇÃO ===")
    print(f"Visualização: {visualization_name}")
    print(f"Delay: {delay_seconds} segundos")
    print(f"Display: {display_seconds} segundos")
    
    # Mapeia visualização para porta
    port_mapping = {
        'visualization1': 8083,
        'visualization2': 8084,
        'visualization3': 8085,
        'visualization4': 8086,
        'visualization5': 8087,
        'visualization6': 8088
    }
    
    port = port_mapping.get(visualization_name)
    if not port:
        print(f"Erro: Visualização {visualization_name} não encontrada")
        return
    
    url = f"http://localhost:{port}/config"
    data = {
        visualization_name: {
            'delay_seconds': delay_seconds,
            'display_seconds': display_seconds,
            'port': port,
            'is_active': True
        }
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Configuração atualizada: {result['message']}")
        else:
            print(f"✗ Erro ao atualizar: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Erro de conexão: {e}")

def resetar_configuracoes():
    """Reseta todas as configurações para os valores padrão"""
    print("=== RESETANDO CONFIGURAÇÕES ===")
    
    servers = [
        {"name": "visualization1", "url": "http://localhost:8083"},
        {"name": "visualization2", "url": "http://localhost:8084"},
        {"name": "visualization3", "url": "http://localhost:8085"},
        {"name": "visualization4", "url": "http://localhost:8086"},
        {"name": "visualization5", "url": "http://localhost:8087"},
        {"name": "visualization6", "url": "http://localhost:8088"}
    ]
    
    for server in servers:
        try:
            print(f"Resetando {server['name']}...")
            response = requests.post(f"{server['url']}/config/reset", timeout=10)
            if response.status_code == 200:
                result = response.json()
                print(f"✓ {server['name']}: {result['message']}")
            else:
                print(f"✗ {server['name']}: Erro {response.status_code}")
        except Exception as e:
            print(f"✗ {server['name']}: Erro de conexão - {e}")

def mostrar_ajuda():
    """Mostra a ajuda do script"""
    print("=== GERENCIADOR DE CONFIGURAÇÕES ===")
    print()
    print("Uso:")
    print("  python gerenciar_configuracoes.py mostrar")
    print("  python gerenciar_configuracoes.py atualizar <visualization> <delay> <display>")
    print("  python gerenciar_configuracoes.py resetar")
    print()
    print("Exemplos:")
    print("  python gerenciar_configuracoes.py mostrar")
    print("  python gerenciar_configuracoes.py atualizar visualization1 45 15")
    print("  python gerenciar_configuracoes.py resetar")
    print()
    print("Parâmetros:")
    print("  <visualization>: visualization1, visualization2, ..., visualization6")
    print("  <delay>: tempo de espera em segundos (ex: 30, 45, 60)")
    print("  <display>: tempo de exibição em segundos (ex: 10, 15, 20)")

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        mostrar_ajuda()
        return
    
    comando = sys.argv[1].lower()
    
    if comando == "mostrar":
        mostrar_configuracoes()
    elif comando == "atualizar":
        if len(sys.argv) != 5:
            print("Erro: Comando 'atualizar' requer 3 parâmetros")
            print("Uso: python gerenciar_configuracoes.py atualizar <visualization> <delay> <display>")
            return
        
        visualization = sys.argv[2]
        try:
            delay = int(sys.argv[3])
            display = int(sys.argv[4])
        except ValueError:
            print("Erro: delay e display devem ser números inteiros")
            return
        
        atualizar_configuracao(visualization, delay, display)
    elif comando == "resetar":
        resetar_configuracoes()
    else:
        print(f"Comando desconhecido: {comando}")
        mostrar_ajuda()

if __name__ == "__main__":
    main() 