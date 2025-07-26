#!/usr/bin/env python3
# The MIT License (MIT)
# Copyright © 2025 <kisa134>

"""
🧪 ПОЛНЫЙ СИСТЕМНЫЙ ТЕСТ SWARMIND 🧪

Комплексная проверка всех компонентов системы перед запуском:
- Импорты и зависимости
- P2P соединения  
- LLM интеграция (Ollama)
- Эволюционные модули
- Docker окружение
"""

import asyncio
import sys
import subprocess
import requests
import time
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def print_header(title):
    """Красивый заголовок"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def test_result(test_name, success, details=""):
    """Форматирование результата теста"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    └─ {details}")
    return success

async def test_imports():
    """Тест импортов"""
    print_header("ПРОВЕРКА ИМПОРТОВ")
    
    all_passed = True
    
    # Базовые модули
    try:
        import swarm_mind
        test_result("SwarmMind core package", True)
    except Exception as e:
        test_result("SwarmMind core package", False, str(e))
        all_passed = False
    
    # P2P модули
    try:
        from swarm_mind.p2p import P2PManager
        test_result("P2P Manager", True)
    except Exception as e:
        test_result("P2P Manager", False, str(e))
        all_passed = False
    
    # Нейроны
    try:
        from swarm_mind.neuron import BaseNeuron
        from swarm_mind.miners.base_miner import BaseMiner
        from swarm_mind.validators.base_validator import BaseValidator
        test_result("Neuron classes", True)
    except Exception as e:
        test_result("Neuron classes", False, str(e))
        all_passed = False
    
    # Эволюционные модули
    try:
        from swarm_mind.evolution import SelfImprover, CodeGenerator, EvolutionaryNeuron
        test_result("Evolution modules", True)
    except Exception as e:
        test_result("Evolution modules", False, str(e))
        all_passed = False
    
    return all_passed

async def test_dependencies():
    """Тест зависимостей"""
    print_header("ПРОВЕРКА ЗАВИСИМОСТЕЙ")
    
    all_passed = True
    
    dependencies = [
        ("libtorrent", "import libtorrent"),
        ("requests", "import requests"),
        ("psutil", "import psutil"),
        ("astor", "import astor"),
        ("pydantic", "import pydantic"),
        ("transformers", "import transformers"),
        ("torch", "import torch"),
    ]
    
    for name, import_cmd in dependencies:
        try:
            exec(import_cmd)
            test_result(f"{name} library", True)
        except Exception as e:
            test_result(f"{name} library", False, str(e))
            all_passed = False
    
    return all_passed

