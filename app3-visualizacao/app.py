from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from sqlalchemy import create_engine, Column, String, LargeBinary, DateTime, Time
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

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# PostgreSQL database configuration
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASS = os.getenv('POSTGRES_PASSWORD', 'postgres')
DB_HOST = os.getenv('POSTGRES_HOST', 'postgres')
DB_NAME = os.getenv('POSTGRES_DB', 'gestao_img')

# Configure PostgreSQL database
DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Image(Base):
    __tablename__ = 'images'
    cpf = Column(String, primary_key=True)
    image_data = Column(LargeBinary, nullable=False)
    content_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ScheduleEntry(Base):
    __tablename__ = 'schedule_entries'
    id = Column(String, primary_key=True)  # CPF + timestamp
    cpf = Column(String, nullable=False)
    entry_time = Column(Time, nullable=False)  # Horário de entrada (HH:MM:SS)
    wait_time = Column(Time, nullable=False)   # Tempo de espera (HH:MM:SS)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Configuração das visualizações
VISUALIZATION_CONFIG = {
    'visualization1': {'port': 8083, 'delay_seconds': 0},      # Primeira exibição
    'visualization2': {'port': 8084, 'delay_seconds': 10},     # +10 segundos
    'visualization3': {'port': 8085, 'delay_seconds': 20},     # +20 segundos
    'visualization4': {'port': 8086, 'delay_seconds': 30},     # +30 segundos
    'visualization5': {'port': 8087, 'delay_seconds': 40},     # +40 segundos
    'visualization6': {'port': 8088, 'delay_seconds': 50},     # +50 segundos
}

# Estado global
current_images = {viz: None for viz in VISUALIZATION_CONFIG.keys()}
scheduler = BackgroundScheduler()
scheduler.start()

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

def schedule_image_display(cpf, entry_time_str, wait_time_str):
    """Agenda a exibição de uma imagem em todas as visualizações"""
    try:
        # Calcula horário da primeira exibição
        first_display_time = calculate_display_time(entry_time_str, wait_time_str)
        
        # Converte para datetime (assumindo hoje)
        today = datetime.now().date()
        first_display_datetime = datetime.combine(today, first_display_time)
        
        # Se o horário já passou hoje, agenda para amanhã
        if first_display_datetime <= datetime.now():
            first_display_datetime += timedelta(days=1)
        
        # Agenda para cada visualização
        for viz_name, config in VISUALIZATION_CONFIG.items():
            display_datetime = first_display_datetime + timedelta(seconds=config['delay_seconds'])
            
            # Cria job único para esta exibição
            job_id = f"{cpf}_{viz_name}_{display_datetime.strftime('%Y%m%d_%H%M%S')}"
            
            scheduler.add_job(
                func=display_image,
                trigger=DateTrigger(run_date=display_datetime),
                args=[cpf, viz_name],
                id=job_id,
                replace_existing=True
            )
            
            print(f"Agendado: {cpf} em {viz_name} às {display_datetime.strftime('%H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"Erro ao agendar exibição: {e}")
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
        else:
            print(f"ERROR: Imagem não encontrada para CPF: {cpf}")
            
    except Exception as e:
        print(f"ERROR: Erro ao exibir imagem: {e}")
        import traceback
        traceback.print_exc()

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
        
        # Descobre o delay deste visualizador
        delay = int(os.getenv('DELAY', 0))
        # Usa id determinístico
        entry_id = f"{cpf}_{entry_time}_{wait_time}_{delay}"
        # Verifica se já existe
        exists = session.query(ScheduleEntry).filter_by(id=entry_id).first()
        if not exists:
            schedule_entry = ScheduleEntry(
                id=entry_id,
                cpf=cpf,
                entry_time=datetime.strptime(entry_time, '%H:%M:%S').time(),
                wait_time=datetime.strptime(wait_time, '%H:%M:%S').time()
            )
            session.add(schedule_entry)
            session.commit()
        # Agenda a exibição
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
    
    # Agrupa jobs por CPF
    schedule_by_cpf = {}
    for job in jobs:
        if len(job.args) >= 2:
            cpf = job.args[0]
            viz_name = job.args[1]
            
            if cpf not in schedule_by_cpf:
                schedule_by_cpf[cpf] = {}
            
            schedule_by_cpf[cpf][viz_name] = {
                'scheduled_time': job.next_run_time.strftime('%H:%M:%S') if job.next_run_time else None,
                'job_id': job.id
            }
    
    return jsonify({
        'current_images': current_images,
        'scheduled_jobs': schedule_by_cpf,
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

    # Conta quantos agendamentos existem no banco para este delay
    session = Session()
    try:
        # O id do agendamento é determinístico: cpf_entrytime_waittime_delay
        # Então filtramos todos os schedule_entries cujo id termina com _{delay}
        delay_str = f"_{delay}"
        queue_count = session.query(ScheduleEntry).filter(ScheduleEntry.id.like(f"%{delay_str}")).count()
    finally:
        session.close()

    return jsonify({
        'current_image': current_cpf,
        'remaining_time': None,  # Não aplicável no novo sistema
        'queue_size': queue_count
    })

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
            # Converte para string no formato HH:MM:SS
            entry_time_str = entry.entry_time.strftime('%H:%M:%S')
            wait_time_str = entry.wait_time.strftime('%H:%M:%S')
            
            # Agenda a exibição
            schedule_image_display(entry.cpf, entry_time_str, wait_time_str)
            
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
        
        now = datetime.now()
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
            
            # Cria datetime para hoje
            display_datetime = datetime.combine(today, display_time)
            
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