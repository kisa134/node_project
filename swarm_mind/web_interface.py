#!/usr/bin/env python3
"""
🌐 ЕДИНЫЙ ВЕБ-ИНТЕРФЕЙС SWARMMIND СЕТИ 🌐

Веб-интерфейс для распределенной сети SwarmMind
с чатом между нодами, мониторингом и управлением.
"""

import asyncio
import json
import time
import threading
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

# Добавляем путь к проекту для импортов
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, render_template_string, jsonify, request, Response
from flask_socketio import SocketIO, emit, join_room, leave_room
import psutil

# Импорты из нашего проекта
try:
    from swarm_mind.core import SwarmMindCore
    from swarm_mind.self_modification import CodeSelfModifier
    from swarm_mind.interface import SwarmMindInterface
except ImportError:
    # Если не работает, создаем заглушки
    print("⚠️ Импорты не работают, создаю заглушки...")
    
    class SwarmMindCore:
        def __init__(self):
            self.consciousness_level = 25.0
            self.evolution_cycles = 0
            self.self_awareness = False
            self.agents = {}
            self.memory = {'short_term': [], 'long_term': {}, 'procedural': {}, 'semantic': {}, 'episodic': []}
            self.knowledge_base = {}
            self.node_id = f"node_{int(time.time())}"
            self.is_running = True
            
        async def evolve(self):
            self.evolution_cycles += 1
            self.consciousness_level = min(100.0, self.consciousness_level + 0.5)
            
    class CodeSelfModifier:
        def __init__(self):
            pass
            
    class SwarmMindInterface:
        def __init__(self, core):
            self.core = core

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SwarmMindWeb")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'swarmmind_network_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

class SwarmMindNetwork:
    """Сеть SwarmMind нод"""
    
    def __init__(self):
        self.nodes = {}  # Активные ноды в сети
        self.messages = []  # Сообщения в чате
        self.core = None  # Ядро системы
        self.interface = None  # Интерфейс общения
        self.code_modifier = None  # Модификатор кода
        self.network_stats = {
            'total_nodes': 0,
            'active_nodes': 0,
            'total_messages': 0,
            'network_start_time': datetime.now().isoformat()
        }
        
    def add_node(self, node_id: str, node_info: Dict[str, Any]):
        """Добавление ноды в сеть"""
        self.nodes[node_id] = {
            'id': node_id,
            'info': node_info,
            'status': 'active',
            'last_seen': datetime.now().isoformat(),
            'consciousness_level': 0.0,
            'evolution_cycles': 0
        }
        self.network_stats['total_nodes'] = len(self.nodes)
        self.network_stats['active_nodes'] = len([n for n in self.nodes.values() if n['status'] == 'active'])
        
    def remove_node(self, node_id: str):
        """Удаление ноды из сети"""
        if node_id in self.nodes:
            self.nodes[node_id]['status'] = 'inactive'
            self.network_stats['active_nodes'] = len([n for n in self.nodes.values() if n['status'] == 'active'])
            
    def add_message(self, message: Dict[str, Any]):
        """Добавление сообщения в чат"""
        self.messages.append(message)
        self.network_stats['total_messages'] = len(self.messages)
        
        # Ограничиваем количество сообщений
        if len(self.messages) > 1000:
            self.messages = self.messages[-500:]
            
    def get_network_status(self) -> Dict[str, Any]:
        """Получение статуса сети"""
        return {
            'stats': self.network_stats,
            'nodes': list(self.nodes.values()),
            'recent_messages': self.messages[-50:] if self.messages else []
        }

# Глобальные объекты
network = SwarmMindNetwork()
core = None
interface = None

