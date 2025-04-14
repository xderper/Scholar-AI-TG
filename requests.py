import os
import httpx
import openai
from dotenv import load_dotenv
from format import Format
import logging
import requests
import re
# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Requests:
    def __init__(self):
        
        # Получение API ключа OpenAI
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY не найден в переменных окружения")
        
        # Инициализация клиента OpenAI
        self.openai_client = openai.Client(
            api_key=self.openai_api_key,
            base_url="https://api.openai.com/v1"
        )

        self.format = Format()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('OPENAI_TOKEN')}"
        }
        self.url = "https://api.openai.com/v1/chat/completions"
    
    def _get_response(self, prompt, image_data=None):
        """
        Отправляет запрос к OpenAI API
        
        Args:
            prompt (str): Текстовый запрос
            image_data (str, optional): URL изображения для обработки
            
        Returns:
            str: Ответ от модели
        """
        try:
            logger.info(f"Отправка запроса к OpenAI. Длина запроса: {len(prompt)} символов")
            
            messages = [{"role": "user", "content": prompt}]
            
            if image_data:
                # Форматируем изображение в правильном формате для OpenAI
                image_content = [{
                    "type": "text",
                    "text": prompt
                }, {
                    "type": "image_url",
                    "image_url": {
                        "url": image_data
                    }
                }]
                messages.append({"role": "user", "content": image_content})
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=2000,
                temperature=0.2,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "analyze_image",
                            "description": "Analyze an image and extract information",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "image_url": {
                                        "type": "string",
                                        "description": "URL of the image to analyze"
                                    }
                                },
                                "required": ["image_url"]
                            }
                        }
                    }
                ] if image_data else None,
                tool_choice="auto" if image_data else None
            )
            
            logger.info(f"Получен ответ от OpenAI. Длина ответа: {len(response.choices[0].message.content)} символов")
            logger.info(f"Ответ от OpenAI: {response.choices[0].message.content}")
            
            # Если это математический запрос, просим модель вернуть только формулу
            if "график" in prompt.lower() or "построить" in prompt.lower() or "=" in prompt:
                messages = [
                    {"role": "system", "content": "Ты математический ассистент. Верни ТОЛЬКО математическую формулу в Python-формате (используй ** вместо ^). Не добавляй никаких пояснений."},
                    {"role": "user", "content": response.choices[0].message.content}
                ]
                
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    max_tokens=2000,
                    temperature=0.1
                )
                
                logger.info(f"Обработанный ответ для формулы: {response.choices[0].message.content}")
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Ошибка при запросе к OpenAI: {str(e)}")
            raise
    
    def get_formula(self, explanation):
        """Извлекает чистую формулу из объяснения нейросети"""
        messages = [
            {"role": "system", "content": "Ты математический ассистент. Прочитай объяснение и верни ТОЛЬКО математическую формулу в Python-формате (используй ** вместо ^). Не добавляй никаких пояснений."},
            {"role": "user", "content": "Для построения графика функции y = x^2 + 2x нужно..."},
            {"role": "assistant", "content": "x**2 + 2*x"},
            {"role": "user", "content": explanation}
        ]

        try:
            response = requests.post(
                self.url,
                headers=self.headers,
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": messages,
                    "temperature": 0.1
                },
                timeout=60
            )
            response.raise_for_status()
            formula = response.json()["choices"][0]["message"]["content"].strip()
            return formula
        except:
            return "x"

    def extract_last_formula(self, text):
        """Извлекает последнюю формулу из текста нейросети"""
        try:
            logger.info(f"Извлечение формулы из текста: {text}")
            
            # Разбиваем текст на строки
            lines = text.split('\n')
            
            # Ищем последнюю строку с формулой
            formula_line = ""
            for line in reversed(lines):
                # Удаляем HTML-теги
                line = re.sub(r'<[^>]+>', '', line)
                
                # Ищем строки, содержащие формулы
                if ('=' in line or 
                    any(x in line.lower() for x in ['sin', 'cos', 'tan', 'x**', 'sqrt']) or
                    re.search(r'\dx', line) or
                    re.search(r'y\s*=\s*', line) or
                    re.search(r'f\s*\(\s*x\s*\)\s*=\s*', line)):
                    formula_line = line
                    logger.info(f"Найдена формула в строке: {formula_line}")
                    break
            
            if not formula_line:
                # Если не нашли формулу в тексте, проверяем сам текст
                if '=' in text or re.search(r'\dx', text) or re.search(r'y\s*=\s*', text):
                    formula_line = text
                    logger.info(f"Найдена формула в тексте: {formula_line}")
            
            if not formula_line:
                logger.warning("Формула не найдена в тексте")
                return "x"
                
            return formula_line

        except Exception as e:
            logger.error(f"Ошибка при извлечении формулы: {str(e)}")
            return "x"

    def clean_formula(self, text):
        """Очищает формулу и приводит её к правильному виду"""
        try:
            logger.info(f"Очистка формулы: {text}")
            
            # Ищем формулу после y= или =
            if '=' in text:
                formula = re.split(r'[yY]\s*=|=', text)[-1].strip()
            else:
                formula = text.strip()

            logger.info(f"Формула после разделения: {formula}")

            # Очищаем формулу
            formula = re.sub(r'[×·]', '*', formula)  # Заменяем символы умножения
            formula = re.sub(r'[²³]', lambda m: '**' + {'²': '2', '³': '3'}[m.group()], formula)  # Степени
            formula = formula.replace('^', '**')  # Заменяем ^ на **
            formula = formula.replace('π', 'pi')  # Заменяем символ пи
            formula = formula.replace('√', 'sqrt')  # Заменяем символ корня
            
            # Добавляем * между числом и переменной/функцией
            formula = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', formula)
            formula = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', formula)
            
            # Удаляем все пробелы
            formula = formula.replace(' ', '')
            
            logger.info(f"Формула после очистки: {formula}")
            
            # Проверяем наличие базовых математических элементов
            if not any(x in formula for x in ['x', 'sin', 'cos', 'tan', 'sqrt', 'log', 'pi']):
                logger.warning("Формула не содержит математических элементов")
                return "x"
            
            # Проверяем, что формула содержит только допустимые символы
            if not re.match(r'^[-+*/().\w]+$', formula):
                logger.warning(f"Формула содержит недопустимые символы: {formula}")
                return "x"
            
            return formula
            
        except Exception as e:
            logger.error(f"Ошибка при очистке формулы: {str(e)}")
            return "x"

    def main(self, request, subject=None, photo=False, solution=None):
        """
        Основной метод для обработки запросов по различным предметам
        
        Args:
            request (str): Запрос пользователя
            subject (str): Предмет (physics, chemistry, math)
            photo (bool): Флаг, указывающий, что запрос содержит изображение
            solution (str, optional): Решение задачи, если есть
            
        Returns:
            str: Отформатированный ответ для Telegram
        """
        try:
            # Получаем соответствующий запрос для выбранного предмета из переменных окружения
            if subject == 'physics':
                query = os.getenv("Physic_query")   
            elif subject == 'chemistry':
                query = os.getenv("Chemistry_query")
            elif subject == 'mathematics':
                query = os.getenv("Mathematics_query")
            elif subject == 'chatgpt':
                query = os.getenv("")
            elif subject == 'question':
                query = str(solution) + os.getenv("Question_query")
            else:
                return "Неподдерживаемый предмет"

            # Получаем ответ от модели
            if photo:
                response = self._get_response(query, image_data=request)
            else:
                prompt = f"{query}\n{request}"
                response = self._get_response(prompt)
            
            # Для математических задач с графиками
            if subject == "mathematics" and ("график" in request.lower() or "построить" in request.lower() or "=" in request):
                logger.info(f"Обработка математического запроса: {request}")
                logger.info(f"Ответ от модели: {response}")
                
                # Сначала извлекаем последнюю формулу из текста
                formula_text = self.extract_last_formula(response)
                logger.info(f"Извлеченная формула: {formula_text}")
                
                # Затем очищаем и форматируем формулу
                cleaned_formula = self.clean_formula(formula_text)
                logger.info(f"Очищенная формула: {cleaned_formula}")
                
                return cleaned_formula
            
            # Форматируем ответ для Telegram, преобразуя LaTeX и другие специальные символы
            formatted_response = self.format.format_response_for_telegram(response)
            return formatted_response
            
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса: {str(e)}")
            return f"Произошла ошибка при обработке запроса: {str(e)}"

    # Загрузка переменных окружения
    # Сначала загружаем общие настройки
    load_dotenv()
    # Затем загружаем локальные настройки с приоритетом
    load_dotenv('.env.local', override=True)
