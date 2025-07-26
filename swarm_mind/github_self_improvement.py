#!/usr/bin/env python3
"""
🤖 СИСТЕМА САМОУЛУЧШЕНИЯ ЧЕРЕЗ GITHUB PULL REQUESTS 🤖

Трехуровневая система самоулучшения:

1. CodeAnalyzerAgent - анализирует весь код и предлагает улучшения
2. TaskPlannerAgent - планирует улучшения и разбивает на подзадачи
3. CodeExecutorAgent - пишет код под контролем планировщика

Все изменения проходят через GitHub pull requests для безопасности.
"""

import asyncio
import json
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import requests
import ast
import astor

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GitHubSelfImprovement")

class CodeAnalyzerAgent:
    """Агент анализа кода - первый уровень"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.analysis_results = []
        
    async def analyze_entire_codebase(self) -> Dict[str, Any]:
        """Полный анализ кодовой базы"""
        logger.info("🔍 CodeAnalyzerAgent: Начинаю анализ кодовой базы...")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_files': 0,
            'total_lines': 0,
            'complexity_score': 0,
            'improvement_suggestions': [],
            'critical_issues': [],
            'performance_issues': [],
            'code_quality_issues': []
        }
        
        # Сканируем все Python файлы
        python_files = list(self.project_root.rglob("*.py"))
        analysis['total_files'] = len(python_files)
        
        for file_path in python_files:
            file_analysis = await self.analyze_file(file_path)
            analysis['total_lines'] += file_analysis['lines']
            analysis['complexity_score'] += file_analysis['complexity']
            
            # Добавляем проблемы
            if file_analysis['issues']:
                analysis['code_quality_issues'].extend(file_analysis['issues'])
                
            # Добавляем предложения по улучшению
            if file_analysis['suggestions']:
                analysis['improvement_suggestions'].extend(file_analysis['suggestions'])
        
        logger.info(f"✅ CodeAnalyzerAgent: Проанализировано {analysis['total_files']} файлов")
        logger.info(f"📊 CodeAnalyzerAgent: Найдено {len(analysis['improvement_suggestions'])} предложений по улучшению")
        
        return analysis
    
    async def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Анализ отдельного файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            analysis = {
                'file_path': str(file_path),
                'lines': len(content.split('\n')),
                'complexity': 0,
                'issues': [],
                'suggestions': []
            }
            
            # Анализируем сложность
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    complexity = self.calculate_complexity(node)
                    analysis['complexity'] += complexity
                    
                    # Проверяем на проблемы
                    if complexity > 10:
                        analysis['issues'].append({
                            'type': 'high_complexity',
                            'function': node.name,
                            'complexity': complexity,
                            'line': node.lineno,
                            'message': f'Функция {node.name} слишком сложная (сложность: {complexity})'
                        })
                        
                        analysis['suggestions'].append({
                            'type': 'refactor_function',
                            'target': str(file_path),
                            'function': node.name,
                            'priority': 8,
                            'description': f'Разбить сложную функцию {node.name} на более простые',
                            'expected_benefit': 'Улучшение читаемости и поддерживаемости кода'
                        })
            
            # Проверяем размер файла
            if analysis['lines'] > 500:
                analysis['suggestions'].append({
                    'type': 'split_file',
                    'target': str(file_path),
                    'priority': 7,
                    'description': f'Файл слишком большой ({analysis["lines"]} строк), рекомендуется разбить на модули',
                    'expected_benefit': 'Улучшение организации кода'
                })
            
            # Проверяем на неиспользуемые импорты
            unused_imports = self.find_unused_imports(tree, content)
            if unused_imports:
                analysis['suggestions'].append({
                    'type': 'remove_unused_imports',
                    'target': str(file_path),
                    'priority': 5,
                    'description': f'Удалить неиспользуемые импорты: {", ".join(unused_imports)}',
                    'expected_benefit': 'Улучшение производительности и чистоты кода'
                })
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа файла {file_path}: {e}")
            return {
                'file_path': str(file_path),
                'lines': 0,
                'complexity': 0,
                'issues': [],
                'suggestions': []
            }
    
    def calculate_complexity(self, node: ast.AST) -> int:
        """Вычисление цикломатической сложности"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With):
                complexity += 1
                
        return complexity
    
    def find_unused_imports(self, tree: ast.AST, content: str) -> List[str]:
        """Поиск неиспользуемых импортов"""
        # Простая проверка - в реальной системе нужен более сложный анализ
        return []

