#!/usr/bin/env python3
"""
🧬 ВИЗУАЛИЗАТОР ЭВОЛЮЦИИ SWARMIND 🧬

Система визуализации в реальном времени показывает:
- Графики производительности
- Эволюционные циклы
- Улучшения кода
- Рост интеллекта системы
- Метрики самоулучшения
"""

import asyncio
import json
import time
import psutil
import threading
from datetime import datetime, timedelta
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
from swarm_mind.logger import log_event

# Добавляем путь к проекту
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

app = Flask(__name__)

# Глобальные переменные для хранения данных эволюции
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

class EvolutionTracker:
    def __init__(self):
        self.cycle_count = 0
        self.improvement_count = 0
        self.last_performance = 0
        self.intelligence_baseline = 50  # Базовый уровень интеллекта
        
    def track_cycle(self, performance_metrics):
        """Отслеживание эволюционного цикла"""
        self.cycle_count += 1
        
        # Анализируем улучшения
        current_performance = performance_metrics.get('success_rate', 0) * 100
        performance_improvement = max(0, current_performance - self.last_performance)
        
        # Рассчитываем уровень интеллекта
        intelligence_growth = min(10, performance_improvement * 0.5)
        current_intelligence = self.intelligence_baseline + (self.cycle_count * 2) + intelligence_growth
        
        # Обновляем данные
        timestamp = datetime.now()
        evolution_data["timestamps"].append(timestamp)
        evolution_data["cpu_usage"].append(psutil.cpu_percent())
        evolution_data["memory_usage"].append(psutil.virtual_memory().percent)
        evolution_data["evolution_cycles"].append(self.cycle_count)
        evolution_data["performance_score"].append(current_performance)
        evolution_data["intelligence_level"].append(current_intelligence)
        evolution_data["learning_rate"].append(performance_improvement)
        
        # Симулируем улучшения кода
        code_improvements = max(1, int(performance_improvement / 10))
        evolution_data["code_improvements"].append(code_improvements)
        evolution_data["modules_created"].append(max(0, int(performance_improvement / 20)))
        evolution_data["bugs_fixed"].append(max(0, int(performance_improvement / 15)))
        
        # Записываем историю эволюции
        cycle_data = {
            "cycle": self.cycle_count,
            "timestamp": timestamp.isoformat(),
            "performance": current_performance,
            "intelligence": current_intelligence,
            "improvements": code_improvements,
            "cpu": psutil.cpu_percent(),
            "memory": psutil.virtual_memory().percent,
            "learning_rate": performance_improvement
        }
        evolution_data["evolution_history"].append(cycle_data)
        
        self.last_performance = current_performance
        evolution_data["current_cycle"] = self.cycle_count
        evolution_data["total_improvements"] += code_improvements
        
        return cycle_data

# Создаем трекер эволюции
evolution_tracker = EvolutionTracker()

