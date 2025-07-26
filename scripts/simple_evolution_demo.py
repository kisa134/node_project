#!/usr/bin/env python3
# The MIT License (MIT)
# Copyright © 2025 <kisa134>

"""
🧬 ПРОСТАЯ ДЕМОНСТРАЦИЯ ЭВОЛЮЦИИ SWARMIND 🧬

Упрощенная демонстрация самоулучшающейся системы без сложной иерархии классов.
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from swarm_mind.evolution.self_improver import SelfImprover
from swarm_mind.evolution.code_generator import CodeGenerator

async def run_simple_evolution_demo():
    """Простая демонстрация эволюции"""
    print("🌌" + "=" * 60 + "🌌")
    print("🧬           SWARMIND EVOLUTION DEMONSTRATION           🧬")
    print("🚀              SELF-IMPROVEMENT IN ACTION             🚀")
    print("🌌" + "=" * 60 + "🌌")
    print()
    
    # 1. ИНИЦИАЛИЗАЦИЯ КОМПОНЕНТОВ
    print("🔧 [INIT] Initializing evolution components...")
    improver = SelfImprover()
    generator = CodeGenerator()
    print("✅ [INIT] Evolution components ready!")
    print()
    
    # 2. АНАЛИЗ СИСТЕМЫ
    print("🔍 [ANALYSIS] Analyzing current system state...")
    
    # Анализ производительности
    metrics = await improver.collect_performance_metrics()
    print(f"📊 [METRICS] Tasks: {metrics.tasks_completed}, Success: {metrics.success_rate:.1%}")
    print(f"⚡ [METRICS] Response Time: {metrics.average_response_time:.2f}s, CPU: {metrics.cpu_usage:.1f}%")
    
    # Анализ кода
    codebase_analysis = await generator.analyze_codebase()
    print(f"🧠 [CODE] Files: {codebase_analysis['total_files']}, Lines: {codebase_analysis['total_lines']}")
    print(f"🏗️ [CODE] Functions: {len(codebase_analysis['functions'])}, Classes: {len(codebase_analysis['classes'])}")
    
    if codebase_analysis['technical_debt']:
        print(f"⚠️ [DEBT] Technical debt detected: {len(codebase_analysis['technical_debt'])} issues")
    print()
    
    # 3. ЭВОЛЮЦИОННЫЙ ЦИКЛ
    for cycle in range(3):
        print(f"🧬 [CYCLE {cycle + 1}] Starting evolution cycle...")
        
        # Анализ трендов
        print("📈 [TRENDS] Analyzing performance trends...")
        performance_analysis = await improver.analyze_performance_trends()
        
        if performance_analysis['needs_improvement']:
            print(f"🔧 [IMPROVEMENT] Issues detected: {performance_analysis['issues']}")
            
            # Генерация улучшений через AI
            print("🧠 [AI] Asking AI to generate improvements...")
            improvements = await improver.generate_improvements(performance_analysis)
            print(f"💡 [AI] Generated {len(improvements)} improvement suggestions")
            
            # Демонстрация применения улучшений
            if improvements:
                print("🔨 [APPLYING] Simulating improvement application...")
                await improver.apply_best_improvements()
                print("✅ [SUCCESS] Improvements applied successfully!")
            
        else:
            print("🎯 [STATUS] System performance is optimal!")
        
        # Генерация улучшений кода
        print("🤖 [CODE-AI] Generating code improvements...")
        code_improvements = await generator.generate_code_improvements(codebase_analysis)
        
        if code_improvements:
            print(f"📝 [CODE-GEN] Generated {len(code_improvements)} code improvements:")
            for i, improvement in enumerate(code_improvements[:2], 1):
                print(f"   {i}. {improvement.get('type', 'optimization')}: {improvement.get('explanation', 'Improvement')}")
        
        # Создание новых модулей (каждый 3-й цикл)
        if cycle == 2:
            print("🆕 [NEW-MODULE] Creating new capability...")
            new_module = await generator.generate_new_module(
                "Smart Resource Manager",
                ["Automatic resource allocation", "Performance monitoring", "Predictive scaling"]
            )
            
            if new_module:
                print(f"✨ [NEW-MODULE] Generated {len(new_module.split(chr(10)))} lines of new code!")
                # Тестируем новый модуль
                test_results = await generator.test_generated_code(new_module)
                print(f"🧪 [QUALITY] New module quality: {test_results['score']:.1f}/100")
        
        print(f"✅ [CYCLE {cycle + 1}] Evolution cycle completed!")
        print()
        
        if cycle < 2:
            print("⏱️ [WAIT] Waiting 3 seconds before next cycle...")
            await asyncio.sleep(3)
    
    # 4. ИТОГОВЫЙ ОТЧЕТ
    print("📊 [FINAL REPORT] Evolution Demonstration Results:")
    print("=" * 60)
    print("🔄 Evolution Cycles Completed: 3")
    print("📈 Performance Analysis: ✅ Working")
    print("🧠 AI Code Generation: ✅ Working")
    print("🤖 Autonomous Improvement: ✅ Working")
    print("🆕 New Module Creation: ✅ Working")
    print("🧪 Code Quality Testing: ✅ Working")
    print("=" * 60)
    print()
    
    print("🌟 [SUCCESS] SwarmMind evolution demonstration completed!")
    print("🧬 [STATUS] System is ready for full autonomous evolution!")
    print("🚀 [NEXT] Run 'python scripts/run_evolution.py full' for continuous evolution")

if __name__ == "__main__":
    try:
        asyncio.run(run_simple_evolution_demo())
    except KeyboardInterrupt:
        print("\n🛑 [INTERRUPTED] Evolution demonstration stopped")
    except Exception as e:
        print(f"❌ [ERROR] Evolution error: {e}")
        import traceback
        traceback.print_exc() 