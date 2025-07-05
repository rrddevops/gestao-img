#!/usr/bin/env python3
"""
Script de diagnóstico para o Sistema de Gerenciamento de Imagens
"""

import requests
import time
import json
import subprocess
import sys

def check_docker():
    """Verifica se Docker está rodando"""
    print("🔍 Verificando Docker...")
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker está rodando")
            return True
        else:
            print("❌ Docker não está rodando")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar Docker: {e}")
        return False

def check_containers():
    """Verifica status dos containers"""
    print("🔍 Verificando containers...")
    try:
        result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True)
        print(result.stdout)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erro ao verificar containers: {e}")
        return False

def check_backend_health():
    """Verifica se o backend está respondendo"""
    print("🔍 Verificando backend...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend está respondendo")
            return True
        else:
            print(f"❌ Backend retornou status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend não está acessível")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar backend: {e}")
        return False

def check_database():
    """Verifica conexão com banco de dados"""
    print("🔍 Verificando banco de dados...")
    try:
        result = subprocess.run([
            'docker-compose', 'exec', '-T', 'db', 
            'pg_isready', '-U', 'postgres', '-d', 'gestao_img'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Banco de dados está funcionando")
            return True
        else:
            print("❌ Banco de dados não está funcionando")
            print(f"Erro: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False

def check_logs():
    """Verifica logs dos containers"""
    print("🔍 Verificando logs...")
    try:
        print("\n📋 Logs do Backend:")
        result = subprocess.run(['docker-compose', 'logs', '--tail=20', 'backend'], 
                              capture_output=True, text=True)
        print(result.stdout)
        
        print("\n📋 Logs do Banco:")
        result = subprocess.run(['docker-compose', 'logs', '--tail=10', 'db'], 
                              capture_output=True, text=True)
        print(result.stdout)
        
    except Exception as e:
        print(f"❌ Erro ao verificar logs: {e}")

def test_endpoints():
    """Testa endpoints básicos"""
    print("🔍 Testando endpoints...")
    
    endpoints = [
        ("/", "Página inicial"),
        ("/docs", "Documentação API"),
        ("/cadastro", "Interface de cadastro"),
        ("/scheduler/status", "Status do agendador"),
        ("/websocket/status", "Status do WebSocket"),
    ]
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {description}: OK")
            else:
                print(f"⚠️  {description}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: Erro - {e}")

def main():
    """Função principal de diagnóstico"""
    print("🔧 Diagnóstico do Sistema de Gerenciamento de Imagens")
    print("=" * 60)
    
    checks = [
        ("Docker", check_docker),
        ("Containers", check_containers),
        ("Backend", check_backend_health),
        ("Banco de Dados", check_database),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}")
        print("-" * 40)
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            results.append((check_name, False))
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DO DIAGNÓSTICO")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{check_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} verificações passaram")
    
    if passed < total:
        print("\n🔍 Verificando logs para mais detalhes...")
        check_logs()
        
        print("\n🧪 Testando endpoints...")
        test_endpoints()
        
        print("\n💡 Sugestões:")
        print("1. Execute: docker-compose down")
        print("2. Execute: docker-compose up -d --build")
        print("3. Aguarde 30 segundos e execute: python diagnose.py")
        print("4. Se persistir, execute: ./fix_postgres.sh")
    else:
        print("\n🎉 Sistema parece estar funcionando corretamente!")
        print("Execute: python test_system.py para testes completos")

if __name__ == "__main__":
    main() 