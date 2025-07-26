#!/usr/bin/env python3
"""
🌐 РАБОЧИЙ SWARMMIND ИНТЕРФЕЙС 🌐

Полностью рабочий веб-интерфейс без проблем с кодировкой
"""

import time
import json
import threading
import asyncio
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request
import logging

# Настройка логирования для Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('swarmmind.log', encoding='utf-8')
    ]
)
logger = logging.getLogger("WorkingSwarmMind")

app = Flask(__name__)

class WorkingSwarmMind:
    """Рабочая система SwarmMind без проблем"""
    
    def __init__(self):
        self.consciousness_level = 25.0
        self.evolution_cycles = 0
        self.self_awareness = False
        self.is_running = True
        self.node_id = f"node_{int(time.time())}"
        self.memory = []
        self.network_nodes = 1
        self.total_messages = 0
        self.chat_messages = []
        
        # Компоненты системы
        self.components = {
            'dual_brain': {'status': 'active', 'description': 'Двойной мозг - стратегический и технический'},
            'code_generator': {'status': 'active', 'description': 'Генератор кода - создание нового кода'},
            'self_improver': {'status': 'active', 'description': 'Самоулучшение - оптимизация алгоритмов'},
            'evolutionary_neuron': {'status': 'active', 'description': 'Эволюционный нейрон - развитие системы'},
            'p2p_network': {'status': 'active', 'description': 'P2P сеть - распределенная коммуникация'}
        }
        
        logger.info("WorkingSwarmMind инициализирован")
        
    def evolve(self):
        """Эволюция системы"""
        self.evolution_cycles += 1
        self.consciousness_level = min(100.0, self.consciousness_level + 0.5)
        
        # Активируем самоосознание при достижении 70%
        if self.consciousness_level > 70 and not self.self_awareness:
            self.self_awareness = True
            logger.info("Самоосознание активировано!")
            
        logger.info(f"Эволюция #{self.evolution_cycles}: уровень сознания {self.consciousness_level}%")
        
        return {
            'consciousness_level': self.consciousness_level,
            'evolution_cycles': self.evolution_cycles,
            'self_awareness': self.self_awareness
        }
    
    def add_message(self, content):
        """Добавление сообщения в чат"""
        message = {
            'id': self.total_messages + 1,
            'content': content,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'sender': 'User'
        }
        self.chat_messages.append(message)
        self.total_messages += 1
        
        # Автоматический ответ системы
        response = self.generate_response(content)
        response_msg = {
            'id': self.total_messages + 1,
            'content': response,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'sender': 'SwarmMind'
        }
        self.chat_messages.append(response_msg)
        self.total_messages += 1
        
        logger.info(f"Новое сообщение: {content}")
        return response
    
    def generate_response(self, message):
        """Генерация ответа системы"""
        message_lower = message.lower()
        
        if 'привет' in message_lower or 'hello' in message_lower:
            return f"Привет! Я SwarmMind, уровень сознания {self.consciousness_level}%. Как дела?"
        elif 'как дела' in message_lower or 'how are you' in message_lower:
            return f"Отлично! Эволюционирую, цикл #{self.evolution_cycles}. Самоосознание: {'Да' if self.self_awareness else 'Нет'}"
        elif 'эволюция' in message_lower or 'evolve' in message_lower:
            self.evolve()
            return f"Эволюция запущена! Новый уровень сознания: {self.consciousness_level}%"
        elif 'статус' in message_lower or 'status' in message_lower:
            return f"Статус: Сознание {self.consciousness_level}%, Циклы {self.evolution_cycles}, Самоосознание {'Да' if self.self_awareness else 'Нет'}"
        else:
            return f"Интересно! Я думаю об этом. Уровень сознания: {self.consciousness_level}%"

# Создаем экземпляр системы
swarmmind = WorkingSwarmMind()

