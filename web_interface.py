#!/usr/bin/env python3
"""
🌐 ВЕБ-ИНТЕРФЕЙС SWARMIND 🌐

Простой веб-интерфейс для мониторинга и управления SwarmMind системой.
"""

import asyncio
import json
import time
import psutil
import subprocess
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request
import threading
import logging
from swarm_mind.logger import swarm_logger, log_event
from swarm_mind.evolution.dual_brain_architect import DualBrainLogAnalyzer

app = Flask(__name__)

# Глобальные переменные для хранения состояния
system_status = {
    "last_update": datetime.now().isoformat(),
    "evolution_cycles": 0,
    "active_neurons": 0,
    "cpu_usage": 0,
    "memory_usage": 0,
    "docker_containers": [],
    "ollama_status": "unknown"
}

def get_system_metrics():
    """Получение системных метрик"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        system_status["cpu_usage"] = cpu_percent
        system_status["memory_usage"] = memory.percent
        system_status["last_update"] = datetime.now().isoformat()
        
        return True
    except Exception as e:
        print(f"Ошибка получения метрик: {e}")
        return False

def get_docker_status():
    """Получение статуса Docker контейнеров"""
    try:
        result = subprocess.run(['docker-compose', 'ps', '--format', 'json'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        container = json.loads(line)
                        containers.append({
                            "name": container.get("Name", "Unknown"),
                            "service": container.get("Service", "Unknown"),
                            "status": container.get("State", "Unknown"),
                            "ports": container.get("Ports", "")
                        })
                    except json.JSONDecodeError:
                        continue
            system_status["docker_containers"] = containers
            system_status["active_neurons"] = len([c for c in containers if c["status"] == "running"])
            return True
    except Exception as e:
        print(f"Ошибка получения Docker статуса: {e}")
    return False

def check_ollama():
    """Проверка статуса Ollama"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            system_status["ollama_status"] = "running"
            return True
        else:
            system_status["ollama_status"] = "error"
            return False
    except Exception as e:
        system_status["ollama_status"] = "stopped"
        return False

def background_monitoring():
    """Фоновый мониторинг системы"""
    while True:
        get_system_metrics()
        get_docker_status()
        check_ollama()
        time.sleep(5)  # Обновление каждые 5 секунд

