#!/usr/bin/env python3
"""
🌐 ЕДИНЫЙ ИНТЕРФЕЙС SWARMIND 🌐

Объединяет все функции в одном удобном интерфейсе:
- Мониторинг системы
- Визуализация эволюции  
- Просмотр логов
- AI-инсайты
- Управление системой
"""

import asyncio
import json
import time
import psutil
import subprocess
import threading
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
import base64
import numpy as np
from collections import deque
import os
import sys
import logging

# Добавляем путь к проекту
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
sys.path.insert(0, project_root)

from swarm_mind.logger import swarm_logger, log_event
from swarm_mind.evolution.dual_brain_architect import DualBrainLogAnalyzer
from github_integration import setup_github_integration, GitHubIntegration

app = Flask(__name__)

# Глобальные переменные для данных
system_status = {
    "last_update": datetime.now().isoformat(),
    "evolution_cycles": 0,
    "active_neurons": 0,
    "cpu_usage": 0,
    "memory_usage": 0,
    "docker_containers": [],
    "ollama_status": "unknown"
}

# Данные эволюции
evolution_data = {
    "timestamps": deque(maxlen=1000),
    "cpu_usage": deque(maxlen=1000),
    "memory_usage": deque(maxlen=1000),
    "evolution_cycles": deque(maxlen=1000),
    "code_improvements": deque(maxlen=1000),
    "performance_score": deque(maxlen=1000),
    "intelligence_level": deque(maxlen=1000),
    "modules_created": deque(maxlen=1000),
    "bugs_fixed": deque(maxlen=1000),
    "learning_rate": deque(maxlen=1000),
    "current_cycle": 0,
    "total_improvements": 0,
    "start_time": datetime.now(),
    "evolution_history": [],
    "evolution_active": True
}

# Инициализация AI-аналитика
log_analyzer = DualBrainLogAnalyzer()
log_analyzer.start()

# Инициализация GitHub интеграции
github_integration = setup_github_integration()

def get_system_metrics():
    """Получение метрик системы"""
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        system_status["cpu_usage"] = cpu_usage
        system_status["memory_usage"] = memory_usage
        system_status["last_update"] = datetime.now().isoformat()
        
        return cpu_usage, memory_usage
    except Exception as e:
        log_event(f"Ошибка получения метрик системы: {str(e)}", logging.ERROR)
        return 0, 0

def get_docker_status():
    """Получение статуса Docker контейнеров"""
    try:
        result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Пропускаем заголовок
            containers = []
            for line in lines:
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        containers.append({
                            'name': parts[0],
                            'status': parts[1],
                            'ports': parts[2] if len(parts) > 2 else ''
                        })
            system_status["docker_containers"] = containers
            return containers
        else:
            system_status["docker_containers"] = []
            return []
    except Exception as e:
        log_event(f"Ошибка получения Docker статуса: {str(e)}", logging.ERROR)
        system_status["docker_containers"] = []
        return []