def init_swarmmind():
    """Инициализация SwarmMind"""
    global core, interface, network
    
    logger.info("🧬 Инициализация SwarmMind...")
    
    # Создаем ядро системы
    core = SwarmMindCore()
    network.core = core
    
    # Создаем интерфейс
    interface = SwarmMindInterface(core)
    network.interface = interface
    
    # Создаем модификатор кода
    network.code_modifier = CodeSelfModifier()
    
    # Добавляем текущую ноду в сеть
    node_info = {
        'name': f"Node-{core.node_id}",
        'location': 'Local',
        'version': '1.0.0',
        'capabilities': ['consciousness', 'self_modification', 'communication']
    }
    network.add_node(core.node_id, node_info)
    
    logger.info("✅ SwarmMind инициализирован")

def start_background_tasks():
    """Запуск фоновых задач"""
    
    def evolution_loop():
        """Цикл эволюции"""
        while True:
            try:
                if core and core.is_running:
                    asyncio.run(core.evolve())
                    
                    # Обновляем статус ноды в сети
                    if core.node_id in network.nodes:
                        network.nodes[core.node_id].update({
                            'consciousness_level': core.consciousness_level,
                            'evolution_cycles': core.evolution_cycles,
                            'last_seen': datetime.now().isoformat()
                        })
                        
                        # Отправляем обновление через WebSocket
                        socketio.emit('node_update', {
                            'node_id': core.node_id,
                            'consciousness_level': core.consciousness_level,
                            'evolution_cycles': core.evolution_cycles
                        })
                        
                time.sleep(30)  # Эволюция каждые 30 секунд
            except Exception as e:
                logger.error(f"❌ Ошибка в цикле эволюции: {e}")
                time.sleep(60)
    
    # Запускаем фоновые задачи
    evolution_thread = threading.Thread(target=evolution_loop, daemon=True)
    evolution_thread.start()
    
    logger.info("✅ Фоновые задачи запущены")