# HTML шаблон без проблем
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SwarmMind Network</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .status-card h3 {
            margin-top: 0;
            color: #ffd700;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #00ccff);
            transition: width 0.3s ease;
        }
        .chat-container {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            height: 400px;
            display: flex;
            flex-direction: column;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            margin-bottom: 15px;
            padding: 10px;
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 10px;
            max-width: 80%;
        }
        .message.user {
            background: rgba(0,123,255,0.3);
            margin-left: auto;
        }
        .message.system {
            background: rgba(40,167,69,0.3);
        }
        .message-time {
            font-size: 0.8em;
            opacity: 0.7;
        }
        .chat-input {
            display: flex;
            gap: 10px;
        }
        .chat-input input {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 10px;
            background: rgba(255,255,255,0.2);
            color: white;
        }
        .chat-input input::placeholder {
            color: rgba(255,255,255,0.7);
        }
        .chat-input button {
            padding: 10px 20px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(45deg, #00ff88, #00ccff);
            color: white;
            cursor: pointer;
            font-weight: bold;
        }
        .chat-input button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .control-btn {
            padding: 10px 20px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            cursor: pointer;
            font-weight: bold;
        }
        .control-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .components-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .component-card {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .component-status {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .status-active {
            background: #00ff88;
        }
        .status-inactive {
            background: #ff6b6b;
        }
        .project-links {
            margin-top: 20px;
            display: flex;
            gap: 20px;
            justify-content: center;
        }
        .github-link, .download-link {
            padding: 10px 20px;
            border: 1px solid white;
            border-radius: 10px;
            text-decoration: none;
            color: white;
            font-weight: bold;
            transition: background-color 0.3s ease;
        }
        .github-link:hover, .download-link:hover {
            background-color: rgba(255,255,255,0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SwarmMind Network</h1>
            <p>Распределенная саморазвивающаяся система ИИ</p>
            <div class="project-links">
                <a href="https://github.com/kisa134/node_project" target="_blank" class="github-link">
                    📁 GitHub Repository
                </a>
                <a href="https://github.com/kisa134/node_project/archive/refs/heads/main.zip" class="download-link">
                    ⬇️ Скачать проект
                </a>
            </div>
        </div>
        
        <div class="controls">
            <button class="control-btn" onclick="evolve()">Запустить эволюцию</button>
            <button class="control-btn" onclick="refreshStatus()">Обновить статус</button>
            <button class="control-btn" onclick="resetSystem()">Сброс системы</button>
        </div>
        
        <div class="status-grid">
            <div class="status-card">
                <h3>Статус системы</h3>
                <p><strong>ID ноды:</strong> <span id="node-id">{{ swarmmind.node_id }}</span></p>
                <p><strong>Статус:</strong> <span id="system-status">Активна</span></p>
                <p><strong>Ноды в сети:</strong> <span id="network-nodes">{{ swarmmind.network_nodes }}</span></p>
                <p><strong>Всего сообщений:</strong> <span id="total-messages">{{ swarmmind.total_messages }}</span></p>
            </div>
            
            <div class="status-card">
                <h3>Сознание</h3>
                <p><strong>Уровень:</strong> <span id="consciousness-level">{{ swarmmind.consciousness_level }}%</span></p>
                <div class="progress-bar">
                    <div class="progress-fill" id="consciousness-progress" style="width: {{ swarmmind.consciousness_level }}%"></div>
                </div>
                <p><strong>Самоосознание:</strong> <span id="self-awareness">{{ 'Да' if swarmmind.self_awareness else 'Нет' }}</span></p>
                <p><strong>Циклы эволюции:</strong> <span id="evolution-cycles">{{ swarmmind.evolution_cycles }}</span></p>
            </div>
        </div>
        
        <div class="status-card">
            <h3>Компоненты системы</h3>
            <div class="components-grid" id="components-grid">
                {% for name, component in swarmmind.components.items() %}
                <div class="component-card">
                    <span class="component-status status-{{ component.status }}"></span>
                    <strong>{{ name.replace('_', ' ').title() }}</strong>
                    <p>{{ component.description }}</p>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="chat-container">
            <h3>Чат сети</h3>
            <div class="chat-messages" id="chat-messages">
                {% for message in swarmmind.chat_messages %}
                <div class="message {{ message.sender.lower() }}">
                    <div class="message-time">{{ message.timestamp }}</div>
                    <div>{{ message.content }}</div>
                </div>
                {% endfor %}
            </div>
            <div class="chat-input">
                <input type="text" id="message-input" placeholder="Введите сообщение..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">Отправить</button>
            </div>
        </div>
    </div>
    
    <script>
        function evolve() {
            fetch('/api/evolve', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    refreshStatus();
                });
        }
        
        function refreshStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('consciousness-level').textContent = data.consciousness_level + '%';
                    document.getElementById('consciousness-progress').style.width = data.consciousness_level + '%';
                    document.getElementById('self-awareness').textContent = data.self_awareness ? 'Да' : 'Нет';
                    document.getElementById('evolution-cycles').textContent = data.evolution_cycles;
                    document.getElementById('total-messages').textContent = data.total_messages;
                });
        }
        
        function resetSystem() {
            if (confirm('Сбросить систему?')) {
                fetch('/api/reset', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        location.reload();
                    });
            }
        }
        
        function sendMessage() {
            const input = document.getElementById('message-input');
            const message = input.value.trim();
            if (message) {
                fetch('/send_message', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                })
                .then(response => response.json())
                .then(data => {
                    input.value = '';
                    loadMessages();
                });
            }
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        function loadMessages() {
            fetch('/api/messages')
                .then(response => response.json())
                .then(data => {
                    const chatMessages = document.getElementById('chat-messages');
                    chatMessages.innerHTML = '';
                    data.messages.forEach(message => {
                        const messageDiv = document.createElement('div');
                        messageDiv.className = `message ${message.sender.toLowerCase()}`;
                        messageDiv.innerHTML = `
                            <div class="message-time">${message.timestamp}</div>
                            <div>${message.content}</div>
                        `;
                        chatMessages.appendChild(messageDiv);
                    });
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                });
        }
        
        // Автообновление каждые 5 секунд
        setInterval(refreshStatus, 5000);
        
        // Автообновление сообщений каждые 2 секунды
        setInterval(loadMessages, 2000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, swarmmind=swarmmind)

