from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from sqlalchemy import create_engine, Column, String, LargeBinary, DateTime, Time, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import io
from datetime import datetime, timedelta, time
import os
from queue import PriorityQueue
import threading
import time as time_module
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import pytz
import asyncio
from websocket_client import start_websocket_client, get_websocket_client

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Configuração de timezone para Brasília
TIMEZONE = pytz.timezone('America/Sao_Paulo')

# PostgreSQL database configuration
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASS = os.getenv('POSTGRES_PASSWORD', 'postgres')
DB_HOST = os.getenv('POSTGRES_HOST', 'postgres')
DB_NAME = os.getenv('POSTGRES_DB', 'gestao_img')

# Configure PostgreSQL database
DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
engine = create_engine(DATABASE_URL, 
                      pool_size=10, 
                      max_overflow=20, 
                      pool_pre_ping=True,
                      pool_recycle=300)
Base = declarative_base()

class Image(Base):
    __tablename__ = 'images'
    cpf = Column(String, primary_key=True)
    image_data = Column(LargeBinary, nullable=False)
    content_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(TIMEZONE))

class ScheduleEntry(Base):
    __tablename__ = 'schedule_entries'
    sequence_id = Column(Integer, primary_key=True, autoincrement=True)  # Campo autonumero sequencial
    id = Column(String, nullable=False)  # CPF + visualization + timestamp
    cpf = Column(String, nullable=False)
    visualization_name = Column(String, nullable=False)  # Nome da visualização (ex: visualization1)
    entry_time = Column(Time, nullable=False)  # Horário de entrada (HH:MM:SS)
    wait_time = Column(Time, nullable=False)   # Tempo de espera (HH:MM:SS)
    display_time = Column(Time, nullable=False)  # Horário que será exibido (HH:MM:SS)
    display_datetime = Column(DateTime(timezone=True), nullable=False)  # Data e hora completa da exibição
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(TIMEZONE))

class VisualizationConfig(Base):
    __tablename__ = 'visualization_config'
    id = Column(Integer, primary_key=True, autoincrement=True)
    visualization_name = Column(String, nullable=False, unique=True)  # visualization1, visualization2, etc.
    port = Column(Integer, nullable=False)  # Porta externa (8083, 8084, etc.)
    delay_seconds = Column(Integer, nullable=False)  # Delay em segundos
    display_seconds = Column(Integer, nullable=False)  # Tempo de exibição em segundos
    is_active = Column(Boolean, default=True)  # Se a visualização está ativa
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(TIMEZONE))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(TIMEZONE), onupdate=lambda: datetime.now(TIMEZONE))

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def initialize_visualization_config():
    """Inicializa a configuração das visualizações no banco de dados se não existir nenhuma"""
    session = Session()
    try:
        # Só inicializa se não houver nenhuma configuração
        existing_config = session.query(VisualizationConfig).first()
        if existing_config:
            print("Configuração das visualizações já existe no banco de dados")
            return
        # Inicializa com padrão apenas se o banco estiver vazio
        print("Inicializando configurações padrão das visualizações no banco de dados...")
        default_config = [
            {"name": "visualization1", "port": 8083, "delay_seconds": 30, "display_seconds": 10},
            {"name": "visualization2", "port": 8084, "delay_seconds": 40, "display_seconds": 10},
            {"name": "visualization3", "port": 8085, "delay_seconds": 50, "display_seconds": 10},
            {"name": "visualization4", "port": 8086, "delay_seconds": 60, "display_seconds": 10},
            {"name": "visualization5", "port": 8087, "delay_seconds": 70, "display_seconds": 10},
            {"name": "visualization6", "port": 8088, "delay_seconds": 80, "display_seconds": 10}
        ]
        for config in default_config:
            viz_config = VisualizationConfig(
                visualization_name=config["name"],
                port=config["port"],
                delay_seconds=config["delay_seconds"],
                display_seconds=config["display_seconds"]
            )
            session.add(viz_config)
        session.commit()
        print("Configuração das visualizações inicializada no banco de dados")
    except Exception as e:
        print(f"Erro ao inicializar configuração: {e}")
        session.rollback()
    finally:
        session.close()

