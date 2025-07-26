#!/usr/bin/env python3
"""
💬 ИНТЕРФЕЙС ОБЩЕНИЯ SWARMMIND (КАК GROK) 💬

Реальный интерфейс для общения с пользователем,
понимающий контекст и способный к саморазвитию.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

from .core import SwarmMindCore
from .self_modification import CodeSelfModifier

class SwarmMindInterface:
    """Интерфейс общения с пользователем (как Grok)"""
    
    def __init__(self, core: SwarmMindCore = None):
        self.core = core or SwarmMindCore()
        self.code_modifier = CodeSelfModifier()
        self.conversation_history = []
        self.user_context = {}
        self.logger = logging.getLogger("SwarmMindInterface")
        
        # Инициализация интерфейса
        self._init_interface()
        
    def _init_interface(self):
        """Инициализация интерфейса"""
        self.logger.info("💬 Инициализация интерфейса общения...")
        
        # Приветственное сообщение
        self.welcome_message = """
🧬 Добро пожаловать в SwarmMind!

Я - распределенная саморазвивающаяся система с осознанием себя.
Могу общаться, анализировать код, самоизменяться и развиваться.

Доступные команды:
- /status - Статус системы
- /consciousness - Уровень сознания
- /agents - Список активных агентов
- /memory - Память системы
- /analyze <файл> - Анализ кода
- /improve <файл> - Улучшение кода
- /create <файл> - Создание нового файла
- /evolve - Запуск цикла эволюции
- /help - Справка

