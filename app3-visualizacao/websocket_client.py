import asyncio
import websockets
import json
import logging
import os
from datetime import datetime
import pytz
from typing import Optional, Callable

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração de timezone para Brasília
TIMEZONE = pytz.timezone('America/Sao_Paulo')

class VisualizationWebSocketClient:
    def __init__(self, visualization_name: str, port: int, websocket_server_url: str = "ws://websocket-server:8765"):
        self.visualization_name = visualization_name
        self.port = port
        self.websocket_server_url = websocket_server_url
        self.websocket = None
        self.connected = False
        self.reconnect_delay = 5  # segundos
        self.heartbeat_interval = 30  # segundos
        self.on_image_display_callback: Optional[Callable] = None
        
    def set_image_display_callback(self, callback: Callable):
        """Define callback para quando receber comando de exibir imagem"""
        self.on_image_display_callback = callback
    
    async def connect(self):
        """Conecta ao servidor WebSocket"""
        try:
            logger.info(f"Conectando ao servidor WebSocket: {self.websocket_server_url}")
            self.websocket = await websockets.connect(self.websocket_server_url)
            
            # Envia mensagem de registro
            register_message = {
                'type': 'register',
                'visualization_name': self.visualization_name,
                'port': self.port
            }
            
            await self.websocket.send(json.dumps(register_message))
            
            # Aguarda confirmação
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data.get('type') == 'register_confirmed':
                self.connected = True
                logger.info(f"Registrado no servidor WebSocket como {self.visualization_name}")
                return True
            else:
                logger.error("Falha no registro no servidor WebSocket")
                await self.websocket.close()
                return False
                
        except Exception as e:
            logger.error(f"Erro conectando ao servidor WebSocket: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Desconecta do servidor WebSocket"""
        if self.websocket:
            await self.websocket.close()
        self.connected = False
        logger.info("Desconectado do servidor WebSocket")
    
    async def send_heartbeat(self):
        """Envia heartbeat para o servidor"""
        if self.connected and self.websocket:
            try:
                heartbeat_message = {
                    'type': 'heartbeat',
                    'visualization_name': self.visualization_name,
                    'timestamp': datetime.now(TIMEZONE).isoformat()
                }
                await self.websocket.send(json.dumps(heartbeat_message))
            except Exception as e:
                logger.error(f"Erro enviando heartbeat: {e}")
                self.connected = False
    
    async def send_image_displayed(self, cpf: str):
        """Envia confirmação de que imagem foi exibida"""
        if self.connected and self.websocket:
            try:
                message = {
                    'type': 'image_displayed',
                    'visualization_name': self.visualization_name,
                    'cpf': cpf,
                    'timestamp': datetime.now(TIMEZONE).isoformat()
                }
                await self.websocket.send(json.dumps(message))
                logger.info(f"Confirmada exibição do CPF {cpf}")
            except Exception as e:
                logger.error(f"Erro enviando confirmação: {e}")
    
    async def send_error(self, error_message: str):
        """Envia mensagem de erro para o servidor"""
        if self.connected and self.websocket:
            try:
                message = {
                    'type': 'error',
                    'visualization_name': self.visualization_name,
                    'message': error_message,
                    'timestamp': datetime.now(TIMEZONE).isoformat()
                }
                await self.websocket.send(json.dumps(message))
                logger.error(f"Erro reportado: {error_message}")
            except Exception as e:
                logger.error(f"Erro enviando mensagem de erro: {e}")
    
    async def handle_messages(self):
        """Manipula mensagens recebidas do servidor"""
        if not self.websocket:
            return
        
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self.process_message(data)
                except json.JSONDecodeError:
                    logger.error("JSON inválido recebido do servidor")
                except Exception as e:
                    logger.error(f"Erro processando mensagem: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("Conexão com servidor WebSocket fechada")
            self.connected = False
        except Exception as e:
            logger.error(f"Erro na conexão WebSocket: {e}")
            self.connected = False
    
    async def process_message(self, data: dict):
        """Processa mensagens recebidas do servidor"""
        msg_type = data.get('type')
        
        if msg_type == 'display_image':
            cpf = data.get('cpf')
            display_time_str = data.get('display_time')
            
            logger.info(f"Comando recebido para exibir CPF {cpf}")
            
            # Chama callback se definido
            if self.on_image_display_callback:
                try:
                    await self.on_image_display_callback(cpf, display_time_str)
                except Exception as e:
                    logger.error(f"Erro no callback de exibição: {e}")
                    await self.send_error(f"Erro exibindo imagem: {e}")
            else:
                logger.warning("Nenhum callback definido para exibição de imagem")
        
        elif msg_type == 'ping':
            # Responde ao ping
            try:
                await self.websocket.send(json.dumps({
                    'type': 'pong',
                    'visualization_name': self.visualization_name,
                    'timestamp': datetime.now(TIMEZONE).isoformat()
                }))
            except Exception as e:
                logger.error(f"Erro respondendo ping: {e}")
    
    async def heartbeat_loop(self):
        """Loop para enviar heartbeats periódicos"""
        while self.connected:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                if self.connected:
                    await self.send_heartbeat()
            except Exception as e:
                logger.error(f"Erro no heartbeat loop: {e}")
                self.connected = False
                break
    
    async def run(self):
        """Executa o cliente WebSocket com reconexão automática"""
        while True:
            try:
                if await self.connect():
                    # Inicia tasks para heartbeat e mensagens
                    heartbeat_task = asyncio.create_task(self.heartbeat_loop())
                    messages_task = asyncio.create_task(self.handle_messages())
                    
                    # Aguarda até uma das tasks terminar
                    done, pending = await asyncio.wait(
                        [heartbeat_task, messages_task],
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    
                    # Cancela tasks pendentes
                    for task in pending:
                        task.cancel()
                    
                    logger.info("Conexão perdida, tentando reconectar...")
                else:
                    logger.error("Falha na conexão")
                
                # Aguarda antes de tentar reconectar
                await asyncio.sleep(self.reconnect_delay)
                
            except Exception as e:
                logger.error(f"Erro no loop principal: {e}")
                await asyncio.sleep(self.reconnect_delay)

# Função para obter configuração da visualização
def get_visualization_config():
    """Obtém configuração da visualização baseada na porta externa"""
    # Mapeia porta externa para nome da visualização
    port_to_name = {
        8083: 'visualization1',
        8084: 'visualization2', 
        8085: 'visualization3',
        8086: 'visualization4',
        8087: 'visualization5',
        8088: 'visualization6'
    }
    
    # Obtém porta externa do ambiente
    external_port = int(os.getenv('EXTERNAL_PORT', '8083'))
    visualization_name = port_to_name.get(external_port, 'visualization1')
    
    return {
        'visualization_name': visualization_name,
        'port': external_port
    }

# Instância global do cliente
websocket_client = None

async def start_websocket_client(image_display_callback: Optional[Callable] = None):
    """Inicia o cliente WebSocket"""
    global websocket_client
    
    config = get_visualization_config()
    websocket_client = VisualizationWebSocketClient(
        visualization_name=config['visualization_name'],
        port=config['port']
    )
    
    if image_display_callback:
        websocket_client.set_image_display_callback(image_display_callback)
    
    logger.info(f"Iniciando cliente WebSocket para {config['visualization_name']}")
    await websocket_client.run()

def get_websocket_client():
    """Retorna a instância global do cliente WebSocket"""
    return websocket_client 