from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from sqlalchemy import create_engine, Column, String, LargeBinary, DateTime, Time, Integer
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

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def load_visualization_config():
    """Carrega configuração das visualizações do arquivo JSON"""
    config_file = 'visualization_config.json'
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        print(f"Configuração carregada de {config_file}")
        return config
    except FileNotFoundError:
        print(f"Arquivo {config_file} não encontrado. Usando configuração padrão.")
        # Configuração padrão (compatibilidade)
        return {
            "visualizations": [
                {"name": "visualization1", "port": 8083, "delay_seconds": 0, "display_seconds": 10},
                {"name": "visualization2", "port": 8084, "delay_seconds": 10, "display_seconds": 10},
                {"name": "visualization3", "port": 8085, "delay_seconds": 20, "display_seconds": 10},
                {"name": "visualization4", "port": 8086, "delay_seconds": 30, "display_seconds": 10},
                {"name": "visualization5", "port": 8087, "delay_seconds": 40, "display_seconds": 10},
                {"name": "visualization6", "port": 8088, "delay_seconds": 50, "display_seconds": 10}
            ]
        }

# Carrega configuração das visualizações
VISUALIZATION_CONFIG = {}
config_data = load_visualization_config()
for viz in config_data["visualizations"]:
    VISUALIZATION_CONFIG[viz["name"]] = {
        'port': viz["port"],
        'delay_seconds': viz["delay_seconds"],
        'display_seconds': viz["display_seconds"]
    }