def check_ollama():
    """Проверка статуса Ollama"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            system_status["ollama_status"] = "running"
            return "running"
        else:
            system_status["ollama_status"] = "stopped"
            return "stopped"
    except Exception as e:
        system_status["ollama_status"] = "error"
        return "error"

def generate_evolution_chart():
    """Генерация графика эволюции"""
    try:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.patch.set_facecolor('#1a1a1a')
        
        # График производительности и интеллекта
        if len(evolution_data["timestamps"]) > 0:
            timestamps = list(evolution_data["timestamps"])
            performance = list(evolution_data["performance_score"])
            intelligence = list(evolution_data["intelligence_level"])
            
            ax1.plot(timestamps, performance, 'g-', label='Производительность', linewidth=2)
            ax1.plot(timestamps, intelligence, 'b-', label='Интеллект', linewidth=2)
            ax1.set_ylabel('Уровень (%)', color='white')
            ax1.set_title('Эволюция SwarmMind', color='white', fontsize=14)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.set_facecolor('#2a2a2a')
            ax1.tick_params(colors='white')
            
            # График улучшений
            improvements = list(evolution_data["code_improvements"])
            ax2.bar(range(len(improvements)), improvements, color='#4ecdc4', alpha=0.7)
            ax2.set_ylabel('Улучшения', color='white')
            ax2.set_xlabel('Циклы', color='white')
            ax2.set_title('Код улучшения', color='white')
            ax2.set_facecolor('#2a2a2a')
            ax2.tick_params(colors='white')
        
        plt.tight_layout()
        
        # Конвертируем в base64
        canvas = FigureCanvas(fig)
        canvas.draw()
        img_data = io.BytesIO()
        fig.savefig(img_data, format='png', facecolor='#1a1a1a', bbox_inches='tight')
        img_data.seek(0)
        img_base64 = base64.b64encode(img_data.getvalue()).decode()
        plt.close(fig)
        
        return img_base64
    except Exception as e:
        log_event(f"Ошибка генерации графика: {str(e)}", logging.ERROR)
        return None

def background_monitoring():
    """Фоновый мониторинг системы"""
    while True:
        try:
            get_system_metrics()
            get_docker_status()
            check_ollama()
            time.sleep(5)
        except Exception as e:
            log_event(f"Ошибка мониторинга: {str(e)}", logging.ERROR)
            time.sleep(10)

def background_evolution_simulation():
    """Симуляция эволюции в фоне"""
    cycle = 0
    while evolution_data["evolution_active"]:
        try:
            cycle += 1
            current_time = datetime.now()
            
            # Симуляция метрик эволюции
            performance = min(100, 50 + cycle * 2 + np.random.normal(0, 3))
            intelligence = min(100, 40 + cycle * 1.5 + np.random.normal(0, 2))
            improvements = max(0, int(np.random.poisson(2) + cycle * 0.1))
            
            # Обновляем данные
            evolution_data["timestamps"].append(current_time.strftime("%H:%M:%S"))
            evolution_data["cpu_usage"].append(system_status["cpu_usage"])
            evolution_data["memory_usage"].append(system_status["memory_usage"])
            evolution_data["evolution_cycles"].append(cycle)
            evolution_data["performance_score"].append(performance)
            evolution_data["intelligence_level"].append(intelligence)
            evolution_data["code_improvements"].append(improvements)
            evolution_data["current_cycle"] = cycle
            evolution_data["total_improvements"] += improvements
            
            # Логируем событие
            log_event(f"Evolution cycle {cycle}: perf={performance:.2f}%, intelligence={intelligence:.2f}, improvements={improvements}")
            
            time.sleep(10)  # Обновляем каждые 10 секунд
            
        except Exception as e:
            log_event(f"Ошибка симуляции эволюции: {str(e)}", logging.ERROR)
            time.sleep(30)

# HTML шаблон для единого интерфейса
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌐 SwarmMind Unified Interface</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
            color: #fff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        .header {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid #4ecdc4;
        }
        .nav {
            background: rgba(0,0,0,0.2);
            padding: 10px;
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }
        .nav button {
            background: #4ecdc4;
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        .nav button:hover { background: #45b7aa; transform: translateY(-2px); }
        .nav button.active { background: #ff6b6b; }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        .section {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid #4ecdc4;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: rgba(78, 205, 196, 0.1);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #4ecdc4;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #4ecdc4;
        }
        .metric-label {
            color: #ccc;
            margin-top: 5px;
        }
        .chart-container {
            text-align: center;
            margin: 20px 0;
        }
        .chart-container img {
            max-width: 100%;
            border-radius: 8px;
            border: 2px solid #4ecdc4;
        }
        .log-container {
            background: #111;
            border-radius: 8px;
            padding: 15px;
            max-height: 400px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 12px;
        }
        .log-line {
            padding: 2px 0;
            border-bottom: 1px solid #333;
        }
        .log-line:last-child { border-bottom: none; }
        .log-error { color: #ff6b6b; }
        .log-warning { color: #ffd700; }
        .log-info { color: #90ee90; }
        .insights-container {
            background: rgba(78, 205, 196, 0.1);
            border-radius: 8px;
            padding: 15px;
        }
        .insight {
            background: rgba(0,0,0,0.3);
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 3px solid #4ecdc4;
        }
        .hidden { display: none; }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .status-running { background: #90ee90; }
        .status-stopped { background: #ff6b6b; }
        .status-unknown { background: #ffd700; }
        .controls {
            display: flex;
            gap: 10px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .control-btn {
            background: #4ecdc4;
            color: #000;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        .control-btn:hover { background: #45b7aa; }
        .control-btn.danger { background: #ff6b6b; }
        .control-btn.danger:hover { background: #ff5252; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌐 SwarmMind Unified Interface</h1>
        <p>Единый интерфейс для мониторинга и управления AI-системой</p>
    </div>
    
    <div class="nav">
        <button onclick="showSection('dashboard')" class="active">📊 Дашборд</button>
        <button onclick="showSection('evolution')">🧬 Эволюция</button>
        <button onclick="showSection('logs')">📝 Логи</button>
        <button onclick="showSection('insights')">🤖 AI Инсайты</button>
        <button onclick="showSection('control')">⚙️ Управление</button>
        <button onclick="showSection('github')">🔗 GitHub</button>
    </div>
    
    <div class="container">
        <!-- Дашборд -->
        <div id="dashboard" class="section">
            <h2>📊 Системный мониторинг</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value" id="cpu-usage">0%</div>
                    <div class="metric-label">CPU</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="memory-usage">0%</div>
                    <div class="metric-label">Память</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="evolution-cycles">0</div>
                    <div class="metric-label">Циклы эволюции</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="active-neurons">0</div>
                    <div class="metric-label">Активные нейроны</div>
                </div>
            </div>
            
            <h3>🐳 Docker контейнеры</h3>
            <div id="docker-status">Загрузка...</div>
            
            <h3>🤖 Ollama статус</h3>
            <div id="ollama-status">Загрузка...</div>
        </div>
        
        <!-- Эволюция -->
        <div id="evolution" class="section hidden">
            <h2>🧬 Визуализация эволюции</h2>
            <div class="chart-container">
                <img id="evolution-chart" src="" alt="График эволюции">
            </div>
            <div class="controls">
                <button class="control-btn" onclick="startEvolution()">▶️ Запустить эволюцию</button>
                <button class="control-btn" onclick="pauseEvolution()">⏸️ Пауза</button>
                <button class="control-btn" onclick="resetEvolution()">🔄 Сброс</button>
            </div>
        </div>
        
        <!-- Логи -->
        <div id="logs" class="section hidden">
            <h2>📝 Лог событий</h2>
            <div class="controls">
                <button class="control-btn" onclick="refreshLogs()">🔄 Обновить</button>
                <button class="control-btn" onclick="clearLogs()">🗑️ Очистить</button>
            </div>
            <div class="log-container" id="log-content">
                Загрузка логов...
            </div>
        </div>
        
        <!-- AI Инсайты -->
        <div id="insights" class="section hidden">
            <h2>🤖 AI Инсайты (DualBrain)</h2>
            <div class="controls">
                <button class="control-btn" onclick="refreshInsights()">🔄 Обновить инсайты</button>
            </div>
            <div class="insights-container" id="insights-content">
                Загрузка инсайтов...
            </div>
        </div>
        
        <!-- Управление -->
        <div id="control" class="section hidden">
            <h2>⚙️ Управление системой</h2>
            <div class="controls">
                <button class="control-btn" onclick="startDocker()">🐳 Запустить Docker</button>
                <button class="control-btn" onclick="stopDocker()">🛑 Остановить Docker</button>
                <button class="control-btn" onclick="startOllama()">🤖 Запустить Ollama</button>
                <button class="control-btn danger" onclick="emergencyStop()">🚨 Экстренная остановка</button>
            </div>
            <div id="control-status">
                <h3>Статус операций:</h3>
                <div id="control-messages"></div>
            </div>
        </div>

        <!-- GitHub -->
        <div id="github" class="section hidden">
            <h2>🔗 GitHub Integration</h2>
            <div class="controls">
                <button class="control-btn" onclick="testGitHubConnection()">🔗 Проверить подключение</button>
                <button class="control-btn" onclick="analyzeRepository()">🔍 Анализировать репозиторий</button>
                <button class="control-btn" onclick="createImprovementPR()">🚀 Создать PR улучшений</button>
                <button class="control-btn" onclick="autoImproveCode()">🤖 Автоулучшение кода</button>
            </div>
            <div id="github-status">
                <h3>Статус GitHub:</h3>
                <div id="github-messages"></div>
            </div>
            <div id="github-improvements">
                <h3>Найденные улучшения:</h3>
                <div id="improvements-list"></div>
            </div>
        </div>
    </div>

    <script>
        let currentSection = 'dashboard';
        
        function showSection(sectionName) {
            // Скрываем все секции
            document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
            // Показываем нужную секцию
            document.getElementById(sectionName).classList.remove('hidden');
            // Обновляем активную кнопку
            document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
            currentSection = sectionName;
        }
        
        function updateDashboard() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('cpu-usage').textContent = data.cpu_usage.toFixed(1) + '%';
                    document.getElementById('memory-usage').textContent = data.memory_usage.toFixed(1) + '%';
                    document.getElementById('evolution-cycles').textContent = data.evolution_cycles;
                    document.getElementById('active-neurons').textContent = data.active_neurons;
                    
                    // Обновляем Docker статус
                    let dockerHtml = '';
                    data.docker_containers.forEach(container => {
                        const statusClass = container.status.includes('Up') ? 'status-running' : 'status-stopped';
                        dockerHtml += `<div><span class="status-indicator ${statusClass}"></span>${container.name}: ${container.status}</div>`;
                    });
                    document.getElementById('docker-status').innerHTML = dockerHtml || 'Нет активных контейнеров';
                    
                    // Обновляем Ollama статус
                    const ollamaClass = data.ollama_status === 'running' ? 'status-running' : 
                                      data.ollama_status === 'stopped' ? 'status-stopped' : 'status-unknown';
                    document.getElementById('ollama-status').innerHTML = 
                        `<span class="status-indicator ${ollamaClass}"></span>Ollama: ${data.ollama_status}`;
                })
                .catch(error => console.error('Ошибка обновления дашборда:', error));
        }
        
        function updateEvolutionChart() {
            fetch('/api/evolution_chart')
                .then(response => response.json())
                .then(data => {
                    if (data.chart_data) {
                        document.getElementById('evolution-chart').src = 'data:image/png;base64,' + data.chart_data;
                    }
                })
                .catch(error => console.error('Ошибка обновления графика:', error));
        }
        
        function refreshLogs() {
            fetch('/api/log')
                .then(response => response.json())
                .then(data => {
                    let logHtml = '';
                    data.log.forEach(line => {
                        const lineClass = line.includes('ERROR') ? 'log-error' : 
                                        line.includes('WARNING') ? 'log-warning' : 'log-info';
                        logHtml += `<div class="log-line ${lineClass}">${line}</div>`;
                    });
                    document.getElementById('log-content').innerHTML = logHtml;
                })
                .catch(error => console.error('Ошибка загрузки логов:', error));
        }
        
        function refreshInsights() {
            fetch('/api/insights')
                .then(response => response.json())
                .then(data => {
                    let insightsHtml = '';
                    data.insights.forEach(insight => {
                        insightsHtml += `<div class="insight">${insight}</div>`;
                    });
                    document.getElementById('insights-content').innerHTML = insightsHtml || 'Инсайты не найдены';
                })
                .catch(error => console.error('Ошибка загрузки инсайтов:', error));
        }
        
        function startEvolution() {
            fetch('/api/start_evolution', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Эволюция запущена!');
                    } else {
                        alert('Ошибка запуска эволюции: ' + data.message);
                    }
                });
        }
        
        function pauseEvolution() {
            fetch('/api/pause_evolution', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Эволюция приостановлена!');
                    } else {
                        alert('Ошибка приостановки эволюции: ' + data.message);
                    }
                });
        }
        
        function resetEvolution() {
            fetch('/api/reset_evolution', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Эволюция сброшена!');
                    } else {
                        alert('Ошибка сброса эволюции: ' + data.message);
                    }
                });
        }
        
        function startDocker() {
            fetch('/api/start_docker', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    document.getElementById('control-messages').innerHTML += 
                        `<div>🐳 ${data.message}</div>`;
                });
        }
        
        function stopDocker() {
            fetch('/api/stop_docker', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    document.getElementById('control-messages').innerHTML += 
                        `<div>🛑 ${data.message}</div>`;
                });
        }
        
        function startOllama() {
            fetch('/api/start_ollama', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    document.getElementById('control-messages').innerHTML += 
                        `<div>🤖 ${data.message}</div>`;
                });
        }
        
        function emergencyStop() {
            if (confirm('Вы уверены? Это остановит всю систему!')) {
                fetch('/api/emergency_stop', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('control-messages').innerHTML += 
                            `<div style="color: #ff6b6b;">🚨 ${data.message}</div>`;
                    });
            }
        }

        function testGitHubConnection() {
            fetch('/api/github/test_connection', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    document.getElementById('github-messages').innerHTML += 
                        `<div style="color: ${data.success ? '#90ee90' : '#ff6b6b'};">🔗 ${data.message}</div>`;
                });
        }
        
        function analyzeRepository() {
            fetch('/api/github/analyze', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    document.getElementById('github-messages').innerHTML += 
                        `<div>🔍 ${data.message}</div>`;
                    if (data.improvements) {
                        let improvementsHtml = '';
                        data.improvements.forEach(imp => {
                            improvementsHtml += `<div class="insight">
                                <strong>${imp.file_path}</strong>: ${imp.description} (Приоритет: ${imp.priority})
                            </div>`;
                        });
                        document.getElementById('improvements-list').innerHTML = improvementsHtml;
                    }
                });
        }
        
        function createImprovementPR() {
            fetch('/api/github/create_pr', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    document.getElementById('github-messages').innerHTML += 
                        `<div style="color: ${data.success ? '#90ee90' : '#ff6b6b'};">🚀 ${data.message}</div>`;
                });
        }
        
        function autoImproveCode() {
            fetch('/api/github/auto_improve', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    document.getElementById('github-messages').innerHTML += 
                        `<div style="color: ${data.success ? '#90ee90' : '#ff6b6b'};">🤖 ${data.message}</div>`;
                });
        }
        
        // Автообновление
        setInterval(() => {
            updateDashboard();
            if (currentSection === 'evolution') {
                updateEvolutionChart();
            }
        }, 5000);
        
        // Инициализация
        updateDashboard();
        refreshLogs();
        refreshInsights();
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Главная страница единого интерфейса"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def api_status():
    """API для получения статуса системы"""
    return jsonify(system_status)

@app.route('/api/evolution_chart')
def api_evolution_chart():
    """API для получения графика эволюции"""
    chart_data = generate_evolution_chart()
    return jsonify({"chart_data": chart_data})

@app.route('/api/log')
def api_log():
    """API для получения логов"""
    return jsonify({"log": swarm_logger.get_recent_events(100)})

@app.route('/api/insights')
def api_insights():
    """API для получения AI-инсайтов"""
    return jsonify({"insights": log_analyzer.get_insights(10)})

@app.route('/api/start_evolution', methods=['POST'])
def api_start_evolution():
    """API для запуска эволюции"""
    try:
        evolution_data["evolution_active"] = True
        log_event("Эволюция запущена через API")
        return jsonify({"success": True, "message": "Эволюция запущена"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/pause_evolution', methods=['POST'])
def api_pause_evolution():
    """API для приостановки эволюции"""
    try:
        evolution_data["evolution_active"] = False
        log_event("Эволюция приостановлена через API")
        return jsonify({"success": True, "message": "Эволюция приостановлена"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/reset_evolution', methods=['POST'])
def api_reset_evolution():
    """API для сброса эволюции"""
    try:
        evolution_data["current_cycle"] = 0
        evolution_data["total_improvements"] = 0
        evolution_data["evolution_history"].clear()
        for key in evolution_data:
            if isinstance(evolution_data[key], deque):
                evolution_data[key].clear()
        log_event("Эволюция сброшена через API")
        return jsonify({"success": True, "message": "Эволюция сброшена"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/start_docker', methods=['POST'])
def api_start_docker():
    """API для запуска Docker"""
    try:
        subprocess.run(['docker-compose', 'up', '-d'], check=True)
        log_event("Docker контейнеры запущены через API")
        return jsonify({"success": True, "message": "Docker контейнеры запущены"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Ошибка запуска Docker: {str(e)}"})

@app.route('/api/stop_docker', methods=['POST'])
def api_stop_docker():
    """API для остановки Docker"""
    try:
        subprocess.run(['docker-compose', 'down'], check=True)
        log_event("Docker контейнеры остановлены через API")
        return jsonify({"success": True, "message": "Docker контейнеры остановлены"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Ошибка остановки Docker: {str(e)}"})

@app.route('/api/start_ollama', methods=['POST'])
def api_start_ollama():
    """API для запуска Ollama"""
    try:
        subprocess.run(['ollama', 'serve'], check=True)
        log_event("Ollama запущен через API")
        return jsonify({"success": True, "message": "Ollama запущен"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Ошибка запуска Ollama: {str(e)}"})

@app.route('/api/emergency_stop', methods=['POST'])
def api_emergency_stop():
    """API для экстренной остановки"""
    try:
        subprocess.run(['docker-compose', 'down'], check=True)
        log_event("ЭКСТРЕННАЯ ОСТАНОВКА: Все сервисы остановлены")
        return jsonify({"success": True, "message": "Экстренная остановка выполнена"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Ошибка экстренной остановки: {str(e)}"})

@app.route('/api/github/test_connection', methods=['POST'])
def api_github_test_connection():
    """API для проверки подключения к GitHub"""
    if github_integration:
        success = github_integration.test_connection()
        return jsonify({
            "success": success,
            "message": "GitHub подключение успешно" if success else "GitHub подключение не удалось"
        })
    else:
        return jsonify({
            "success": False,
            "message": "GitHub интеграция не настроена. Установите GITHUB_TOKEN"
        })

@app.route('/api/github/analyze', methods=['POST'])
def api_github_analyze():
    """API для анализа репозитория"""
    if not github_integration:
        return jsonify({"success": False, "message": "GitHub интеграция не настроена"})
    
    try:
        files = github_integration.get_repository_files()
        improvements = []
        
        for file in files:
            if file["name"].endswith('.py'):
                content = github_integration.get_file_content(file["path"])
                if content:
                    file_improvements = github_integration.analyze_code_quality(file["path"], content)
                    improvements.extend(file_improvements)
        
        return jsonify({
            "success": True,
            "message": f"Проанализировано {len(files)} файлов, найдено {len(improvements)} улучшений",
            "improvements": [
                {
                    "file_path": imp.file_path,
                    "description": imp.description,
                    "priority": imp.priority,
                    "type": imp.improvement_type
                }
                for imp in improvements
            ]
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Ошибка анализа: {str(e)}"})

@app.route('/api/github/create_pr', methods=['POST'])
def api_github_create_pr():
    """API для создания pull request"""
    if not github_integration:
        return jsonify({"success": False, "message": "GitHub интеграция не настроена"})
    
    try:
        prs = github_integration.auto_improve_repository()
        if prs:
            success = github_integration.create_pull_request(prs[0])
            return jsonify({
                "success": success,
                "message": f"Pull request создан: {prs[0].title}" if success else "Ошибка создания PR"
            })
        else:
            return jsonify({"success": False, "message": "Улучшения не найдены"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Ошибка создания PR: {str(e)}"})

@app.route('/api/github/auto_improve', methods=['POST'])
def api_github_auto_improve():
    """API для автоматического улучшения кода"""
    if not github_integration:
        return jsonify({"success": False, "message": "GitHub интеграция не настроена"})
    
    try:
        prs = github_integration.auto_improve_repository()
        if prs:
            success = github_integration.create_pull_request(prs[0])
            return jsonify({
                "success": success,
                "message": f"Автоулучшение выполнено: {prs[0].title}" if success else "Ошибка автоулучшения"
            })
        else:
            return jsonify({"success": False, "message": "Улучшения не найдены"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Ошибка автоулучшения: {str(e)}"})

def main():
    """Главная функция"""
    print("🌐 Запуск единого интерфейса SwarmMind...")
    log_event("Unified interface started")
    
    # Запускаем фоновые потоки
    monitoring_thread = threading.Thread(target=background_monitoring, daemon=True)
    monitoring_thread.start()
    
    evolution_thread = threading.Thread(target=background_evolution_simulation, daemon=True)
    evolution_thread.start()
    
    print("📊 Интерфейс доступен по адресу: http://localhost:5000")
    print("🔄 Автообновление каждые 5 секунд")
    
    # Запускаем Flask приложение
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main() 