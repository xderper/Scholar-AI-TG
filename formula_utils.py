import openai
import os
import logging
import re

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