from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Evento, Cadastro
from app.views.websocket import manager
from datetime import datetime, time
import json
import logging
from typing import List

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        
        # Agendar verificação a cada segundo
        self.scheduler.add_job(
            self.check_events,
            IntervalTrigger(seconds=1),
            id='check_events',
            replace_existing=True
        )
        
        logger.info("Agendador de eventos iniciado")
    
    async def check_events(self):
        """
        Verifica eventos que devem ser exibidos agora
        """
        try:
            db = SessionLocal()
            hora_atual = datetime.now().time()
            
            # Buscar eventos ativos (hora_exibicao <= agora < hora_fim)
            eventos_ativos = db.query(Evento).filter(
                Evento.hora_exibicao <= hora_atual,
                Evento.hora_fim > hora_atual
            ).all()
            
            for evento in eventos_ativos:
                await self.process_event(evento, db)
                
        except Exception as e:
            logger.error(f"Erro ao verificar eventos: {str(e)}")
        finally:
            db.close()
    
    async def process_event(self, evento: Evento, db: Session):
        """
        Processa um evento específico
        """
        try:
            # Buscar dados do cadastro
            cadastro = db.query(Cadastro).filter(Cadastro.cpf == evento.cpf).first()
            if not cadastro:
                logger.warning(f"CPF {evento.cpf} não encontrado no cadastro")
                return
            
            # Preparar mensagem WebSocket
            ws_message = {
                "cpf": evento.cpf,
                "caminho_imagem": cadastro.caminho_imagem,
                "visualization": evento.visualization,
                "timestamp": datetime.now().isoformat(),
                "hora_exibicao": str(evento.hora_exibicao),
                "hora_fim": str(evento.hora_fim)
            }
            
            # Enviar via WebSocket
            await manager.send_personal_message(
                json.dumps(ws_message), 
                evento.visualization
            )
            
            logger.info(f"Evento processado: {evento.visualization} - CPF: {evento.cpf}")
            
        except Exception as e:
            logger.error(f"Erro ao processar evento {evento.id}: {str(e)}")
    
    def add_event(self, evento: Evento):
        """
        Adiciona um evento ao agendador
        """
        try:
            # O evento será processado automaticamente pelo check_events
            logger.info(f"Evento adicionado ao agendador: {evento.visualization} - CPF: {evento.cpf}")
        except Exception as e:
            logger.error(f"Erro ao adicionar evento: {str(e)}")
    
    def get_scheduler_status(self):
        """
        Retorna status do agendador
        """
        return {
            "running": self.scheduler.running,
            "jobs": len(self.scheduler.get_jobs()),
            "next_run_time": str(self.scheduler.get_job('check_events').next_run_time) if self.scheduler.get_job('check_events') else None
        }
    
    def stop(self):
        """
        Para o agendador
        """
        self.scheduler.shutdown()
        logger.info("Agendador de eventos parado")

# Instância global do agendador
event_scheduler = EventScheduler() 