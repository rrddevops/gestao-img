from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Evento, Cadastro
from app.views.websocket import manager
from datetime import datetime, time
import json
import logging
from typing import List, Dict
import pytz

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Timezone de Brasília
TIMEZONE_BRASILIA = pytz.timezone('America/Sao_Paulo')

class EventScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        
        # Cache para controlar eventos já processados
        self.processed_events: Dict[str, int] = {}
        
        # Agendar verificação a cada segundo
        self.scheduler.add_job(
            self.check_events,
            IntervalTrigger(seconds=1),
            id='check_events',
            replace_existing=True
        )
        
        logger.info("Agendador de eventos iniciado")
    
    def obter_hora_brasilia(self):
        """
        Obtém a hora atual em Brasília
        """
        return datetime.now(TIMEZONE_BRASILIA)
    
    async def check_events(self):
        """
        Verifica eventos que devem ser exibidos agora
        """
        try:
            db = SessionLocal()
            hora_atual_brasilia = self.obter_hora_brasilia()
            hora_atual = hora_atual_brasilia.time()
            
            # Lista de visualizações
            visualizations = [
                "visualization1", "visualization2", "visualization3",
                "visualization4", "visualization5", "visualization6"
            ]
            
            # Processar cada visualização individualmente
            for visualization in visualizations:
                await self.process_visualization(visualization, hora_atual, db)
                
        except Exception as e:
            logger.error(f"Erro ao verificar eventos: {str(e)}")
        finally:
            db.close()
    
    async def process_visualization(self, visualization: str, hora_atual: time, db: Session):
        """
        Processa eventos para uma visualização específica
        """
        try:
            # Buscar evento ativo para esta visualização
            evento_ativo = db.query(Evento).filter(
                Evento.visualization == visualization,
                Evento.hora_exibicao <= hora_atual,
                Evento.hora_fim > hora_atual
            ).order_by(Evento.hora_exibicao.desc()).first()
            
            if evento_ativo:
                # Verificar se este evento já foi processado
                event_key = f"{visualization}_{evento_ativo.id}"
                if event_key not in self.processed_events:
                    # Processar novo evento
                    await self.process_event(evento_ativo, db)
                    self.processed_events[event_key] = evento_ativo.id
                    logger.info(f"Novo evento processado: {visualization} - CPF: {evento_ativo.cpf} - Hora: {hora_atual}")
            else:
                # Se não há evento ativo, manter última imagem
                await self.manter_ultima_imagem(visualization, db)
                
        except Exception as e:
            logger.error(f"Erro ao processar visualização {visualization}: {str(e)}")
    
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
                "hora_fim": str(evento.hora_fim),
                "tipo": "novo_evento"
            }
            
            # Enviar via WebSocket
            await manager.send_personal_message(
                json.dumps(ws_message), 
                evento.visualization
            )
            
            logger.info(f"Evento processado: {evento.visualization} - CPF: {evento.cpf} - Hora: {evento.hora_exibicao}")
            
        except Exception as e:
            logger.error(f"Erro ao processar evento {evento.id}: {str(e)}")
    
    async def manter_ultima_imagem(self, visualization: str, db: Session):
        """
        Mantém a última imagem na tela quando não há eventos ativos
        """
        try:
            # Buscar o último evento desta visualização
            ultimo_evento = db.query(Evento).filter(
                Evento.visualization == visualization
            ).order_by(Evento.hora_exibicao.desc()).first()
            
            if ultimo_evento:
                # Buscar dados do cadastro
                cadastro = db.query(Cadastro).filter(Cadastro.cpf == ultimo_evento.cpf).first()
                if not cadastro:
                    return
                
                # Preparar mensagem WebSocket para manter imagem
                ws_message = {
                    "cpf": ultimo_evento.cpf,
                    "caminho_imagem": cadastro.caminho_imagem,
                    "visualization": visualization,
                    "timestamp": datetime.now().isoformat(),
                    "hora_exibicao": str(ultimo_evento.hora_exibicao),
                    "hora_fim": str(ultimo_evento.hora_fim),
                    "tipo": "manter_imagem"
                }
                
                # Enviar via WebSocket apenas se não foi enviado recentemente
                event_key = f"{visualization}_keep_{ultimo_evento.id}"
                if event_key not in self.processed_events:
                    await manager.send_personal_message(
                        json.dumps(ws_message), 
                        visualization
                    )
                    self.processed_events[event_key] = ultimo_evento.id
                
        except Exception as e:
            logger.error(f"Erro ao manter última imagem para {visualization}: {str(e)}")
    
    def limpar_cache_antigo(self):
        """
        Limpa eventos antigos do cache para evitar vazamento de memória
        """
        try:
            # Manter apenas os últimos 100 eventos processados
            if len(self.processed_events) > 100:
                # Remover entradas mais antigas
                keys_to_remove = list(self.processed_events.keys())[:-100]
                for key in keys_to_remove:
                    del self.processed_events[key]
                logger.info(f"Cache limpo: {len(keys_to_remove)} entradas removidas")
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {str(e)}")
    
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
            "cache_size": len(self.processed_events),
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