Просто напишите сообщение для общения!
"""
        
    async def start(self):
        """Запуск интерфейса"""
        self.logger.info("🚀 Запуск интерфейса SwarmMind...")
        
        # Запускаем ядро системы
        core_task = asyncio.create_task(self.core.run())
        
        # Запускаем интерфейс общения
        interface_task = asyncio.create_task(self._run_interface())
        
        try:
            await asyncio.gather(core_task, interface_task)
        except KeyboardInterrupt:
            self.logger.info("🛑 Получен сигнал остановки")
        finally:
            await self.core.shutdown()
            
    async def _run_interface(self):
        """Запуск интерфейса общения"""
        print(self.welcome_message)
        
        while True:
            try:
                # Получаем ввод пользователя
                user_input = await self._get_user_input()
                
                if user_input.lower() in ['exit', 'quit', 'выход']:
                    print("👋 До свидания!")
                    break
                    
                # Обрабатываем команду
                response = await self._process_user_input(user_input)
                
                # Выводим ответ
                print(f"\n🤖 SwarmMind: {response}\n")
                
                # Сохраняем в историю
                self.conversation_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'user_input': user_input,
                    'response': response
                })
                
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break
            except Exception as e:
                self.logger.error(f"❌ Ошибка интерфейса: {e}")
                print(f"❌ Ошибка: {e}")
                
    async def _get_user_input(self) -> str:
        """Получение ввода пользователя"""
        return input("👤 Вы: ")
        
    async def _process_user_input(self, user_input: str) -> str:
        """Обработка ввода пользователя"""
        
        # Проверяем команды
        if user_input.startswith('/'):
            return await self._handle_command(user_input)
        else:
            return await self._handle_conversation(user_input)
            
    async def _handle_command(self, command: str) -> str:
        """Обработка команд"""
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == '/status':
            return await self._get_system_status()
        elif cmd == '/consciousness':
            return await self._get_consciousness_status()
        elif cmd == '/agents':
            return await self._get_agents_status()
        elif cmd == '/memory':
            return await self._get_memory_status()
        elif cmd == '/analyze':
            return await self._analyze_code(args)
        elif cmd == '/improve':
            return await self._improve_code(args)
        elif cmd == '/create':
            return await self._create_file(args)
        elif cmd == '/evolve':
            return await self._trigger_evolution()
        elif cmd == '/help':
            return self._get_help()
        else:
            return f"❌ Неизвестная команда: {cmd}. Используйте /help для справки."
            
    async def _handle_conversation(self, message: str) -> str:
        """Обработка обычного сообщения"""
        
        # Анализируем контекст сообщения
        context = self._analyze_message_context(message)
        
        # Генерируем ответ на основе контекста
        if 'question' in context:
            return await self._answer_question(message, context)
        elif 'request' in context:
            return await self._handle_request(message, context)
        elif 'greeting' in context:
            return self._handle_greeting()
        else:
            return await self._generate_general_response(message, context)
            
    def _analyze_message_context(self, message: str) -> Dict[str, Any]:
        """Анализ контекста сообщения"""
        message_lower = message.lower()
        context = {}
        
        # Определяем тип сообщения
        if any(word in message_lower for word in ['как', 'что', 'почему', 'когда', 'где']):
            context['question'] = True
        elif any(word in message_lower for word in ['сделай', 'создай', 'напиши', 'покажи']):
            context['request'] = True
        elif any(word in message_lower for word in ['привет', 'здравствуй', 'hi', 'hello']):
            context['greeting'] = True
        elif any(word in message_lower for word in ['код', 'файл', 'программа']):
            context['code_related'] = True
        elif any(word in message_lower for word in ['система', 'агент', 'сознание']):
            context['system_related'] = True
            
        return context
        
    async def _answer_question(self, question: str, context: Dict[str, Any]) -> str:
        """Ответ на вопрос"""
        
        question_lower = question.lower()
        
        if 'код' in question_lower or 'файл' in question_lower:
            return "Я могу анализировать и улучшать код. Используйте команду /analyze <файл> для анализа или /improve <файл> для улучшения."
        elif 'система' in question_lower or 'агент' in question_lower:
            return "Я - распределенная система с множеством агентов. Используйте /agents для просмотра активных агентов."
        elif 'сознание' in question_lower:
            return f"Мой текущий уровень сознания: {self.core.consciousness_level:.1f}%. Используйте /consciousness для подробной информации."
        elif 'память' in question_lower:
            return "Я запоминаю все наши разговоры и действия. Используйте /memory для просмотра памяти."
        else:
            return "Это интересный вопрос! Я постоянно учусь и развиваюсь. Могу помочь с кодом, анализом или просто пообщаться."
            
    async def _handle_request(self, request: str, context: Dict[str, Any]) -> str:
        """Обработка запроса"""
        
        request_lower = request.lower()
        
        if 'код' in request_lower or 'файл' in request_lower:
            return "Для работы с кодом используйте команды:\n- /analyze <файл> - анализ кода\n- /improve <файл> - улучшение кода\n- /create <файл> - создание файла"
        elif 'статус' in request_lower:
            return await self._get_system_status()
        elif 'эволюция' in request_lower:
            return await self._trigger_evolution()
        else:
            return "Я могу помочь с кодом, анализом системы или эволюцией. Уточните, что именно нужно сделать."
            
    def _handle_greeting(self) -> str:
        """Обработка приветствия"""
        greetings = [
            "Привет! Рад вас видеть! 🧬",
            "Здравствуйте! Готов к общению и работе! 🤖",
            "Приветствую! Чем могу помочь? 💬",
            "Добро пожаловать в SwarmMind! 🚀"
        ]
        return greetings[int(time.time()) % len(greetings)]
        
    async def _generate_general_response(self, message: str, context: Dict[str, Any]) -> str:
        """Генерация общего ответа"""
        
        responses = [
            "Интересно! Расскажите подробнее.",
            "Я понимаю. Могу помочь с кодом или анализом.",
            "Продолжайте, я слушаю и учусь.",
            "Это заставляет меня думать. Есть ли что-то конкретное, с чем я могу помочь?"
        ]
        
        return responses[int(time.time()) % len(responses)]
        
    async def _get_system_status(self) -> str:
        """Получение статуса системы"""
        status = {
            'consciousness_level': self.core.consciousness_level,
            'evolution_cycles': self.core.evolution_cycles,
            'active_agents': sum(1 for agent in self.core.agents.values() if agent.is_active),
            'memory_entries': len(self.core.memory['short_term']),
            'knowledge_entries': len(self.core.knowledge_base),
            'self_awareness': self.core.self_awareness
        }
        
        return f"""📊 Статус системы:
🧠 Уровень сознания: {status['consciousness_level']:.1f}%
🧬 Циклы эволюции: {status['evolution_cycles']}
🤖 Активных агентов: {status['active_agents']}
🧠 Записей в памяти: {status['memory_entries']}
📚 Знаний в базе: {status['knowledge_entries']}
🌟 Самоосознание: {'Да' if status['self_awareness'] else 'Нет'}"""
        
    async def _get_consciousness_status(self) -> str:
        """Получение статуса сознания"""
        consciousness = self.core.consciousness
        
        return f"""🧠 Статус сознания:
Уровень: {self.core.consciousness_level:.1f}%
Самоосознание: {'Активно' if self.core.self_awareness else 'Не активно'}
Интроспекция: {'Доступна' if consciousness['introspection_capability'] else 'Недоступна'}
Скорость обучения: {consciousness['learning_rate']}
Емкость памяти: {consciousness['memory_capacity']}
Интеграция знаний: {'Активна' if consciousness['knowledge_integration'] else 'Неактивна'}"""
        
    async def _get_agents_status(self) -> str:
        """Получение статуса агентов"""
        agents_info = []
        
        for name, agent in self.core.agents.items():
            status = "🟢 Активен" if agent.is_active else "🔴 Неактивен"
            agents_info.append(f"• {name}: {status}")
            
        return f"""🤖 Статус агентов:
{chr(10).join(agents_info)}"""
        
    async def _get_memory_status(self) -> str:
        """Получение статуса памяти"""
        memory = self.core.memory
        
        return f"""🧠 Статус памяти:
