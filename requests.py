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
            # logger.info(f"Отправка запроса к OpenAI. Длина запроса: {len(prompt) символов")
            
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
                model="gpt-4o",
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
            
            # logger.info(f"Получен ответ от OpenAI. Длина ответа: {len(response.choices[0].message.content)} символов")
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Ошибка при запросе к OpenAI: {str(e)}")
            raise
    
    def main(self, request: str, subject: str, photo: bool = False, solution: str = None) -> Union[str, Tuple[BinaryIO, str]]:
        """
        Основной метод для обработки запросов по различным предметам
        
        Args:
            request (str): Запрос пользователя
            subject (str): Предмет (physics, chemistry, math)
            photo (bool): Флаг, указывающий, что запрос содержит изображение
            solution (str): Тип решения (например, "graph" для построения графика)
            
        Returns:
            Union[str, Tuple[BinaryIO, str]]: Отформатированный ответ для Telegram или кортеж (изображение, подпись)
        """
        try:


            print(subject, solution)
            # Получаем соответствующий запрос для выбранного предмета из переменных окружения
            if subject == 'physics':
                query = os.getenv("Physic_query")   
            elif subject == 'chemistry':
                query = os.getenv("Chemistry_query")
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
                    query = os.getenv("Mathematics_query")
            elif subject == 'chatgpt':
                query = ""
            elif subject == 'question':
                query = str(solution) + os.getenv("Question_query")
            elif subject == 'abstract':
                query = os.getenv("Abstract_query")
            else:
                return "Неподдерживаемый предмет"

            # Получаем ответ от модели
            if photo:
                response = self._get_response(query, image_data=request)
            else:
                prompt = f"{query}\n{request}"
                response = self._get_response(prompt)
            
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