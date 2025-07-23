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
            .top-info-bar {{
                position: fixed;
                top: 5px;
                left: 5px;
                right: 5px;
                background: rgba(0,0,0,0.9);
                color: white;
                padding: 8px 12px;
                border-radius: 5px;
                font-size: 12px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                z-index: 1000;
                height: 20px;
            }}
            .info-left {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            .info-right {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            .status-indicator {{
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
            }}
            .status-connected {{
                background: rgba(0,128,0,0.8);
            }}
            .status-disconnected {{
                background: rgba(255,0,0,0.8);
            }}
            .status-error {{
                background: rgba(255,0,0,0.8);
            }}
            .event-type {{
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
            }}
            .event-new {{
                background: rgba(0,128,0,0.8);
            }}
            .event-chronological {{
                background: rgba(255,165,0,0.8);
            }}
            .event-waiting {{
                background: rgba(0,0,255,0.8);
            }}
            .loading {{
                color: white;
                font-size: 24px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="top-info-bar">
            <div class="info-left">
                <span><strong>{0}</strong></span>
                <span>Porta: {1}</span>
                <span id="connection-status">🔴 Desconectado</span>
                <span id="event-info" style="display: none;">
                    <span id="event-type" class="event-type"></span>
                    <span id="cpf-info"></span>
                    <span id="timer-info"></span>
                </span>
            </div>
            <div class="info-right">
                <span id="next-event-info" style="display: none;">
                    Próxima: <span id="next-cpf"></span> em <span id="next-timer">0</span>s
                </span>
            </div>
        </div>
        
        <div class="container" id="container">
            <div class="loading">
                Aguardando conexão WebSocket...
            </div>
        </div>
        
        <script>
            // Forçar recarregamento se for versão antiga
            if (localStorage.getItem('visualization_version') !== '4.0') {{
                localStorage.setItem('visualization_version', '4.0');
                location.reload(true);
            }}
            
            let ws = null;
            let currentImage = null;
            let timerInterval = null;
            let timeLeft = 10;
            let lastImageData = null;
            
            function anonymizeCPF(cpf) {{
                if (!cpf || cpf.length < 5) return cpf;
                return cpf.substring(0, 3) + '******' + cpf.substring(cpf.length - 2);
            }}

            function connectWebSocket() {{
                const wsUrl = `ws://${{window.location.hostname}}:8000/websocket/{3}`;
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function() {{
                    document.getElementById('connection-status').innerHTML = '🟢 Conectado';
                    document.getElementById('connection-status').className = 'status-indicator status-connected';
                }};
                
                ws.onmessage = function(event) {{
                    const data = JSON.parse(event.data);
                    displayImage(data);
                }};
                
                ws.onclose = function() {{
                    document.getElementById('connection-status').innerHTML = '🔴 Desconectado';
                    document.getElementById('connection-status').className = 'status-indicator status-disconnected';
                    // Tentar reconectar em 5 segundos
                    setTimeout(connectWebSocket, 5000);
                }};
                
                ws.onerror = function(error) {{
                    console.error('WebSocket error:', error);
                    document.getElementById('connection-status').innerHTML = '❌ Erro';
                    document.getElementById('connection-status').className = 'status-indicator status-error';
                }};
            }}
            
            function displayImage(data) {{
                const container = document.getElementById('container');
                const eventInfo = document.getElementById('event-info');
                const nextEventInfo = document.getElementById('next-event-info');
                
                // Limpar timer anterior
                if (timerInterval) {{
                    clearInterval(timerInterval);
                }}
                
                // Salvar dados da imagem atual
                lastImageData = data;
                
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
                    
                    // Mostrar informações do evento
                    eventInfo.style.display = 'block';
                    document.getElementById('event-type').textContent = '🆕 NOVO';
                    document.getElementById('event-type').className = 'event-type event-new';
                    document.getElementById('cpf-info').textContent = `CPF: ${{anonymizeCPF(data.cpf)}}`;
                    
                    // Mostrar timer
                    timeLeft = 10;
                    document.getElementById('timer-info').textContent = `Timer: ${{timeLeft}}s`;
                    
                    timerInterval = setInterval(function() {{
                        timeLeft--;
                        document.getElementById('timer-info').textContent = `Timer: ${{timeLeft}}s`;
                        
                        if (timeLeft <= 0) {{
                            clearInterval(timerInterval);
                            document.getElementById('timer-info').textContent = '';
                        }}
                    }}, 1000);
                    
                    // Esconder info do próximo evento
                    nextEventInfo.style.display = 'none';
                    
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
                    
                    // Mostrar informações do evento
                    eventInfo.style.display = 'block';
                    document.getElementById('event-type').textContent = '🔄 CRONO';
                    document.getElementById('event-type').className = 'event-type event-chronological';
                    document.getElementById('cpf-info').textContent = `CPF: ${{anonymizeCPF(data.cpf)}}`;
                    document.getElementById('timer-info').textContent = '';
                    
                    // Esconder info do próximo evento
                    nextEventInfo.style.display = 'none';
                    
                    console.log(`🔄 MANTENDO IMAGEM CRONOLÓGICA: CPF ${{anonymizeCPF(data.cpf)}} - Último evento: ${{data.hora_exibicao}}`);
                }} else if (data.tipo === 'aguardando_proximo_evento') {{
                    // Aguardando próximo evento - NÃO exibir nova imagem, apenas mostrar timer de espera
                    // Manter a imagem atual na tela
                    
                    // Mostrar informações do próximo evento
                    nextEventInfo.style.display = 'block';
                    document.getElementById('next-cpf').textContent = anonymizeCPF(data.cpf);
                    
                    let tempoRestante = Math.ceil(data.tempo_restante);
                    document.getElementById('next-timer').textContent = tempoRestante;
                    
                    // Esconder info do evento atual
                    eventInfo.style.display = 'none';
                    
                    timerInterval = setInterval(function() {{
                        tempoRestante--;
                        document.getElementById('next-timer').textContent = tempoRestante;
                        if (tempoRestante <= 0) {{
                            clearInterval(timerInterval);
                            nextEventInfo.style.display = 'none';
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
                    
                    // Mostrar informações básicas
                    eventInfo.style.display = 'block';
                    document.getElementById('event-type').textContent = '📺 IMG';
                    document.getElementById('event-type').className = 'event-type event-waiting';
                    document.getElementById('cpf-info').textContent = `CPF: ${{anonymizeCPF(data.cpf)}}`;
                    document.getElementById('timer-info').textContent = '';
                    
                    // Esconder info do próximo evento
                    nextEventInfo.style.display = 'none';
                    
                    console.log(`📺 IMAGEM: CPF ${{anonymizeCPF(data.cpf)}}`);
                }}
            }}
            
            // Iniciar conexão WebSocket
            connectWebSocket();
        </script>
    </body>
    </html>
    """.format(visualization_name, port, visualization_name, visualization_name)

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