#!/usr/bin/env python3
"""
🚀 ЕДИНЫЙ ЗАПУСК SWARMIND С ОБЪЕДИНЕННЫМ ИНТЕРФЕЙСОМ 🚀

Запускает всю систему SwarmMind с единым интерфейсом:
1. Docker контейнеры с нейронами
2. Единый веб-интерфейс (мониторинг + эволюция + логи + инсайты + управление)
3. Эволюционная система
4. Фоновый мониторинг и логирование

Теперь всё в одном месте - удобно и наглядно!
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

class UnifiedSwarmMind:
    def __init__(self):
        self.processes = []
        self.running = True
        self.interface_port = 5000

    def print_banner(self):
        print("🌌" + "=" * 60 + "🌌")
        print("🚀        SWARMIND UNIFIED SYSTEM        🚀")
        print("🧬      SELF-EVOLVING AI NETWORK         🧬")
        print("⚡      TECHNOLOGICAL SINGULARITY        ⚡")
        print("🌐         UNIFIED INTERFACE             🌐")
        print("🌌" + "=" * 60 + "🌌")
        print()

    def check_prerequisites(self):
        """Проверка предварительных требований"""
        print("🔍 [CHECK] Проверка предварительных требований...")
        
        # Проверяем Docker
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ [CHECK] Docker доступен")
            else:
                print("❌ [CHECK] Docker не найден")
                return False
        except Exception as e:
            print(f"❌ [CHECK] Ошибка проверки Docker: {e}")
            return False

        # Проверяем Docker Compose
        try:
            result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ [CHECK] Docker Compose доступен")
            else:
                print("❌ [CHECK] Docker Compose не найден")
                return False
        except Exception as e:
            print(f"❌ [CHECK] Ошибка проверки Docker Compose: {e}")
            return False

        # Проверяем Python зависимости
        try:
            import flask
            import psutil
            import matplotlib
            import numpy
            print("✅ [CHECK] Python зависимости установлены")
        except ImportError as e:
            print(f"❌ [CHECK] Отсутствуют Python зависимости: {e}")
            return False

        print("✅ [CHECK] Все предварительные требования выполнены!")
        return True

    def start_docker_containers(self):
        """Запуск Docker контейнеров"""
        print("🐳 [DOCKER] Запуск SwarmMind контейнеров...")
        
        try:
            # Останавливаем существующие контейнеры
            subprocess.run(['docker-compose', 'down'], capture_output=True, timeout=30)
            time.sleep(2)
            
            # Запускаем новые контейнеры с увеличенным таймаутом
            result = subprocess.run(
                ['docker-compose', 'up', '-d'], 
                capture_output=True, 
                text=True, 
                timeout=120  # Увеличенный таймаут
            )
            
            if result.returncode == 0:
                print("✅ [DOCKER] Контейнеры успешно запущены")
                return True
            else:
                print(f"❌ [DOCKER] Ошибка запуска контейнеров: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ [DOCKER] Таймаут запуска контейнеров")
            return False
        except Exception as e:
            print(f"❌ [DOCKER] Ошибка запуска контейнеров: {e}")
            return False

    def start_unified_interface(self):
        """Запуск единого интерфейса"""
        print("🌐 [INTERFACE] Запуск единого интерфейса...")
        
        try:
            # Запускаем единый интерфейс
            process = subprocess.Popen(
                [sys.executable, 'unified_interface.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes.append(process)
            print("✅ [INTERFACE] Единый интерфейс запущен")
            return True
            
        except Exception as e:
            print(f"❌ [INTERFACE] Ошибка запуска интерфейса: {e}")
            return False

    def start_evolution_system(self):
        """Запуск эволюционной системы"""
        print("🧬 [EVOLUTION] Запуск эволюционной системы...")
        
        try:
            # Запускаем эволюционную систему в фоне
            process = subprocess.Popen(
                [sys.executable, 'scripts/run_evolution.py', 'demo'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes.append(process)
            print("✅ [EVOLUTION] Эволюционная система запущена")
            return True
            
        except Exception as e:
            print(f"❌ [EVOLUTION] Ошибка запуска эволюции: {e}")
            return False

    def open_browser(self):
        """Открытие браузера с интерфейсом"""
        print("🌐 [BROWSER] Открытие интерфейса в браузере...")
        
        try:
            time.sleep(3)  # Ждем запуска интерфейса
            webbrowser.open(f'http://localhost:{self.interface_port}')
            print("✅ [BROWSER] Браузер открыт")
        except Exception as e:
            print(f"❌ [BROWSER] Ошибка открытия браузера: {e}")

    def start_monitoring(self):
        """Фоновый мониторинг системы"""
        print("📊 [MONITORING] Запуск фонового мониторинга...")
        
        def monitoring_loop():
            while self.running:
                try:
                    # Проверяем статус процессов
                    for i, process in enumerate(self.processes):
                        if process.poll() is not None:
                            print(f"⚠️ [MONITORING] Процесс {i} завершился")
                    
                    time.sleep(10)
                except Exception as e:
                    print(f"❌ [MONITORING] Ошибка мониторинга: {e}")
                    time.sleep(30)
        
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
        print("✅ [MONITORING] Мониторинг запущен")

    def signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        print("\n🛑 [SHUTDOWN] Получен сигнал остановки...")
        self.running = False
        self.shutdown()

    def shutdown(self):
        """Остановка всех процессов"""
        print("🛑 [SHUTDOWN] Остановка системы...")
        
        # Останавливаем процессы
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=10)
            except:
                process.kill()
        
        # Останавливаем Docker контейнеры
        try:
            subprocess.run(['docker-compose', 'down'], capture_output=True, timeout=30)
            print("✅ [SHUTDOWN] Docker контейнеры остановлены")
        except Exception as e:
            print(f"❌ [SHUTDOWN] Ошибка остановки Docker: {e}")
        
        print("✅ [SHUTDOWN] Система остановлена")

    def run(self):
        """Главный метод запуска"""
        self.print_banner()
        
        # Проверяем предварительные требования
        if not self.check_prerequisites():
            print("❌ [ERROR] Предварительные требования не выполнены!")
            return False
        
        print("🚀 [START] Запуск единой SwarmMind системы...")
        
        # Запускаем Docker контейнеры
        if not self.start_docker_containers():
            print("❌ [ERROR] Не удалось запустить Docker контейнеры!")
            print("💡 [TIP] Попробуйте запустить Docker Desktop или проверить права доступа")
            return False
        
        # Запускаем единый интерфейс
        if not self.start_unified_interface():
            print("❌ [ERROR] Не удалось запустить единый интерфейс!")
            return False
        
        # Запускаем эволюционную систему
        if not self.start_evolution_system():
            print("⚠️ [WARNING] Не удалось запустить эволюционную систему")
            print("💡 [TIP] Система будет работать без эволюции")
        
        # Запускаем мониторинг
        self.start_monitoring()
        
        # Открываем браузер
        self.open_browser()
        
        print("\n🌟 [SUCCESS] SwarmMind система запущена!")
        print(f"🌐 [ACCESS] Единый интерфейс: http://localhost:{self.interface_port}")
        print("📊 [FEATURES] Доступные функции:")
        print("   • Мониторинг системы (CPU, память, Docker)")
        print("   • Визуализация эволюции (графики)")
        print("   • Просмотр логов событий")
        print("   • AI-инсайты и анализ")
        print("   • Управление системой (запуск/остановка)")
        print("\n🔄 [INFO] Система работает автономно")
        print("🛑 [INFO] Для остановки нажмите Ctrl+C")
        
        # Настраиваем обработчик сигналов
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Ждем завершения
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 [INTERRUPT] Получен сигнал прерывания")
            self.shutdown()

def main():
    """Главная функция"""
    try:
        system = UnifiedSwarmMind()
        system.run()
    except Exception as e:
        print(f"❌ [FATAL] Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 