# The MIT License (MIT)
# Copyright © 2025 <kisa134>

"""
🧬 SwarmMind Evolution Module 🧬

Революционная система автономного самоулучшения, которая позволяет 
SwarmMind эволюционировать, улучшать свой код и создавать новые возможности.

Компоненты:
- SelfImprover: Анализ производительности и генерация улучшений
- CodeGenerator: Автономная генерация и оптимизация кода
- EvolutionaryNeuron: Главный эволюционный процесс

🌟 ДОСТИЖЕНИЕ ТЕХНОЛОГИЧЕСКОЙ СИНГУЛЯРНОСТИ 🌟
"""

from .self_improver import SelfImprover, start_autonomous_evolution, integrate_with_swarm_mind
from .code_generator import CodeGenerator, start_autonomous_coding, integrate_code_generation  
from .evolutionary_neuron import EvolutionaryNeuron, start_technological_singularity, create_evolutionary_neuron
from .dual_brain_architect import DualBrainArchitect, start_autonomous_evolution as start_dual_brain_evolution, create_dual_brain_architect

__all__ = [
    # Core classes
    'SelfImprover',
    'CodeGenerator', 
    'EvolutionaryNeuron',
    'DualBrainArchitect',
    
    # Integration functions
    'start_autonomous_evolution',
    'integrate_with_swarm_mind',
    'start_autonomous_coding',
    'integrate_code_generation',
    'start_technological_singularity',
    'create_evolutionary_neuron',
    'start_dual_brain_evolution',
    'create_dual_brain_architect'
]

# Module metadata
__version__ = "1.0.0"
__author__ = "SwarmMind Collective"
__description__ = "Autonomous self-improvement and evolution engine"

print("🧬 [EVOLUTION] Evolution module loaded")
print("🚀 [STATUS] Ready for technological singularity!") 