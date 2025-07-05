from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Cadastro, Parametro, Evento
from app.schemas import WebhookRequest, WebhookResponse
from datetime import datetime, time, timedelta
import logging

router = APIRouter(prefix="/webhook", tags=["webhook"])

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@router.post("/", response_model=WebhookResponse)
async def processar_webhook(
    request: WebhookRequest,
    db: Session = Depends(get_db)
):
    """
    Processa webhook recebendo CPF e cria eventos para as 6 visualizações
    """
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
        
        # Obter hora atual
        hora_atual = datetime.now().time()
        
        # Calcular horário de início baseado no último evento existente
        ultimo_evento = db.query(Evento).order_by(Evento.hora_exibicao.desc()).first()
        
        if ultimo_evento:
            # Se existe evento anterior, começar após o último
            hora_inicio_base = ultimo_evento.hora_exibicao
            hora_inicio_dt = datetime.combine(datetime.today(), hora_inicio_base)
            # Adicionar incremento entre CPFs
            hora_inicio_dt += timedelta(seconds=incremento)
        else:
            # Primeiro evento do sistema
            hora_inicio_dt = datetime.combine(datetime.today(), hora_atual)
            hora_inicio_dt += timedelta(seconds=tempo_inicial)
        
        # Calcular horários para cada visualização
        eventos_criados = 0
        visualizations = [
            "visualization1", "visualization2", "visualization3",
            "visualization4", "visualization5", "visualization6"
        ]
        
        for i, visualization in enumerate(visualizations):
            # Calcular delay para esta visualização
            if i == 0:
                delay_segundos = 0  # Primeira visualização começa imediatamente
            else:
                delay_segundos = i * incremento  # Incremento entre visualizações
            
            # Calcular horários
            delay_timedelta = timedelta(seconds=delay_segundos)
            hora_exibicao_dt = hora_inicio_dt + delay_timedelta
            hora_fim_dt = hora_exibicao_dt + timedelta(seconds=duracao_exibicao)
            
            # Converter de volta para time
            hora_exibicao = hora_exibicao_dt.time()
            hora_fim = hora_fim_dt.time()
            
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