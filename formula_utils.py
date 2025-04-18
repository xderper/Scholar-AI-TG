import openai
import os
import logging
import re
import numpy as np
import matplotlib.pyplot as plt

class FormulaUtils:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        openai.api_key = self.api_key
        self.client = openai.OpenAI()
        
        # Настройка логирования
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def get_formula(self, request):
        """Извлекает чистую формулу из объяснения нейросети"""
        try:
            # Получаем ответ от ChatGPT
            response = self._get_response(request)
            
            # Отправляем второй запрос для извлечения чистой формулы
            formula_request = "Extract only the mathematical expression from this text, without any explanations or words. If there are multiple expressions, use the last one. Return only the expression itself: " + response
            
            formula = self._get_response(formula_request)
            
            # Очищаем формулу от лишнего текста
            formula = self._clean_formula(formula)
            
            # Если формула пустая или содержит только 'x', возвращаем 'x'
            if not formula or formula == 'x':
                return 'x'
                
            return formula
            
        except Exception as e:
            self.logger.error(f"Error in get_formula: {e}")
            return "x"  # устанавливаем простейшую формулу в случае ошибки

    def _clean_formula(self, formula):
        """Очищает формулу от лишнего текста и символов"""
        # Заменяем текстовые обозначения тригонометрических функций на символьные
        formula = formula.lower()  # приводим к нижнему регистру для унификации
        
        # Удаляем 'y = ' если есть
        if 'y = ' in formula:
            formula = formula.split('y =')[-1].strip()
            
        # Заменяем текстовые обозначения на математические
        trig_replacements = {
            'sin': 'sin',
            'cos': 'cos',
            'tan': 'tan',
            'cot': 'cot',
            'arcsin': 'asin',
            'arccos': 'acos',
            'arctg': 'atan',
            'arcctg': 'acot',
            'tg': 'tan',
            'ctg': 'cot',
            'ln': 'log',
            'lg': 'log10',
            'sqrt': 'sqrt',
            'pi': 'pi',
            '^': '**',
            '÷': '/',
            '×': '*'
        }
        
        # Добавляем пробелы вокруг операторов для правильной замены
        formula = re.sub(r'([+\-*/^()])', r' \1 ', formula)
        
        # Заменяем текстовые обозначения на символьные
        words = formula.split()
        for i, word in enumerate(words):
            if word.lower() in trig_replacements:
                words[i] = trig_replacements[word.lower()]
        formula = ' '.join(words)
        
        # Удаляем лишние пробелы
        formula = re.sub(r'\s+', ' ', formula).strip()
        
        # Удаляем пробелы между функцией и скобкой
        formula = re.sub(r'(sin|cos|tan|cot|asin|acos|atan|acot|log|sqrt) \(', r'\1(', formula)
        
        return formula

    def _get_response(self, prompt):
        """Делает запрос к ChatGPT"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts mathematical expressions. Return only the expression itself, without any additional text or explanations."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error in _get_response: {e}")
            raise 
            
    def plot_function(self, formula, x_min=-10, x_max=10, points=1000, plot_modulus=False):
        """
        Строит график функции на основе заданной формулы
        
        Args:
            formula (str): Формула функции в виде строки
            x_min (float): Минимальное значение x
            x_max (float): Максимальное значение x
            points (int): Количество точек для построения
            plot_modulus (bool): Построить график с модулем функции
            
        Returns:
            tuple: (figure, axes) объекты matplotlib
        """
        try:
            # Создаем массив значений x
            x = np.linspace(x_min, x_max, points)
            
            # Заменяем математические функции на numpy эквиваленты
            formula_np = self._convert_to_numpy(formula)
            
            # Безопасное вычисление значений функции
            y = self._safe_eval(formula_np, x)
            
            # Создаем график
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Построение обычного графика
            ax.plot(x, y, label='f(x)')
            
            # Если требуется график с модулем, добавляем его
            if plot_modulus:
                ax.plot(x, np.abs(y), 'r--', label='|f(x)|')
            
            # Настройка графика
            ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            ax.grid(True, alpha=0.3)
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_title(f'График функции: {formula}')
            ax.legend()
            
            return fig, ax
            
        except Exception as e:
            self.logger.error(f"Error plotting function: {e}")
            # Создаем пустой график в случае ошибки
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, f'Ошибка построения графика: {str(e)}', 
                    horizontalalignment='center', verticalalignment='center')
            return fig, ax
    
    def _convert_to_numpy(self, formula):
        """Преобразует математическую формулу для работы с numpy"""
        # Замена стандартных функций на numpy эквиваленты
        replacements = {
            'sin': 'np.sin',
            'cos': 'np.cos',
            'tan': 'np.tan',
            'cot': '1/np.tan',
            'asin': 'np.arcsin',
            'acos': 'np.arccos',
            'atan': 'np.arctan',
            'acot': 'np.pi/2 - np.arctan',
            'log': 'np.log',
            'log10': 'np.log10',
            'sqrt': 'np.sqrt',
            'pi': 'np.pi',
            'e': 'np.e',
            '**': '**',
            'abs': 'np.abs'
        }
        
        for old, new in replacements.items():
            # Убедимся, что заменяем только целые слова, а не части слов
            formula = re.sub(r'\b' + old + r'\b', new, formula)
            
        return formula
    
    def _safe_eval(self, formula_np, x):
        """Безопасное вычисление значений функции"""
        try:
            # Создаем локальный namespace с numpy и x
            namespace = {'np': np, 'x': x}
            # Вычисляем значения y
            y = eval(formula_np, {"__builtins__": {}}, namespace)
            
            # Заменяем бесконечные значения на NaN для лучшей визуализации
            y = np.where(np.isinf(y), np.nan, y)
            return y
            
        except Exception as e:
            self.logger.error(f"Error evaluating formula: {e}")
            raise
    
    def save_plot(self, fig, filename='function_plot.png', dpi=300):
        """Сохраняет график в файл"""
        try:
            fig.savefig(filename, dpi=dpi, bbox_inches='tight')
            return True
        except Exception as e:
            self.logger.error(f"Error saving plot: {e}")
            return False 