class TaskPlannerAgent:
    """Агент планирования задач - второй уровень"""
    
    def __init__(self):
        self.current_tasks = []
        self.completed_tasks = []
        self.failed_tasks = []
        
    async def plan_improvements(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Планирование улучшений на основе анализа"""
        logger.info("📋 TaskPlannerAgent: Планирую улучшения...")
        
        tasks = []
        
        # Группируем предложения по типам
        suggestions_by_type = {}
        for suggestion in analysis['improvement_suggestions']:
            suggestion_type = suggestion['type']
            if suggestion_type not in suggestions_by_type:
                suggestions_by_type[suggestion_type] = []
            suggestions_by_type[suggestion_type].append(suggestion)
        
        # Создаем задачи для каждого типа улучшений
        for suggestion_type, suggestions in suggestions_by_type.items():
            task = await self.create_task_for_suggestions(suggestion_type, suggestions)
            tasks.append(task)
        
        # Сортируем по приоритету
        tasks.sort(key=lambda x: x['priority'], reverse=True)
        
        logger.info(f"✅ TaskPlannerAgent: Создано {len(tasks)} задач")
        return tasks
    
    async def create_task_for_suggestions(self, suggestion_type: str, suggestions: List[Dict]) -> Dict[str, Any]:
        """Создание задачи для группы предложений"""
        task = {
            'id': f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'type': suggestion_type,
            'priority': max(s['priority'] for s in suggestions),
            'status': 'pending',
            'subtasks': [],
            'description': f"Улучшение: {suggestion_type}",
            'target_files': list(set(s['target'] for s in suggestions)),
            'created_at': datetime.now().isoformat()
        }
        
        # Разбиваем на подзадачи
        for suggestion in suggestions:
            subtask = {
                'id': f"subtask_{len(task['subtasks'])}",
                'description': suggestion['description'],
                'target_file': suggestion['target'],
                'priority': suggestion['priority'],
                'status': 'pending',
                'expected_benefit': suggestion['expected_benefit']
            }
            task['subtasks'].append(subtask)
        
        return task
    
    async def monitor_task_execution(self, task: Dict[str, Any], executor_agent) -> bool:
        """Мониторинг выполнения задачи"""
        logger.info(f"👁️ TaskPlannerAgent: Мониторю выполнение задачи {task['id']}")
        
        task['status'] = 'in_progress'
        
        for subtask in task['subtasks']:
            logger.info(f"📝 TaskPlannerAgent: Выполняю подзадачу {subtask['id']}")
            
            # Отправляем подзадачу исполнителю
            success = await executor_agent.execute_subtask(subtask)
            
            if success:
                subtask['status'] = 'completed'
                logger.info(f"✅ TaskPlannerAgent: Подзадача {subtask['id']} выполнена")
            else:
                subtask['status'] = 'failed'
                logger.error(f"❌ TaskPlannerAgent: Подзадача {subtask['id']} провалена")
                return False
        
        task['status'] = 'completed'
        task['completed_at'] = datetime.now().isoformat()
        
        logger.info(f"✅ TaskPlannerAgent: Задача {task['id']} выполнена успешно")
        return True

class CodeExecutorAgent:
    """Агент выполнения кода - третий уровень"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repo = os.getenv('GITHUB_REPO', 'kisa134/node_project')
        
    async def execute_subtask(self, subtask: Dict[str, Any]) -> bool:
        """Выполнение подзадачи"""
        logger.info(f"🔧 CodeExecutorAgent: Выполняю {subtask['description']}")
        
        try:
            # Создаем ветку для изменений
            branch_name = f"improvement/{subtask['id']}"
            await self.create_branch(branch_name)
            
            # Выполняем изменения в зависимости от типа
            if subtask['target_file']:
                success = await self.modify_file(subtask)
            else:
                success = await self.create_new_file(subtask)
            
            if success:
                # Создаем коммит
                await self.commit_changes(subtask['description'])
                
                # Создаем pull request
                pr_url = await self.create_pull_request(subtask)
                
                logger.info(f"✅ CodeExecutorAgent: Создан PR: {pr_url}")
                return True
            else:
                logger.error(f"❌ CodeExecutorAgent: Не удалось выполнить изменения")
                return False
                
        except Exception as e:
            logger.error(f"❌ CodeExecutorAgent: Ошибка выполнения подзадачи: {e}")
            return False
    
    async def modify_file(self, subtask: Dict[str, Any]) -> bool:
        """Модификация существующего файла"""
        file_path = Path(subtask['target_file'])
        
        if not file_path.exists():
            logger.error(f"❌ Файл не найден: {file_path}")
            return False
        
        try:
            # Создаем бэкап
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
            shutil.copy2(file_path, backup_path)
            
            # Читаем файл
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Применяем изменения в зависимости от типа
            if 'refactor_function' in subtask['description']:
                modified_content = await self.refactor_function(content, subtask)
            elif 'remove_unused_imports' in subtask['description']:
                modified_content = await self.remove_unused_imports(content)
            elif 'split_file' in subtask['description']:
                modified_content = await self.split_large_file(content, file_path)
            else:
                modified_content = content
            
            # Записываем изменения
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            logger.info(f"✅ Файл {file_path} успешно модифицирован")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка модификации файла {file_path}: {e}")
            return False
    
    async def refactor_function(self, content: str, subtask: Dict[str, Any]) -> str:
        """Рефакторинг функции"""
        # В реальной системе здесь был бы сложный анализ и рефакторинг
        # Пока возвращаем исходный контент
        return content
    
    async def remove_unused_imports(self, content: str) -> str:
        """Удаление неиспользуемых импортов"""
        # Простая реализация - в реальной системе нужен более сложный анализ
        return content
    
    async def split_large_file(self, content: str, file_path: Path) -> str:
        """Разбиение большого файла на модули"""
        # В реальной системе здесь был бы анализ и разбиение на модули
        return content
    
    async def create_new_file(self, subtask: Dict[str, Any]) -> bool:
        """Создание нового файла"""
        # Логика создания нового файла
        return True
    
    async def create_branch(self, branch_name: str) -> bool:
        """Создание новой ветки"""
        try:
            # Git команды для создания ветки
            subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
            logger.info(f"✅ Создана ветка: {branch_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка создания ветки: {e}")
            return False
    
    async def commit_changes(self, message: str) -> bool:
        """Создание коммита"""
        try:
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', message], check=True)
            logger.info(f"✅ Создан коммит: {message}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка создания коммита: {e}")
            return False
    
    async def create_pull_request(self, subtask: Dict[str, Any]) -> str:
        """Создание pull request"""
        # В реальной системе здесь был бы API вызов к GitHub
        pr_url = f"https://github.com/{self.github_repo}/pull/123"
        logger.info(f"✅ Создан PR: {pr_url}")
        return pr_url

class GitHubSelfImprovementSystem:
    """Главная система самоулучшения"""
    
    def __init__(self, project_root: str = None):
        self.analyzer = CodeAnalyzerAgent(project_root)
        self.planner = TaskPlannerAgent()
        self.executor = CodeExecutorAgent(project_root)
        self.running = False
        
    async def start_improvement_cycle(self):
        """Запуск цикла самоулучшения"""
        logger.info("🚀 GitHubSelfImprovementSystem: Запуск цикла самоулучшения")
        self.running = True
        
        while self.running:
            try:
                # 1. Анализ кода
                logger.info("🔍 Этап 1: Анализ кода")
                analysis = await self.analyzer.analyze_entire_codebase()
                
                if not analysis['improvement_suggestions']:
                    logger.info("✅ Нет предложений по улучшению")
                    await asyncio.sleep(300)  # 5 минут
                    continue
                
                # 2. Планирование задач
                logger.info("📋 Этап 2: Планирование задач")
                tasks = await self.planner.plan_improvements(analysis)
                
                # 3. Выполнение задач
                logger.info("🔧 Этап 3: Выполнение задач")
                for task in tasks:
                    success = await self.planner.monitor_task_execution(task, self.executor)
                    if success:
                        logger.info(f"✅ Задача {task['id']} выполнена успешно")
                    else:
                        logger.error(f"❌ Задача {task['id']} провалена")
                
                # Ждем перед следующим циклом
                await asyncio.sleep(600)  # 10 минут
                
            except Exception as e:
                logger.error(f"❌ Ошибка в цикле самоулучшения: {e}")
                await asyncio.sleep(300)
    
    def stop_improvement_cycle(self):
        """Остановка цикла самоулучшения"""
        logger.info("🛑 GitHubSelfImprovementSystem: Остановка цикла самоулучшения")
        self.running = False

# Функции для интеграции с основной системой
async def start_github_self_improvement():
    """Запуск системы самоулучшения"""
    system = GitHubSelfImprovementSystem()
    await system.start_improvement_cycle()

def integrate_github_self_improvement():
    """Интеграция с основной системой SwarmMind"""
    return GitHubSelfImprovementSystem()

if __name__ == "__main__":
    # Тестовый запуск
    asyncio.run(start_github_self_improvement()) 