# Estado global
current_images = {viz: None for viz in VISUALIZATION_CONFIG.keys()}
image_display_timers = {}  # Para controlar tempo de exibição
scheduler = BackgroundScheduler(timezone=str(TIMEZONE))
scheduler.start()

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
    """Agenda a exibição de uma imagem apenas para esta visualização específica"""
    try:
        print(f"DEBUG: Iniciando agendamento para CPF {cpf}")
        
        # Identifica qual visualização este container representa
        delay = int(os.getenv('DELAY', 0))
        viz_name = None
        for name, config in VISUALIZATION_CONFIG.items():
            if config['delay_seconds'] == delay:
                viz_name = name
                break
        
        if not viz_name:
            print(f"ERROR: Não foi possível identificar a visualização para delay {delay}")
            return False
        
        print(f"DEBUG: Este container representa a visualização: {viz_name}")
        
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
        
        # Agenda apenas para esta visualização específica
        config = VISUALIZATION_CONFIG[viz_name]
        display_datetime = first_display_datetime + timedelta(seconds=config['delay_seconds'])
        display_time = display_datetime.time()
        
        # Cria job único para esta exibição
        job_id = f"{cpf}_{viz_name}_{display_datetime.strftime('%Y%m%d_%H%M%S')}"
        
        # Verifica se já existe um registro com este ID
        session = Session()
        try:
            existing_entry = session.query(ScheduleEntry).filter_by(id=job_id).first()
            if existing_entry:
                print(f"WARNING: Registro já existe para {job_id}, pulando...")
                return True  # Retorna True pois o registro já existe
            
            # Salva no banco de dados
            schedule_entry = ScheduleEntry(
                id=job_id,
                cpf=cpf,
                visualization_name=viz_name,
                entry_time=entry_time_brasilia,
                wait_time=wait_time_brasilia,
                display_time=display_time,
                display_datetime=display_datetime,
                created_at=get_brasilia_now()
            )
            session.add(schedule_entry)
            session.commit()
            
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
            
        except Exception as e:
            print(f"ERROR: Erro ao agendar {cpf} para {viz_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            session.rollback()
            raise
        finally:
            session.close()
        
        print(f"SUCCESS: Agendamento concluído para CPF {cpf} na visualização {viz_name}")
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
            
            # Agenda remoção da imagem após o tempo de exibição configurado
            display_seconds = VISUALIZATION_CONFIG[visualization_name]['display_seconds']
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
    # Identifica qual visualização está sendo acessada
    # Por simplicidade, vamos usar o DELAY environment variable
    delay = int(os.getenv('DELAY', 0))
    
    # Mapeia delay para nome da visualização
    viz_name = None
    for name, config in VISUALIZATION_CONFIG.items():
        if config['delay_seconds'] == delay:
            viz_name = name
            break
    
    if viz_name and current_images[viz_name]:
        return jsonify({'image_url': f'/image/{current_images[viz_name]}'})
    else:
        return jsonify({'image_url': None})

@app.route('/schedule', methods=['POST'])
def schedule_display():
    """Nova rota para agendar exibição baseada em horário"""
    data = request.json
    cpf = data.get('cpf')
    entry_time = data.get('entry_time')  # formato HH:MM:SS
    wait_time = data.get('wait_time')    # formato HH:MM:SS
    
    if not all([cpf, entry_time, wait_time]):
        return jsonify({'error': 'CPF, entry_time e wait_time são obrigatórios'}), 400
    
    # Valida formato dos tempos
    try:
        datetime.strptime(entry_time, '%H:%M:%S')
        datetime.strptime(wait_time, '%H:%M:%S')
    except ValueError:
        return jsonify({'error': 'Formato de tempo inválido. Use HH:MM:SS'}), 400
    
    # Verifica se a imagem existe
    session = Session()
    try:
        image = session.query(Image).filter_by(cpf=cpf).first()
        if not image:
            return jsonify({'error': 'Imagem não encontrada'}), 404
        
        # Não cria mais registro aqui!
        # Apenas agenda a exibição para todas as visualizações
        if schedule_image_display(cpf, entry_time, wait_time):
            return jsonify({
                'message': 'Exibição agendada com sucesso',
                'cpf': cpf,
                'entry_time': entry_time,
                'wait_time': wait_time
            }), 200
        else:
            return jsonify({'error': 'Erro ao agendar exibição'}), 500
                
    except Exception as e:
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

@app.route('/queue-status')
def queue_status():
    """Mostra a fila real de agendamentos no banco para este visualizador"""
    delay = int(os.getenv('DELAY', 0))
    viz_name = None
    for name, config in VISUALIZATION_CONFIG.items():
        if config['delay_seconds'] == delay:
            viz_name = name
            break

    current_cpf = current_images.get(viz_name) if viz_name else None

    # Conta apenas os jobs ativos do scheduler para esta visualização específica
    # que ainda não foram executados
    active_jobs = scheduler.get_jobs()
    queue_count = 0
    
    print(f"DEBUG: Verificando jobs para {viz_name} (delay={delay})")
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

def reload_schedules_from_database():
    """Recarrega todos os agendamentos do banco de dados"""
    try:
        # Limpa todos os jobs existentes antes de recarregar
        scheduler.remove_all_jobs()
        print("Jobs existentes removidos.")
        
        session = Session()
        entries = session.query(ScheduleEntry).all()
        session.close()
        
        print(f"Recarregando {len(entries)} agendamentos do banco de dados...")
        
        for entry in entries:
            # Cria job único para esta exibição baseado no registro existente
            job_id = entry.id
            
            # Agenda o job no scheduler (não cria novo registro no banco)
            scheduler.add_job(
                func=display_image,
                trigger=DateTrigger(run_date=entry.display_datetime),
                args=[entry.cpf, entry.visualization_name],
                id=job_id,
                replace_existing=True
            )
            
            print(f"Recarregado: {entry.cpf} em {entry.visualization_name} às {entry.display_datetime.strftime('%H:%M:%S')}")
            
        print(f"Recarregamento concluído. Total de jobs: {len(scheduler.get_jobs())}")
        
    except Exception as e:
        print(f"Erro ao recarregar agendamentos: {e}")
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
                display_image(entry.cpf, 'visualization1')  # Executa na primeira visualização
                
    except Exception as e:
        print(f"Erro ao executar jobs pendentes: {e}")

# Recarrega agendamentos na inicialização
reload_schedules_from_database()
execute_pending_jobs()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003) 