def generate_performance_chart():
    """Генерация графика производительности"""
    if len(evolution_data["timestamps"]) < 2:
        return None
        
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    fig.patch.set_facecolor('#1a1a1a')
    
    # График производительности и интеллекта
    timestamps = list(evolution_data["timestamps"])
    performance = list(evolution_data["performance_score"])
    intelligence = list(evolution_data["intelligence_level"])
    
    ax1.plot(timestamps, performance, 'g-', label='Производительность', linewidth=2)
    ax1.plot(timestamps, intelligence, 'b-', label='Уровень интеллекта', linewidth=2)
    ax1.set_ylabel('Очки', color='white')
    ax1.set_title('Эволюция производительности и интеллекта', color='white', fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_facecolor('#2a2a2a')
    
    # График системных ресурсов
    cpu_usage = list(evolution_data["cpu_usage"])
    memory_usage = list(evolution_data["memory_usage"])
    
    ax2.plot(timestamps, cpu_usage, 'r-', label='CPU', linewidth=2)
    ax2.plot(timestamps, memory_usage, 'y-', label='Память', linewidth=2)
    ax2.set_ylabel('Использование (%)', color='white')
    ax2.set_xlabel('Время', color='white')
    ax2.set_title('Использование системных ресурсов', color='white', fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_facecolor('#2a2a2a')
    
    # Настройка цветов
    for ax in [ax1, ax2]:
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
    
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

def generate_improvements_chart():
    """Генерация графика улучшений"""
    if len(evolution_data["timestamps"]) < 2:
        return None
        
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#1a1a1a')
    
    timestamps = list(evolution_data["timestamps"])
    improvements = list(evolution_data["code_improvements"])
    modules = list(evolution_data["modules_created"])
    bugs_fixed = list(evolution_data["bugs_fixed"])
    
    x = range(len(timestamps))
    width = 0.25
    
    ax.bar([i - width for i in x], improvements, width, label='Улучшения кода', color='green', alpha=0.7)
    ax.bar(x, modules, width, label='Новые модули', color='blue', alpha=0.7)
    ax.bar([i + width for i in x], bugs_fixed, width, label='Исправленные баги', color='red', alpha=0.7)
    
    ax.set_ylabel('Количество', color='white')
    ax.set_xlabel('Эволюционные циклы', color='white')
    ax.set_title('Эволюционные улучшения', color='white', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_facecolor('#2a2a2a')
    ax.tick_params(colors='white')
    
    for spine in ax.spines.values():
        spine.set_color('white')
    
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

# HTML шаблон для визуализации
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧬 SwarmMind Evolution Visualizer</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .header h1 {
            font-size: 2.5em;
            margin: 0;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.2);
            text-align: center;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.9em;
            opacity: 0.8;
        }
        .chart-container {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .chart-title {
            text-align: center;
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #4ecdc4;
        }
        .evolution-log {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            padding: 15px;
            max-height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        .log-entry {
            margin: 5px 0;
            padding: 5px;
            border-radius: 5px;
        }
        .log-cycle { color: #4ecdc4; }
        .log-improvement { color: #45b7d1; }
        .log-intelligence { color: #ff6b6b; }
        .log-performance { color: #96ceb4; }
        .controls {
            text-align: center;
            margin: 20px 0;
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
        .intelligence-bar {
            width: 100%;
            height: 30px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }
        .intelligence-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1);
            transition: width 0.5s ease;
            border-radius: 15px;
        }
        .auto-refresh {
            text-align: center;
            margin-top: 20px;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .status-active { background: #4ecdc4; }
        .status-paused { background: #ff6b6b; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧬 SwarmMind Evolution Visualizer</h1>
            <p>Визуализация роста и развития автономной системы</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Текущий цикл эволюции</div>
                <div class="metric-value" id="current-cycle">{{ current_cycle }}</div>
                <div class="intelligence-bar">
                    <div class="intelligence-fill" id="intelligence-fill" style="width: {{ intelligence_percent }}%"></div>
                </div>
                <div class="metric-label">Уровень интеллекта: {{ "%.1f"|format(intelligence_level) }}</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Общая производительность</div>
                <div class="metric-value" id="performance-score">{{ "%.1f"|format(performance_score) }}%</div>
                <div class="metric-label">Успешность операций</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Всего улучшений</div>
                <div class="metric-value" id="total-improvements">{{ total_improvements }}</div>
                <div class="metric-label">Код оптимизирован</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Время работы</div>
                <div class="metric-value" id="uptime">{{ uptime }}</div>
                <div class="metric-label">Система активна</div>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">📈 График производительности и интеллекта</div>
            <img id="performance-chart" src="data:image/png;base64,{{ performance_chart }}" 
                 style="width: 100%; max-width: 100%; height: auto;" alt="Performance Chart">
        </div>
        
        <div class="chart-container">
            <div class="chart-title">🔧 График эволюционных улучшений</div>
            <img id="improvements-chart" src="data:image/png;base64,{{ improvements_chart }}" 
                 style="width: 100%; max-width: 100%; height: auto;" alt="Improvements Chart">
        </div>
        
        <div class="chart-container">
            <div class="chart-title">📝 Журнал эволюции</div>
            <div class="evolution-log" id="evolution-log">
                {% for entry in recent_history %}
                <div class="log-entry log-{{ entry.type }}">
                    <span class="status-indicator status-active"></span>
                    [{{ entry.timestamp }}] {{ entry.message }}
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="startEvolution()">🚀 Запустить эволюцию</button>
            <button class="btn" onclick="pauseEvolution()">⏸️ Пауза</button>
            <button class="btn" onclick="resetEvolution()">🔄 Сброс</button>
            <button class="btn" onclick="refreshData()">🔄 Обновить</button>
        </div>
        
        <div class="auto-refresh">
            <label>
                <input type="checkbox" id="auto-refresh" checked> Автообновление каждые 3 секунды
            </label>
        </div>
    </div>
    
    <script>
        let autoRefreshInterval;
        let evolutionActive = true;
        
        function startAutoRefresh() {
            if (document.getElementById('auto-refresh').checked) {
                autoRefreshInterval = setInterval(refreshData, 3000);
            }
        }
        
        function stopAutoRefresh() {
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
            }
        }
        
        function refreshData() {
            fetch('/api/evolution_data')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('current-cycle').textContent = data.current_cycle;
                    document.getElementById('performance-score').textContent = data.performance_score.toFixed(1) + '%';
                    document.getElementById('total-improvements').textContent = data.total_improvements;
                    document.getElementById('uptime').textContent = data.uptime;
                    document.getElementById('intelligence-fill').style.width = data.intelligence_percent + '%';
                    
                    // Обновляем графики
                    if (data.performance_chart) {
                        document.getElementById('performance-chart').src = 'data:image/png;base64,' + data.performance_chart;
                    }
                    if (data.improvements_chart) {
                        document.getElementById('improvements-chart').src = 'data:image/png;base64,' + data.improvements_chart;
                    }
                    
                    // Обновляем лог
                    updateEvolutionLog(data.recent_history);
                })
                .catch(error => console.error('Ошибка обновления данных:', error));
        }
        
        function updateEvolutionLog(history) {
            const logContainer = document.getElementById('evolution-log');
            logContainer.innerHTML = '';
            
            history.forEach(entry => {
                const logEntry = document.createElement('div');
                logEntry.className = `log-entry log-${entry.type}`;
                logEntry.innerHTML = `
                    <span class="status-indicator status-active"></span>
                    [${entry.timestamp}] ${entry.message}
                `;
                logContainer.appendChild(logEntry);
            });
            
            logContainer.scrollTop = logContainer.scrollHeight;
        }
        
        function startEvolution() {
            fetch('/api/start_evolution', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    evolutionActive = true;
                    alert(data.message);
                    refreshData();
                })
                .catch(error => console.error('Ошибка запуска эволюции:', error));
        }
        
        function pauseEvolution() {
            fetch('/api/pause_evolution', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    evolutionActive = false;
                    alert(data.message);
                })
                .catch(error => console.error('Ошибка паузы эволюции:', error));
        }
        
        function resetEvolution() {
            if (confirm('Вы уверены, что хотите сбросить все данные эволюции?')) {
                fetch('/api/reset_evolution', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        alert(data.message);
                        refreshData();
                    })
                    .catch(error => console.error('Ошибка сброса эволюции:', error));
            }
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

def background_evolution_simulation():
    """Фоновая симуляция эволюции"""
    while True:
        if evolution_data.get("evolution_active", True):
            # Симулируем эволюционный цикл
            performance_metrics = {
                'success_rate': min(0.99, 0.85 + (evolution_tracker.cycle_count * 0.01)),
                'response_time': max(0.1, 0.5 - (evolution_tracker.cycle_count * 0.02)),
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent
            }
            
            cycle_data = evolution_tracker.track_cycle(performance_metrics)
            
            # Добавляем запись в лог
            log_event(f"Evolution cycle {cycle_data['cycle']}: perf={cycle_data['performance']:.2f}%, intelligence={cycle_data['intelligence']:.2f}, improvements={cycle_data['improvements']}")
            
            # Записываем историю эволюции
            cycle_data = {
                "type": "cycle",
                "timestamp": cycle_data["timestamp"][11:19],  # Только время
                "message": f"Цикл {cycle_data['cycle']}: Производительность {cycle_data['performance']:.1f}%, Интеллект {cycle_data['intelligence']:.1f}"
            }
            
            if cycle_data["improvements"] > 0:
                improvement_entry = {
                    "type": "improvement",
                    "timestamp": cycle_data["timestamp"][11:19],
                    "message": f"✨ Создано {cycle_data['improvements']} улучшений кода"
                }
                evolution_data["evolution_history"].append(improvement_entry)
            
            if cycle_data["learning_rate"] > 5:
                learning_entry = {
                    "type": "intelligence",
                    "timestamp": cycle_data["timestamp"][11:19],
                    "message": f"🧠 Рост интеллекта: +{cycle_data['learning_rate']:.1f} очков"
                }
                evolution_data["evolution_history"].append(learning_entry)
            
            evolution_data["evolution_history"].append(cycle_data)
            
            # Ограничиваем историю
            if len(evolution_data["evolution_history"]) > 50:
                evolution_data["evolution_history"] = evolution_data["evolution_history"][-50:]
        
        time.sleep(5)  # Эволюционный цикл каждые 5 секунд

@app.route('/')
def dashboard():
    """Главная страница визуализации"""
    # Генерируем графики
    performance_chart = generate_performance_chart() or ""
    improvements_chart = generate_improvements_chart() or ""
    
    # Рассчитываем метрики
    current_intelligence = evolution_data["intelligence_level"][-1] if evolution_data["intelligence_level"] else 50
    current_performance = evolution_data["performance_score"][-1] if evolution_data["performance_score"] else 85
    intelligence_percent = min(100, (current_intelligence / 200) * 100)  # Максимум 200 очков интеллекта
    
    # Рассчитываем время работы
    uptime = datetime.now() - evolution_data["start_time"]
    uptime_str = f"{uptime.days}д {uptime.seconds // 3600}ч {(uptime.seconds % 3600) // 60}м"
    
    # Получаем последние записи истории
    recent_history = evolution_data["evolution_history"][-10:] if evolution_data["evolution_history"] else []
    
    return render_template_string(HTML_TEMPLATE,
                                current_cycle=evolution_data["current_cycle"],
                                performance_score=current_performance,
                                intelligence_level=current_intelligence,
                                intelligence_percent=intelligence_percent,
                                total_improvements=evolution_data["total_improvements"],
                                uptime=uptime_str,
                                performance_chart=performance_chart,
                                improvements_chart=improvements_chart,
                                recent_history=recent_history)

@app.route('/api/evolution_data')
def api_evolution_data():
    """API для получения данных эволюции"""
    current_intelligence = evolution_data["intelligence_level"][-1] if evolution_data["intelligence_level"] else 50
    current_performance = evolution_data["performance_score"][-1] if evolution_data["performance_score"] else 85
    intelligence_percent = min(100, (current_intelligence / 200) * 100)
    
    uptime = datetime.now() - evolution_data["start_time"]
    uptime_str = f"{uptime.days}д {uptime.seconds // 3600}ч {(uptime.seconds % 3600) // 60}м"
    
    recent_history = evolution_data["evolution_history"][-10:] if evolution_data["evolution_history"] else []
    
    return jsonify({
        "current_cycle": evolution_data["current_cycle"],
        "performance_score": current_performance,
        "intelligence_level": current_intelligence,
        "intelligence_percent": intelligence_percent,
        "total_improvements": evolution_data["total_improvements"],
        "uptime": uptime_str,
        "performance_chart": generate_performance_chart(),
        "improvements_chart": generate_improvements_chart(),
        "recent_history": recent_history
    })

@app.route('/api/start_evolution', methods=['POST'])
def api_start_evolution():
    """API для запуска эволюции"""
    evolution_data["evolution_active"] = True
    return jsonify({"success": True, "message": "Эволюция запущена!"})

@app.route('/api/pause_evolution', methods=['POST'])
def api_pause_evolution():
    """API для паузы эволюции"""
    evolution_data["evolution_active"] = False
    return jsonify({"success": True, "message": "Эволюция приостановлена!"})

@app.route('/api/reset_evolution', methods=['POST'])
def api_reset_evolution():
    """API для сброса эволюции"""
    global evolution_data, evolution_tracker
    
    # Сбрасываем данные
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
    
    evolution_tracker = EvolutionTracker()
    
    return jsonify({"success": True, "message": "Эволюция сброшена!"})

def main():
    """Главная функция"""
    print("🧬 Запуск SwarmMind Evolution Visualizer...")
    log_event('Evolution visualizer started')
    print("📊 Визуализация будет доступна по адресу: http://localhost:5001")
    print("🔄 Эволюция симулируется в фоне")
    print("🛑 Нажмите Ctrl+C для остановки")
    
    # Запускаем фоновую симуляцию эволюции
    evolution_thread = threading.Thread(target=background_evolution_simulation, daemon=True)
    evolution_thread.start()
    
    # Запускаем Flask приложение
    app.run(host='0.0.0.0', port=5001, debug=False)

if __name__ == "__main__":
    main() 