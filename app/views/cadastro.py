from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Cadastro
from app.schemas import CadastroCreate, CadastroResponse
import base64
from typing import List

router = APIRouter(prefix="/cadastro", tags=["cadastro"])

@router.get("/", response_class=HTMLResponse)
async def cadastro_interface():
    """
    Interface HTML para cadastro de CPF e imagem
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cadastro de CPF e Imagem</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input[type="text"], input[type="file"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
            button { background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { margin-top: 20px; padding: 15px; border-radius: 5px; }
            .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .cadastros { margin-top: 30px; }
            .cadastro-item { padding: 10px; border: 1px solid #ddd; margin: 5px 0; border-radius: 5px; }
            .btn { display: inline-block; padding: 8px 16px; background: #6c757d; color: white; text-decoration: none; border-radius: 3px; margin: 2px; }
            .btn:hover { background: #545b62; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📝 Cadastro de CPF e Imagem</h1>
            
            <form id="cadastroForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="cpf">CPF (11 dígitos):</label>
                    <input type="text" id="cpf" name="cpf" maxlength="11" pattern="[0-9]{11}" required>
                </div>
                
                <div class="form-group">
                    <label for="imagem">Imagem:</label>
                    <input type="file" id="imagem" name="imagem" accept="image/*" required>
                </div>
                
                <button type="submit">Cadastrar</button>
            </form>
            
            <div id="result"></div>
            
            <div class="cadastros">
                <h2>📋 Cadastros Existentes</h2>
                <button onclick="carregarCadastros()">Atualizar Lista</button>
                <div id="cadastrosLista"></div>
            </div>
            
            <div class="section">
                <h2>📁 Cadastro em Massa</h2>
                <p>Cadastre múltiplas imagens de um diretório onde os arquivos seguem o padrão CPF.jpg</p>
                <form id="bulkForm">
                    <div class="form-group">
                        <label for="diretorio">Caminho do Diretório:</label>
                        <input type="text" id="diretorio" name="diretorio" placeholder="/caminho/para/imagens" required>
                    </div>
                    <button type="submit">Cadastrar em Massa</button>
                </form>
                <div id="bulkResult"></div>
            </div>
        </div>
        
        <script>
            document.getElementById('cadastroForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData();
                formData.append('cpf', document.getElementById('cpf').value);
                formData.append('imagem', document.getElementById('imagem').files[0]);
                
                try {
                    const response = await fetch('/cadastro/', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        document.getElementById('result').innerHTML = 
                            `<div class="result success">✅ ${result.message || 'Cadastro realizado com sucesso!'}</div>`;
                        document.getElementById('cadastroForm').reset();
                        carregarCadastros();
                    } else {
                        document.getElementById('result').innerHTML = 
                            `<div class="result error">❌ ${result.detail || 'Erro ao cadastrar'}</div>`;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = 
                        `<div class="result error">❌ Erro de conexão: ${error.message}</div>`;
                }
            });
            
            async function carregarCadastros() {
                try {
                    const response = await fetch('/cadastro/list');
                    const cadastros = await response.json();
                    
                    const lista = document.getElementById('cadastrosLista');
                    lista.innerHTML = '';
                    
                    cadastros.forEach(cadastro => {
                        const item = document.createElement('div');
                        item.className = 'cadastro-item';
                        item.innerHTML = `
                            <strong>CPF:</strong> ${cadastro.cpf}<br>
                            <strong>Imagem:</strong> <img src="/cadastro/${cadastro.cpf}/imagem" style="max-width: 100px; max-height: 100px; border: 1px solid #ddd; border-radius: 5px;" alt="Imagem do CPF ${cadastro.cpf}"><br>
                            <a href="/cadastro/${cadastro.cpf}" class="btn">Ver Detalhes</a>
                            <button onclick="deletarCadastro('${cadastro.cpf}')" class="btn">Deletar</button>
                        `;
                        lista.appendChild(item);
                    });
                } catch (error) {
                    console.error('Erro ao carregar cadastros:', error);
                }
            }
            
            async function deletarCadastro(cpf) {
                if (confirm(`Tem certeza que deseja deletar o CPF ${cpf}?`)) {
                    try {
                        const response = await fetch(`/cadastro/${cpf}`, {
                            method: 'DELETE'
                        });
                        
                        if (response.ok) {
                            carregarCadastros();
                        } else {
                            alert('Erro ao deletar cadastro');
                        }
                    } catch (error) {
                        alert('Erro de conexão');
                    }
                }
            }
            
            // Carregar cadastros ao abrir a página
            carregarCadastros();
            
            // Cadastro em massa
            document.getElementById('bulkForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const diretorio = document.getElementById('diretorio').value;
                const resultDiv = document.getElementById('bulkResult');
                
                resultDiv.innerHTML = '<div class="result">⏳ Processando cadastro em massa...</div>';
                
                try {
                    const formData = new FormData();
                    formData.append('diretorio', diretorio);
                    
                    const response = await fetch('/cadastro/bulk', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        let html = `<div class="result success">
                            <h3>✅ ${result.message}</h3>
                            <p><strong>Cadastros realizados:</strong> ${result.cadastros_realizados}</p>
                            <p><strong>Total de arquivos:</strong> ${result.total_arquivos}</p>
                        `;
                        
                        if (result.erros && result.erros.length > 0) {
                            html += `<h4>⚠️ Erros encontrados:</h4><ul>`;
                            result.erros.forEach(erro => {
                                html += `<li>${erro}</li>`;
                            });
                            html += `</ul>`;
                        }
                        
                        html += `</div>`;
                        resultDiv.innerHTML = html;
                        
                        // Atualizar lista de cadastros
                        carregarCadastros();
                    } else {
                        resultDiv.innerHTML = `<div class="result error">❌ ${result.detail || 'Erro ao realizar cadastro em massa'}</div>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<div class="result error">❌ Erro de conexão: ${error.message}</div>`;
                }
            });
        </script>
    </body>
    </html>
    """