def get_visualization_config():
    """Carrega configuração das visualizações do banco de dados"""
    session = Session()
    try:
        configs = session.query(VisualizationConfig).filter_by(is_active=True).all()
        config_dict = {}
        for config in configs:
            config_dict[config.visualization_name] = {
                'port': config.port,
                'delay_seconds': config.delay_seconds,
                'display_seconds': config.display_seconds
            }
        return config_dict
    except Exception as e:
        print(f"Erro ao carregar configuração: {e}")
        return {}
    finally:
        session.close()

# Inicializa configuração no banco
initialize_visualization_config()

def sync_visualization_configs():
    """Sincroniza as configurações de todas as visualizações no banco de dados"""
    session = Session()
    try:
        # Mapeia todas as visualizações possíveis
        all_visualizations = {
            '30': {'name': 'visualization1', 'port': 8083},
            '40': {'name': 'visualization2', 'port': 8084},
            '50': {'name': 'visualization3', 'port': 8085},
            '60': {'name': 'visualization4', 'port': 8086},
            '70': {'name': 'visualization5', 'port': 8087},
            '80': {'name': 'visualization6', 'port': 8088}
        }
        
        # Verifica e cria configurações faltantes
        for delay, config in all_visualizations.items():
            existing = session.query(VisualizationConfig).filter_by(
                visualization_name=config['name']
            ).first()
            
            if not existing:
                viz_config = VisualizationConfig(
                    visualization_name=config['name'],
                    port=config['port'],
                    delay_seconds=int(delay),
                    display_seconds=10
                )
                session.add(viz_config)
                print(f"Configuração criada para {config['name']} (DELAY={delay})")
        
        session.commit()
        print("Sincronização de configurações concluída")
        
    except Exception as e:
        print(f"Erro ao sincronizar configurações: {e}")
        session.rollback()
    finally:
        session.close()

# Sincroniza configurações (garante que todas as visualizações existam no banco)
sync_visualization_configs()

# Estado global
current_images = {}
image_display_timers = {}  # Para controlar tempo de exibição
scheduler = BackgroundScheduler(timezone=str(TIMEZONE))
scheduler.start()

# Função callback para WebSocket
async def websocket_image_display_callback(cpf: str, display_time_str: str = None):
    """Callback chamado quando recebe comando via WebSocket para exibir imagem"""
    try:
        # Identifica a visualização atual
        visualization_name = get_current_visualization_name()
        
        # Exibe a imagem imediatamente
        display_image(cpf, visualization_name)
        
        # Envia confirmação
        client = get_websocket_client()
        if client:
            await client.send_image_displayed(cpf)
            
        print(f"Imagem do CPF {cpf} exibida via WebSocket em {visualization_name}")
        
    except Exception as e:
        print(f"Erro exibindo imagem via WebSocket: {e}")
        client = get_websocket_client()
        if client:
            await client.send_error(f"Erro exibindo imagem: {e}")

def get_current_visualization_name():
    """Identifica o nome da visualização atual baseado na porta externa"""
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
    return port_to_name.get(external_port, 'visualization1')

def get_brasilia_now():
    """Retorna o horário atual de Brasília"""
    return datetime.now(TIMEZONE)

def time_to_seconds(time_obj):
    """Converte objeto time para segundos desde meia-noite"""
    return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second

