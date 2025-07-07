from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Cadastro, Parametro, Evento
from app.schemas import WebhookRequest, WebhookResponse
from datetime import datetime, time, timedelta
import logging
import asyncio
import pytz

router = APIRouter(prefix="/webhook", tags=["webhook"])

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lock para garantir processamento sequencial
webhook_lock = asyncio.Lock()

# Timezone de Brasília
TIMEZONE_BRASILIA = pytz.timezone('America/Sao_Paulo')

def obter_parametro(db: Session, nome: str) -> int:
    """
    Obtém um parâmetro da tabela parametros
    """
    parametro = db.query(Parametro).filter(Parametro.nome == nome).first()
    if not parametro:
        # Valores padrão se não existirem na tabela
        valores_padrao = {
            "tempo_inicial_segundos": "30",
            "incremento_segundos": "10",
            "duracao_exibicao_seg": "10"
        }
        return int(valores_padrao.get(nome, "0"))
    return int(parametro.valor)

def obter_hora_brasilia():
    """
    Obtém a hora atual em Brasília
    """
    return datetime.now(TIMEZONE_BRASILIA)

@router.post("/", response_model=WebhookResponse)
async def processar_webhook(
    request: WebhookRequest,
    db: Session = Depends(get_db)
):
    """
    Processa webhook recebendo CPF e cria eventos para as 6 visualizações em sequência
    Cada visualização tem sua própria sequência independente
    """
    async with webhook_lock:  # Garantir processamento sequencial
        try:
            cpf = request.cpf
            
            # Verificar se CPF existe no cadastro
            cadastro = db.query(Cadastro).filter(Cadastro.cpf == cpf).first()
            if not cadastro:
                raise HTTPException(status_code=404, detail="CPF não encontrado no cadastro")
            
            # Obter parâmetros de tempo
            tempo_inicial = obter_parametro(db, "tempo_inicial_segundos")
            incremento = obter_parametro(db, "incremento_segundos")
            duracao_exibicao = obter_parametro(db, "duracao_exibicao_seg")
            
            # Obter hora atual em Brasília
            hora_atual_brasilia = obter_hora_brasilia()
            hora_atual = hora_atual_brasilia.time()
            
            # Lista de visualizações
            visualizations = [
                "visualization1", "visualization2", "visualization3",
                "visualization4", "visualization5", "visualization6"
            ]
            
            # Calcular horários para cada visualização individualmente
            eventos_criados = 0
            
            for i, visualization in enumerate(visualizations):
                # Buscar o último evento desta visualização específica
                ultimo_evento_visualization = db.query(Evento).filter(
                    Evento.visualization == visualization
                ).order_by(Evento.hora_fim.desc()).first()
                
                if ultimo_evento_visualization:
                    # Se existe evento anterior nesta visualização, começar após o último terminar
                    hora_inicio_base = ultimo_evento_visualization.hora_fim
                    
                    # Verificar se o último evento já terminou
                    if hora_inicio_base <= hora_atual:
                        # Último evento já terminou, começar imediatamente
                        # Aplicar delay baseado nos parâmetros da tabela
                        delay_inicial = tempo_inicial + (i * incremento)
                        hora_inicio_dt = hora_atual_brasilia + timedelta(seconds=delay_inicial)
                    else:
                        # Último evento ainda está ativo, começar após ele terminar
                        # Converter para datetime com timezone de Brasília
                        data_atual = hora_atual_brasilia.date()
                        hora_inicio_dt = TIMEZONE_BRASILIA.localize(
                            datetime.combine(data_atual, hora_inicio_base)
                        )
                        # Aplicar delay baseado nos parâmetros da tabela
                        delay_inicial = tempo_inicial + (i * incremento)
                        hora_inicio_dt += timedelta(seconds=delay_inicial)
                else:
                    # Primeiro evento desta visualização
                    # Calcular delay baseado no índice da visualização
                    delay_inicial = tempo_inicial + (i * incremento)
                    hora_inicio_dt = hora_atual_brasilia + timedelta(seconds=delay_inicial)
                
                # Calcular horários para este evento
                hora_exibicao_dt = hora_inicio_dt
                hora_fim_dt = hora_exibicao_dt + timedelta(seconds=duracao_exibicao)
                
                # Converter de volta para time (sem timezone para o banco)
                hora_exibicao = hora_exibicao_dt.time()
                hora_fim = hora_fim_dt.time()
                
                # Calcular delay (diferença entre hora atual e hora de exibição)
                delay_timedelta = hora_exibicao_dt - hora_atual_brasilia
                
                # Criar evento
                evento = Evento(
                    cpf=cpf,
                    visualization=visualization,
                    hora_acesso=hora_atual,
                    delay=delay_timedelta,
                    hora_exibicao=hora_exibicao,
                    hora_fim=hora_fim
                )
                
                db.add(evento)
                eventos_criados += 1
                
                logger.info(f"Evento criado: {visualization} - CPF: {cpf} - Exibição: {hora_exibicao} - Fim: {hora_fim}")
            
            db.commit()
            
            return WebhookResponse(
                message=f"Webhook processado com sucesso para CPF {cpf}",
                cpf=cpf,
                hora_acesso=hora_atual,
                eventos_criados=eventos_criados
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao processar webhook: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao processar webhook: {str(e)}")

@router.get("/eventos", response_model=list)
async def listar_eventos(db: Session = Depends(get_db)):
    """
    Lista todos os eventos agendados
    """
    eventos = db.query(Evento).order_by(Evento.hora_exibicao).all()
    return [
        {
            "id": e.id,
            "cpf": e.cpf,
            "visualization": e.visualization,
            "hora_acesso": str(e.hora_acesso),
            "delay": str(e.delay),
            "hora_exibicao": str(e.hora_exibicao),
            "hora_fim": str(e.hora_fim)
        }
        for e in eventos
    ]

@router.get("/eventos/{cpf}", response_model=list)
async def listar_eventos_cpf(cpf: str, db: Session = Depends(get_db)):
    """
    Lista eventos de um CPF específico
    """
    eventos = db.query(Evento).filter(Evento.cpf == cpf).order_by(Evento.hora_exibicao).all()
    return [
        {
            "id": e.id,
            "cpf": e.cpf,
            "visualization": e.visualization,
            "hora_acesso": str(e.hora_acesso),
            "delay": str(e.delay),
            "hora_exibicao": str(e.hora_exibicao),
            "hora_fim": str(e.hora_fim)
        }
        for e in eventos
    ]

@router.delete("/eventos/{cpf}")
async def deletar_eventos_cpf(cpf: str, db: Session = Depends(get_db)):
    """
    Deleta todos os eventos de um CPF específico
    """
    eventos = db.query(Evento).filter(Evento.cpf == cpf).all()
    if not eventos:
        raise HTTPException(status_code=404, detail="Nenhum evento encontrado para este CPF")
    
    for evento in eventos:
        db.delete(evento)
    
    db.commit()
    
    return {"message": f"Todos os eventos do CPF {cpf} foram deletados"}

@router.delete("/eventos")
async def limpar_todos_eventos(db: Session = Depends(get_db)):
    """
    Deleta todos os eventos do sistema
    """
    eventos = db.query(Evento).all()
    count = len(eventos)
    
    for evento in eventos:
        db.delete(evento)
    
    db.commit()
    
    return {"message": f"Todos os {count} eventos foram deletados"}

@router.get("/status")
async def status_webhook(db: Session = Depends(get_db)):
    """
    Retorna status dos eventos
    """
    total_eventos = db.query(Evento).count()
    eventos_por_cpf = db.query(Evento.cpf, db.func.count(Evento.id)).group_by(Evento.cpf).all()
    
    return {
        "total_eventos": total_eventos,
        "cpfs_ativos": len(eventos_por_cpf),
        "eventos_por_cpf": [{"cpf": cpf, "count": count} for cpf, count in eventos_por_cpf]
    } 