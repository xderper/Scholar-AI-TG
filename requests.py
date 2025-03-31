import os
import httpx
import openai
from dotenv import load_dotenv
from format import Format
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Requests:
    def __init__(self):
        self.physic_query = os.getenv("Physic_query")
        self.mathematic_query = os.getenv("Mathematic_query")
        
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
        logger.info("Инициализация класса Requests завершена")
    
    def _get_response(self, prompt, role="user", image_data=None):
        """
        Отправляет запрос к OpenAI и возвращает ответ
        
        Args:
            prompt (str): Текст запроса к модели
            role (str): Роль, которая будет использоваться в запросе
            image_data (str, optional): Base64-кодированное изображение
        Returns:
            str: Ответ от модели
        """
        try:
            logger.info(f"Начало отправки запроса к OpenAI")
            logger.info(f"Тип запроса: {'изображение' if image_data else 'текст'}")
            
            # Формируем сообщения для запроса
            messages = [
                {"role": role, "content": prompt}
            ]
            
            # Если есть изображение, добавляем его в запрос
            if image_data:
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Решите задачу по физике с изображения"},
                        {"type": "image_url", "image_url": {"url": image_data}}
                    ]
                })
            
            # Отправка запроса к OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.2,
                max_tokens=2000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            logger.info(f"Запрос к OpenAI успешно выполнен")
            
            # Возвращаем текст ответа
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Ошибка при запросе к OpenAI: {str(e)}")
            return f"Произошла ошибка при запросе к OpenAI: {str(e)}"
    
    def physics(self, request, photo=False):
        """
        Метод для обработки запросов по физике
        
        Args:
            request (str): запрос
            photo (bool): Флаг, указывающий, что запрос пришел от фотографии
            
        Returns:
            str: Отформатированный ответ для Telegram
        """
        try:
            logger.info(f"Начало обработки запроса по физике")
            logger.info(f"Тип запроса: {'изображение' if photo else 'текст'}")
            
            # Формируем запрос к модели
            prompt = f"{self.physic_query}\n{request}"
            
            # Получаем ответ от модели
            if photo:
                response = self._get_response(prompt, image_data=request)
            else:
                response = self._get_response(prompt)
            
            # Форматируем ответ для Telegram
            formatted_response = self.format.format_response_for_telegram(response)
            
            logger.info(f"Завершение обработки запроса по физике. Длина ответа: {len(formatted_response)} символов")
            return formatted_response
            
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса по физике: {str(e)}")
            return f"Произошла ошибка при обработке запроса: {str(e)}"

    def mathematics(self, request):
        """
        Метод для обработки математических запросов
        
        Args:
            request (str): запрос
            
        Returns:
            str: Отформатированный ответ для Telegram
        """
        try:
            logger.info(f"Начало обработки математического запроса")
            
            # Формируем запрос к модели
            prompt = f"{self.mathematic_query}\n{request}"
            
            # Получаем ответ от модели
            response = self._get_response(prompt)
            
            # Форматируем ответ для Telegram
            formatted_response = self.format.format_response_for_telegram(response)
            
            logger.info(f"Завершение обработки математического запроса. Длина ответа: {len(formatted_response)} символов")
            return formatted_response
            
        except Exception as e:
            logger.error(f"Ошибка при обработке математического запроса: {str(e)}")
            return f"Произошла ошибка при обработке запроса: {str(e)}"

    # Загрузка переменных окружения
    load_dotenv()
    load_dotenv('.env.local', override=True)  # Приоритет локальным настройкам
