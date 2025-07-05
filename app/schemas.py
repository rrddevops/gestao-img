from pydantic import BaseModel
from typing import Optional
from datetime import time, timedelta

# Schemas para Cadastro
class CadastroCreate(BaseModel):
    cpf: str
    imagem_base64: str

class CadastroResponse(BaseModel):
    cpf: str
    caminho_imagem: str
    
    class Config:
        from_attributes = True

# Schemas para Webhook
class WebhookRequest(BaseModel):
    cpf: str

class WebhookResponse(BaseModel):
    message: str
    cpf: str
    hora_acesso: time
    eventos_criados: int

# Schemas para Eventos
class EventoCreate(BaseModel):
    cpf: str
    visualization: str
    hora_acesso: time
    delay: timedelta
    hora_exibicao: time
    hora_fim: time

class EventoResponse(BaseModel):
    id: int
    cpf: str
    visualization: str
    hora_acesso: time
    delay: timedelta
    hora_exibicao: time
    hora_fim: time
    
    class Config:
        from_attributes = True

# Schemas para Parâmetros
class ParametroCreate(BaseModel):
    nome: str
    valor: str

class ParametroResponse(BaseModel):
    nome: str
    valor: str
    
    class Config:
        from_attributes = True

# Schema para WebSocket
class WebSocketMessage(BaseModel):
    cpf: str
    caminho_imagem: str
    visualization: str 