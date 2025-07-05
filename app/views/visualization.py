from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import json

router = APIRouter(tags=["visualization"])

def create_visualization_page(visualization_name: str, port: int):
    """
    Cria página HTML para uma visualização específica
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{visualization_name.title()}</title>
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: #000;
                font-family: Arial, sans-serif;
                overflow: hidden;
            }}
            .container {{
                width: 100vw;
                height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }}
            .image-container {{
                max-width: 90vw;
                max-height: 80vh;
                text-align: center;
            }}
            .image {{
                max-width: 100%;
                max-height: 100%;
                object-fit: contain;
                border: 2px solid #333;
                border-radius: 10px;
            }}
            .info {{
                position: fixed;
                top: 10px;
                left: 10px;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }}
            .status {{
                position: fixed;
                top: 10px;
                right: 10px;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }}
            .loading {{
                color: white;
                font-size: 24px;
                text-align: center;
            }}
            .timer {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 10px 20px;
                border-radius: 20px;
                font-size: 16px;
            }}
        </style>
    </head>
    <body>
        <div class="info">
            <strong>{visualization_name.title()}</strong><br>
            Porta: {port}<br>
            WebSocket: ws://localhost:8000/websocket/{visualization_name}<br>
            <small>Versão: 2.0 (CPF removido)</small>
        </div>
        
        <div class="status" id="status">
            🔴 Desconectado
        </div>
        
        <div class="container" id="container">
            <div class="loading">
                Aguardando conexão WebSocket...
            </div>
        </div>
        
        <div class="timer" id="timer" style="display: none;">
            <span id="timer-text">10</span>s
        </div>
        
        <script>
            // Forçar recarregamento se for versão antiga
            if (localStorage.getItem('visualization_version') !== '2.0') {{
                localStorage.setItem('visualization_version', '2.0');
                location.reload(true);
            }}
            
            let ws = null;
            let currentImage = null;
            let timerInterval = null;
            let timeLeft = 10;
            let lastImageData = null;
            
            function connectWebSocket() {{
                const wsUrl = `ws://${{window.location.hostname}}:8000/websocket/{visualization_name}`;
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function() {{
                    document.getElementById('status').innerHTML = '🟢 Conectado';
                    document.getElementById('status').style.background = 'rgba(0,128,0,0.8)';
                }};
                
                ws.onmessage = function(event) {{
                    const data = JSON.parse(event.data);
                    displayImage(data);
                }};
                
                ws.onclose = function() {{
                    document.getElementById('status').innerHTML = '🔴 Desconectado';
                    document.getElementById('status').style.background = 'rgba(255,0,0,0.8)';
                    // Tentar reconectar em 5 segundos
                    setTimeout(connectWebSocket, 5000);
                }};
                
                ws.onerror = function(error) {{
                    console.error('WebSocket error:', error);
                    document.getElementById('status').innerHTML = '❌ Erro';
                    document.getElementById('status').style.background = 'rgba(255,0,0,0.8)';
                }};
            }}
            
            function displayImage(data) {{
                const container = document.getElementById('container');
                const timer = document.getElementById('timer');
                
                // Limpar timer anterior
                if (timerInterval) {{
                    clearInterval(timerInterval);
                }}
                
                // Salvar dados da imagem atual
                lastImageData = data;
                
                // Criar elemento de imagem
                const imageContainer = document.createElement('div');
                imageContainer.className = 'image-container';
                
                const img = document.createElement('img');
                img.className = 'image';
                img.src = `data:image/jpeg;base64,${{data.caminho_imagem}}`;
                
                imageContainer.appendChild(img);
                
                // Limpar container e adicionar nova imagem
                container.innerHTML = '';
                container.appendChild(imageContainer);
                
                // Verificar se é um novo evento ou manter imagem
                if (data.tipo === 'novo_evento') {{
                    // Iniciar timer apenas para novos eventos
                    timeLeft = 10;
                    timer.style.display = 'block';
                    document.getElementById('timer-text').textContent = timeLeft;
                    
                    timerInterval = setInterval(function() {{
                        timeLeft--;
                        document.getElementById('timer-text').textContent = timeLeft;
                        
                        if (timeLeft <= 0) {{
                            clearInterval(timerInterval);
                            timer.style.display = 'none';
                            // Não remover a imagem, apenas esconder o timer
                        }}
                    }}, 1000);
                }} else {{
                    // Para manter imagem, não mostrar timer
                    timer.style.display = 'none';
                }}
                
                console.log(`Imagem exibida: ${{data.tipo === 'novo_evento' ? 'Novo evento' : 'Mantendo imagem'}}`);
            }}
            
            // Iniciar conexão WebSocket
            connectWebSocket();
        </script>
    </body>
    </html>
    """

@router.get("/visualization1", response_class=HTMLResponse)
async def visualization1():
    return create_visualization_page("visualization1", 8083)

@router.get("/visualization2", response_class=HTMLResponse)
async def visualization2():
    return create_visualization_page("visualization2", 8084)

@router.get("/visualization3", response_class=HTMLResponse)
async def visualization3():
    return create_visualization_page("visualization3", 8085)

@router.get("/visualization4", response_class=HTMLResponse)
async def visualization4():
    return create_visualization_page("visualization4", 8086)

@router.get("/visualization5", response_class=HTMLResponse)
async def visualization5():
    return create_visualization_page("visualization5", 8087)

@router.get("/visualization6", response_class=HTMLResponse)
async def visualization6():
    return create_visualization_page("visualization6", 8088) 