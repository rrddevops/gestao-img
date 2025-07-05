#!/usr/bin/env python3
"""
Script simples para cadastro em massa - Interface amigável
"""

import os
import requests
import glob
import time

def main():
    print("🚀 CADASTRO EM MASSA - SISTEMA DE GESTÃO DE IMAGENS")
    print("=" * 60)
    
    # Solicita a pasta com as imagens
    while True:
        pasta = input("📁 Digite o caminho da pasta com as imagens: ").strip()
        
        if os.path.exists(pasta) and os.path.isdir(pasta):
            break
        else:
            print("❌ Pasta não encontrada. Tente novamente.")
    
    # Pergunta se quer agendar automaticamente
    agendar = input("📅 Agendar exibição automaticamente? (s/N): ").strip().lower() in ['s', 'sim', 'y', 'yes']
    
    # Encontra as imagens
    extensoes = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']
    imagens = []
    
    for ext in extensoes:
        imagens.extend(glob.glob(os.path.join(pasta, ext)))
        imagens.extend(glob.glob(os.path.join(pasta, ext.upper())))
    
    if not imagens:
        print("❌ Nenhuma imagem encontrada!")
        return
    
    print(f"\n📁 Encontradas {len(imagens)} imagens:")
    for img in imagens:
        print(f"   - {os.path.basename(img)}")
    
    # Confirmação final
    print(f"\n⚠️  ATENÇÃO: Serão processadas {len(imagens)} imagens")
    if agendar:
        print("📅 Cada imagem será cadastrada E agendada para exibição")
    else:
        print("📝 Apenas cadastro será realizado (sem agendamento)")
    
    confirma = input("\nDeseja continuar? (s/N): ").strip().lower()
    if confirma not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        return
    
    # Processa as imagens
    print("\n🔄 Iniciando processamento...")
    print("=" * 60)
    
    sucessos = 0
    erros = 0
    
    for i, imagem in enumerate(imagens, 1):
        cpf = os.path.splitext(os.path.basename(imagem))[0]
        
        print(f"\n[{i}/{len(imagens)}] Processando: {cpf}")
        
        # Cadastra a imagem
        try:
            with open(imagem, 'rb') as f:
                files = {'image': (f'{cpf}.jpg', f, 'image/jpeg')}
                data = {'cpf': cpf}
                
                response = requests.post("http://localhost:5001/upload", files=files, data=data)
                
                if response.status_code == 200:
                    print(f"   ✅ Cadastrado com sucesso")
                    sucessos += 1
                    
                    # Agenda se solicitado
                    if agendar:
                        try:
                            webhook_response = requests.post("http://localhost:5002/webhook", 
                                                           json={'cpf': cpf})
                            if webhook_response.status_code == 200:
                                print(f"   📅 Agendado com sucesso")
                            else:
                                print(f"   ⚠️  Erro no agendamento")
                        except Exception as e:
                            print(f"   ⚠️  Erro no agendamento: {e}")
                    
                    # Delay entre processamentos
                    if i < len(imagens):
                        print("   ⏳ Aguardando 1 segundo...")
                        time.sleep(1)
                        
                else:
                    print(f"   ❌ Erro no cadastro: {response.text}")
                    erros += 1
                    
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            erros += 1
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL")
    print("=" * 60)
    print(f"📁 Total processado: {len(imagens)}")
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Erros: {erros}")
    print("=" * 60)
    
    if sucessos > 0:
        print("🎉 Processamento concluído!")
        if agendar:
            print("📺 As imagens estão sendo exibidas nas telas de visualização")
    else:
        print("😞 Nenhuma imagem foi processada com sucesso")

if __name__ == "__main__":
    main() 