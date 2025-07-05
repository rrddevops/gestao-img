import asyncio
import websockets
import json
import logging
from datetime import datetime
import pytz
from typing import Dict, Set, Optional

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração de timezone para Brasília
TIMEZONE = pytz.timezone('America/Sao_Paulo')

class VisualizationWebSocketServer:
    def __init__(self, host='0.0.0.0', port=8765):
        self.host = host
        self.port = port
        self.visualization_clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.client_info: Dict[str, Dict] = {}  # Informações sobre cada cliente
        
    async def register_client(self, websocket, path):
        """Registra um novo cliente de visualização"""
        try:
            # Aguarda mensagem de identificação do cliente
            message = await websocket.recv()
            data = json.loads(message)
            
            if data.get('type') == 'register':
                visualization_name = data.get('visualization_name')
                port = data.get('port')
                
                if visualization_name and port:
                    self.visualization_clients[visualization_name] = websocket
                    self.client_info[visualization_name] = {
                        'port': port,
                        'connected_at': datetime.now(TIMEZONE),
                        'last_heartbeat': datetime.now(TIMEZONE)
                    }
                    
                    logger.info(f"Cliente registrado: {visualization_name} (porta {port})")
                    
                    # Confirma registro
                    await websocket.send(json.dumps({
                        'type': 'register_confirmed',
                        'visualization_name': visualization_name
                    }))
                    
                    # Mantém conexão ativa
                    await self.handle_client_messages(websocket, visualization_name)
                else:
                    logger.error("Dados de registro inválidos")
                    await websocket.close()
            else:
                logger.error("Mensagem de registro esperada")
                await websocket.close()
                
        except websockets.exceptions.ConnectionClosed:
            logger.info("Conexão fechada durante registro")
        except Exception as e:
            logger.error(f"Erro durante registro: {e}")
            await websocket.close()
    
    async def handle_client_messages(self, websocket, visualization_name):
        """Manipula mensagens do cliente"""
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.process_client_message(visualization_name, data)
                except json.JSONDecodeError:
                    logger.error(f"JSON inválido recebido de {visualization_name}")
                except Exception as e:
                    logger.error(f"Erro processando mensagem de {visualization_name}: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Cliente {visualization_name} desconectado")
        finally:
            await self.unregister_client(visualization_name)
    
    async def process_client_message(self, visualization_name, data):
        """Processa mensagens dos clientes"""
        msg_type = data.get('type')
        
        if msg_type == 'heartbeat':
            # Atualiza heartbeat
            if visualization_name in self.client_info:
                self.client_info[visualization_name]['last_heartbeat'] = datetime.now(TIMEZONE)
                logger.debug(f"Heartbeat de {visualization_name}")
        
        elif msg_type == 'image_displayed':
            # Confirmação de que imagem foi exibida
            cpf = data.get('cpf')
            logger.info(f"Imagem do CPF {cpf} exibida em {visualization_name}")
        
        elif msg_type == 'error':
            # Erro reportado pelo cliente
            error_msg = data.get('message', 'Erro desconhecido')
            logger.error(f"Erro em {visualization_name}: {error_msg}")
    
    async def unregister_client(self, visualization_name):
        """Remove cliente da lista de conectados"""
        if visualization_name in self.visualization_clients:
            del self.visualization_clients[visualization_name]
        if visualization_name in self.client_info:
            del self.client_info[visualization_name]
        logger.info(f"Cliente {visualization_name} removido")
    
    async def broadcast_image(self, cpf: str, display_time: Optional[datetime] = None):
        """Envia comando para exibir imagem em todos os servidores conectados"""
        if not self.visualization_clients:
            logger.warning("Nenhum servidor de visualização conectado")
            return False
        
        message = {
            'type': 'display_image',
            'cpf': cpf,
            'timestamp': datetime.now(TIMEZONE).isoformat()
        }
        
        if display_time:
            message['display_time'] = display_time.isoformat()
        
        # Envia para todos os clientes conectados
        disconnected_clients = []
        success_count = 0
        
        for viz_name, websocket in self.visualization_clients.items():
            try:
                await websocket.send(json.dumps(message))
                success_count += 1
                logger.info(f"Comando enviado para {viz_name}")
            except websockets.exceptions.ConnectionClosed:
                logger.warning(f"Cliente {viz_name} desconectado durante broadcast")
                disconnected_clients.append(viz_name)
            except Exception as e:
                logger.error(f"Erro enviando para {viz_name}: {e}")
                disconnected_clients.append(viz_name)
        
        # Remove clientes desconectados
        for viz_name in disconnected_clients:
            await self.unregister_client(viz_name)
        
        logger.info(f"Broadcast concluído: {success_count} servidores notificados")
        return success_count > 0
    
    async def send_to_visualization(self, visualization_name: str, cpf: str, display_time: Optional[datetime] = None):
        """Envia comando para exibir imagem em um servidor específico"""
        if visualization_name not in self.visualization_clients:
            logger.error(f"Servidor {visualization_name} não está conectado")
            return False
        
        message = {
            'type': 'display_image',
            'cpf': cpf,
            'timestamp': datetime.now(TIMEZONE).isoformat()
        }
        
        if display_time:
            message['display_time'] = display_time.isoformat()
        
        try:
            await self.visualization_clients[visualization_name].send(json.dumps(message))
            logger.info(f"Comando enviado para {visualization_name}")
            return True
        except websockets.exceptions.ConnectionClosed:
            logger.error(f"Cliente {visualization_name} desconectado")
            await self.unregister_client(visualization_name)
            return False
        except Exception as e:
            logger.error(f"Erro enviando para {visualization_name}: {e}")
            return False
    
    def get_connected_visualizations(self):
        """Retorna lista de visualizações conectadas"""
        return list(self.visualization_clients.keys())
    
    def get_client_status(self):
        """Retorna status de todos os clientes"""
        status = {}
        now = datetime.now(TIMEZONE)
        
        for viz_name, info in self.client_info.items():
            connected = viz_name in self.visualization_clients
            last_heartbeat = info.get('last_heartbeat')
            heartbeat_age = (now - last_heartbeat).total_seconds() if last_heartbeat else None
            
            status[viz_name] = {
                'connected': connected,
                'port': info.get('port'),
                'connected_at': info.get('connected_at').isoformat() if info.get('connected_at') else None,
                'last_heartbeat': last_heartbeat.isoformat() if last_heartbeat else None,
                'heartbeat_age_seconds': heartbeat_age
            }
        
        return status
    
    async def start_server(self):
        """Inicia o servidor WebSocket"""
        logger.info(f"Iniciando servidor WebSocket em {self.host}:{self.port}")
        
        async with websockets.serve(self.register_client, self.host, self.port):
            logger.info("Servidor WebSocket iniciado e aguardando conexões")
            await asyncio.Future()  # Mantém servidor rodando indefinidamente

# Instância global do servidor
websocket_server = VisualizationWebSocketServer()

async def main():
    """Função principal para iniciar o servidor"""
    await websocket_server.start_server()

if __name__ == "__main__":
    asyncio.run(main()) 