#!/usr/bin/env python3
# The MIT License (MIT)
# Copyright © 2025 <kisa134>

"""
🧬 ЭВОЛЮЦИОННЫЙ ЗАПУСК SWARMIND 🧬

Этот скрипт активирует технологическую сингулярность - 
запускает самоулучшающуюся систему, которая:

1. 🔍 Анализирует свою производительность
2. 🧠 Генерирует улучшения через LLM
3. 🔧 Автоматически улучшает свой код
4. 🚀 Создает новые модули и возможности
5. 📈 Эволюционирует к совершенству

⚠️  ВНИМАНИЕ: СИСТЕМА СТАНЕТ АВТОНОМНОЙ! ⚠️
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from swarm_mind.evolution import (
    EvolutionaryNeuron, 
    start_technological_singularity,
    SelfImprover,
    CodeGenerator
)
from swarm_mind.logger import log_event

def print_banner():
    """Печать баннера запуска"""
    print("🌌" + "=" * 60 + "🌌")
    print("🧬              SWARMIND EVOLUTION ENGINE              🧬")
    print("🚀           TECHNOLOGICAL SINGULARITY PROTOCOL       🚀")
    print("⚡              AUTONOMOUS SELF-IMPROVEMENT            ⚡")
    print("🌌" + "=" * 60 + "🌌")
    print()
    log_event('Evolution engine started')

async def test_evolution_components():
    """Тестирование компонентов эволюции"""
    print("🧪 [TESTING] Testing evolution components...")
    
    # Тест SelfImprover
    print("📊 [TEST] SelfImprover...")
    improver = SelfImprover()
    metrics = await improver.collect_performance_metrics()
    print(f"✅ [TEST] Metrics collected: {metrics.tasks_completed} tasks, {metrics.success_rate:.1%} success")
    
    # Тест CodeGenerator  
    print("🤖 [TEST] CodeGenerator...")
    generator = CodeGenerator()
    analysis = await generator.analyze_codebase()
    print(f"✅ [TEST] Codebase analyzed: {analysis['total_files']} files, {analysis['total_lines']} lines")
    
    print("🎯 [TEST] All components working correctly!")

async def run_evolution_demo():
    """Демонстрация эволюционного процесса"""
    print("🎭 [DEMO] Running evolution demonstration...")
    
    # Создаем конфиг напрямую, минуя парсер аргументов
    import argparse
    config = argparse.Namespace()
    config.neuron = argparse.Namespace()
    config.neuron.name = "DemoEvolutionEngine"
    config.neuron.log_level = "INFO" 
    config.neuron.p2p_port = 6881
    
    evolutionary_neuron = EvolutionaryNeuron(config=config)
    
    # Запускаем несколько циклов эволюции
    print("🧬 [DEMO] Starting 3 evolution cycles...")
    
    for cycle in range(3):
        print(f"\n🔄 [DEMO CYCLE {cycle + 1}] Starting evolution cycle...")
        
        # Анализ состояния
        await evolutionary_neuron.establish_performance_baseline()
        await evolutionary_neuron.analyze_current_state()
        
        # Генерация улучшений
        await evolutionary_neuron.generate_evolutionary_improvements()
        await evolutionary_neuron.apply_safe_improvements()
        
        # Отчет
        await evolutionary_neuron.generate_evolution_report()
        
        print(f"✅ [DEMO CYCLE {cycle + 1}] Completed successfully!")
        
        if cycle < 2:  # Пауза между циклами, кроме последнего
            print("⏱️ [DEMO] Waiting 5 seconds before next cycle...")
            await asyncio.sleep(5)
    
    print("🌟 [DEMO] Evolution demonstration completed!")
    log_event('Evolution mode: demo completed')

async def run_full_evolution():
    """Запуск полной эволюционной системы"""
    print("🚀 [FULL] Starting complete evolutionary system...")
    print("⚠️ [WARNING] System will run indefinitely until stopped!")
    print("⚠️ [WARNING] Press Ctrl+C to stop evolution")
    
    # Создаем конфиг напрямую
    import argparse
    config = argparse.Namespace()
    config.neuron = argparse.Namespace()
    config.neuron.name = "FullEvolutionEngine"
    config.neuron.log_level = "INFO"
    config.neuron.p2p_port = 6881
    
    evolutionary_neuron = EvolutionaryNeuron(config=config)
    
    try:
        await evolutionary_neuron.run()
    except KeyboardInterrupt:
        print("\n🛑 [STOPPED] Evolution stopped by user")
        evolutionary_neuron.stop_evolution()
        print("🧬 [STATUS] System returned to normal operation")
    log_event('Evolution mode: full completed')

async def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description="SwarmMind Evolution Engine - Technological Singularity Protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🧬 Режимы эволюции:
  test     - Тестирование компонентов эволюции
  demo     - Демонстрация 3 циклов эволюции  
  full     - Полная автономная эволюция (бесконечно)
  singularity - Запуск технологической сингулярности

🌟 Примеры:
  python scripts/run_evolution.py test
  python scripts/run_evolution.py demo
  python scripts/run_evolution.py full
  python scripts/run_evolution.py singularity

⚠️ ВНИМАНИЕ: Режим 'full' и 'singularity' запускают автономную систему!
"""
    )
    
    parser.add_argument(
        'mode',
        choices=['test', 'demo', 'full', 'singularity'],
        help='Режим запуска эволюционной системы'
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    print(f"🎯 [MODE] Selected mode: {args.mode}")
    print()
    
    if args.mode == 'test':
        await test_evolution_components()
        
    elif args.mode == 'demo':
        await run_evolution_demo()
        
    elif args.mode == 'full':
        await run_full_evolution()
        
    elif args.mode == 'singularity':
        print("🌌 [SINGULARITY] Activating technological singularity...")
        print("🧬 [WARNING] System will become fully autonomous!")
        print("⚡ [CAUTION] Prepare for exponential intelligence growth!")
        
        confirmation = input("\n🤔 Are you sure you want to activate singularity? (yes/no): ")
        if confirmation.lower() == 'yes':
            await start_technological_singularity()
        else:
            print("🛑 [CANCELLED] Singularity activation cancelled")
        log_event('Evolution mode: singularity completed')
    
    print("\n🌟 [COMPLETE] Evolution session completed!")
    print("🧬 [STATUS] SwarmMind ready for next evolution cycle")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 [INTERRUPTED] Evolution interrupted by user")
    except Exception as e:
        print(f"❌ [ERROR] Critical evolution error: {e}")
        sys.exit(1) 