async def test_ollama_connection():
    """Тест подключения к Ollama"""
    print_header("ПРОВЕРКА OLLAMA LLM")
    
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            version = response.json().get('version', 'unknown')
            test_result("Ollama server connection", True, f"Version: {version}")
            
            # Проверяем доступные модели
            models_response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if models_response.status_code == 200:
                models = models_response.json().get('models', [])
                model_count = len(models)
                test_result("Ollama models", model_count > 0, f"{model_count} models available")
                
                # Выводим список моделей
                if models:
                    print("    🤖 Available models:")
                    for model in models[:5]:  # Показываем первые 5
                        name = model.get('name', 'Unknown')
                        size = model.get('size', 0)
                        size_gb = size / (1024**3) if size else 0
                        print(f"       • {name} ({size_gb:.1f} GB)")
                
                return True
            else:
                test_result("Ollama models", False, "Cannot fetch model list")
                return False
        else:
            test_result("Ollama server connection", False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        test_result("Ollama server connection", False, str(e))
        return False

async def test_p2p_functionality():
    """Тест P2P функциональности"""
    print_header("ПРОВЕРКА P2P СИСТЕМЫ")
    
    try:
        from swarm_mind.p2p import P2PManager
        
        # Создаем P2P менеджер
        p2p = P2PManager(port=6882)  # Используем другой порт для теста
        
        # Проверяем создание сессии
        await p2p.start()
        test_result("P2P session creation", True)
        
        # Останавливаем
        p2p.stop()
        test_result("P2P session cleanup", True)
        
        return True
        
    except Exception as e:
        test_result("P2P functionality", False, str(e))
        return False

async def test_evolution_components():
    """Тест эволюционных компонентов"""
    print_header("ПРОВЕРКА ЭВОЛЮЦИОННОЙ СИСТЕМЫ")
    
    all_passed = True
    
    # Тест SelfImprover
    try:
        from swarm_mind.evolution import SelfImprover
        improver = SelfImprover()
        
        # Быстрый тест сбора метрик
        metrics = await improver.collect_performance_metrics()
        test_result("SelfImprover metrics collection", True, 
                   f"Success rate: {metrics.success_rate:.1%}")
        
    except Exception as e:
        test_result("SelfImprover", False, str(e))
        all_passed = False
    
    # Тест CodeGenerator
    try:
        from swarm_mind.evolution import CodeGenerator
        generator = CodeGenerator()
        
        # Быстрый тест анализа кода
        analysis = await generator.analyze_codebase("./swarm_mind")
        test_result("CodeGenerator analysis", True, 
                   f"{analysis['total_files']} files, {analysis['total_lines']} lines")
        
    except Exception as e:
        test_result("CodeGenerator", False, str(e))
        all_passed = False
    
    return all_passed

async def test_docker_environment():
    """Тест Docker окружения"""
    print_header("ПРОВЕРКА DOCKER ОКРУЖЕНИЯ")
    
    # Проверяем наличие Docker
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            test_result("Docker availability", True, version)
        else:
            test_result("Docker availability", False, "Docker not found")
            return False
    except Exception as e:
        test_result("Docker availability", False, str(e))
        return False
    
    # Проверяем docker-compose
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            test_result("Docker Compose availability", True, version)
        else:
            test_result("Docker Compose availability", False, "docker-compose not found")
            return False
    except Exception as e:
        test_result("Docker Compose availability", False, str(e))
        return False
    
    return True

async def test_complete_workflow():
    """Тест полного рабочего процесса"""
    print_header("ИНТЕГРАЦИОННЫЙ ТЕСТ")
    
    try:
        print("🧪 [INTEGRATION] Testing complete SwarmMind workflow...")
        
        # 1. Создаем базовый нейрон
        from swarm_mind.neuron import BaseNeuron
        import argparse
        
        config = argparse.Namespace()
        config.neuron = argparse.Namespace()
        config.neuron.name = "TestNeuron"
        config.neuron.log_level = "INFO"
        config.neuron.p2p_port = 6883
        
        # Простой тестовый нейрон
        class TestNeuron(BaseNeuron):
            async def main_loop_logic(self):
                await asyncio.sleep(0.1)
        
        neuron = TestNeuron(config=config)
        test_result("Neuron creation", True)
        
        # 2. Тестируем эволюционный компонент
        from swarm_mind.evolution import EvolutionaryNeuron
        evo_neuron = EvolutionaryNeuron(config=config)
        test_result("Evolutionary neuron creation", True)
        
        # 3. Проверяем интеграцию с Ollama (без длительных запросов)
        improver = evo_neuron.self_improver
        metrics = await improver.collect_performance_metrics()
        test_result("Metrics integration", metrics.success_rate > 0)
        
        return True
        
    except Exception as e:
        test_result("Complete workflow", False, str(e))
        return False

async def main():
    """Главная функция тестирования"""
    print("🌌" + "="*60 + "🌌")
    print("🧪                SWARMIND SYSTEM TEST                🧪")
    print("🚀             COMPREHENSIVE HEALTH CHECK             🚀")
    print("🌌" + "="*60 + "🌌")
    
    start_time = time.time()
    all_tests = []
    
    # Выполняем все тесты
    all_tests.append(await test_imports())
    all_tests.append(await test_dependencies())
    all_tests.append(await test_ollama_connection())
    all_tests.append(await test_p2p_functionality())
    all_tests.append(await test_evolution_components())
    all_tests.append(await test_docker_environment())
    all_tests.append(await test_complete_workflow())
    
    # Итоговый отчет
    print_header("ИТОГОВЫЙ ОТЧЕТ")
    
    passed = sum(all_tests)
    total = len(all_tests)
    success_rate = (passed / total) * 100
    
    duration = time.time() - start_time
    
    print(f"📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"   ✅ Пройдено: {passed}/{total} тестов")
    print(f"   📈 Успешность: {success_rate:.1f}%")
    print(f"   ⏱️ Время выполнения: {duration:.1f}s")
    
    if success_rate == 100:
        print(f"\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! СИСТЕМА ГОТОВА К ЗАПУСКУ! 🎉")
        print(f"🚀 Можно запускать: python scripts/simple_evolution_demo.py")
        print(f"🧬 Или полную эволюцию: python scripts/run_evolution.py demo")
        return True
    elif success_rate >= 80:
        print(f"\n⚠️ СИСТЕМА ЧАСТИЧНО ГОТОВА ({success_rate:.1f}%)")
        print(f"💡 Рекомендуется исправить проблемы перед запуском")
        return False
    else:
        print(f"\n❌ КРИТИЧЕСКИЕ ОШИБКИ! СИСТЕМА НЕ ГОТОВА!")
        print(f"🔧 Необходимо исправить ошибки перед запуском")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n🛑 [INTERRUPTED] Тестирование прервано")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ [FATAL] Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 