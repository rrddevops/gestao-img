from flask import Flask, request, jsonify, render_template
import requests
import os
import asyncio
import aiohttp
import websockets
import json
from datetime import datetime
import pytz

app = Flask(__name__)

# Configuração de timezone para Brasília
TIMEZONE = pytz.timezone('America/Sao_Paulo')

# Configuração do servidor WebSocket
WEBSOCKET_SERVER_URL = "ws://websocket-server:8765"

# Configuração dos servidores de visualização (para compatibilidade)
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

def get_brasilia_now():
    """Retorna o horário atual de Brasília"""
    return datetime.now(TIMEZONE)

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
        print(f"DEBUG: Notificando {server['name']} em {server['url']}/schedule")
        async with session.post(
            f"{server['url']}/schedule",
            json={
                'cpf': cpf,
                'entry_time': entry_time,
                'wait_time': wait_time
            }
        ) as response:
            result = await response.json()
            print(f"DEBUG: Resposta de {server['name']}: {result}")
            return result
    except Exception as e:
        print(f"ERROR: Erro notificando servidor {server['name']}: {str(e)}")
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
    """Notifica apenas o primeiro servidor para criar todos os agendamentos"""
    print(f"DEBUG: Iniciando notificação para CPF {cpf}")
    async with aiohttp.ClientSession() as session:
        # Notifica apenas o primeiro servidor (visualization1) que criará todos os agendamentos
        first_server = VISUALIZATION_SERVERS[0]
        print(f"DEBUG: Notificando apenas {first_server['name']} para criar todos os agendamentos")
        result = await notify_server_schedule(session, first_server, cpf, entry_time, wait_time)
        
        # Após criar os agendamentos, notifica todos os servidores para recarregar
        print(f"DEBUG: Notificando todos os servidores para recarregar agendamentos")
        reload_tasks = []
        for server in VISUALIZATION_SERVERS:
            try:
                async with session.post(f"{server['url']}/reload-schedules") as response:
                    reload_result = await response.json()
                    print(f"DEBUG: Recarregamento em {server['name']}: {reload_result}")
                    reload_tasks.append(reload_result)
            except Exception as e:
                print(f"ERROR: Erro ao recarregar {server['name']}: {str(e)}")
                reload_tasks.append({'error': str(e)})
        
        # Retorna o mesmo resultado para todos os servidores (para compatibilidade)
        results = [result] * len(VISUALIZATION_SERVERS)
        print(f"DEBUG: Resultados obtidos: {results}")
        return results

async def notify_all_servers_legacy(cpf):
    """Notifica todos os servidores usando sistema legado"""
    async with aiohttp.ClientSession() as session:
        tasks = [
            notify_server_legacy(session, server, cpf)
            for server in VISUALIZATION_SERVERS
        ]
        return await asyncio.gather(*tasks)

async def send_image_via_websocket(cpf: str):
    """Envia comando para exibir imagem via WebSocket"""
    try:
        print(f"Enviando comando via WebSocket para exibir CPF {cpf}")
        
        async with websockets.connect(WEBSOCKET_SERVER_URL) as websocket:
            message = {
                'type': 'display_image',
                'cpf': cpf,
                'timestamp': datetime.now(TIMEZONE).isoformat()
            }
            
            await websocket.send(json.dumps(message))
            print(f"Comando enviado via WebSocket para CPF {cpf}")
            
            # Aguarda confirmação (opcional)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"Resposta do WebSocket: {response}")
            except asyncio.TimeoutError:
                print("Timeout aguardando resposta do WebSocket")
            
            return {'success': True, 'message': 'Comando enviado via WebSocket'}
            
    except Exception as e:
        print(f"Erro enviando comando via WebSocket: {e}")
        return {'error': str(e)}

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    cpf = data.get('cpf')
    
    if not cpf:
        return jsonify({'error': 'CPF não fornecido'}), 400

    # Gerencia automaticamente a data/hora
    now = get_brasilia_now()
    entry_time = now.strftime('%H:%M:%S')  # Horário atual de Brasília
    
    # Obtém configuração das visualizações do banco de dados
    try:
        response = requests.get(f"{VISUALIZATION_SERVERS[0]['url']}/config", timeout=5)
        if response.status_code == 200:
            config_data = response.json()
            viz_config = config_data.get('visualization_config', {})
            
            # Encontra a primeira visualização (visualization1)
            first_viz_config = viz_config.get('visualization1')
            
            if first_viz_config:
                first_delay_seconds = first_viz_config.get('delay_seconds', 30)
                wait_time_seconds = first_delay_seconds
                wait_time = f"00:00:{wait_time_seconds:02d}"
                print(f"Agendando CPF {cpf} para exibição às {entry_time} + {wait_time} (primeira visualização em {first_delay_seconds}s)")
            else:
                # Fallback para configuração padrão
                wait_time = "00:00:30"
                print(f"Agendando CPF {cpf} para exibição às {entry_time} + {wait_time} (configuração padrão)")
        else:
            # Fallback para configuração padrão
            wait_time = "00:00:30"
            print(f"Agendando CPF {cpf} para exibição às {entry_time} + {wait_time} (erro ao obter configuração)")
    except Exception as e:
        # Fallback para configuração padrão
        wait_time = "00:00:30"
        print(f"Agendando CPF {cpf} para exibição às {entry_time} + {wait_time} (erro: {e})")

    # Criar um loop de eventos para chamadas assíncronas
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Enviar comando via WebSocket para exibição imediata
        result = loop.run_until_complete(send_image_via_websocket(cpf))
        
        # Preparar URLs de visualização
        view_urls = []
        for server in VISUALIZATION_SERVERS:
            external_url = get_external_url(server['url'], server['external_port'])
            view_urls.append({
                'server': server['name'],
                'delay': server['delay'],
                'url': f"{external_url}/view/",
                'websocket_result': result
            })
        
        return jsonify({
            'message': f'CPF {cpf} enviado para exibição via WebSocket',
            'cpf': cpf,
            'entry_time': entry_time,
            'wait_time': wait_time,
            'websocket_result': result,
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
    now = get_brasilia_now()
    entry_time = now.strftime('%H:%M:%S')  # Horário atual de Brasília
    
    # Calcula wait_time baseado no delay da primeira visualização (visualization1)
    # O wait_time deve ser o tempo até a primeira exibição
    first_delay_seconds = 30  # delay_seconds da visualization1
    wait_time_seconds = first_delay_seconds
    wait_time = f"00:00:{wait_time_seconds:02d}"
    
    print(f"Agendando CPF {cpf} para exibição às {entry_time} + {wait_time} (primeira visualização em {first_delay_seconds}s)")

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
    
    # Usa horário atual de Brasília como horário de entrada
    now = get_brasilia_now()
    entry_time = now.strftime('%H:%M:%S')
    
    # Chama o sistema novo de agendamento diretamente
    return schedule_webhook_internal(cpf, entry_time, wait_time)

def schedule_webhook_internal(cpf, entry_time, wait_time):
    """Função interna para processar agendamento"""
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002) 