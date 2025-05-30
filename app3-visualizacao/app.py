from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from sqlalchemy import create_engine, Column, String, LargeBinary, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import io
from datetime import datetime, timedelta
import os
from queue import PriorityQueue
import threading
import time

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Configure SQLite database connection
DB_PATH = os.path.join('data', 'images.db')
os.makedirs('data', exist_ok=True)
engine = create_engine(f'sqlite:///{DB_PATH}')
Base = declarative_base()

class Image(Base):
    __tablename__ = 'images'
    cpf = Column(String, primary_key=True)
    image_data = Column(LargeBinary, nullable=False)
    content_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Session = sessionmaker(bind=engine)

# Fila de prioridade para as imagens
image_queue = PriorityQueue()
current_image = None
current_image_end_time = None
queue_lock = threading.Lock()

def process_queue():
    global current_image, current_image_end_time
    
    while True:
        with queue_lock:
            now = datetime.now()
            
            # Se não há imagem atual ou o tempo expirou
            if (current_image is None or 
                (current_image_end_time is not None and now >= current_image_end_time)):
                
                # Tenta pegar próxima imagem da fila
                if not image_queue.empty():
                    _, (cpf, display_time) = image_queue.get()
                    current_image = cpf
                    current_image_end_time = now + timedelta(milliseconds=display_time)
        
        time.sleep(1)  # Verifica a cada segundo

# Inicia o processamento da fila em uma thread separada
queue_thread = threading.Thread(target=process_queue, daemon=True)
queue_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view/')
def view():
    return render_template('view.html')

@app.route('/current-image')
def get_current_image():
    with queue_lock:
        if current_image is None:
            return jsonify({'image_url': None})
        return jsonify({'image_url': f'/image/{current_image}'})

@app.route('/display', methods=['POST'])
def schedule_display():
    data = request.json
    cpf = data.get('cpf')
    display_time = data.get('display_time', 30000)  # tempo em milissegundos
    
    if not cpf:
        return jsonify({'error': 'CPF não fornecido'}), 400
    
    # Verifica se a imagem existe no banco
    session = Session()
    try:
        image = session.query(Image).filter_by(cpf=cpf).first()
        if not image:
            return jsonify({'error': 'Imagem não encontrada'}), 404
        
        # Adiciona à fila com prioridade baseada no tempo atual
        priority = datetime.now().timestamp()
        image_queue.put((priority, (cpf, display_time)))
        
        return jsonify({
            'message': 'Exibição agendada',
            'cpf': cpf,
            'position': image_queue.qsize()
        }), 200
        
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

@app.route('/queue-status')
def queue_status():
    with queue_lock:
        return jsonify({
            'current_image': current_image,
            'remaining_time': int((current_image_end_time - datetime.now()).total_seconds() * 1000) if current_image_end_time else None,
            'queue_size': image_queue.qsize()
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003) 