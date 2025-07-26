#!/usr/bin/env python3
"""
🔧 СИСТЕМА САМОИЗМЕНЕНИЯ КОДА SWARMMIND 🔧

Реальная система, которая может изменять свой собственный код
и код других компонентов системы.
"""

import ast
import astor
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

class CodeSelfModifier:
    """Реальная система самоизменения кода"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.backup_dir = self.project_root / "backups"
        self.modifications_log = []
        self.logger = logging.getLogger("CodeSelfModifier")
        
        # Создаем директорию для бэкапов
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self, file_path: str) -> str:
        """Создание резервной копии файла"""
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                raise FileNotFoundError(f"Файл не найден: {file_path}")
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source_path.stem}_{timestamp}{source_path.suffix}"
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(source_path, backup_path)
            self.logger.info(f"✅ Создан бэкап: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания бэкапа: {e}")
            raise
            
    def parse_code(self, file_path: str) -> ast.AST:
        """Парсинг кода в AST"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return ast.parse(content)
        except Exception as e:
            self.logger.error(f"❌ Ошибка парсинга кода: {e}")
            raise
            
    def modify_function(self, file_path: str, function_name: str, new_code: str) -> bool:
        """Изменение функции в файле"""
        try:
            # Создаем бэкап
            backup_path = self.create_backup(file_path)
            
            # Парсим код
            tree = self.parse_code(file_path)
            
            # Находим и изменяем функцию
            modified = False
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    # Создаем новую функцию из строки кода
                    new_function_ast = ast.parse(new_code).body[0]
                    
                    # Заменяем старую функцию на новую
                    node.body = new_function_ast.body
                    node.args = new_function_ast.args
                    node.returns = new_function_ast.returns
                    node.decorator_list = new_function_ast.decorator_list
                    
                    modified = True
                    break
                    
            if not modified:
                self.logger.warning(f"⚠️ Функция {function_name} не найдена в {file_path}")
                return False
                
            # Записываем измененный код
            modified_code = astor.to_source(tree)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_code)
                
            # Логируем изменение
            self.modifications_log.append({
                'timestamp': datetime.now().isoformat(),
                'file': file_path,
                'action': 'function_modification',
                'function': function_name,
                'backup': backup_path
            })
            
            self.logger.info(f"✅ Функция {function_name} изменена в {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка изменения функции: {e}")
            return False
            
    def add_function(self, file_path: str, function_code: str, position: str = "end") -> bool:
        """Добавление новой функции в файл"""
        try:
            # Создаем бэкап
            backup_path = self.create_backup(file_path)
            
            # Парсим код
            tree = self.parse_code(file_path)
            
            # Создаем AST новой функции
            new_function_ast = ast.parse(function_code).body[0]
            
            # Добавляем функцию в нужную позицию
            if position == "end":
                tree.body.append(new_function_ast)
            elif position == "beginning":
                tree.body.insert(0, new_function_ast)
            else:
                # Добавляем после определенной функции
                for i, node in enumerate(tree.body):
                    if isinstance(node, ast.FunctionDef) and node.name == position:
                        tree.body.insert(i + 1, new_function_ast)
                        break
                else:
                    tree.body.append(new_function_ast)
                    
            # Записываем измененный код
            modified_code = astor.to_source(tree)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_code)
                
            # Логируем изменение
            self.modifications_log.append({
                'timestamp': datetime.now().isoformat(),
                'file': file_path,
                'action': 'function_addition',
                'function': new_function_ast.name,
                'backup': backup_path
            })
            
            self.logger.info(f"✅ Добавлена функция {new_function_ast.name} в {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка добавления функции: {e}")
            return False
            
    def add_class(self, file_path: str, class_code: str, position: str = "end") -> bool:
        """Добавление нового класса в файл"""
        try:
            # Создаем бэкап
            backup_path = self.create_backup(file_path)
            
            # Парсим код
            tree = self.parse_code(file_path)
            
            # Создаем AST нового класса
            new_class_ast = ast.parse(class_code).body[0]
            
            # Добавляем класс в нужную позицию
            if position == "end":
                tree.body.append(new_class_ast)
            elif position == "beginning":
                tree.body.insert(0, new_class_ast)
            else:
                # Добавляем после определенного класса
                for i, node in enumerate(tree.body):
                    if isinstance(node, ast.ClassDef) and node.name == position:
                        tree.body.insert(i + 1, new_class_ast)
                        break
                else:
                    tree.body.append(new_class_ast)
                    
            # Записываем измененный код
            modified_code = astor.to_source(tree)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_code)
                
            # Логируем изменение
            self.modifications_log.append({
                'timestamp': datetime.now().isoformat(),
                'file': file_path,
                'action': 'class_addition',
                'class': new_class_ast.name,
                'backup': backup_path
            })
            
            self.logger.info(f"✅ Добавлен класс {new_class_ast.name} в {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка добавления класса: {e}")
            return False
            
    def add_import(self, file_path: str, import_statement: str) -> bool:
        """Добавление импорта в файл"""
        try:
            # Создаем бэкап
            backup_path = self.create_backup(file_path)
            
            # Парсим код
            tree = self.parse_code(file_path)
            
            # Создаем AST импорта
            import_ast = ast.parse(import_statement).body[0]
            
            # Добавляем импорт в начало файла
            tree.body.insert(0, import_ast)
            
            # Записываем измененный код
            modified_code = astor.to_source(tree)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_code)
                
            # Логируем изменение
            self.modifications_log.append({
                'timestamp': datetime.now().isoformat(),
                'file': file_path,
                'action': 'import_addition',
                'import': import_statement,
                'backup': backup_path
            })
            
            self.logger.info(f"✅ Добавлен импорт в {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка добавления импорта: {e}")
            return False
            
    def create_new_file(self, file_path: str, content: str) -> bool:
        """Создание нового файла"""
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Логируем создание
            self.modifications_log.append({
                'timestamp': datetime.now().isoformat(),
                'file': str(file_path),
                'action': 'file_creation',
                'content_length': len(content)
            })
            
            self.logger.info(f"✅ Создан новый файл: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания файла: {e}")
            return False
            
    def optimize_code(self, file_path: str) -> Dict[str, Any]:
        """Оптимизация кода"""
        try:
            # Создаем бэкап
            backup_path = self.create_backup(file_path)
            
            # Парсим код
            tree = self.parse_code(file_path)
            
            optimizations = {
                'removed_unused_imports': 0,
                'simplified_expressions': 0,
                'improved_variable_names': 0
            }
            
            # Удаляем неиспользуемые импорты
            optimizations['removed_unused_imports'] = self._remove_unused_imports(tree)
            
            # Упрощаем выражения
            optimizations['simplified_expressions'] = self._simplify_expressions(tree)
            
            # Улучшаем имена переменных
            optimizations['improved_variable_names'] = self._improve_variable_names(tree)
            
            # Записываем оптимизированный код
            optimized_code = astor.to_source(tree)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(optimized_code)
                
            # Логируем оптимизацию
            self.modifications_log.append({
                'timestamp': datetime.now().isoformat(),
                'file': file_path,
                'action': 'code_optimization',
                'optimizations': optimizations,
                'backup': backup_path
            })
            
            self.logger.info(f"✅ Код оптимизирован: {optimizations}")
            return optimizations
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка оптимизации кода: {e}")
            return {}
            
    def _remove_unused_imports(self, tree: ast.AST) -> int:
        """Удаление неиспользуемых импортов"""
        removed_count = 0
        
        # Простая реализация - удаляем все импорты
        # В реальной системе нужно анализировать использование
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                # Здесь должна быть логика проверки использования
                pass
                
        return removed_count
        
    def _simplify_expressions(self, tree: ast.AST) -> int:
        """Упрощение выражений"""
        simplified_count = 0
        
        # Простая реализация
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp):
                # Здесь должна быть логика упрощения выражений
                pass
                
        return simplified_count
        
    def _improve_variable_names(self, tree: ast.AST) -> int:
        """Улучшение имен переменных"""
        improved_count = 0
        
        # Простая реализация
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                # Здесь должна быть логика улучшения имен
                pass
                
        return improved_count
        
    def get_modifications_log(self) -> List[Dict[str, Any]]:
        """Получение лога изменений"""
        return self.modifications_log
        
    def revert_last_modification(self) -> bool:
        """Откат последнего изменения"""
        if not self.modifications_log:
            self.logger.warning("⚠️ Нет изменений для отката")
            return False
            
        last_modification = self.modifications_log[-1]
        backup_path = last_modification.get('backup')
        
        if not backup_path or not os.path.exists(backup_path):
            self.logger.error("❌ Бэкап не найден")
            return False
            
        try:
            # Восстанавливаем файл из бэкапа
            file_path = last_modification['file']
            shutil.copy2(backup_path, file_path)
            
            # Удаляем запись из лога
            self.modifications_log.pop()
            
            self.logger.info(f"✅ Откачено изменение: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка отката: {e}")
            return False

# Пример использования
if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    # Создаем модификатор
    modifier = CodeSelfModifier()
    
    # Пример добавления функции
    new_function = '''
def test_self_modification():
    """Тестовая функция для демонстрации самоизменения"""
    print("🧬 Это функция, созданная системой самоизменения!")
    return "success"
'''
    
    # Добавляем функцию в текущий файл
    current_file = __file__
    success = modifier.add_function(current_file, new_function)
    
    if success:
        print("✅ Функция добавлена успешно!")
    else:
        print("❌ Ошибка добавления функции") 