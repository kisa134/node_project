import asyncio
import sys
import os
import argparse

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Импортируем базовые классы.
# Мы будем создавать конкретные реализации ниже.
from swarm_mind.miners.base_miner import BaseMiner
from swarm_mind.validators.base_validator import BaseValidator
from swarm_mind.validators.llm_validator import LLMValidator

# --- Пример конкретного Майнера ---
class DemoMiner(BaseMiner):
    def forward(self, query: dict) -> dict:
        # Простая логика: майнер получает число и возвращает его в квадрате.
        number = query.get("number", 0)
        return {"result": number ** 2}

# --- Пример конкретного Валидатора ---
class DemoValidator(BaseValidator):
    async def query_network(self):
        # В реальности здесь будет P2P-запрос к майнерам.
        # Сейчас мы просто симулируем вызов.
        print(f"[{self.config.neuron.name}] Querying miners with a sample task...")
        demo_miner = DemoMiner() # Симулируем наличие майнера
        query = {"number": 5}
        response = demo_miner.forward(query)
        print(f"[{self.config.neuron.name}] Received response: {response}")
        return [response] # Возвращаем список ответов

    async def score_responses(self, responses: list):
        # Простая логика оценки: проверяем, что результат равен 25.
        for response in responses:
            if response.get("result") == 25:
                print(f"[{self.config.neuron.name}] Scoring response: Correct! (Score: 1.0)")
            else:
                print(f"[{self.config.neuron.name}] Scoring response: Incorrect! (Score: 0.0)")

def run(neuron_type: str, remaining_argv: list):
    """
    Основная функция запуска нейрона на основе типа.
    """
    if neuron_type == 'miner':
        print("Starting SwarmMind Miner...")
        neuron = DemoMiner()
    elif neuron_type == 'validator':
        print("Starting SwarmMind Validator...")
        neuron = DemoValidator()
    elif neuron_type == 'llm_validator':
        print("Starting SwarmMind LLM Validator (Prometheus)...")
        neuron = LLMValidator()
    else:
        print(f"Error: Unknown neuron type '{neuron_type}'. Use 'miner', 'validator', or 'llm_validator'.")
        return

    try:
        asyncio.run(neuron.run())
    except KeyboardInterrupt:
        print("\nNeuron stopped by user.")
    finally:
        neuron.stop()
        print("Shutdown complete.")

def main():
    """
    Главная точка входа для запуска нейронов.
    Парсит аргумент --type, чтобы определить, какой нейрон запустить,
    а затем инициализирует его.
    """
    # Создаем временный парсер только для определения --type
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--type', type=str, required=True, help="Type of neuron to run (e.g., 'miner', 'llm_validator')")
    
    # Парсим только известные аргументы, чтобы получить --type
    args, remaining_argv = parser.parse_known_args()
    
    # Заменяем sys.argv на "чистые" аргументы без --type
    # Это нужно, чтобы нейроны не видели аргумент --type в своих парсерах
    original_argv = sys.argv[:]
    sys.argv = [sys.argv[0]] + remaining_argv
    
    try:
        # Передаем оставшиеся аргументы в основную функцию запуска
        run(args.type, remaining_argv)
    finally:
        # Восстанавливаем оригинальные аргументы (на всякий случай)
        sys.argv = original_argv

if __name__ == "__main__":
    # sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    main() 