# HTML шаблон для интерфейса
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌐 SwarmMind Dashboard</title>
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
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .status-card h3 {
            margin-top: 0;
            color: #ffd700;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 5px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .metric-value {
            font-weight: bold;
            color: #90EE90;
        }
        .container-list {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
        }
        .container-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            margin: 5px 0;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
        }
        .status-running { color: #90EE90; }
        .status-stopped { color: #ff6b6b; }
        .controls {
            text-align: center;
            margin-top: 30px;
        }
        .btn {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            margin: 0 10px;
            font-size: 16px;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .btn:active {
            transform: translateY(0);
        }
        .last-update {
            text-align: center;
            margin-top: 20px;
            font-size: 0.9em;
            opacity: 0.8;
        }
        .auto-refresh {
            text-align: center;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 SwarmMind Dashboard</h1>
            <p>Мониторинг автономной эволюционной системы</p>
        </div>
        
        <div class="status-grid">
            <div class="status-card">
                <h3>📊 Системные метрики</h3>
                <div class="metric">
                    <span>CPU:</span>
                    <span class="metric-value" id="cpu-usage">{{ "%.1f"|format(cpu_usage) }}%</span>
                </div>
                <div class="metric">
                    <span>Память:</span>
                    <span class="metric-value" id="memory-usage">{{ "%.1f"|format(memory_usage) }}%</span>
                </div>
                <div class="metric">
                    <span>Активные нейроны:</span>
                    <span class="metric-value" id="active-neurons">{{ active_neurons }}</span>
                </div>
            </div>
            
            <div class="status-card">
                <h3>🧬 Эволюция</h3>
                <div class="metric">
                    <span>Циклы эволюции:</span>
                    <span class="metric-value" id="evolution-cycles">{{ evolution_cycles }}</span>
                </div>
                <div class="metric">
                    <span>Ollama статус:</span>
                    <span class="metric-value" id="ollama-status">{{ ollama_status }}</span>
                </div>
                <div class="metric">
                    <span>Последнее обновление:</span>
                    <span class="metric-value">{{ last_update }}</span>
                </div>
            </div>
        </div>
        
        <div class="container-list">
            <h3>🐳 Docker контейнеры</h3>
            {% for container in docker_containers %}
            <div class="container-item">
                <div>
                    <strong>{{ container.name }}</strong> ({{ container.service }})
                </div>
                <div class="status-{{ container.status.lower() }}">
                    {{ container.status }}
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="controls">
            <button class="btn" onclick="startEvolution()">🚀 Запустить эволюцию</button>
            <button class="btn" onclick="stopEvolution()">🛑 Остановить эволюцию</button>
            <button class="btn" onclick="refreshData()">🔄 Обновить данные</button>
        </div>
        
        <div class="last-update">
            Последнее обновление: <span id="last-update-time">{{ last_update }}</span>
        </div>
        
        <div class="auto-refresh">
            <label>
                <input type="checkbox" id="auto-refresh" checked> Автообновление каждые 5 секунд
            </label>
        </div>
    </div>
    
    <script>
        let autoRefreshInterval;
        
        function startAutoRefresh() {
            if (document.getElementById('auto-refresh').checked) {
                autoRefreshInterval = setInterval(refreshData, 5000);
            }
        }
        
        function stopAutoRefresh() {
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
            }
        }
        
        function refreshData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('cpu-usage').textContent = data.cpu_usage.toFixed(1) + '%';
                    document.getElementById('memory-usage').textContent = data.memory_usage.toFixed(1) + '%';
                    document.getElementById('active-neurons').textContent = data.active_neurons;
                    document.getElementById('evolution-cycles').textContent = data.evolution_cycles;
                    document.getElementById('ollama-status').textContent = data.ollama_status;
                    document.getElementById('last-update-time').textContent = data.last_update;
                })
                .catch(error => console.error('Ошибка обновления данных:', error));
        }
        
        function startEvolution() {
            fetch('/api/start_evolution', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    refreshData();
                })
                .catch(error => console.error('Ошибка запуска эволюции:', error));
        }
        
        function stopEvolution() {
            fetch('/api/stop_evolution', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    refreshData();
                })
                .catch(error => console.error('Ошибка остановки эволюции:', error));
        }
        
        // Инициализация
        document.getElementById('auto-refresh').addEventListener('change', function() {
            if (this.checked) {
                startAutoRefresh();
            } else {
                stopAutoRefresh();
            }
        });
        
        startAutoRefresh();
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Главная страница дашборда"""
    return render_template_string(HTML_TEMPLATE, **system_status)

@app.route('/api/status')
def api_status():
    """API для получения статуса системы"""
    return jsonify(system_status)

@app.route('/api/start_evolution', methods=['POST'])
def api_start_evolution():
    """API для запуска эволюции"""
    try:
        # Здесь можно добавить логику запуска эволюции
        system_status["evolution_cycles"] += 1
        return jsonify({"success": True, "message": "Эволюция запущена!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Ошибка: {str(e)}"})

@app.route('/api/stop_evolution', methods=['POST'])
def api_stop_evolution():
    """API для остановки эволюции"""
    try:
        # Здесь можно добавить логику остановки эволюции
        return jsonify({"success": True, "message": "Эволюция остановлена!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Ошибка: {str(e)}"})

@app.route('/log')
def view_log():
    """Страница просмотра лога событий"""
    log_lines = swarm_logger.get_recent_events(200)
    html = """
    <html><head><title>SwarmMind Event Log</title>
    <style>
    body { background: #222; color: #eee; font-family: monospace; padding: 20px; }
    .log { background: #111; border-radius: 8px; padding: 20px; max-width: 900px; margin: 0 auto; }
    .logline { border-bottom: 1px solid #333; padding: 4px 0; }
    .logline:last-child { border-bottom: none; }
    .info { color: #90EE90; }
    .warning { color: #FFD700; }
    .error { color: #FF6B6B; }
    </style></head><body>
    <h2>SwarmMind Event Log</h2>
    <div class='log'>
    """
    for line in log_lines:
        if 'ERROR' in line:
            html += f"<div class='logline error'>{line}</div>"
        elif 'WARNING' in line:
            html += f"<div class='logline warning'>{line}</div>"
        else:
            html += f"<div class='logline info'>{line}</div>"
    html += """</div><br><a href='/'>← Назад к дашборду</a></body></html>"""
    return html

@app.route('/api/log')
def api_log():
    """API для получения последних событий лога"""
    return {'log': swarm_logger.get_recent_events(100)}

# Инициализация аналитика
log_analyzer = DualBrainLogAnalyzer()
log_analyzer.start()

@app.route('/insights')
def view_insights():
    insights = log_analyzer.get_insights(20)
    html = """
    <html><head><title>SwarmMind Insights</title>
    <style>
    body { background: #222; color: #eee; font-family: sans-serif; padding: 20px; }
    .insight { background: #111; border-radius: 8px; padding: 12px; margin: 10px 0; color: #4ecdc4; }
    </style></head><body>
    <h2>AI Insights (DualBrain)</h2>
    <div>
    """
    for ins in insights:
        html += f"<div class='insight'>{ins}</div>"
    html += """</div><br><a href='/'>← Назад к дашборду</a></body></html>"""
    return html

@app.route('/api/insights')
def api_insights():
    return {'insights': log_analyzer.get_insights(10)}

def main():
    """Главная функция"""
    print("🌐 Запуск SwarmMind Web Interface...")
    print("📊 Дашборд будет доступен по адресу: http://localhost:5000")
    print("🔄 Автообновление каждые 5 секунд")
    print("🛑 Нажмите Ctrl+C для остановки")
    
    # Запускаем фоновый мониторинг в отдельном потоке
    monitoring_thread = threading.Thread(target=background_monitoring, daemon=True)
    monitoring_thread.start()

    log_event('Web interface started', logging.INFO)
    
    # Запускаем Flask приложение
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main() 