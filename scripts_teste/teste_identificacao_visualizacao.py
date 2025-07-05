#!/usr/bin/env python3
"""
Script para testar se a identificação das visualizações está funcionando.
Testa o endpoint /current-image em todas as visualizações.
"""

import requests
import json

# URLs das visualizações
VISUALIZATIONS = [
    ("visualization1", "http://localhost:8083"),
    ("visualization2", "http://localhost:8084"),
    ("visualization3", "http://localhost:8085"),
    ("visualization4", "http://localhost:8086"),
    ("visualization5", "http://localhost:8087"),
    ("visualization6", "http://localhost:8088")
]

def test_visualization_identification():
    """Testa se cada visualização consegue se identificar corretamente"""
    print("🔧 TESTE DE IDENTIFICAÇÃO DAS VISUALIZAÇÕES")
    print("=" * 60)
    
    results = []
    
    for viz_name, url in VISUALIZATIONS:
        try:
            print(f"\n🔄 Testando {viz_name} em {url}")
            
            # Testa o endpoint /current-image
            response = requests.get(f"{url}/current-image", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {viz_name}: Status 200 - {data}")
                results.append({
                    'visualization': viz_name,
                    'url': url,
                    'status': 'success',
                    'response': data
                })
            else:
                print(f"❌ {viz_name}: Status {response.status_code} - {response.text}")
                results.append({
                    'visualization': viz_name,
                    'url': url,
                    'status': 'error',
                    'error': f"Status {response.status_code}"
                })
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {viz_name}: Erro de conexão - container não está rodando")
            results.append({
                'visualization': viz_name,
                'url': url,
                'status': 'error',
                'error': 'Connection error'
            })
        except Exception as e:
            print(f"❌ {viz_name}: Erro inesperado - {e}")
            results.append({
                'visualization': viz_name,
                'url': url,
                'status': 'error',
                'error': str(e)
            })
    
    # Resumo dos resultados
    print(f"\n📊 RESUMO DOS RESULTADOS")
    print("=" * 60)
    
    success_count = 0
    for result in results:
        status = result['status']
        viz_name = result['visualization']
        
        if status == 'success':
            print(f"✅ {viz_name}: OK")
            success_count += 1
        else:
            print(f"❌ {viz_name}: {result.get('error', 'Unknown error')}")
    
    print(f"\n🎯 RESULTADO FINAL: {success_count}/{len(VISUALIZATIONS)} visualizações funcionando")
    
    if success_count == len(VISUALIZATIONS):
        print("🎉 Todas as visualizações estão funcionando corretamente!")
        print("📺 Agora você pode testar o agendamento de imagens.")
    else:
        print("⚠️  Algumas visualizações não estão funcionando.")
        print("🔧 Verifique se todos os containers estão rodando:")
        print("   docker-compose ps")

def test_config_endpoint():
    """Testa o endpoint /config para verificar a configuração"""
    try:
        print(f"\n📊 Testando endpoint /config...")
        response = requests.get("http://localhost:8083/config", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Configuração obtida com sucesso!")
            print(f"📋 CONFIGURAÇÃO:")
            
            viz_config = data.get('visualization_config', {})
            for viz_name, config in sorted(viz_config.items()):
                port = config.get('port', 0)
                delay = config.get('delay_seconds', 0)
                display = config.get('display_seconds', 0)
                print(f"• {viz_name} (porta {port}): delay={delay}s, display={display}s")
            
            return True
        else:
            print(f"❌ Erro ao obter configuração: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar configuração: {e}")
        return False

def main():
    # 1. Testa configuração
    if not test_config_endpoint():
        print("❌ Falha ao obter configuração. Verifique se os containers estão rodando.")
        return
    
    # 2. Testa identificação das visualizações
    test_visualization_identification()
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print(f"1. Se todas as visualizações estiverem OK, teste o agendamento:")
    print(f"   python teste_correcao_wait_time.py")
    print(f"2. Monitore as visualizações:")
    for viz_name, url in VISUALIZATIONS:
        print(f"   • {viz_name}: {url}/view/")

if __name__ == "__main__":
    main() 