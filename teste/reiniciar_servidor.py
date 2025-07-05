#!/usr/bin/env python3
"""
Script para reiniciar o servidor e forçar atualização das visualizações
"""

import requests
import time
import subprocess
import sys
import os

def verificar_servidor():
    """Verifica se o servidor está rodando"""
    try:
        response = requests.get("http://localhost:8000/webhook/status", timeout=5)
        return response.status_code == 200
    except:
        return False

def parar_servidor():
    """Para o servidor se estiver rodando"""
    print("🛑 Parando servidor...")
    
    # Tentar parar via HTTP (se houver endpoint de shutdown)
    try:
        requests.post("http://localhost:8000/shutdown", timeout=5)
        time.sleep(2)
    except:
        pass
    
    # Verificar se ainda está rodando
    if verificar_servidor():
        print("⚠️  Servidor ainda está rodando. Pare manualmente e pressione Enter...")
        input()
    else:
        print("✅ Servidor parado")

def iniciar_servidor():
    """Inicia o servidor"""
    print("🚀 Iniciando servidor...")
    
    # Navegar para o diretório raiz
    os.chdir("..")
    
    # Iniciar servidor em background
    try:
        # Windows
        if os.name == 'nt':
            subprocess.Popen(["python", "start.bat"], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
        else:
            # Linux/Mac
            subprocess.Popen(["python", "start.sh"], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
        
        print("⏳ Aguardando servidor iniciar...")
        
        # Aguardar servidor ficar disponível
        for i in range(30):  # 30 segundos
            if verificar_servidor():
                print("✅ Servidor iniciado com sucesso!")
                return True
            time.sleep(1)
        
        print("❌ Servidor não iniciou em 30 segundos")
        return False
        
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {str(e)}")
        return False

def limpar_cache_navegador():
    """Instruções para limpar cache do navegador"""
    print("\n🧹 INSTRUÇÕES PARA LIMPAR CACHE:")
    print("="*50)
    print("1. Abra a visualização no navegador")
    print("2. Pressione Ctrl+Shift+Delete (ou Cmd+Shift+Delete no Mac)")
    print("3. Selecione 'Limpar dados' e clique em 'Limpar'")
    print("4. Ou pressione Ctrl+F5 para forçar recarregamento")
    print("5. Ou use modo incógnito/anônimo")
    print("\n💡 A versão 2.0 deve aparecer no canto superior esquerdo")

def verificar_atualizacao():
    """Verifica se a atualização foi aplicada"""
    print("\n🔍 VERIFICANDO ATUALIZAÇÃO:")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:8000/visualization1", timeout=10)
        if response.status_code == 200:
            html = response.text
            
            if "Versão: 2.0 (CPF removido)" in html:
                print("✅ Versão 2.0 detectada no HTML")
                return True
            else:
                print("❌ Versão 2.0 não encontrada")
                return False
        else:
            print(f"❌ Erro ao acessar visualização: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar atualização: {str(e)}")
        return False

def main():
    """Função principal"""
    print("🔄 REINICIANDO SERVIDOR PARA ATUALIZAÇÃO")
    print("="*60)
    
    # 1. Verificar se servidor está rodando
    if verificar_servidor():
        print("✅ Servidor está rodando")
        
        # 2. Verificar se já está na versão 2.0
        if verificar_atualizacao():
            print("✅ Servidor já está na versão 2.0")
            limpar_cache_navegador()
            return
        
        # 3. Parar servidor
        parar_servidor()
    else:
        print("❌ Servidor não está rodando")
    
    # 4. Iniciar servidor
    if iniciar_servidor():
        # 5. Verificar atualização
        if verificar_atualizacao():
            print("\n🎉 ATUALIZAÇÃO APLICADA COM SUCESSO!")
            print("✅ Servidor reiniciado")
            print("✅ Versão 2.0 ativa")
            print("✅ CPF removido da visualização")
            
            limpar_cache_navegador()
        else:
            print("\n❌ ATUALIZAÇÃO NÃO FOI APLICADA")
            print("Verificar se as modificações foram salvas corretamente")
    else:
        print("\n❌ FALHA AO REINICIAR SERVIDOR")
        print("Inicie manualmente o servidor")

if __name__ == "__main__":
    main() 