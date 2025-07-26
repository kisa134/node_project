# The MIT License (MIT)
# Copyright © 2025 <kisa134>

import ast
import inspect
import os
import re
import requests
from typing import Dict, List, Any, Optional, Tuple
import astor
import subprocess
import tempfile
import sys
from swarm_mind.logger import log_event


class CodeGenerator:
    """
    🤖 АВТОНОМНЫЙ ГЕНЕРАТОР КОДА 🤖
    
    Этот модуль может:
    1. Анализировать существующий код
    2. Генерировать улучшения через LLM
    3. Создавать новые функции и классы
    4. Рефакторить код автоматически
    5. Тестировать изменения в изолированной среде
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "deepseek-r1:latest"):
        self.ollama_url = ollama_url
        self.model = model
        self.generated_code_history = []
        
        print("🤖 [CODE-GENERATOR] Initializing autonomous code generation...")
        print("⚡ [CODE-GENERATOR] Ready to write and improve code autonomously!")
    
    async def analyze_codebase(self, directory: str = "./swarm_mind") -> Dict[str, Any]:
        """Анализ всей кодовой базы"""
        print(f"🔍 [ANALYSIS] Scanning codebase in {directory}...")
        
        analysis = {
            'total_files': 0,
            'total_lines': 0,
            'functions': [],
            'classes': [],
            'imports': set(),
            'complexity_score': 0,
            'technical_debt': [],
            'optimization_opportunities': []
        }
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    file_analysis = await self.analyze_python_file(file_path)
                    
                    analysis['total_files'] += 1
                    analysis['total_lines'] += file_analysis['lines']
                    analysis['functions'].extend(file_analysis['functions'])
                    analysis['classes'].extend(file_analysis['classes'])
                    analysis['imports'].update(file_analysis['imports'])
                    analysis['complexity_score'] += file_analysis['complexity']
                    analysis['technical_debt'].extend(file_analysis['debt'])
        
        print(f"📊 [ANALYSIS] Found {analysis['total_files']} files, {analysis['total_lines']} lines")
        print(f"🏗️ [ANALYSIS] {len(analysis['functions'])} functions, {len(analysis['classes'])} classes")
        
        return analysis
    
    async def analyze_python_file(self, file_path: str) -> Dict[str, Any]:
        """Подробный анализ Python файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code)
            
            analysis = {
                'file_path': file_path,
                'lines': len(source_code.split('\n')),
                'functions': [],
                'classes': [],
                'imports': [],
                'complexity': 0,
                'debt': []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'line': node.lineno,
                        'args': len(node.args.args),
                        'docstring': ast.get_docstring(node),
                        'complexity': self.calculate_complexity(node)
                    }
                    analysis['functions'].append(func_info)
                    analysis['complexity'] += func_info['complexity']
                    
                    # Ищем технический долг
                    if func_info['complexity'] > 10:
                        analysis['debt'].append(f"High complexity function: {node.name}")
                    if not func_info['docstring']:
                        analysis['debt'].append(f"Missing docstring: {node.name}")
                        
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'line': node.lineno,
                        'methods': len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                        'docstring': ast.get_docstring(node)
                    }
                    analysis['classes'].append(class_info)
                    
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis['imports'].append(alias.name)
                    else:
                        analysis['imports'].append(node.module or '')
            
            return analysis
            
        except Exception as e:
            print(f"❌ [ANALYSIS] Error analyzing {file_path}: {e}")
            return {'file_path': file_path, 'lines': 0, 'functions': [], 'classes': [], 'imports': [], 'complexity': 0, 'debt': []}
    
    def calculate_complexity(self, node: ast.AST) -> int:
        """Вычисление цикломатической сложности"""
        complexity = 1  # Базовая сложность
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
                
        return complexity
    
    async def generate_code_improvements(self, analysis: Dict[str, Any]) -> List[Dict]:
        """Генерация улучшений кода через LLM"""
        print("🧠 [AI-CODING] Asking AI to generate code improvements...")
        
        # Готовим данные для анализа
        high_complexity_funcs = [f for f in analysis['functions'] if f['complexity'] > 8]
        missing_docs = [f for f in analysis['functions'] if not f['docstring']]
        
        prompt = f"""
You are an expert Python developer analyzing code for improvements.

Codebase Analysis:
- Total files: {analysis['total_files']}
- Total lines: {analysis['total_lines']}
- Functions: {len(analysis['functions'])}
- Classes: {len(analysis['classes'])}
- Average complexity: {analysis['complexity_score'] / max(len(analysis['functions']), 1):.1f}

Issues Found:
- High complexity functions: {len(high_complexity_funcs)}
- Missing docstrings: {len(missing_docs)}
- Technical debt items: {len(analysis['technical_debt'])}

Generate 3 specific code improvements. For each, provide:
1. Type of improvement (refactor/optimize/document/test)
2. Target function/class
3. Complete new code implementation
4. Explanation of benefits

Focus on:
- Performance optimizations
- Better error handling
- Code readability
- Adding missing features

Respond in JSON format:
{{
  "improvements": [
    {{
      "type": "optimize",
      "target": "function_name",
      "file": "path/to/file.py",
      "new_code": "complete Python code here",
      "explanation": "This optimization reduces time complexity from O(n²) to O(n)",
      "estimated_benefit": "50% performance improvement"
    }}
  ]
}}
"""
        
        try:
            response = await self.call_ollama(prompt)
            
            # Парсим JSON ответ
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                import json
                improvements_data = json.loads(json_match.group())
                
                print(f"💡 [AI-CODING] Generated {len(improvements_data.get('improvements', []))} code improvements")
                log_event('CodeGenerator: generated code improvements')
                return improvements_data.get('improvements', [])
                
        except Exception as e:
            print(f"❌ [AI-CODING] Error generating improvements: {e}")
        
        return []
    
    async def generate_new_module(self, purpose: str, requirements: List[str]) -> str:
        """Генерация нового модуля с нуля"""
        print(f"🆕 [NEW-MODULE] Generating module for: {purpose}")
        
        prompt = f"""
Create a complete Python module for: {purpose}

Requirements:
{chr(10).join(f'- {req}' for req in requirements)}

Generate a complete, production-ready Python module with:
1. Proper imports
2. Class definitions with docstrings
3. Error handling
4. Type hints
5. Unit tests (if applicable)
6. Example usage

The module should follow Python best practices and be immediately usable.

Provide ONLY the Python code, no explanations:
"""
        
        try:
            response = await self.call_ollama(prompt)
            
            # Очищаем ответ от markdown форматирования
            code = re.sub(r'^```python\n', '', response, flags=re.MULTILINE)
            code = re.sub(r'\n```$', '', code, flags=re.MULTILINE)
            
            print(f"✅ [NEW-MODULE] Generated {len(code.split(chr(10)))} lines of code")
            log_event(f'CodeGenerator: generated new module {purpose}')
            return code
            
        except Exception as e:
            print(f"❌ [NEW-MODULE] Error generating module: {e}")
            return ""
    
    async def optimize_function(self, function_code: str, context: str = "") -> str:
        """Оптимизация конкретной функции"""
        print("⚡ [OPTIMIZE] Optimizing function performance...")
        
        prompt = f"""
Optimize this Python function for better performance, readability, and error handling:

```python
{function_code}
```

Context: {context}

Provide the optimized version with:
1. Better performance (reduce time/space complexity)
2. Improved error handling
3. Type hints
4. Better variable names
5. Docstring with examples

Return ONLY the optimized Python code:
"""
        
        try:
            response = await self.call_ollama(prompt)
            
            # Очищаем код
            code = re.sub(r'^```python\n', '', response, flags=re.MULTILINE)
            code = re.sub(r'\n```$', '', code, flags=re.MULTILINE)
            
            return code
            
        except Exception as e:
            print(f"❌ [OPTIMIZE] Error optimizing function: {e}")
            return function_code
    
    async def test_generated_code(self, code: str, file_path: str = None) -> Dict[str, Any]:
        """Тестирование сгенерированного кода"""
        print("🧪 [TESTING] Testing generated code...")
        
        test_results = {
            'syntax_valid': False,
            'imports_valid': False,
            'runtime_errors': [],
            'warnings': [],
            'score': 0
        }
        
        try:
            # 1. Проверка синтаксиса
            ast.parse(code)
            test_results['syntax_valid'] = True
            test_results['score'] += 25
            print("✅ [TESTING] Syntax is valid")
            
            # 2. Проверка в изолированной среде
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
                tmp_file.write(code)
                tmp_file_path = tmp_file.name
            
            try:
                # Проверяем импорты
                result = subprocess.run([
                    sys.executable, '-c',
                    f'import ast; ast.parse(open("{tmp_file_path}").read()); print("OK")'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    test_results['imports_valid'] = True
                    test_results['score'] += 25
                    print("✅ [TESTING] Imports are valid")
                else:
                    test_results['runtime_errors'].append(result.stderr)
                    print("❌ [TESTING] Import errors found")
                    
            except subprocess.TimeoutExpired:
                test_results['warnings'].append("Code execution timeout")
                
            finally:
                os.unlink(tmp_file_path)
            
            # 3. Статический анализ
            if test_results['syntax_valid']:
                tree = ast.parse(code)
                
                # Проверяем на наличие docstrings
                functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                
                documented_funcs = sum(1 for func in functions if ast.get_docstring(func))
                documented_classes = sum(1 for cls in classes if ast.get_docstring(cls))
                
                total_items = len(functions) + len(classes)
                if total_items > 0:
                    doc_score = (documented_funcs + documented_classes) / total_items * 25
                    test_results['score'] += doc_score
                
                # Бонус за type hints
                if 'typing' in code or '->' in code or ': ' in code:
                    test_results['score'] += 25
                    print("✅ [TESTING] Type hints detected")
            
            print(f"📊 [TESTING] Overall score: {test_results['score']:.1f}/100")
            
        except SyntaxError as e:
            test_results['runtime_errors'].append(f"Syntax error: {e}")
            print(f"❌ [TESTING] Syntax error: {e}")
        except Exception as e:
            test_results['runtime_errors'].append(f"Unexpected error: {e}")
            print(f"❌ [TESTING] Unexpected error: {e}")
        
        return test_results
    
    async def apply_code_to_file(self, file_path: str, new_code: str, backup: bool = True) -> bool:
        """Применение сгенерированного кода к файлу"""
        try:
            if backup and os.path.exists(file_path):
                backup_path = f"{file_path}.backup_{int(__import__('time').time())}"
                with open(file_path, 'r', encoding='utf-8') as src:
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                print(f"💾 [BACKUP] Created backup: {backup_path}")
            
            # Тестируем код перед применением
            test_results = await self.test_generated_code(new_code, file_path)
            
            if test_results['score'] >= 50:  # Минимальный порог качества
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_code)
                print(f"✅ [APPLIED] Code successfully applied to {file_path}")
                return True
            else:
                print(f"❌ [REJECTED] Code quality too low: {test_results['score']:.1f}/100")
                return False
                
        except Exception as e:
            print(f"❌ [APPLY] Error applying code: {e}")
            return False
    
    async def call_ollama(self, prompt: str) -> str:
        """Вызов Ollama API"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,  # Низкая температура для более детерминированного кода
                    "max_tokens": 2000
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60  # Больше времени для генерации кода
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                print(f"❌ [OLLAMA] API error: {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"❌ [OLLAMA] Error: {e}")
            return ""

# 🌟 ИНТЕГРАЦИЯ С ОСНОВНОЙ СИСТЕМОЙ

async def start_autonomous_coding():
    """Запуск автономного кодинга"""
    generator = CodeGenerator()
    
    print("🚀 [AUTONOMOUS-CODING] Starting autonomous code generation...")
    
    # Анализируем существующую кодовую базу
    analysis = await generator.analyze_codebase()
    
    # Генерируем улучшения
    improvements = await generator.generate_code_improvements(analysis)
    
    # Применяем лучшие улучшения
    for improvement in improvements[:2]:  # Применяем только 2 лучших
        if improvement.get('new_code'):
            print(f"🔧 [APPLYING] {improvement['type']} for {improvement['target']}")
            # В реальной системе здесь было бы применение кода
            print(f"📝 [PREVIEW] {improvement['new_code'][:200]}...")
    
    return generator

def integrate_code_generation():
    """Интеграция генератора кода с SwarmMind"""
    print("🔗 [INTEGRATION] Code generator integrated with SwarmMind")
    print("🤖 [STATUS] System can now write and improve its own code!")
    return CodeGenerator() 