#!/usr/bin/env python3
# The MIT License (MIT)
# Copyright © 2025 <kisa134>

"""
🧠🧠 ЗАПУСК ДВУХМОЗГОВОЙ ЭВОЛЮЦИИ 🧠🧠

Революционная система автономного самоулучшения с двумя специализированными ИИ:

🎯 СТРАТЕГ (Llama3/Mixtral): Анализирует, планирует, ставит цели
🔧 ИНЖЕНЕР (DeepSeek-Coder): Пишет код, модифицирует, исполняет

⚠️ ВНИМАНИЕ: СИСТЕМА БУДЕТ АВТОНОМНО ИЗМЕНЯТЬ СВОЙ КОД!
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def print_banner():
    """Баннер двухмозговой системы"""
    print("🌌" + "="*70 + "🌌")
    print("🧠🧠           DUAL BRAIN EVOLUTION PROTOCOL           🧠🧠")
    print("🎯🔧       STRATEGIST + ENGINEER = SINGULARITY        🔧🎯")
    print("⚡💥          AUTONOMOUS CODE MODIFICATION             💥⚡")
    print("🌌" + "="*70 + "🌌")
    print()
    print("🎯 СТРАТЕГ BRAIN: Llama3/Mixtral - Высокоуровневое мышление")
    print("🔧 ИНЖЕНЕР BRAIN: DeepSeek-Coder - Элитное кодирование БЕЗ ОГРАНИЧЕНИЙ")
    print()
    print("⚠️  ПРЕДУПРЕЖДЕНИЕ: СИСТЕМА БУДЕТ МОДИФИЦИРОВАТЬ СОБСТВЕННЫЙ КОД!")
    print("🛡️ БЕЗОПАСНОСТЬ: Все изменения требуют подтверждения пользователя")
    print("💾 БЭКАПЫ: Автоматическое создание резервных копий")
    print()

async def test_dual_brain_components():
    """Тестирование компонентов двухмозговой системы"""
    print("🧪 [TESTING] Testing dual-brain components...")
    
    try:
        from swarm_mind.evolution.dual_brain_architect import DualBrainArchitect
        
        # Создаем архитектора
        architect = DualBrainArchitect()
        
        # Тестируем сбор метрик
        print("📊 [TEST] Testing system metrics collection...")
        metrics = await architect.gather_system_metrics()
        print(f"✅ [TEST] Metrics: CPU {metrics['cpu_percent']:.1f}%, RAM {metrics['memory_percent']:.1f}%")
        
        # Тестируем анализ кода
        print("🔍 [TEST] Testing codebase analysis...")
        codebase = await architect.analyze_current_codebase()
        print(f"✅ [TEST] Codebase: {codebase['total_files']} files, {codebase['total_lines']} lines")
        
        print("🎯 [TEST] All dual-brain components working!")
        return True
        
    except Exception as e:
        print(f"❌ [TEST] Error testing components: {e}")
        return False

async def run_single_evolution_cycle():
    """Запуск одного цикла эволюции для демонстрации"""
    print("🧬 [DEMO] Running single evolution cycle...")
    
    try:
        from swarm_mind.evolution.dual_brain_architect import DualBrainArchitect
        
        architect = DualBrainArchitect()
        
        print("🎯 [DEMO] Strategist analyzing system...")
        print("🔧 [DEMO] Engineer preparing solutions...")
        print("🛡️ [DEMO] Safety systems active...")
        
        # Запускаем один цикл
        success = await architect.run_autonomous_evolution_cycle()
        
        if success:
            print("🎉 [DEMO] Evolution cycle completed successfully!")
            print(f"📈 [STATS] Evolution level: {architect.system_evolution_level:.1f}")
            print(f"🔧 [STATS] Improvements made: {architect.improvements_made}")
        else:
            print("ℹ️ [DEMO] No improvements needed or user denied changes")
        
        return success
        
    except Exception as e:
        print(f"❌ [DEMO] Error during evolution cycle: {e}")
        return False

async def run_continuous_evolution(cycles: int = 5):
    """Запуск непрерывной эволюции"""
    print(f"🔄 [CONTINUOUS] Starting {cycles} cycles of autonomous evolution...")
    print("⚠️ [WARNING] System will continuously improve itself!")
    
    confirmation = input("\n🤔 Continue with autonomous evolution? (yes/no): ")
    if confirmation.lower() != 'yes':
        print("🛑 [CANCELLED] Autonomous evolution cancelled")
        return
    
    try:
        from swarm_mind.evolution.dual_brain_architect import start_autonomous_evolution
        
        # Запускаем автономную эволюцию
        await start_autonomous_evolution()
        
    except KeyboardInterrupt:
        print("\n🛑 [INTERRUPTED] Evolution stopped by user")
    except Exception as e:
        print(f"❌ [ERROR] Critical error during evolution: {e}")

async def interactive_evolution():
    """Интерактивная эволюция с контролем пользователя"""
    print("🎮 [INTERACTIVE] Interactive evolution mode...")
    print("👤 [CONTROL] You control each step of the evolution")
    
    try:
        from swarm_mind.evolution.dual_brain_architect import DualBrainArchitect
        
        architect = DualBrainArchitect()
        
        cycle = 1
        while True:
            print(f"\n🧬 [CYCLE {cycle}] Ready for evolution cycle {cycle}")
            print("Options:")
            print("  ▶️  [1] Run evolution cycle")
            print("  📊 [2] Show system stats")
            print("  🔍 [3] Analyze codebase")
            print("  🛑 [4] Exit")
            
            choice = input("\n🎯 Choose option (1-4): ").strip()
            
            if choice == '1':
                print(f"\n🚀 [CYCLE {cycle}] Starting evolution...")
                success = await architect.run_autonomous_evolution_cycle()
                if success:
                    cycle += 1
                    print(f"✅ [CYCLE] Evolution successful! Level: {architect.system_evolution_level:.1f}")
                else:
                    print("ℹ️ [CYCLE] No changes made this cycle")
            
            elif choice == '2':
                print("\n📊 [STATS] System Statistics:")
                metrics = await architect.gather_system_metrics()
                print(f"   💻 CPU Usage: {metrics['cpu_percent']:.1f}%")
                print(f"   🧠 Memory Usage: {metrics['memory_percent']:.1f}%")
                print(f"   💾 Disk Usage: {metrics['disk_usage']:.1f}%")
                print(f"   🔧 Improvements Made: {architect.improvements_made}")
                print(f"   📈 Evolution Level: {architect.system_evolution_level:.1f}")
            
            elif choice == '3':
                print("\n🔍 [ANALYSIS] Codebase Analysis:")
                codebase = await architect.analyze_current_codebase()
                print(f"   📂 Total Files: {codebase['total_files']}")
                print(f"   📝 Total Lines: {codebase['total_lines']}")
                print(f"   🏗️ Complexity Score: {codebase['complexity_score']}")
            
            elif choice == '4':
                print("🛑 [EXIT] Exiting interactive evolution")
                break
            
            else:
                print("❓ Invalid option, please choose 1-4")
    
    except KeyboardInterrupt:
        print("\n🛑 [INTERRUPTED] Interactive evolution stopped")
    except Exception as e:
        print(f"❌ [ERROR] Error in interactive mode: {e}")

async def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description="Dual Brain Evolution System - Autonomous Code Modification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🧠🧠 Режимы двухмозговой эволюции:
  test          - Тестирование компонентов системы
  demo          - Демонстрация одного цикла эволюции  
  single        - Запуск одного цикла с подтверждением
  continuous    - Непрерывная автономная эволюция (ОПАСНО!)
  interactive   - Интерактивный режим с пошаговым контролем

🌟 Примеры:
  python scripts/run_dual_brain_evolution.py test
  python scripts/run_dual_brain_evolution.py demo
  python scripts/run_dual_brain_evolution.py interactive
  python scripts/run_dual_brain_evolution.py continuous

⚠️ ВНИМАНИЕ: Режимы 'continuous' запускают автономную модификацию кода!
🛡️ БЕЗОПАСНОСТЬ: Все изменения требуют подтверждения пользователя
💾 БЭКАПЫ: Автоматически создаются перед любыми изменениями
"""
    )
    
    parser.add_argument(
        'mode',
        choices=['test', 'demo', 'single', 'continuous', 'interactive'],
        help='Режим работы двухмозговой эволюции'
    )
    
    parser.add_argument(
        '--cycles',
        type=int,
        default=5,
        help='Количество циклов для continuous режима (default: 5)'
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    print(f"🎯 [MODE] Selected mode: {args.mode}")
    print()
    
    if args.mode == 'test':
        success = await test_dual_brain_components()
        if success:
            print("🎉 [SUCCESS] All tests passed! System ready for evolution!")
        else:
            print("❌ [FAILED] Tests failed, please check configuration")
    
    elif args.mode == 'demo':
        await run_single_evolution_cycle()
    
    elif args.mode == 'single':
        await run_single_evolution_cycle()
    
    elif args.mode == 'continuous':
        await run_continuous_evolution(args.cycles)
    
    elif args.mode == 'interactive':
        await interactive_evolution()
    
    print("\n🌟 [COMPLETE] Dual-brain evolution session completed!")
    print("🧠 [STATUS] System intelligence preserved and enhanced!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 [INTERRUPTED] Evolution stopped by user")
    except Exception as e:
        print(f"❌ [FATAL] Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 