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
        
        # Cache para controlar última imagem enviada por visualização
        self.last_sent_images: Dict[str, Dict] = {}
        
        # Agendar verificação a cada segundo
        self.scheduler.add_job(
            self.check_events,
            IntervalTrigger(seconds=1),
            id='check_events',
            replace_existing=True
        )
        
        # Agendar limpeza de cache a cada 5 minutos
        self.scheduler.add_job(
            self.limpar_cache_antigo,
            IntervalTrigger(minutes=5),
            id='limpar_cache',
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
                event_key = f"{visualization}_active_{evento_ativo.id}"
                if event_key not in self.processed_events:
                    # Processar novo evento
                    await self.process_event(evento_ativo, db)
                    self.processed_events[event_key] = evento_ativo.id
                    logger.info(f"🆕 NOVO EVENTO: {visualization} - CPF: {evento_ativo.cpf} - Hora: {hora_atual}")
            else:
                # Se não há evento ativo, manter última imagem cronológica
                await self.manter_ultima_imagem_cronologica(visualization, db)
                
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
            
            # Atualizar cache da última imagem enviada
            self.last_sent_images[evento.visualization] = {
                "cpf": evento.cpf,
                "evento_id": evento.id,
                "timestamp": datetime.now().timestamp()
            }
            
            logger.info(f"✅ Evento processado: {evento.visualization} - CPF: {evento.cpf} - Hora: {evento.hora_exibicao}")
            
        except Exception as e:
            logger.error(f"Erro ao processar evento {evento.id}: {str(e)}")
    
    async def manter_ultima_imagem_cronologica(self, visualization: str, db: Session):
        """
        Mantém a última imagem cronológica na tela quando não há eventos ativos
        """
        try:
            # Buscar o último evento cronológico desta visualização (que já terminou)
            ultimo_evento = db.query(Evento).filter(
                Evento.visualization == visualization,
                Evento.hora_fim <= self.obter_hora_brasilia().time()  # Apenas eventos que já terminaram
            ).order_by(Evento.hora_fim.desc()).first()
            
            if not ultimo_evento:
                # Se não há eventos para esta visualização, não fazer nada
                return
            
            # Buscar dados do cadastro
            cadastro = db.query(Cadastro).filter(Cadastro.cpf == ultimo_evento.cpf).first()
            if not cadastro:
                return
            
            # Verificar se já enviamos esta imagem recentemente
            current_time = datetime.now().timestamp()
            last_sent = self.last_sent_images.get(visualization, {})
            
            # Se é a mesma imagem e foi enviada há menos de 60 segundos, não reenviar
            if (last_sent.get("cpf") == ultimo_evento.cpf and 
                last_sent.get("evento_id") == ultimo_evento.id and
                current_time - last_sent.get("timestamp", 0) < 60):
                return
            
            # Preparar mensagem WebSocket para manter imagem
            ws_message = {
                "cpf": ultimo_evento.cpf,
                "caminho_imagem": cadastro.caminho_imagem,
                "visualization": visualization,
                "timestamp": datetime.now().isoformat(),
                "hora_exibicao": str(ultimo_evento.hora_exibicao),
                "hora_fim": str(ultimo_evento.hora_fim),
                "tipo": "manter_imagem_cronologica"
            }
            
            # Enviar via WebSocket
            await manager.send_personal_message(
                json.dumps(ws_message), 
                visualization
            )
            
            # Atualizar cache da última imagem enviada
            self.last_sent_images[visualization] = {
                "cpf": ultimo_evento.cpf,
                "evento_id": ultimo_evento.id,
                "timestamp": current_time
            }
            
            logger.info(f"🔄 MANTENDO IMAGEM CRONOLÓGICA: {visualization} - CPF: {ultimo_evento.cpf} (último evento: {ultimo_evento.hora_fim})")
                
        except Exception as e:
            logger.error(f"Erro ao manter última imagem cronológica para {visualization}: {str(e)}")
    
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
                logger.info(f"🧹 Cache limpo: {len(keys_to_remove)} entradas removidas")
                
            # Limpar cache de imagens antigas (mais de 1 hora)
            current_time = datetime.now().timestamp()
            keys_to_remove = []
            for viz, data in self.last_sent_images.items():
                if current_time - data.get("timestamp", 0) > 3600:  # 1 hora
                    keys_to_remove.append(viz)
            
            for key in keys_to_remove:
                del self.last_sent_images[key]
                
            if keys_to_remove:
                logger.info(f"🧹 Cache de imagens limpo: {len(keys_to_remove)} entradas removidas")
                
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {str(e)}")
    
    def add_event(self, evento: Evento):
        """
        Adiciona um evento ao agendador
        """
        try:
            logger.info(f"Evento adicionado: {evento.visualization} - CPF: {evento.cpf}")
        except Exception as e:
            logger.error(f"Erro ao adicionar evento: {str(e)}")
    
    def get_scheduler_status(self):
        """
        Retorna status do agendador
        """
        try:
            return {
                "running": self.scheduler.running,
                "jobs": len(self.scheduler.get_jobs()),
                "processed_events": len(self.processed_events),
                "last_sent_images": len(self.last_sent_images)
            }
        except Exception as e:
            logger.error(f"Erro ao obter status do agendador: {str(e)}")
            return {"error": str(e)}
    
    def stop(self):
        """
        Para o agendador
        """
        try:
            self.scheduler.shutdown()
            logger.info("Agendador de eventos parado")
        except Exception as e:
            logger.error(f"Erro ao parar agendador: {str(e)}")

# Instância global do agendador
event_scheduler = EventScheduler() 