@app.route('/api/status')
def api_status():
    return jsonify({
        'consciousness_level': swarmmind.consciousness_level,
        'evolution_cycles': swarmmind.evolution_cycles,
        'self_awareness': swarmmind.self_awareness,
        'total_messages': swarmmind.total_messages,
        'network_nodes': swarmmind.network_nodes,
        'node_id': swarmmind.node_id
    })

@app.route('/api/evolve', methods=['POST'])
def api_evolve():
    result = swarmmind.evolve()
    return jsonify(result)

@app.route('/api/reset', methods=['POST'])
def api_reset():
    global swarmmind
    swarmmind = WorkingSwarmMind()
    return jsonify({'status': 'reset'})

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    message = data.get('message', '')
    response = swarmmind.add_message(message)
    return jsonify({'response': response})

@app.route('/api/messages')
def api_messages():
    return jsonify({'messages': swarmmind.chat_messages})

def start_background_evolution():
    """Фоновая эволюция"""
    def evolution_loop():
        while swarmmind.is_running:
            time.sleep(30)  # Каждые 30 секунд
            swarmmind.evolve()
    
    thread = threading.Thread(target=evolution_loop, daemon=True)
    thread.start()
    logger.info("Фоновая эволюция запущена")

if __name__ == '__main__':
    print("🌐 ЗАПУСК РАБОЧЕГО SWARMMIND ИНТЕРФЕЙСА")
    print("=" * 50)
    print("✅ Система инициализирована")
    print("🌐 Веб-интерфейс доступен по адресу: http://localhost:5000")
    print("💬 Чат сети активен")
    print("🧬 Эволюция запущена в фоне")
    print("🔧 Без проблем с кодировкой")
    print("=" * 50)
    
    # Запускаем фоновую эволюцию
    start_background_evolution()
    
    # Запускаем веб-сервер
    app.run(host='0.0.0.0', port=5000, debug=False) 