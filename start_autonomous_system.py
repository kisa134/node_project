#!/usr/bin/env python3
"""
🚀 АВТОНОМНЫЙ ЗАПУСК SWARMIND 🚀

Этот скрипт запускает всю SwarmMind систему в автономном режиме:
1. Docker контейнеры с нейронами
2. Веб-интерфейс для мониторинга
3. Эволюционную систему
4. Фоновый мониторинг

Система будет работать автономно до остановки пользователем.
"""

import asyncio
import subprocess
import time
import threading
import signal
import sys
import os
from pathlib import Path

class AutonomousSwarmMind:
    def __init__(self):
        self.processes = []
        self.running = True
        self.web_interface_port = 5000
        
    def print_banner(self):
        """Печать баннера запуска"""
        print("🌌" + "="*60 + "🌌")
        print("🚀           SWARMIND AUTONOMOUS SYSTEM           🚀")
        print("🧬         SELF-EVOLVING AI NETWORK              🧬")
        print("⚡         TECHNOLOGICAL SINGULARITY             ⚡")
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
            stdout, stderr = process.communicate(timeout=120)
            
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
        print("🌐 [WEB] Запуск веб-интерфейса...")
        
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
        print("🔄 [SHUTDOWN] Остановка автономной системы...")
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
        
        # Проверяем предварительные требования
        if not self.check_prerequisites():
            print("❌ [ERROR] Предварительные требования не выполнены!")
            return False
            
        # Устанавливаем обработчик сигналов
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🚀 [START] Запуск автономной SwarmMind системы...")
        
        # Запускаем компоненты
        if not self.start_docker_containers():
            print("❌ [ERROR] Не удалось запустить Docker контейнеры!")
            return False
            
        if not self.start_web_interface():
            print("❌ [ERROR] Не удалось запустить веб-интерфейс!")
            return False
            
        if not self.start_evolution_system():
            print("❌ [ERROR] Не удалось запустить эволюционную систему!")
            return False
            
        # Запускаем мониторинг
        self.start_monitoring()
        
        print("\n" + "="*60)
        print("🎉 [SUCCESS] SwarmMind автономная система запущена!")
        print("="*60)
        print(f"🌐 Веб-интерфейс: http://localhost:{self.web_interface_port}")
        print("🐳 Docker контейнеры: docker-compose ps")
        print("🧬 Эволюция: работает в фоне")
        print("📊 Мониторинг: активен")
        print("🛑 Для остановки нажмите Ctrl+C")
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
    autonomous_system = AutonomousSwarmMind()
    success = autonomous_system.run()
    
    if success:
        print("🌟 [COMPLETE] Автономная система завершена успешно!")
        sys.exit(0)
    else:
        print("❌ [ERROR] Ошибка запуска автономной системы!")
        sys.exit(1)

if __name__ == "__main__":
    main() 