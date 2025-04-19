import os
import httpx
import openai
from dotenv import load_dotenv
from format import Format
import logging
from graphs import Graphs
import json
import time
import re
from typing import Optional, Tuple, Union, Dict, Any, BinaryIO

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Requests:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        openai.api_key = self.api_key
        self.client = openai.OpenAI()
        self.format = Format()
    
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
            logger.info(f"Отправка запроса к OpenAI. Текст: {prompt[:50]}...")
            
            if image_data:
                # Форматируем сообщение с текстом и изображением
                messages = [{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data
                            }
                        }
                    ]
                }]
            else:
                # Только текстовое сообщение
                messages = [{"role": "user", "content": prompt}]
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=2000,
                temperature=0.2
            )
            
            logger.info(f"Получен ответ от OpenAI. Длина ответа: {len(response.choices[0].message.content)} символов")
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Ошибка при запросе к OpenAI: {str(e)}")
            raise
    
    def main(self, request: str, subject: str, photo=None, solution: str = None) -> Union[str, Tuple[BinaryIO, str]]:
        """
        Основной метод для обработки запросов по различным предметам
        
        Args:
            request (str): Запрос пользователя
            subject (str): Предмет (physics, chemistry, math)
            photo: Данные изображения в формате base64 или None
            solution (str): Тип решения (например, "graph" для построения графика)
            
        Returns:
            Union[str, Tuple[BinaryIO, str]]: Отформатированный ответ для Telegram или кортеж (изображение, подпись)
        """
        try:
            # Проверка на пустой запрос
            if not request:
                request = "Помоги мне с этим заданием."
                
            logger.info(f"Обработка запроса. Предмет: {subject}, Решение: {solution}, Фото: {'Да' if photo else 'Нет'}")
            
            # Получаем соответствующий запрос для выбранного предмета из переменных окружения
            if subject == 'physics':
                query = os.getenv("Physic_query") or ""   
            elif subject == 'chemistry':
                query = os.getenv("Chemistry_query") or ""
            elif subject == 'mathematics':
                if solution == "graph":
                    graphs = Graphs(request, subject, solution)
                    try:
                        image_buffer, formula = graphs.draw_graph_math()
                        if image_buffer and formula:
                            return image_buffer, f"График функции: {formula}"
                        else:
                            return "Не удалось построить график: недостаточно данных"
                    except Exception as e:
                        logger.error(f"Ошибка при построении графика: {e}")
                        return f"Не удалось построить график: {str(e)}"
                elif solution == None:
                    query = os.getenv("Mathematics_query") or ""
            elif subject == 'chatgpt':
                query = ""
            elif subject == 'question':
                solution_str = str(solution) if solution else ""
                query = solution_str + (os.getenv("Question_query") or "")
            elif subject == 'abstract':
                query = os.getenv("Abstract_query") or ""
            else:
                return "Неподдерживаемый предмет"

            prompt = f"{query}\n{request}"
            # Получаем ответ от модели
            logger.info(f"Финальный запрос: {prompt[:100]}...")
            
            if photo:
                response = self._get_response(prompt, image_data=photo)
            else:
                response = self._get_response(prompt)
            
            # Форматируем ответ для Telegram, преобразуя LaTeX и другие специальные символы
            formatted_response = self.format.format_response_for_telegram(response)

            return formatted_response
            
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса: {str(e)}", exc_info=True)
            return f"Произошла ошибка при обработке запроса: {str(e)}"

    # Загрузка переменных окружения
    # Сначала загружаем общие настройки
    load_dotenv()
    # Затем загружаем локальные настройки с приоритетом
    load_dotenv('.env.local', override=True)