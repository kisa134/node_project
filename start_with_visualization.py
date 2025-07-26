#!/usr/bin/env python3
"""
🚀 ИНТЕГРИРОВАННЫЙ ЗАПУСК SWARMIND С ВИЗУАЛИЗАЦИЕЙ 🚀

Запускает всю систему SwarmMind с красивой визуализацией эволюции:
1. Docker контейнеры с нейронами
2. Веб-интерфейс мониторинга
3. Визуализатор эволюции
4. Эволюционная система
5. Фоновый мониторинг

Теперь вы можете видеть, как именно растет и развивается система!
"""

import asyncio
import subprocess
import time
import threading
import signal
import sys
import os
import webbrowser
from pathlib import Path
from swarm_mind.logger import log_event

class SwarmMindWithVisualization:
    def __init__(self):
        self.processes = []
        self.running = True
        self.web_interface_port = 5000
        self.visualization_port = 5001
        
    def print_banner(self):
        """Печать баннера запуска"""
        print("🌌" + "="*60 + "🌌")
        print("🚀      SWARMIND WITH EVOLUTION VISUALIZATION      🚀")
        print("🧬         SEE HOW YOUR AI GROWS AND LEARNS        🧬")
        print("📊         REAL-TIME EVOLUTION TRACKING           📊")
        print("⚡         TECHNOLOGICAL SINGULARITY              ⚡")
        print("🌌" + "="*60 + "🌌")
        print()
        
    def check_prerequisites(self):
        """Проверка предварительных требований"""
        print("🔍 [CHECK] Проверка предварительных требований...")
        
        # Проверяем Docker
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ [CHECK] Docker доступен")
            else:
                print("❌ [CHECK] Docker не найден!")
                return False
        except Exception as e:
            print(f"❌ [CHECK] Ошибка проверки Docker: {e}")
            return False
            
        # Проверяем docker-compose
        try:
            result = subprocess.run(['docker-compose', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ [CHECK] Docker Compose доступен")
            else:
                print("❌ [CHECK] Docker Compose не найден!")
                return False
        except Exception as e:
            print(f"❌ [CHECK] Ошибка проверки Docker Compose: {e}")
            return False
            
        # Проверяем Python зависимости
        try:
            import flask
            import psutil
            import requests
            import matplotlib
            import numpy
            print("✅ [CHECK] Python зависимости установлены")
        except ImportError as e:
            print(f"❌ [CHECK] Отсутствуют Python зависимости: {e}")
            print("💡 Установите: pip install -r requirements.txt")
            return False
            
        print("✅ [CHECK] Все предварительные требования выполнены!")
        return True
        
    def start_docker_containers(self):
        """Запуск Docker контейнеров"""
        print("🐳 [DOCKER] Запуск SwarmMind контейнеров...")
        
        try:
            # Останавливаем существующие контейнеры
            subprocess.run(['docker-compose', 'down'], 
                         capture_output=True, text=True, timeout=30)
            
            # Запускаем контейнеры в фоне
            process = subprocess.Popen(
                ['docker-compose', 'up', '--build', '-d'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Ждем завершения сборки
            stdout, stderr = process.communicate(timeout=180)  # Увеличиваем таймаут
            
            if process.returncode == 0:
                print("✅ [DOCKER] Контейнеры запущены успешно!")
                
                # Проверяем статус контейнеров
                time.sleep(5)
                result = subprocess.run(['docker-compose', 'ps'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print("📊 [DOCKER] Статус контейнеров:")
                    print(result.stdout)
                
                return True
            else:
                print(f"❌ [DOCKER] Ошибка запуска контейнеров: {stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ [DOCKER] Таймаут запуска контейнеров")
            return False
        except Exception as e:
            print(f"❌ [DOCKER] Ошибка: {e}")
            return False
            
    def start_web_interface(self):
        """Запуск веб-интерфейса"""
        print("🌐 [WEB] Запуск веб-интерфейса мониторинга...")
        
        try:
            process = subprocess.Popen(
                [sys.executable, 'web_interface.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Ждем немного для запуска
            time.sleep(3)
            
            if process.poll() is None:
                print(f"✅ [WEB] Веб-интерфейс запущен на http://localhost:{self.web_interface_port}")
                self.processes.append(('web_interface', process))
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ [WEB] Ошибка запуска веб-интерфейса: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ [WEB] Ошибка: {e}")
            return False
            
    def start_visualization(self):
        """Запуск визуализатора эволюции"""
        print("📊 [VISUAL] Запуск визуализатора эволюции...")
        
        try:
            process = subprocess.Popen(
                [sys.executable, 'evolution_visualizer.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Ждем немного для запуска
            time.sleep(3)
            
            if process.poll() is None:
                print(f"✅ [VISUAL] Визуализатор запущен на http://localhost:{self.visualization_port}")
                self.processes.append(('visualization', process))
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ [VISUAL] Ошибка запуска визуализатора: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ [VISUAL] Ошибка: {e}")
            return False
            
    def start_evolution_system(self):
        """Запуск эволюционной системы"""
        print("🧬 [EVOLUTION] Запуск эволюционной системы...")
        
        try:
            process = subprocess.Popen(
                [sys.executable, 'scripts/run_evolution.py', 'full'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Ждем немного для запуска
            time.sleep(2)
            
            if process.poll() is None:
                print("✅ [EVOLUTION] Эволюционная система запущена!")
                self.processes.append(('evolution', process))
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ [EVOLUTION] Ошибка запуска: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ [EVOLUTION] Ошибка: {e}")
            return False
            
    def open_browsers(self):
        """Автоматическое открытие браузеров"""
        print("🌐 [BROWSER] Открытие интерфейсов в браузере...")
        
        try:
            # Открываем визуализатор эволюции
            webbrowser.open(f'http://localhost:{self.visualization_port}')
            time.sleep(1)
            
            # Открываем веб-интерфейс мониторинга
            webbrowser.open(f'http://localhost:{self.web_interface_port}')
            
            print("✅ [BROWSER] Интерфейсы открыты в браузере!")
            
        except Exception as e:
            print(f"⚠️ [BROWSER] Не удалось открыть браузер автоматически: {e}")
            print("💡 Откройте вручную:")
            print(f"   Визуализатор: http://localhost:{self.visualization_port}")
            print(f"   Мониторинг: http://localhost:{self.web_interface_port}")
            
    def start_monitoring(self):
        """Запуск фонового мониторинга"""
        print("📊 [MONITOR] Запуск фонового мониторинга...")
        
        def monitoring_loop():
            while self.running:
                try:
                    # Проверяем статус контейнеров
                    result = subprocess.run(['docker-compose', 'ps'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        running_containers = result.stdout.count('running')
                        if running_containers > 0:
                            print(f"📊 [MONITOR] Активных контейнеров: {running_containers}")
                    
                    # Проверяем веб-интерфейс
                    import requests
                    try:
                        response = requests.get(f"http://localhost:{self.web_interface_port}/api/status", 
                                              timeout=5)
                        if response.status_code == 200:
                            print("✅ [MONITOR] Веб-интерфейс работает")
                    except:
                        print("⚠️ [MONITOR] Веб-интерфейс недоступен")
                        
                    # Проверяем визуализатор
                    try:
                        response = requests.get(f"http://localhost:{self.visualization_port}/api/evolution_data", 
                                              timeout=5)
                        if response.status_code == 200:
                            print("✅ [MONITOR] Визуализатор работает")
                    except:
                        print("⚠️ [MONITOR] Визуализатор недоступен")
                        
                except Exception as e:
                    print(f"⚠️ [MONITOR] Ошибка мониторинга: {e}")
                    
                time.sleep(30)  # Проверка каждые 30 секунд
                
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
        print("✅ [MONITOR] Мониторинг запущен!")
        
    def signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        print("\n🛑 [SHUTDOWN] Получен сигнал остановки...")
        self.shutdown()
        
    def shutdown(self):
        """Корректное завершение системы"""
        print("🔄 [SHUTDOWN] Остановка системы с визуализацией...")
        self.running = False
        
        # Останавливаем процессы
        for name, process in self.processes:
            print(f"🛑 [SHUTDOWN] Остановка {name}...")
            try:
                process.terminate()
                process.wait(timeout=10)
            except:
                process.kill()
                
        # Останавливаем Docker контейнеры
        print("🛑 [SHUTDOWN] Остановка Docker контейнеров...")
        try:
            subprocess.run(['docker-compose', 'down'], 
                         capture_output=True, text=True, timeout=30)
        except:
            pass
            
        print("✅ [SHUTDOWN] Система остановлена корректно!")
        
    def run(self):
        """Главный метод запуска"""
        self.print_banner()
        log_event('Integrated visualization mode started')
        
        # Проверяем предварительные требования
        if not self.check_prerequisites():
            print("❌ [ERROR] Предварительные требования не выполнены!")
            return False
            
        # Устанавливаем обработчик сигналов
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🚀 [START] Запуск SwarmMind с визуализацией...")
        
        # Запускаем компоненты
        if not self.start_docker_containers():
            print("❌ [ERROR] Не удалось запустить Docker контейнеры!")
            return False
            
        if not self.start_web_interface():
            print("❌ [ERROR] Не удалось запустить веб-интерфейс!")
            return False
            
        if not self.start_visualization():
            print("❌ [ERROR] Не удалось запустить визуализатор!")
            return False
            
        if not self.start_evolution_system():
            print("❌ [ERROR] Не удалось запустить эволюционную систему!")
            return False
            
        # Запускаем мониторинг
        self.start_monitoring()
        
        # Открываем браузеры
        time.sleep(5)  # Ждем запуска всех сервисов
        self.open_browsers()
        
        print("\n" + "="*60)
        print("🎉 [SUCCESS] SwarmMind с визуализацией запущен!")
        print("="*60)
        print(f"📊 Визуализатор эволюции: http://localhost:{self.visualization_port}")
        print(f"🌐 Веб-интерфейс мониторинга: http://localhost:{self.web_interface_port}")
        print("🐳 Docker контейнеры: docker-compose ps")
        print("🧬 Эволюция: работает в фоне")
        print("📊 Мониторинг: активен")
        print("🛑 Для остановки нажмите Ctrl+C")
        print("="*60)
        print()
        print("🌟 ЧТО ВЫ УВИДИТЕ:")
        print("   📈 Графики роста производительности и интеллекта")
        print("   🔧 Количество улучшений кода в реальном времени")
        print("   🧠 Уровень интеллекта системы")
        print("   📊 Использование системных ресурсов")
        print("   📝 Журнал эволюции с деталями каждого цикла")
        print("   🚀 Управление эволюцией (запуск/пауза/сброс)")
        print("="*60)
        
        # Основной цикл ожидания
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 [INTERRUPT] Получен сигнал прерывания...")
            self.shutdown()
            
        return True

def main():
    """Главная функция"""
    swarm_mind = SwarmMindWithVisualization()
    success = swarm_mind.run()
    
    if success:
        print("🌟 [COMPLETE] Система с визуализацией завершена успешно!")
        sys.exit(0)
    else:
        print("❌ [ERROR] Ошибка запуска системы с визуализацией!")
        sys.exit(1)

if __name__ == "__main__":
    main() 