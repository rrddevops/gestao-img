#!/usr/bin/env python3
"""
Script de teste para verificar se o sistema está funcionando
"""

import requests
import psycopg2
import base64
from PIL import Image
import io

def testar_api():
    """Testa se a API está funcionando"""
    print("🔍 Testando API...")
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API está funcionando")
            return True
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com API: {e}")
        return False

def testar_banco():
    """Testa se o banco está funcionando"""
    print("🔍 Testando banco de dados...")
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="gestao_img",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cadastro")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"✅ Banco está funcionando - {count} cadastros existentes")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar com banco: {e}")
        return False

def criar_imagem_teste():
    """Cria uma imagem de teste"""
    print("🔍 Criando imagem de teste...")
    try:
        # Criar uma imagem simples
        img = Image.new('RGB', (100, 100), color='red')
        
        # Salvar em bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # Converter para base64
        img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
        
        print("✅ Imagem de teste criada")
        return img_base64
    except Exception as e:
        print(f"❌ Erro ao criar imagem: {e}")
        return None

def testar_cadastro_api():
    """Testa cadastro via API"""
    print("🔍 Testando cadastro via API...")
    try:
        # Criar imagem de teste
        img_base64 = criar_imagem_teste()
        if not img_base64:
            return False
        
        # Decodificar para bytes
        img_bytes = base64.b64decode(img_base64)
        
        # Preparar dados
        files = {
            'cpf': (None, '12345678901'),
            'imagem': ('teste.jpg', img_bytes, 'image/jpeg')
        }
        
        # Enviar para API
        response = requests.post("http://localhost:8000/cadastro/", files=files, timeout=30)
        
        if response.status_code == 200:
            print("✅ Cadastro via API funcionando")
            return True
        else:
            print(f"❌ Erro no cadastro via API: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar cadastro via API: {e}")
        return False

def testar_cadastro_banco():
    """Testa cadastro direto no banco"""
    print("🔍 Testando cadastro direto no banco...")
    try:
        # Conectar ao banco
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="gestao_img",
            user="postgres",
            password="postgres"
        )
        
        # Criar imagem de teste
        img_base64 = criar_imagem_teste()
        if not img_base64:
            conn.close()
            return False
        
        # Verificar se CPF já existe
        cursor = conn.cursor()
        cursor.execute("SELECT cpf FROM cadastro WHERE cpf = %s", ('98765432109',))
        if cursor.fetchone():
            print("⚠️  CPF de teste já existe, pulando...")
            cursor.close()
            conn.close()
            return True
        
        # Inserir teste
        cursor.execute(
            "INSERT INTO cadastro (cpf, caminho_imagem) VALUES (%s, %s)",
            ('98765432109', img_base64)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Cadastro direto no banco funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar cadastro direto no banco: {e}")
        return False

def main():
    print("🧪 TESTE DO SISTEMA DE CADASTRO")
    print("=" * 50)
    print()
    
    # Testar componentes
    api_ok = testar_api()
    banco_ok = testar_banco()
    
    print()
    
    if api_ok and banco_ok:
        print("🎉 Sistema está funcionando!")
        print()
        
        # Testar cadastros
        print("🔧 Testando funcionalidades...")
        print()
        
        api_cadastro_ok = testar_cadastro_api()
        banco_cadastro_ok = testar_cadastro_banco()
        
        print()
        print("=" * 50)
        print("📊 RESULTADO DOS TESTES")
        print("=" * 50)
        print(f"API: {'✅' if api_ok else '❌'}")
        print(f"Banco: {'✅' if banco_ok else '❌'}")
        print(f"Cadastro via API: {'✅' if api_cadastro_ok else '❌'}")
        print(f"Cadastro direto no banco: {'✅' if banco_cadastro_ok else '❌'}")
        print()
        
        if api_cadastro_ok and banco_cadastro_ok:
            print("🎉 Todos os testes passaram!")
            print("   Você pode usar qualquer um dos scripts de cadastro em massa.")
        else:
            print("⚠️  Alguns testes falharam.")
            print("   Use o script que funcionou para você.")
    else:
        print("❌ Sistema não está funcionando corretamente.")
        print("   Execute: docker-compose up -d")
    
    print()
    input("Pressione ENTER para sair...")

if __name__ == "__main__":
    main() 