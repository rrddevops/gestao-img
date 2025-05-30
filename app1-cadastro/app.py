from flask import Flask, request, jsonify, render_template, send_file
from sqlalchemy import create_engine, Column, String, LargeBinary, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
import io

app = Flask(__name__)

# Configure SQLite database
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

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/list')
def list_cpfs():
    session = Session()
    try:
        images = session.query(Image).order_by(Image.created_at.desc()).all()
        return render_template('list.html', cpfs=images)
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

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Nenhuma imagem enviada'}), 400
    
    image = request.files['image']
    cpf = request.form.get('cpf')
    
    if not cpf:
        return jsonify({'error': 'CPF não fornecido'}), 400
    
    if image.filename == '':
        return jsonify({'error': 'Nenhuma imagem selecionada'}), 400
    
    # Validar CPF (11 dígitos)
    if not cpf.isdigit() or len(cpf) != 11:
        return jsonify({'error': 'CPF inválido. Digite exatamente 11 números'}), 400
    
    session = Session()
    
    try:
        image_data = image.read()
        content_type = image.content_type
        
        db_image = Image(
            cpf=cpf,
            image_data=image_data,
            content_type=content_type,
            created_at=datetime.utcnow()
        )
        
        session.merge(db_image)
        session.commit()
        return jsonify({'message': 'Imagem cadastrada com sucesso'}), 200
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 