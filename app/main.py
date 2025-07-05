from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db, engine, SessionLocal
from app.models import Base, Cadastro, Parametro, Evento
from app.views import cadastro, webhook, websocket, visualization
from app.scheduler import event_scheduler
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Gestão de Imagens",
    description="Sistema para cadastro, agendamento e exibição de imagens por CPF",
    version="1.0.0"
)

# Incluir routers
app.include_router(cadastro.router)
app.include_router(webhook.router)
app.include_router(websocket.router)
app.include_router(visualization.router)

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Página inicial com links para todas as funcionalidades
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de Gerenciamento de Imagens</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            .btn { display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }
            .btn:hover { background: #0056b3; }
            .status { padding: 10px; background: #f8f9fa; border-radius: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Sistema de Gerenciamento de Imagens</h1>
            
            <div class="section">
                <h2>📝 Cadastro</h2>
                <p>Cadastre CPFs e imagens no sistema</p>
                <a href="/cadastro" class="btn">Interface de Cadastro</a>
                <a href="/docs#/cadastro" class="btn">API Cadastro</a>
            </div>
            
            <div class="section">
                <h2>🔗 Webhook</h2>
                <p>Envie CPFs para agendamento de exibição</p>
                <a href="/docs#/webhook" class="btn">API Webhook</a>
                <a href="/webhook/eventos" class="btn">Ver Eventos</a>
            </div>
            
            <div class="section">
                <h2>📺 Visualizações</h2>
                <p>Monitores para exibição das imagens</p>
                <a href="/visualization1" class="btn">Visualização 1</a>
                <a href="/visualization2" class="btn">Visualização 2</a>
                <a href="/visualization3" class="btn">Visualização 3</a>
                <a href="/visualization4" class="btn">Visualização 4</a>
                <a href="/visualization5" class="btn">Visualização 5</a>
                <a href="/visualization6" class="btn">Visualização 6</a>
            </div>
            
            <div class="section">
                <h2>🔧 Sistema</h2>
                <p>Status e configurações do sistema</p>
                <a href="/websocket/status" class="btn">Status WebSocket</a>
                <a href="/scheduler/status" class="btn">Status Agendador</a>
                <a href="/docs" class="btn">Documentação API</a>
            </div>
            
            <div class="status">
                <h3>📊 Status do Sistema</h3>
                <p><strong>Agendador:</strong> <span id="scheduler-status">Carregando...</span></p>
                <p><strong>WebSocket:</strong> <span id="websocket-status">Carregando...</span></p>
            </div>
        </div>
        
        <script>
            // Atualizar status do sistema
            async function updateStatus() {
                try {
                    const schedulerResponse = await fetch('/scheduler/status');
                    const schedulerData = await schedulerResponse.json();
                    document.getElementById('scheduler-status').textContent = 
                        schedulerData.running ? '🟢 Ativo' : '🔴 Inativo';
                    
                    const websocketResponse = await fetch('/websocket/status');
                    const websocketData = await websocketResponse.json();
                    document.getElementById('websocket-status').textContent = 
                        `${websocketData.total_connections} conexões ativas`;
                } catch (error) {
                    console.error('Erro ao atualizar status:', error);
                }
            }
            
            // Atualizar status a cada 5 segundos
            updateStatus();
            setInterval(updateStatus, 5000);
        </script>
    </body>
    </html>
    """

@app.get("/scheduler/status")
async def get_scheduler_status():
    """
    Retorna status do agendador
    """
    return event_scheduler.get_scheduler_status()

@app.on_event("startup")
async def startup_event():
    """
    Evento executado na inicialização da aplicação
    """
    # Inicializar parâmetros padrão se não existirem
    db = SessionLocal()
    try:
        parametros_padrao = [
            ("tempo_inicial_segundos", "30"),
            ("incremento_segundos", "10"),
            ("duracao_exibicao_seg", "10")
        ]
        
        for nome, valor in parametros_padrao:
            parametro = db.query(Parametro).filter(Parametro.nome == nome).first()
            if not parametro:
                novo_parametro = Parametro(nome=nome, valor=valor)
                db.add(novo_parametro)
        
        db.commit()
        print("✅ Parâmetros padrão inicializados")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar parâmetros: {e}")
        db.rollback()
    finally:
        db.close()

@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento executado no encerramento da aplicação
    """
    event_scheduler.stop()
    print("🛑 Agendador parado")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 