#!/usr/bin/env python3
"""
Script para verificar o HTML atual da visualização
"""

import requests
import re

def verificar_html_visualizacao():
    """Verifica o HTML da visualização para confirmar remoção do CPF"""
    print("🔍 VERIFICANDO HTML ATUAL DA VISUALIZAÇÃO")
    print("="*60)
    
    try:
        # Verificar visualização 1
        response = requests.get("http://localhost:8000/visualization1", timeout=10)
        
        if response.status_code == 200:
            html_content = response.text
            print("✅ Página carregada com sucesso")
            
            # Verificar elementos relacionados ao CPF
            print("\n📋 ANÁLISE DO HTML:")
            print("-" * 40)
            
            # Verificar se há elementos de CPF
            cpf_elements = [
                "cpf-display",
                "cpf-text", 
                "CPF:",
                "CPF :",
                "cpf:",
                "cpf :"
            ]
            
            encontrados = []
            for element in cpf_elements:
                if element in html_content:
                    encontrados.append(element)
            
            if encontrados:
                print(f"❌ Elementos de CPF ainda presentes:")
                for element in encontrados:
                    print(f"   - '{element}'")
                
                # Mostrar contexto onde foi encontrado
                print(f"\n🔍 CONTEXTO ENCONTRADO:")
                for element in encontrados:
                    # Encontrar a linha onde está o elemento
                    lines = html_content.split('\n')
                    for i, line in enumerate(lines):
                        if element in line:
                            print(f"   Linha {i+1}: {line.strip()}")
                            break
                
                return False
            else:
                print("✅ Nenhum elemento de CPF encontrado no HTML")
            
            # Verificar se há elementos de imagem
            if "image-container" in html_content:
                print("✅ Elemento 'image-container' presente")
            else:
                print("❌ Elemento 'image-container' não encontrado")
            
            # Verificar se há timer
            if "timer" in html_content:
                print("✅ Elemento 'timer' presente")
            else:
                print("❌ Elemento 'timer' não encontrado")
            
            # Verificar se há WebSocket
            if "WebSocket" in html_content:
                print("✅ Configuração WebSocket presente")
            else:
                print("❌ Configuração WebSocket não encontrada")
            
            # Mostrar estrutura básica
            print(f"\n📊 ESTRUTURA DO HTML:")
            print("-" * 30)
            print(f"   Tamanho total: {len(html_content)} caracteres")
            print(f"   Linhas: {len(html_content.split(chr(10)))}")
            
            # Verificar se há JavaScript
            if "<script>" in html_content:
                print("✅ JavaScript presente")
            else:
                print("❌ JavaScript não encontrado")
            
            return True
            
        else:
            print(f"❌ Erro ao carregar página: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar HTML: {str(e)}")
        return False

def verificar_cache_navegador():
    """Dicas para limpar cache do navegador"""
    print(f"\n💡 DICAS PARA LIMPAR CACHE:")
    print("-" * 40)
    print("1. Pressione Ctrl+F5 (ou Cmd+Shift+R no Mac)")
    print("2. Ou abra as ferramentas do desenvolvedor (F12)")
    print("3. Clique com botão direito no botão de recarregar")
    print("4. Selecione 'Esvaziar cache e recarregar'")
    print("5. Ou use Ctrl+Shift+Delete para limpar cache")

def main():
    """Função principal"""
    resultado = verificar_html_visualizacao()
    
    if resultado:
        print(f"\n✅ HTML VERIFICADO - CPF REMOVIDO!")
        print("Se ainda vê o CPF na tela, limpe o cache do navegador")
        verificar_cache_navegador()
    else:
        print(f"\n❌ PROBLEMA ENCONTRADO NO HTML")
        print("O CPF ainda está presente no código")
        print("Verificar se as modificações foram aplicadas corretamente")

if __name__ == "__main__":
    main() 