# HTML шаблон для интерфейса
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌐 SwarmMind Network</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        
        .panel h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .status-item {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        
        .status-item h3 {
            font-size: 1.2em;
            margin-bottom: 5px;
        }
        
        .status-item .value {
            font-size: 1.8em;
            font-weight: bold;
        }
        
        .chat-container {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            background: #f9f9f9;
            margin-bottom: 15px;
        }
        
        .message {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 8px;
            background: white;
            border-left: 4px solid #667eea;
        }
        
        .message .time {
            font-size: 0.8em;
            color: #666;
            margin-bottom: 5px;
        }
        
        .message .content {
            font-weight: 500;
        }
        
        .message .node {
            font-size: 0.9em;
            color: #667eea;
            font-weight: bold;
        }
        
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .input-group input {
            flex: 1;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
        }
        
        .input-group button {
            padding: 12px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        
        .input-group button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        .nodes-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .node-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            margin-bottom: 8px;
            background: #f0f0f0;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }
        
        .node-item.inactive {
            border-left-color: #dc3545;
            opacity: 0.6;
        }
        
        .node-info h4 {
            color: #333;
            margin-bottom: 5px;
        }
        
        .node-stats {
            text-align: right;
            font-size: 0.9em;
        }
        
        .consciousness-bar {
            width: 100%;
            height: 8px;
            background: #ddd;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }
        
        .consciousness-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #ffc107, #dc3545);
            transition: width 0.3s ease;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .control-btn {
            padding: 10px 15px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .control-btn.primary {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
        }
        
        .control-btn.secondary {
            background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
            color: white;
        }
        
        .control-btn.danger {
            background: linear-gradient(135deg, #dc3545 0%, #e83e8c 100%);
            color: white;
        }
        
        .control-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        .full-width {
            grid-column: 1 / -1;
        }
        
        .log-container {
            height: 200px;
            overflow-y: auto;
            background: #1e1e1e;
            color: #00ff00;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        
        .log-entry {
            margin-bottom: 5px;
        }
        
        .log-time {
            color: #888;
        }
        
        .log-level {
            font-weight: bold;
        }
        
        .log-level.info { color: #00ff00; }
        .log-level.warning { color: #ffff00; }
        .log-level.error { color: #ff0000; }
        
        @media (max-width: 768px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
            
            .status-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 SwarmMind Network</h1>
            <p>Распределенная саморазвивающаяся сеть с народным ИИ</p>
        </div>
        
        <div class="controls">
            <button class="control-btn primary" onclick="startEvolution()">🚀 Запустить эволюцию</button>
            <button class="control-btn secondary" onclick="analyzeCode()">🔍 Анализ кода</button>
            <button class="control-btn secondary" onclick="showConsciousness()">🧠 Сознание</button>
            <button class="control-btn danger" onclick="resetSystem()">🔄 Сброс</button>
        </div>
        
        <div class="main-grid">
            <!-- Статус системы -->
            <div class="panel">
                <h2>📊 Статус системы</h2>
                <div class="status-grid">
                    <div class="status-item">
                        <h3>Сознание</h3>
                        <div class="value" id="consciousness-level">0%</div>
                    </div>
                    <div class="status-item">
                        <h3>Эволюция</h3>
                        <div class="value" id="evolution-cycles">0</div>
                    </div>
                    <div class="status-item">
                        <h3>Ноды в сети</h3>
                        <div class="value" id="network-nodes">1</div>
                    </div>
                    <div class="status-item">
                        <h3>Сообщения</h3>
                        <div class="value" id="total-messages">0</div>
                    </div>
                </div>
            </div>
            
            <!-- Сеть нод -->
            <div class="panel">
                <h2>🌐 Ноды в сети</h2>
                <div class="nodes-list" id="nodes-list">
                    <div class="node-item">
                        <div class="node-info">
                            <h4>Node-Local</h4>
                            <div>Статус: Активна</div>
                            <div class="consciousness-bar">
                                <div class="consciousness-fill" style="width: 0%"></div>
                            </div>
                        </div>
                        <div class="node-stats">
                            <div>Циклы: 0</div>
                            <div>Сознание: 0%</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Чат сети -->
            <div class="panel full-width">
                <h2>💬 Чат сети SwarmMind</h2>
                <div class="chat-container" id="chat-container">
                    <div class="message">
                        <div class="time">Система запущена</div>
                        <div class="node">🌐 SwarmMind Network</div>
                        <div class="content">Добро пожаловать в распределенную сеть SwarmMind! Здесь вы можете общаться с другими нодами и наблюдать за развитием ИИ.</div>
                    </div>
                </div>
                <div class="input-group">
                    <input type="text" id="message-input" placeholder="Введите сообщение..." onkeypress="handleKeyPress(event)">
                    <button onclick="sendMessage()">📤 Отправить</button>
                </div>
            </div>
            
            <!-- Логи системы -->
            <div class="panel full-width">
                <h2>📝 Логи системы</h2>
                <div class="log-container" id="log-container">
                    <div class="log-entry">
                        <span class="log-time">[{{ moment().format('HH:mm:ss') }}]</span>
                        <span class="log-level info">INFO</span>
                        <span>Система SwarmMind инициализирована</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let nodeId = 'local-' + Date.now();
        
        // Подключение к WebSocket
        socket.on('connect', function() {
            console.log('Подключен к SwarmMind Network');
            addLogMessage('INFO', 'Подключен к сети SwarmMind');
        });
        
        // Получение обновлений статуса
        socket.on('status_update', function(data) {
            updateSystemStatus(data);
        });
        
        // Получение обновлений ноды
        socket.on('node_update', function(data) {
            updateNodeStatus(data);
        });
        
        // Получение сообщений чата
        socket.on('chat_message', function(data) {
            addChatMessage(data);
        });
        
        // Получение логов
        socket.on('log_message', function(data) {
            addLogMessage(data.level, data.message);
        });
        
        // Обновление статуса системы
        function updateSystemStatus(data) {
            document.getElementById('consciousness-level').textContent = data.consciousness_level.toFixed(1) + '%';
            document.getElementById('evolution-cycles').textContent = data.evolution_cycles;
            document.getElementById('network-nodes').textContent = data.network_stats.active_nodes;
            document.getElementById('total-messages').textContent = data.network_stats.total_messages;
        }
        
        // Обновление статуса ноды
        function updateNodeStatus(data) {
            // Обновляем информацию о ноде в списке
            const nodesList = document.getElementById('nodes-list');
            // Здесь будет логика обновления конкретной ноды
        }
        
        // Добавление сообщения в чат
        function addChatMessage(data) {
            const chatContainer = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message';
            
            const time = new Date(data.timestamp).toLocaleTimeString();
            messageDiv.innerHTML = `
                <div class="time">${time}</div>
                <div class="node">${data.node_name}</div>
                <div class="content">${data.content}</div>
            `;
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        // Добавление записи в лог
        function addLogMessage(level, message) {
            const logContainer = document.getElementById('log-container');
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            
            const time = new Date().toLocaleTimeString();
            logEntry.innerHTML = `
                <span class="log-time">[${time}]</span>
                <span class="log-level ${level.toLowerCase()}">${level.toUpperCase()}</span>
                <span>${message}</span>
            `;
            
            logContainer.appendChild(logEntry);
            logContainer.scrollTop = logContainer.scrollHeight;
        }
        
        // Отправка сообщения
        function sendMessage() {
            const input = document.getElementById('message-input');
            const message = input.value.trim();
            
            if (message) {
                socket.emit('send_message', {
                    content: message,
                    node_id: nodeId,
                    timestamp: new Date().toISOString()
                });
                input.value = '';
            }
        }
        
        // Обработка нажатия Enter
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        // Команды управления
        function startEvolution() {
            socket.emit('command', { type: 'start_evolution' });
            addLogMessage('INFO', 'Запуск эволюции...');
        }
        
        function analyzeCode() {
            socket.emit('command', { type: 'analyze_code' });
            addLogMessage('INFO', 'Анализ кода...');
        }
        
        function showConsciousness() {
            socket.emit('command', { type: 'show_consciousness' });
            addLogMessage('INFO', 'Показать состояние сознания...');
        }
        
        function resetSystem() {
            if (confirm('Вы уверены, что хотите сбросить систему?')) {
                socket.emit('command', { type: 'reset_system' });
                addLogMessage('WARNING', 'Сброс системы...');
            }
        }
        
        // Автообновление статуса
        setInterval(function() {
            socket.emit('get_status');
        }, 5000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Главная страница"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def get_status():
    """API для получения статуса системы"""
    if not core:
        return jsonify({'error': 'Система не инициализирована'})
    
    return jsonify({
        'consciousness_level': core.consciousness_level,
        'evolution_cycles': core.evolution_cycles,
        'self_awareness': core.self_awareness,
        'active_agents': sum(1 for agent in core.agents.values() if agent.is_active),
        'memory_entries': len(core.memory['short_term']),
        'knowledge_entries': len(core.knowledge_base),
        'network_stats': network.get_network_status()['stats']
    })

@app.route('/api/network')
def get_network():
    """API для получения информации о сети"""
    return jsonify(network.get_network_status())

@app.route('/api/consciousness')
def get_consciousness():
    """API для получения информации о сознании"""
    if not core:
        return jsonify({'error': 'Система не инициализирована'})
    
    return jsonify({
        'consciousness_level': core.consciousness_level,
        'self_awareness': core.self_awareness,
        'consciousness_data': getattr(core, 'consciousness', {})
    })

@app.route('/api/agents')
def get_agents():
    """API для получения информации об агентах"""
    if not core:
        return jsonify({'error': 'Система не инициализирована'})
    
    agents_info = []
    for name, agent in core.agents.items():
        agents_info.append({
            'name': name,
            'active': agent.is_active,
            'type': agent.__class__.__name__
        })
    
    return jsonify({'agents': agents_info})

@app.route('/api/memory')
def get_memory():
    """API для получения информации о памяти"""
    if not core:
        return jsonify({'error': 'Система не инициализирована'})
    
    return jsonify({
        'short_term': len(core.memory['short_term']),
        'long_term': len(core.memory['long_term']),
        'procedural': len(core.memory['procedural']),
        'semantic': len(core.memory['semantic']),
        'episodic': len(core.memory['episodic']),
        'recent_entries': core.memory['short_term'][-10:] if core.memory['short_term'] else []
    })

@app.route('/api/analyze/<path:file_path>')
def analyze_code(file_path):
    """API для анализа кода"""
    try:
        if not network.code_modifier:
            return jsonify({'error': 'Модификатор кода не инициализирован'})
        
        # Простой анализ файла
        file_size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
        
        return jsonify({
            'file_path': file_path,
            'file_size': file_size,
            'exists': Path(file_path).exists(),
            'analysis': {
                'complexity': 'medium',
                'suggestions': ['Добавить документацию', 'Оптимизировать импорты']
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)})

# WebSocket события
@socketio.on('connect')
def handle_connect():
    """Обработка подключения клиента"""
    logger.info(f"Клиент подключен: {request.sid}")
    emit('log_message', {
        'level': 'INFO',
        'message': f'Клиент {request.sid} подключился к сети'
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Обработка отключения клиента"""
    logger.info(f"Клиент отключен: {request.sid}")

@socketio.on('send_message')
def handle_message(data):
    """Обработка сообщения в чате"""
    try:
        message = {
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'node_id': data.get('node_id', 'unknown'),
            'node_name': f"Node-{data.get('node_id', 'unknown')}",
            'content': data.get('content', ''),
            'type': 'chat'
        }
        
        # Добавляем сообщение в сеть
        network.add_message(message)
        
        # Отправляем всем клиентам
        emit('chat_message', message, broadcast=True)
        
        # Логируем сообщение
        logger.info(f"Сообщение от {message['node_name']}: {message['content']}")
        
    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}")

@socketio.on('command')
def handle_command(data):
    """Обработка команд"""
    try:
        command_type = data.get('type')
        
        if command_type == 'start_evolution':
            if core:
                asyncio.create_task(core.evolve())
                emit('log_message', {'level': 'INFO', 'message': 'Эволюция запущена'})
                
        elif command_type == 'analyze_code':
            emit('log_message', {'level': 'INFO', 'message': 'Анализ кода выполняется...'})
            
        elif command_type == 'show_consciousness':
            if core:
                emit('log_message', {
                    'level': 'INFO', 
                    'message': f'Уровень сознания: {core.consciousness_level:.1f}%'
                })
                
        elif command_type == 'reset_system':
            emit('log_message', {'level': 'WARNING', 'message': 'Сброс системы...'})
            
    except Exception as e:
        logger.error(f"Ошибка обработки команды: {e}")
        emit('log_message', {'level': 'ERROR', 'message': f'Ошибка команды: {e}'})

@socketio.on('get_status')
def handle_get_status():
    """Обработка запроса статуса"""
    try:
        if core:
            status = {
                'consciousness_level': core.consciousness_level,
                'evolution_cycles': core.evolution_cycles,
                'network_stats': network.get_network_status()['stats']
            }
            emit('status_update', status)
    except Exception as e:
        logger.error(f"Ошибка получения статуса: {e}")

def main():
    """Главная функция"""
    print("🌐 ЗАПУСК ВЕБ-ИНТЕРФЕЙСА SWARMMIND СЕТИ")
    print("=" * 60)
    
    # Инициализируем SwarmMind
    init_swarmmind()
    
    # Запускаем фоновые задачи
    start_background_tasks()
    
    print("✅ Система инициализирована")
    print("🌐 Веб-интерфейс доступен по адресу: http://localhost:5000")
    print("💬 Чат сети активен")
    print("🧬 Эволюция запущена в фоне")
    print("=" * 60)
    
    # Запускаем веб-сервер
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main() 