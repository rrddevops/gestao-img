from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Cadastro, Evento
from app.schemas import WebSocketMessage
from datetime import datetime, time
import json
import logging
from typing import Dict, List

router = APIRouter(prefix="/websocket", tags=["websocket"])

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Armazenar conexões WebSocket ativas
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, visualization: str):
        await websocket.accept()
        self.active_connections[visualization] = websocket
        logger.info(f"Cliente {visualization} conectado")

    def disconnect(self, visualization: str):
        if visualization in self.active_connections:
            del self.active_connections[visualization]
            logger.info(f"Cliente {visualization} desconectado")

    async def send_personal_message(self, message: str, visualization: str):
        if visualization in self.active_connections:
            await self.active_connections[visualization].send_text(message)
            logger.info(f"Mensagem enviada para {visualization}: {message}")

    async def broadcast(self, message: str):
        for visualization in self.active_connections:
            await self.send_personal_message(message, visualization)

manager = ConnectionManager()

@router.websocket("/{visualization}")
async def websocket_endpoint(websocket: WebSocket, visualization: str):
    """
    Endpoint WebSocket para cada visualização
    """
    await manager.connect(websocket, visualization)
    try:
        while True:
            # Manter conexão ativa
            data = await websocket.receive_text()
            # Processar mensagens se necessário
            logger.info(f"Mensagem recebida de {visualization}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(visualization)

@router.post("/send/{visualization}")
async def send_to_visualization(
    visualization: str,
    message: WebSocketMessage,
    db: Session = Depends(get_db)
):
    """
    Envia mensagem para uma visualização específica
    """
    try:
        # Verificar se CPF existe
        cadastro = db.query(Cadastro).filter(Cadastro.cpf == message.cpf).first()
        if not cadastro:
            raise HTTPException(status_code=404, detail="CPF não encontrado")
        
        # Preparar mensagem
        ws_message = {
            "cpf": message.cpf,
            "caminho_imagem": cadastro.caminho_imagem,
            "visualization": visualization,
            "timestamp": datetime.now().isoformat()
        }
        
        # Enviar via WebSocket
        await manager.send_personal_message(json.dumps(ws_message), visualization)
        
        return {"message": f"Mensagem enviada para {visualization}", "data": ws_message}
        
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar mensagem: {str(e)}")

@router.get("/status")
async def get_websocket_status():
    """
    Retorna status das conexões WebSocket
    """
    return {
        "active_connections": list(manager.active_connections.keys()),
        "total_connections": len(manager.active_connections)
    } 