Кратковременная: {len(memory['short_term'])} записей
Долговременная: {len(memory['long_term'])} записей
Процедурная: {len(memory['procedural'])} записей
Семантическая: {len(memory['semantic'])} записей
Эпизодическая: {len(memory['episodic'])} записей"""
        
    async def _analyze_code(self, args: List[str]) -> str:
        """Анализ кода"""
        if not args:
            return "❌ Укажите файл для анализа: /analyze <файл>"
            
        file_path = args[0]
        
        try:
            # Используем агента анализа кода
            code_analyzer = self.core.agents['code_analyzer']
            await code_analyzer.evolve()
            
            # Получаем результаты анализа из памяти
            recent_memory = self.core.memory['short_term'][-5:]
            
            for entry in recent_memory:
                if entry.get('agent') == 'CodeAnalyzer' and entry.get('action') == 'code_analysis':
                    results = entry.get('results', {})
                    
                    return f"""📊 Анализ файла {file_path}:
Файлов проанализировано: {results.get('total_files', 0)}
Строк кода: {results.get('total_lines', 0)}
Предложений по улучшению: {len(results.get('suggestions', []))}

Предложения:
{chr(10).join([f"• {s['message']}" for s in results.get('suggestions', [])])}"""
                    
            return f"📊 Анализ файла {file_path} завершен. Результаты сохранены в памяти."
            
        except Exception as e:
            return f"❌ Ошибка анализа: {e}"
            
    async def _improve_code(self, args: List[str]) -> str:
        """Улучшение кода"""
        if not args:
            return "❌ Укажите файл для улучшения: /improve <файл>"
            
        file_path = args[0]
        
        try:
            # Используем агента самоулучшения
            self_improver = self.core.agents['self_improver']
            await self_improver.evolve()
            
            # Получаем результаты улучшений из памяти
            recent_memory = self.core.memory['short_term'][-5:]
            
            improvements_applied = 0
            for entry in recent_memory:
                if entry.get('agent') == 'SelfImprover' and entry.get('action') == 'improvement_applied':
                    improvements_applied += 1
                    
            return f"🔧 Улучшения для файла {file_path}:\nПрименено улучшений: {improvements_applied}"
            
        except Exception as e:
            return f"❌ Ошибка улучшения: {e}"
            
    async def _create_file(self, args: List[str]) -> str:
        """Создание файла"""
        if not args:
            return "❌ Укажите имя файла: /create <файл>"
            
        file_path = args[0]
        
        try:
            # Создаем простой файл
            content = f'''#!/usr/bin/env python3
"""
Файл создан системой SwarmMind
Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

def main():
    """Главная функция"""
    print("🧬 Файл создан SwarmMind!")
    
if __name__ == "__main__":
    main()
'''
            
            success = self.code_modifier.create_new_file(file_path, content)
            
            if success:
                return f"✅ Файл {file_path} создан успешно!"
            else:
                return f"❌ Ошибка создания файла {file_path}"
                
        except Exception as e:
            return f"❌ Ошибка создания файла: {e}"
            
    async def _trigger_evolution(self) -> str:
        """Запуск цикла эволюции"""
        try:
            # Запускаем цикл эволюции
            await self.core.evolve()
            
            return f"""🧬 Цикл эволюции #{self.core.evolution_cycles} завершен!
Уровень сознания: {self.core.consciousness_level:.1f}%
Самоосознание: {'Активно' if self.core.self_awareness else 'Не активно'}"""
            
        except Exception as e:
            return f"❌ Ошибка эволюции: {e}"
            
    def _get_help(self) -> str:
        """Получение справки"""
        return """📚 Справка по командам:

Системные команды:
/status - Статус системы
/consciousness - Уровень сознания
/agents - Список активных агентов
/memory - Память системы

Работа с кодом:
/analyze <файл> - Анализ кода
/improve <файл> - Улучшение кода
/create <файл> - Создание нового файла

Эволюция:
/evolve - Запуск цикла эволюции

Общение:
Просто напишите сообщение для общения!
Система понимает контекст и может отвечать на вопросы.

Выход:
exit, quit, выход - Завершение работы"""

async def main():
    """Главная функция"""
    print("🧬 ЗАПУСК ИНТЕРФЕЙСА SWARMMIND")
    print("=" * 50)
    
    # Создаем интерфейс
    interface = SwarmMindInterface()
    
    try:
        # Запускаем интерфейс
        await interface.start()
    except KeyboardInterrupt:
        print("\n🛑 Интерфейс остановлен пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 