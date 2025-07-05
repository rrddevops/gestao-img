from sqlalchemy import Column, Integer, String, Time, Interval, Text, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from app.database import Base

# Modelos SQLAlchemy
class Cadastro(Base):
    __tablename__ = "cadastro"
    
    cpf = Column(String, primary_key=True, index=True)
    caminho_imagem = Column(Text, nullable=False)

class Parametro(Base):
    __tablename__ = "parametros"
    
    nome = Column(String, primary_key=True, index=True)
    valor = Column(String, nullable=False)

class Evento(Base):
    __tablename__ = "eventos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cpf = Column(String, nullable=False)
    visualization = Column(String, nullable=False)
    hora_acesso = Column(Time, nullable=False)
    delay = Column(Interval, nullable=False)
    hora_exibicao = Column(Time, nullable=False)
    hora_fim = Column(Time, nullable=False)
