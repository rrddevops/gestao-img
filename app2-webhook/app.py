from flask import Flask, request, jsonify, render_template
import requests
import os
import asyncio
import aiohttp
from datetime import datetime

app = Flask(__name__)

# Configuração dos servidores de visualização
VISUALIZATION_SERVERS = [
    {
        "name": "Servidor 1",
        "url": "http://visualization1:5003",
        "external_port": "8083",
        "delay": 0
    },
    {
        "name": "Servidor 2",
        "url": "http://visualization2:5003",
        "external_port": "8084",
        "delay": 10
    },
    {
        "name": "Servidor 3",
        "url": "http://visualization3:5003",
        "external_port": "8085",
        "delay": 20
    },
    {
        "name": "Servidor 4",
        "url": "http://visualization4:5003",
        "external_port": "8086",
        "delay": 30
    },
    {
        "name": "Servidor 5",
        "url": "http://visualization5:5003",
        "external_port": "8087",
        "delay": 40
    },
    {
        "name": "Servidor 6",
        "url": "http://visualization6:5003",
        "external_port": "8088",
        "delay": 50
    }
]

def get_external_url(internal_url, external_port):
    """Converte URL interno para URL externo"""
    return f"http://localhost:{external_port}"

@app.route('/')
def index():
    # Converter URLs internos para URLs externos para o frontend
    servers_config = []
    for server in VISUALIZATION_SERVERS:
        external_url = get_external_url(server['url'], server['external_port'])
        servers_config.append({
            'name': server['name'],
            'url': external_url,
            'delay': server['delay']
        })
    return render_template('config.html', servers=servers_config)

async def notify_server_schedule(session, server, cpf, entry_time, wait_time):
    """Notifica servidor usando novo sistema de agendamento"""
    try:
        async with session.post(
            f"{server['url']}/schedule",
            json={
                'cpf': cpf,
                'entry_time': entry_time,
                'wait_time': wait_time
            }
        ) as response:
            return await response.json()
    except Exception as e:
        print(f"Error notifying server {server['name']}: {str(e)}")
        return {'error': str(e)}

async def notify_server_legacy(session, server, cpf):
    """Notifica servidor usando sistema legado (para compatibilidade)"""
    try:
        async with session.post(
            f"{server['url']}/display",
            json={
                'cpf': cpf,
                'display_time': server['delay'] * 1000  # Converte para milissegundos
            }
        ) as response:
            return await response.json()
    except Exception as e:
        print(f"Error notifying server {server['name']}: {str(e)}")
        return {'error': str(e)}

async def notify_all_servers_schedule(cpf, entry_time, wait_time):
    """Notifica todos os servidores usando novo sistema de agendamento"""
    async with aiohttp.ClientSession() as session:
        tasks = [
            notify_server_schedule(session, server, cpf, entry_time, wait_time)
            for server in VISUALIZATION_SERVERS
        ]
        return await asyncio.gather(*tasks)

async def notify_all_servers_legacy(cpf):
    """Notifica todos os servidores usando sistema legado"""
    async with aiohttp.ClientSession() as session:
        tasks = [
            notify_server_legacy(session, server, cpf)
            for server in VISUALIZATION_SERVERS
        ]
        return await asyncio.gather(*tasks)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    cpf = data.get('cpf')
    
    if not cpf:
        return jsonify({'error': 'CPF não fornecido'}), 400

    # Criar um loop de eventos para chamadas assíncronas
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Notificar todos os servidores de forma assíncrona (sistema legado)
        results = loop.run_until_complete(notify_all_servers_legacy(cpf))
        
        # Preparar URLs de visualização
        view_urls = []
        for i, server in enumerate(VISUALIZATION_SERVERS):
            external_url = get_external_url(server['url'], server['external_port'])
            view_urls.append({
                'server': server['name'],
                'delay': server['delay'],
                'url': f"{external_url}/view/",
                'status': 'success' if 'error' not in results[i] else 'error',
                'error': results[i].get('error') if 'error' in results[i] else None
            })
        
        return jsonify({
            'message': 'Notificações enviadas',
            'view_urls': view_urls
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao processar webhook: {str(e)}'}), 500
        
    finally:
        loop.close()

@app.route('/schedule', methods=['POST'])
def schedule_webhook():
    """Nova rota para agendamento - recebe apenas CPF e gerencia data/hora automaticamente"""
    data = request.json
    cpf = data.get('cpf')
    
    if not cpf:
        return jsonify({'error': 'CPF é obrigatório'}), 400
    
    # Gerencia automaticamente a data/hora
    now = datetime.now()
    entry_time = now.strftime('%H:%M:%S')  # Horário atual do servidor
    wait_time = "00:00:10"  # 10 segundos de espera padrão
    
    print(f"Agendando CPF {cpf} para exibição às {entry_time} + {wait_time}")

    # Criar um loop de eventos para chamadas assíncronas
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Notificar todos os servidores usando novo sistema de agendamento
        results = loop.run_until_complete(notify_all_servers_schedule(cpf, entry_time, wait_time))
        
        # Preparar URLs de visualização
        view_urls = []
        for i, server in enumerate(VISUALIZATION_SERVERS):
            external_url = get_external_url(server['url'], server['external_port'])
            view_urls.append({
                'server': server['name'],
                'delay': server['delay'],
                'url': f"{external_url}/view/",
                'status': 'success' if 'error' not in results[i] else 'error',
                'error': results[i].get('error') if 'error' in results[i] else None
            })
        
        return jsonify({
            'message': 'Agendamento realizado com sucesso',
            'cpf': cpf,
            'entry_time': entry_time,
            'wait_time': wait_time,
            'view_urls': view_urls
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao processar agendamento: {str(e)}'}), 500
        
    finally:
        loop.close()

@app.route('/schedule-status')
def schedule_status():
    """Retorna status dos agendamentos de todos os servidores"""
    try:
        # Pega status do primeiro servidor (todos devem ter o mesmo status)
        response = requests.get(f"{VISUALIZATION_SERVERS[0]['url']}/schedule-status", timeout=5)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Erro ao obter status dos agendamentos'}), 500
    except Exception as e:
        return jsonify({'error': f'Erro ao conectar com servidor: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002) 