@router.post("/", response_model=CadastroResponse)
async def cadastrar_cpf_imagem(
    cpf: str = Form(...),
    imagem: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Cadastra um CPF com sua imagem em Base64
    """
    try:
        # Validar CPF (formato básico)
        if not cpf.isdigit() or len(cpf) != 11:
            raise HTTPException(status_code=400, detail="CPF deve ter 11 dígitos numéricos")
        
        # Ler e converter imagem para Base64
        conteudo_imagem = await imagem.read()
        imagem_base64 = base64.b64encode(conteudo_imagem).decode('utf-8')
        
        # Verificar se CPF já existe
        cadastro_existente = db.query(Cadastro).filter(Cadastro.cpf == cpf).first()
        if cadastro_existente:
            raise HTTPException(status_code=400, detail="CPF já cadastrado")
        
        # Criar novo cadastro
        novo_cadastro = Cadastro(
            cpf=cpf,
            caminho_imagem=imagem_base64
        )
        
        db.add(novo_cadastro)
        db.commit()
        db.refresh(novo_cadastro)
        
        return CadastroResponse(
            cpf=novo_cadastro.cpf,
            caminho_imagem=novo_cadastro.caminho_imagem
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao cadastrar: {str(e)}")

@router.get("/list", response_model=List[CadastroResponse])
async def listar_cadastros(db: Session = Depends(get_db)):
    """
    Lista todos os cadastros
    """
    cadastros = db.query(Cadastro).all()
    return [
        CadastroResponse(cpf=c.cpf, caminho_imagem=c.caminho_imagem)
        for c in cadastros
    ]

@router.get("/{cpf}", response_model=CadastroResponse)
async def obter_cadastro(cpf: str, db: Session = Depends(get_db)):
    """
    Obtém um cadastro específico por CPF
    """
    cadastro = db.query(Cadastro).filter(Cadastro.cpf == cpf).first()
    if not cadastro:
        raise HTTPException(status_code=404, detail="CPF não encontrado")
    
    return CadastroResponse(
        cpf=cadastro.cpf,
        caminho_imagem=cadastro.caminho_imagem
    )

@router.get("/{cpf}/imagem")
async def obter_imagem_cadastro(cpf: str, db: Session = Depends(get_db)):
    """
    Obtém a imagem de um cadastro específico por CPF
    """
    from fastapi.responses import Response
    
    cadastro = db.query(Cadastro).filter(Cadastro.cpf == cpf).first()
    if not cadastro:
        raise HTTPException(status_code=404, detail="CPF não encontrado")
    
    try:
        # Decodificar base64 para bytes
        import base64
        imagem_bytes = base64.b64decode(cadastro.caminho_imagem)
        
        # Determinar o tipo MIME baseado no conteúdo
        import imghdr
        tipo_imagem = imghdr.what(None, h=imagem_bytes)
        content_type = f"image/{tipo_imagem}" if tipo_imagem else "image/jpeg"
        
        return Response(content=imagem_bytes, media_type=content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}")

@router.delete("/{cpf}")
async def deletar_cadastro(cpf: str, db: Session = Depends(get_db)):
    """
    Deleta um cadastro por CPF
    """
    cadastro = db.query(Cadastro).filter(Cadastro.cpf == cpf).first()
    if not cadastro:
        raise HTTPException(status_code=404, detail="CPF não encontrado")
    
    db.delete(cadastro)
    db.commit()
    
    return {"message": f"CPF {cpf} deletado com sucesso"}

@router.post("/bulk")
async def cadastro_em_massa(
    diretorio: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Cadastra múltiplas imagens de um diretório onde os arquivos seguem o padrão CPF.jpg
    """
    import os
    import glob
    
    try:
        # Verificar se o diretório existe
        if not os.path.exists(diretorio):
            raise HTTPException(status_code=400, detail=f"Diretório {diretorio} não encontrado")
        
        # Buscar arquivos de imagem
        extensoes = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']
        arquivos_encontrados = []
        
        for extensao in extensoes:
            arquivos_encontrados.extend(glob.glob(os.path.join(diretorio, extensao)))
            arquivos_encontrados.extend(glob.glob(os.path.join(diretorio, extensao.upper())))
        
        if not arquivos_encontrados:
            raise HTTPException(status_code=400, detail="Nenhum arquivo de imagem encontrado no diretório")
        
        cadastros_realizados = 0
        erros = []
        
        for arquivo in arquivos_encontrados:
            try:
                # Extrair CPF do nome do arquivo (assumindo formato CPF.extensao)
                nome_arquivo = os.path.basename(arquivo)
                nome_sem_extensao = os.path.splitext(nome_arquivo)[0]
                
                # Validar se o nome é um CPF válido (11 dígitos)
                if not nome_sem_extensao.isdigit() or len(nome_sem_extensao) != 11:
                    erros.append(f"Arquivo {nome_arquivo}: Nome não é um CPF válido")
                    continue
                
                cpf = nome_sem_extensao
                
                # Verificar se CPF já existe
                cadastro_existente = db.query(Cadastro).filter(Cadastro.cpf == cpf).first()
                if cadastro_existente:
                    erros.append(f"CPF {cpf}: Já cadastrado")
                    continue
                
                # Ler e converter imagem para Base64
                with open(arquivo, 'rb') as f:
                    conteudo_imagem = f.read()
                    imagem_base64 = base64.b64encode(conteudo_imagem).decode('utf-8')
                
                # Criar novo cadastro
                novo_cadastro = Cadastro(
                    cpf=cpf,
                    caminho_imagem=imagem_base64
                )
                
                db.add(novo_cadastro)
                cadastros_realizados += 1
                
            except Exception as e:
                erros.append(f"Erro ao processar {arquivo}: {str(e)}")
        
        # Commit de todos os cadastros
        db.commit()
        
        return {
            "message": f"Cadastro em massa concluído",
            "cadastros_realizados": cadastros_realizados,
            "total_arquivos": len(arquivos_encontrados),
            "erros": erros
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro no cadastro em massa: {str(e)}") 