def seconds_to_time(seconds):
    """Converte segundos desde meia-noite para objeto time"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return time(hours, minutes, secs)

def calculate_display_time(entry_time_str, wait_time_str):
    """Calcula o horário de exibição baseado no horário de entrada e tempo de espera"""
    try:
        # Converte strings para objetos time
        entry_time = datetime.strptime(entry_time_str, '%H:%M:%S').time()
        wait_time = datetime.strptime(wait_time_str, '%H:%M:%S').time()
        
        # Converte para segundos
        entry_seconds = time_to_seconds(entry_time)
        wait_seconds = time_to_seconds(wait_time)
        
        # Calcula horário de exibição
        display_seconds = entry_seconds + wait_seconds
        
        # Se passar de 24h, ajusta para o dia seguinte
        if display_seconds >= 86400:
            display_seconds -= 86400
        
        return seconds_to_time(display_seconds)
    except ValueError as e:
        raise ValueError(f"Formato de tempo inválido: {e}")

def check_schedule_conflicts(display_datetime, visualization_name):
    """Verifica se existe conflito de horário para uma visualização"""
    session = Session()
    try:
        # Busca agendamentos existentes para esta visualização
        existing_entries = session.query(ScheduleEntry).filter_by(
            visualization_name=visualization_name
        ).all()
        
        for entry in existing_entries:
            # Se há sobreposição de horários (considerando 10 segundos de exibição)
            if abs((entry.display_datetime - display_datetime).total_seconds()) < 10:
                return True, entry.display_datetime
        
        return False, None
    finally:
        session.close()

def adjust_display_datetime(display_datetime, visualization_name):
    """Ajusta o horário de exibição para evitar conflitos"""
    original_datetime = display_datetime
    attempts = 0
    max_attempts = 10  # Máximo de tentativas para evitar loop infinito
    
    while attempts < max_attempts:
        has_conflict, conflicting_time = check_schedule_conflicts(display_datetime, visualization_name)
        
        if not has_conflict:
            return display_datetime
        
        # Se há conflito, adiciona 10 segundos (tempo de exibição)
        display_datetime += timedelta(seconds=10)
        attempts += 1
        print(f"Ajustando horário para {visualization_name}: {original_datetime} -> {display_datetime} (tentativa {attempts})")
    
    # Se não conseguiu resolver, retorna o horário original
    print(f"AVISO: Não foi possível resolver conflito para {visualization_name}, usando horário original")
    return original_datetime

def schedule_image_display(cpf, entry_time_str, wait_time_str):
    """Agenda a exibição de uma imagem para todas as visualizações em sequência"""
    try:
        print(f"DEBUG: Iniciando agendamento para CPF {cpf}")
        
        # Carrega configuração atual do banco
        viz_config = get_visualization_config()
        print(f"DEBUG: Configuração carregada: {viz_config}")
        
        # Calcula horário da primeira exibição
        first_display_time = calculate_display_time(entry_time_str, wait_time_str)
        
        # Converte para datetime (assumindo hoje em Brasília)
        today = get_brasilia_now().date()
        first_display_datetime = datetime.combine(today, first_display_time)
        first_display_datetime = TIMEZONE.localize(first_display_datetime)
        
        # Se o horário já passou hoje, agenda para amanhã
        if first_display_datetime <= get_brasilia_now():
            first_display_datetime += timedelta(days=1)
        
        # Converte entry_time_str para time em Brasília
        entry_time_brasilia = datetime.strptime(entry_time_str, '%H:%M:%S').time()
        wait_time_brasilia = datetime.strptime(wait_time_str, '%H:%M:%S').time()
        
        print(f"DEBUG: Primeira exibição calculada para {first_display_datetime}")
        
        # Agenda para todas as visualizações em sequência
        session = Session()
        try:
            # Ordena as visualizações pelo número para garantir sequência correta
            sorted_visualizations = sorted(viz_config.items(), 
                                         key=lambda x: int(x[0].replace('visualization', '')))
            
            print(f"DEBUG: Visualizações ordenadas: {[viz[0] for viz in sorted_visualizations]}")
            
            for viz_name, config in sorted_visualizations:
                print(f"DEBUG: Agendando para {viz_name}")
                # Calcula horário de exibição para esta visualização
                # O first_display_datetime já inclui o wait_time, então só adiciona o delta
                first_delay = sorted_visualizations[0][1]['delay_seconds']  # Delay da primeira visualização
                delta_seconds = config['delay_seconds'] - first_delay
                display_datetime = first_display_datetime + timedelta(seconds=delta_seconds)
                display_time = display_datetime.time()
                
                # Calcula o wait_time específico para esta visualização
                wait_time_seconds = config['delay_seconds']
                wait_time_brasilia = seconds_to_time(wait_time_seconds)
                
                # Cria job único para esta exibição com ID baseado na ordem de visualização
                viz_number = viz_name.replace('visualization', '')
                job_id = f"{cpf}_{viz_number}_{display_datetime.strftime('%Y%m%d_%H%M%S')}"
                print(f"DEBUG: Job ID criado: {job_id}")
                
                # Verifica se já existe um registro com este ID
                existing_entry = session.query(ScheduleEntry).filter_by(id=job_id).first()
                if existing_entry:
                    print(f"WARNING: Registro já existe para {job_id}, pulando...")
                    continue
                
                # Salva no banco de dados
                schedule_entry = ScheduleEntry(
                    id=job_id,
                    cpf=cpf,
                    visualization_name=viz_name,
                    entry_time=entry_time_brasilia,
                    wait_time=wait_time_brasilia,  # Usa o wait_time específico desta visualização
                    display_time=display_time,
                    display_datetime=display_datetime,
                    created_at=get_brasilia_now()
                )
                session.add(schedule_entry)
                print(f"DEBUG: Registro adicionado ao session para {viz_name}")
                
                # Agenda a exibição
                scheduler.add_job(
                    func=display_image,
                    trigger='date',
                    run_date=display_datetime,
                    args=[cpf, viz_name],
                    id=job_id,
                    replace_existing=True
                )
                print(f"DEBUG: Agendado {cpf} para {viz_name} em {display_datetime}")
            
            # Commit de todas as entradas de uma vez
            print(f"DEBUG: Fazendo commit de {len(sorted_visualizations)} registros...")
            session.commit()
            print(f"SUCCESS: Agendamento concluído para CPF {cpf} em todas as visualizações")
            
        except Exception as e:
            print(f"ERROR: Erro ao agendar {cpf}: {str(e)}")
            import traceback
            traceback.print_exc()
            session.rollback()
            raise
        finally:
            session.close()
        
        return True
        
    except Exception as e:
        print(f"ERROR: Erro ao agendar exibição para CPF {cpf}: {e}")
        import traceback
        traceback.print_exc()
        return False

def display_image(cpf, visualization_name):
    """Função chamada pelo scheduler para exibir uma imagem"""
    try:
        print(f"DEBUG: Tentando exibir {cpf} em {visualization_name}")
        
        # Verifica se a imagem existe
        session = Session()
        image = session.query(Image).filter_by(cpf=cpf).first()
        session.close()
        
        if image:
            current_images[visualization_name] = cpf
            print(f"SUCCESS: Exibindo {cpf} em {visualization_name}")
            print(f"DEBUG: current_images[{visualization_name}] = {current_images[visualization_name]}")
            
            # Carrega configuração para obter display_seconds
            viz_config = get_visualization_config()
            display_seconds = viz_config.get(visualization_name, {}).get('display_seconds', 10)
            
            # Agenda remoção da imagem após o tempo de exibição configurado
            if display_seconds > 0:
                # Cancela timer anterior se existir
                timer_key = f"{visualization_name}_{cpf}"
                if timer_key in image_display_timers:
                    image_display_timers[timer_key].cancel()
                
                # Cria novo timer para remover a imagem
                timer = threading.Timer(display_seconds, remove_image, args=[visualization_name, cpf])
                timer.start()
                image_display_timers[timer_key] = timer
                print(f"Timer criado: {cpf} será removido de {visualization_name} em {display_seconds} segundos")
        else:
            print(f"ERROR: Imagem não encontrada para CPF: {cpf}")
            
    except Exception as e:
        print(f"ERROR: Erro ao exibir imagem: {e}")
        import traceback
        traceback.print_exc()

def remove_image(visualization_name, cpf):
    """Remove uma imagem de uma visualização após o tempo de exibição"""
    try:
        # Só remove se a imagem atual ainda for a mesma
        if current_images.get(visualization_name) == cpf:
            current_images[visualization_name] = None
            print(f"Imagem {cpf} removida de {visualization_name} após tempo de exibição")
        
        # Remove o timer da lista
        timer_key = f"{visualization_name}_{cpf}"
        if timer_key in image_display_timers:
            del image_display_timers[timer_key]
            
    except Exception as e:
        print(f"Erro ao remover imagem: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view/')
def view():
    return render_template('view.html')

@app.route('/current-image')
def get_current_image():
    # Identifica qual visualização está sendo acessada baseado na porta externa
    # Usa a porta externa que está sendo acessada
    request_port = request.environ.get('HTTP_HOST', '').split(':')[-1] if ':' in request.environ.get('HTTP_HOST', '') else '8083'
    
    # Mapeia porta para nome da visualização
    viz_name = None
    viz_config = get_visualization_config()
    
    print(f"DEBUG: HTTP_HOST={request.environ.get('HTTP_HOST', 'N/A')}")
    print(f"DEBUG: request_port extraído={request_port}")
    print(f"DEBUG: viz_config={viz_config}")
    
    for name, config in viz_config.items():
        if str(config['port']) == request_port:
            viz_name = name
            break
    
    print(f"DEBUG: /current-image chamado - porta={request_port}, viz_name={viz_name}")
    print(f"DEBUG: current_images = {current_images}")
    
    if viz_name and current_images.get(viz_name):
        image_url = f'/image/{current_images[viz_name]}'
        print(f"DEBUG: Retornando imagem: {image_url}")
        return jsonify({'image_url': image_url})
    else:
        print(f"DEBUG: Nenhuma imagem para exibir - viz_name={viz_name}, current_image={current_images.get(viz_name) if viz_name else 'None'}")
        return jsonify({'image_url': None})

@app.route('/schedule', methods=['POST'])
def schedule_display():
    """Nova rota para agendar exibição baseada em horário"""
    print("=" * 50)
    print("DEBUG: FUNÇÃO SCHEDULE_DISPLAY CHAMADA!")
    print(f"DEBUG: Recebido POST /schedule com dados: {request.json}")
    print("=" * 50)
    
    data = request.json
    cpf = data.get('cpf')
    entry_time = data.get('entry_time')  # formato HH:MM:SS
    wait_time = data.get('wait_time')    # formato HH:MM:SS
    
    print(f"DEBUG: CPF={cpf}, entry_time={entry_time}, wait_time={wait_time}")
    
    if not all([cpf, entry_time, wait_time]):
        print(f"DEBUG: Dados obrigatórios não fornecidos")
        return jsonify({'error': 'CPF, entry_time e wait_time são obrigatórios'}), 400
    
    # Valida formato dos tempos
    try:
        datetime.strptime(entry_time, '%H:%M:%S')
        datetime.strptime(wait_time, '%H:%M:%S')
    except ValueError:
        print(f"DEBUG: Formato de tempo inválido")
        return jsonify({'error': 'Formato de tempo inválido. Use HH:MM:SS'}), 400
    
    # Verifica se a imagem existe
    session = Session()
    try:
        image = session.query(Image).filter_by(cpf=cpf).first()
        if not image:
            print(f"DEBUG: Imagem não encontrada para CPF {cpf}")
            return jsonify({'error': 'Imagem não encontrada'}), 404
        
        print(f"DEBUG: Imagem encontrada, chamando schedule_image_display")
        
        # Agenda a exibição
        if schedule_image_display(cpf, entry_time, wait_time):
            print(f"DEBUG: Agendamento bem-sucedido")
            
            # Recarrega os agendamentos do banco para este container
            print(f"DEBUG: Recarregando agendamentos após novo agendamento")
            reload_schedules_from_database()
            
            return jsonify({
                'message': 'Exibição agendada com sucesso',
                'cpf': cpf,
                'entry_time': entry_time,
                'wait_time': wait_time
            }), 200
        else:
            print(f"DEBUG: Erro no agendamento")
            return jsonify({'error': 'Erro ao agendar exibição'}), 500
                
    except Exception as e:
        print(f"DEBUG: Exceção capturada: {str(e)}")
        import traceback
        traceback.print_exc()
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/display', methods=['POST'])
def schedule_display_legacy():
    """Rota legada para compatibilidade - converte milissegundos para datetime"""
    data = request.json
    cpf = data.get('cpf')
    display_time_ms = data.get('display_time', 30000)  # tempo em milissegundos
    
    if not cpf:
        return jsonify({'error': 'CPF não fornecido'}), 400
    
    # Converte milissegundos para formato HH:MM:SS
    seconds = display_time_ms // 1000
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    wait_time = f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    # Usa horário atual como horário de entrada
    now = datetime.now()
    entry_time = now.strftime('%H:%M:%S')
    
    # Chama a nova função de agendamento
    return schedule_display_legacy_internal(cpf, entry_time, wait_time)

def schedule_display_legacy_internal(cpf, entry_time, wait_time):
    """Função interna para processar agendamento legado"""
    # Verifica se a imagem existe
    session = Session()
    try:
        image = session.query(Image).filter_by(cpf=cpf).first()
        if not image:
            return jsonify({'error': 'Imagem não encontrada'}), 404
        
        # Agenda a exibição
        if schedule_image_display(cpf, entry_time, wait_time):
            return jsonify({
                'message': 'Exibição agendada',
                'cpf': cpf,
                'entry_time': entry_time,
                'wait_time': wait_time
            }), 200
        else:
            return jsonify({'error': 'Erro ao agendar exibição'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/image/<cpf>')
def get_image(cpf):
    session = Session()
    try:
        image = session.query(Image).filter_by(cpf=cpf).first()
        if not image:
            return 'Imagem não encontrada', 404
        
        return send_file(
            io.BytesIO(image.image_data),
            mimetype=image.content_type
        )
    
    finally:
        session.close()

@app.route('/schedule-status')
def schedule_status():
    """Retorna status dos agendamentos"""
    jobs = scheduler.get_jobs()
    
    # Agrupa jobs por CPF (mantém para compatibilidade)
    schedule_by_cpf = {}
    chronological_list = []
    for job in jobs:
        if len(job.args) >= 2:
            cpf = job.args[0]
            viz_name = job.args[1]
            scheduled_time = job.next_run_time.strftime('%H:%M:%S') if job.next_run_time else None
            job_id = job.id
            
            # Para lista cronológica
            if scheduled_time:
                chronological_list.append({
                    'cpf': cpf,
                    'visualization': viz_name,
                    'scheduled_time': scheduled_time,
                    'job_id': job_id
                })
            
            # Para agrupamento por CPF
            if cpf not in schedule_by_cpf:
                schedule_by_cpf[cpf] = {}
            schedule_by_cpf[cpf][viz_name] = {
                'scheduled_time': scheduled_time,
                'job_id': job_id
            }
    # Ordena a lista cronológica pelo horário
    chronological_list.sort(key=lambda x: x['scheduled_time'])
    
    return jsonify({
        'current_images': current_images,
        'scheduled_jobs': schedule_by_cpf,
        'scheduled_jobs_chronological': chronological_list,
        'total_jobs': len(jobs)
    })

@app.route('/reload-schedules', methods=['POST'])
def force_reload_schedules():
    """Força o recarregamento dos agendamentos do banco de dados"""
    try:
        print("DEBUG: Recarregamento forçado de agendamentos solicitado")
        reload_schedules_from_database()
        return jsonify({'message': 'Agendamentos recarregados com sucesso'}), 200
    except Exception as e:
        print(f"Erro ao recarregar agendamentos: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/queue-status')
def queue_status():
    """Mostra a fila real de agendamentos no banco para este visualizador"""
    # Identifica qual visualização este container representa baseado no nome do container
    container_name = os.getenv('HOSTNAME', '')
    
    viz_name = None
    viz_config = get_visualization_config()
    
    # Mapeia nome do container para visualização
    if 'visualization1' in container_name:
        viz_name = 'visualization1'
    elif 'visualization2' in container_name:
        viz_name = 'visualization2'
    elif 'visualization3' in container_name:
        viz_name = 'visualization3'
    elif 'visualization4' in container_name:
        viz_name = 'visualization4'
    elif 'visualization5' in container_name:
        viz_name = 'visualization5'
    elif 'visualization6' in container_name:
        viz_name = 'visualization6'

    current_cpf = current_images.get(viz_name) if viz_name else None

    # Conta apenas os jobs ativos do scheduler para esta visualização específica
    # que ainda não foram executados
    active_jobs = scheduler.get_jobs()
    queue_count = 0
    
    print(f"DEBUG: Verificando jobs para {viz_name} (container={container_name})")
    print(f"DEBUG: Total de jobs ativos: {len(active_jobs)}")
    
    for job in active_jobs:
        if len(job.args) >= 2:
            job_cpf = job.args[0]
            job_viz_name = job.args[1]
            
            # Conta apenas jobs para esta visualização específica
            if job_viz_name == viz_name:
                queue_count += 1
                print(f"DEBUG: Job encontrado para {viz_name}: {job_cpf}")

    print(f"DEBUG: Queue count para {viz_name}: {queue_count}")

    return jsonify({
        'current_image': current_cpf,
        'remaining_time': None,  # Não aplicável no novo sistema
        'queue_size': queue_count
    })

@app.route('/schedule-details')
def schedule_details():
    """Retorna detalhes dos agendamentos do banco de dados"""
    session = Session()
    try:
        entries = session.query(ScheduleEntry).order_by(ScheduleEntry.sequence_id).all()
        
        schedule_details = []
        for entry in entries:
            # Garante que os campos DateTime sejam convertidos para Brasília
            display_datetime_brasilia = entry.display_datetime.astimezone(TIMEZONE)
            created_at_brasilia = entry.created_at.astimezone(TIMEZONE)
            
            schedule_details.append({
                'sequence_id': entry.sequence_id,
                'id': entry.id,
                'cpf': entry.cpf,
                'visualization_name': entry.visualization_name,
                'entry_time': entry.entry_time.strftime('%H:%M:%S'),
                'wait_time': entry.wait_time.strftime('%H:%M:%S'),
                'display_time': entry.display_time.strftime('%H:%M:%S'),
                'display_datetime': display_datetime_brasilia.strftime('%Y-%m-%d %H:%M:%S'),
                'created_at': created_at_brasilia.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'schedule_entries': schedule_details,
            'total_entries': len(schedule_details)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/config')
def get_config():
    """Retorna a configuração atual das visualizações"""
    try:
        config = get_visualization_config()
        return jsonify({
            'visualization_config': config,
            'total_visualizations': len(config)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/config', methods=['POST'])
def update_config():
    """Atualiza a configuração das visualizações"""
    try:
        data = request.json
        session = Session()
        
        for viz_name, config in data.items():
            viz_config = session.query(VisualizationConfig).filter_by(visualization_name=viz_name).first()
            if viz_config:
                viz_config.delay_seconds = config.get('delay_seconds', viz_config.delay_seconds)
                viz_config.display_seconds = config.get('display_seconds', viz_config.display_seconds)
                viz_config.port = config.get('port', viz_config.port)
                viz_config.is_active = config.get('is_active', viz_config.is_active)
                viz_config.updated_at = datetime.now(TIMEZONE)
        
        session.commit()
        return jsonify({'message': 'Configuração atualizada com sucesso'}), 200
        
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/config/all', methods=['GET'])
def get_all_configs():
    """Retorna todas as configurações detalhadas do banco de dados"""
    session = Session()
    try:
        configs = session.query(VisualizationConfig).all()
        result = []
        for config in configs:
            result.append({
                'id': config.id,
                'visualization_name': config.visualization_name,
                'port': config.port,
                'delay_seconds': config.delay_seconds,
                'display_seconds': config.display_seconds,
                'is_active': config.is_active,
                'created_at': config.created_at.isoformat() if config.created_at else None,
                'updated_at': config.updated_at.isoformat() if config.updated_at else None
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/config/reset', methods=['POST'])
def reset_configs():
    """Reseta todas as configurações para os valores padrão"""
    try:
        session = Session()
        try:
            # Remove todas as configurações existentes
            session.query(VisualizationConfig).delete()
            
            # Recria com valores padrão
            all_visualizations = {
                '30': {'name': 'visualization1', 'port': 8083},
                '40': {'name': 'visualization2', 'port': 8084},
                '50': {'name': 'visualization3', 'port': 8085},
                '60': {'name': 'visualization4', 'port': 8086},
                '70': {'name': 'visualization5', 'port': 8087},
                '80': {'name': 'visualization6', 'port': 8088}
            }
            
            for delay, config in all_visualizations.items():
                viz_config = VisualizationConfig(
                    visualization_name=config['name'],
                    port=config['port'],
                    delay_seconds=int(delay),
                    display_seconds=10
                )
                session.add(viz_config)
            
            session.commit()
            
            # Recarrega agendamentos
            reload_schedules_from_database()
            
            return jsonify({"message": "Configurações resetadas com sucesso"})
            
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def reload_schedules_from_database():
    """Recarrega agendamentos do banco de dados para esta visualização"""
    try:
        print("DEBUG: Iniciando reload_schedules_from_database()")
        scheduler.remove_all_jobs()
        print("DEBUG: Jobs existentes removidos.")

        # Identifica a porta externa deste container
        import socket
        import requests
        import os

        # Tenta obter a porta externa a partir do mapeamento do host
        # Usa a variável HTTP_HOST se disponível (em request), senão tenta obter do ambiente
        port = None
        if 'HTTP_HOST' in os.environ:
            # Exemplo: 'localhost:8083'
            host = os.environ['HTTP_HOST']
            if ':' in host:
                port = int(host.split(':')[-1])
        else:
            # Tenta obter a porta do mapeamento do docker-compose
            # Busca a porta do arquivo de configuração do banco
            # Como fallback, tenta usar a porta padrão 8083
            port = int(os.getenv('PORT', '8083'))

        print(f"DEBUG: Porta identificada: {port}")

        # Busca o nome da visualização correspondente à porta no banco
        session = Session()
        viz_config = session.query(VisualizationConfig).filter_by(port=port).first()
        if not viz_config:
            print(f"ERRO: Não foi possível identificar a visualização para porta={port}")
            session.close()
            return
        viz_name = viz_config.visualization_name
        print(f"DEBUG: viz_name identificado: {viz_name}")

        # Filtra apenas os registros desta visualização específica
        entries = session.query(ScheduleEntry).filter_by(visualization_name=viz_name).all()
        session.close()

        print(f"DEBUG: Encontrados {len(entries)} agendamentos para {viz_name} no banco de dados...")

        for entry in entries:
            print(f"DEBUG: Processando entry: {entry.id} - {entry.cpf} - {entry.visualization_name} - {entry.display_datetime}")
            job_id = entry.id
            scheduler.add_job(
                func=display_image,
                trigger='date',
                run_date=entry.display_datetime,
                args=[entry.cpf, entry.visualization_name],
                id=job_id,
                replace_existing=True
            )
            print(f"DEBUG: Job adicionado ao scheduler: {job_id}")

        print(f"DEBUG: Recarregamento concluído para {viz_name}. Total de jobs: {len(scheduler.get_jobs())}")

    except Exception as e:
        print(f"ERROR: Erro ao recarregar agendamentos: {e}")
        import traceback
        traceback.print_exc()

def execute_pending_jobs():
    """Executa jobs que deveriam ter sido executados mas não foram"""
    try:
        session = Session()
        entries = session.query(ScheduleEntry).all()
        session.close()
        
        now = get_brasilia_now()
        today = now.date()
        
        for entry in entries:
            # Calcula quando a imagem deveria ter sido exibida
            entry_time = entry.entry_time
            wait_time = entry.wait_time
            
            # Converte para segundos
            entry_seconds = time_to_seconds(entry_time)
            wait_seconds = time_to_seconds(wait_time)
            display_seconds = entry_seconds + wait_seconds
            
            # Se passar de 24h, ajusta
            if display_seconds >= 86400:
                display_seconds -= 86400
            
            # Converte de volta para time
            display_time = seconds_to_time(display_seconds)
            
            # Cria datetime para hoje em Brasília
            display_datetime = datetime.combine(today, display_time)
            display_datetime = TIMEZONE.localize(display_datetime)
            
            # Se o horário já passou hoje, executa imediatamente
            if display_datetime <= now:
                print(f"Executando job pendente para CPF {entry.cpf}")
                display_image(entry.cpf, entry.visualization_name)  # Executa na visualização correta
                
    except Exception as e:
        print(f"Erro ao executar jobs pendentes: {e}")

# Recarrega agendamentos na inicialização
reload_schedules_from_database()
execute_pending_jobs()

if __name__ == '__main__':
    # Inicia o cliente WebSocket em uma thread separada
    def start_websocket():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_websocket_client(websocket_image_display_callback))
    
    websocket_thread = threading.Thread(target=start_websocket, daemon=True)
    websocket_thread.start()
    
    # Debug: Mostra configuração e rotas
    print("=" * 50)
    print("DEBUG: INICIALIZAÇÃO DO APP")
    print(f"DEBUG: Configuração carregada: {get_visualization_config()}")
    print(f"DEBUG: Rotas registradas:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5003) 