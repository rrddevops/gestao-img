from flask import Flask, request, render_template, jsonify
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

app = Flask(__name__)

# Configure SQLite database
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

engine = create_engine('sqlite:///images.db')
Base = declarative_base()

class Image(Base):
    __tablename__ = 'images'
    cpf = Column(String, primary_key=True)
    image_path = Column(String, nullable=False)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@app.route('/')
def index():
    session = Session()
    images = session.query(Image).all()
    session.close()
    return render_template('index.html', images=images)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    cpf = data.get('cpf')
    
    if not cpf:
        return jsonify({'error': 'CPF não fornecido'}), 400
    
    image_path = os.path.join(UPLOAD_FOLDER, f'{cpf}.jpg')
    
    session = Session()
    image = Image(cpf=cpf, image_path=image_path)
    
    try:
        session.merge(image)
        session.commit()
        return jsonify({'message': 'Imagem registrada com sucesso', 'path': image_path}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 