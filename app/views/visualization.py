from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import json

router = APIRouter(tags=["visualization"])

def create_visualization_page(visualization_name: str, port: int):
    """
    Cria uma página de visualização específica
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{0}</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: #000;
                color: white;
                font-family: Arial, sans-serif;
                overflow: hidden;
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
            .image-status {{
                position: fixed;
                bottom: 20px;
                left: 20px;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 10px 15px;
                border-radius: 20px;
                font-size: 12px;
                max-width: 300px;
            }}
        </style>
    </head>
    <body>
        <div class="info">
            <strong>{0}</strong><br>
            Porta: {1}<br>
            WebSocket: ws://localhost:8000/websocket/{2}<br>
            <small>Versão: 3.0 (Imagem Cronológica)</small>
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
        
        <div class="image-status" id="image-status" style="display: none;">
            <span id="image-status-text">Aguardando imagem...</span>
        </div>
        
        <script>
            // Forçar recarregamento se for versão antiga
            if (localStorage.getItem('visualization_version') !== '3.0') {{
                localStorage.setItem('visualization_version', '3.0');
                location.reload(true);
            }}
            
            let ws = null;
            let currentImage = null;
            let timerInterval = null;
            let timeLeft = 10;
            let lastImageData = null;
            let imageStatus = document.getElementById('image-status');
            let imageStatusText = document.getElementById('image-status-text');
            
            function anonymizeCPF(cpf) {{
                if (!cpf || cpf.length < 5) return cpf;
                return cpf.substring(0, 3) + '******' + cpf.substring(cpf.length - 2);
            }}

            function connectWebSocket() {{
                const wsUrl = `ws://${{window.location.hostname}}:8000/websocket/{3}`;
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
                
                // Mostrar status da imagem
                imageStatus.style.display = 'block';
                
                // Verificar tipo de evento e configurar interface
                if (data.tipo === 'novo_evento') {{
                    // Novo evento - exibir nova imagem e mostrar timer
                    const imageContainer = document.createElement('div');
                    imageContainer.className = 'image-container';
                    
                    const img = document.createElement('img');
                    img.className = 'image';
                    img.src = `data:image/jpeg;base64,${{data.caminho_imagem}}`;
                    
                    imageContainer.appendChild(img);
                    
                    // Limpar container e adicionar nova imagem
                    container.innerHTML = '';
                    container.appendChild(imageContainer);
                    
                    // Mostrar timer
                    timeLeft = 10;
                    timer.style.display = 'block';
                    document.getElementById('timer-text').textContent = timeLeft;
                    
                    // Atualizar status
                    imageStatusText.innerHTML = `🆕 <strong>Novo Evento</strong><br>CPF: ${{anonymizeCPF(data.cpf)}}<br>Exibição: ${{data.hora_exibicao}}`;
                    imageStatus.style.background = 'rgba(0,128,0,0.8)';
                    
                    timerInterval = setInterval(function() {{
                        timeLeft--;
                        document.getElementById('timer-text').textContent = timeLeft;
                        
                        if (timeLeft <= 0) {{
                            clearInterval(timerInterval);
                            timer.style.display = 'none';
                            // Não remover a imagem, apenas esconder o timer
                        }}
                    }}, 1000);
                    
                    console.log(`🆕 NOVO EVENTO: CPF ${{anonymizeCPF(data.cpf)}} - Exibição: ${{data.hora_exibicao}}`);
                }} else if (data.tipo === 'manter_imagem_cronologica') {{
                    // Manter imagem cronológica - exibir nova imagem mas não mostrar timer
                    const imageContainer = document.createElement('div');
                    imageContainer.className = 'image-container';
                    
                    const img = document.createElement('img');
                    img.className = 'image';
                    img.src = `data:image/jpeg;base64,${{data.caminho_imagem}}`;
                    
                    imageContainer.appendChild(img);
                    
                    // Limpar container e adicionar nova imagem
                    container.innerHTML = '';
                    container.appendChild(imageContainer);
                    
                    // Não mostrar timer
                    timer.style.display = 'none';
                    
                    // Atualizar status
                    imageStatusText.innerHTML = `🔄 <strong>Imagem Cronológica</strong><br>CPF: ${{anonymizeCPF(data.cpf)}}<br>Último evento: ${{data.hora_exibicao}}`;
                    imageStatus.style.background = 'rgba(255,165,0,0.8)';
                    
                    console.log(`🔄 MANTENDO IMAGEM CRONOLÓGICA: CPF ${{anonymizeCPF(data.cpf)}} - Último evento: ${{data.hora_exibicao}}`);
                }} else if (data.tipo === 'aguardando_proximo_evento') {{
                    // Aguardando próximo evento - NÃO exibir nova imagem, apenas mostrar timer de espera
                    // Manter a imagem atual na tela
                    
                    // Mostrar timer de espera
                    let tempoRestante = Math.ceil(data.tempo_restante);
                    timer.style.display = 'block';
                    document.getElementById('timer-text').textContent = tempoRestante;
                    
                    // Atualizar status
                    imageStatusText.innerHTML = `⏳ <strong>Aguardando próxima imagem</strong><br>CPF: ${{anonymizeCPF(data.cpf)}}<br>Exibição prevista: ${{data.hora_exibicao}}`;
                    imageStatus.style.background = 'rgba(0,0,255,0.8)';
                    
                    timerInterval = setInterval(function() {{
                        tempoRestante--;
                        document.getElementById('timer-text').textContent = tempoRestante;
                        if (tempoRestante <= 0) {{
                            clearInterval(timerInterval);
                            timer.style.display = 'none';
                        }}
                    }}, 1000);
                    
                    console.log(`⏳ AGUARDANDO PRÓXIMO EVENTO: CPF ${{anonymizeCPF(data.cpf)}} - Exibição prevista: ${{data.hora_exibicao}}`);
                }} else {{
                    // Outro tipo - exibir nova imagem mas não mostrar timer
                    const imageContainer = document.createElement('div');
                    imageContainer.className = 'image-container';
                    
                    const img = document.createElement('img');
                    img.className = 'image';
                    img.src = `data:image/jpeg;base64,${{data.caminho_imagem}}`;
                    
                    imageContainer.appendChild(img);
                    
                    // Limpar container e adicionar nova imagem
                    container.innerHTML = '';
                    container.appendChild(imageContainer);
                    
                    // Não mostrar timer
                    timer.style.display = 'none';
                    
                    // Atualizar status
                    imageStatusText.innerHTML = `📺 <strong>Imagem</strong><br>CPF: ${{anonymizeCPF(data.cpf)}}`;
                    imageStatus.style.background = 'rgba(0,0,255,0.8)';
                    
                    console.log(`📺 IMAGEM: CPF ${{anonymizeCPF(data.cpf)}}`);
                }}
            }}
            
            // Iniciar conexão WebSocket
            connectWebSocket();
        </script>
    </body>
    </html>
    """.format(
        visualization_name.title(),
        port,
        visualization_name,
        visualization_name
    )

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