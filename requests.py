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
        
        # Создаем HTTP-клиент без прокси
        http_client = httpx.Client()
        
        # Инициализация клиента OpenAI
        self.openai_client = openai.OpenAI(
            api_key=self.openai_api_key,
            http_client=http_client
        )

        self.format = Format()
        logger.info("Инициализация класса Requests завершена")
    
    def _get_response(self, prompt, role="user", image_data=None):
        """
        Отправляет запрос к ChatGPT и возвращает ответ
        
        Args:
            prompt (str): Текст запроса к модели
            role (str): Роль, которая будет использоваться в запросе
            image_data (str, optional): Base64-кодированное изображение
        Returns:
            str: Ответ от модели
        """
        try:
            logger.info(f"Начало отправки запроса к ChatGPT")
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
            
            # Отправка запроса к ChatGPT
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Используем модель GPT-4o
                messages=messages,
                temperature=0.2,  # Настройка креативности (0.0 - 1.0)
                max_tokens=2000,  # Максимальная длина ответа
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            logger.info(f"Запрос к ChatGPT успешно выполнен")
            
            # Возвращаем текст ответа
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Ошибка при запросе к ChatGPT: {str(e)}")
            # В случае ошибки возвращаем сообщение об ошибке
            return f"Произошла ошибка при запросе к ChatGPT: {str(e)}"
    
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
            
            # Формируем базовый запрос
            base_prompt = self.physic_query
            
            # Если это изображение, отправляем его в запросе
            if photo:
                logger.info("Отправка запроса с изображением")
                response = self._get_response(
                    prompt=base_prompt,
                    role="system",
                    image_data=request
                )
            else:
                logger.info("Отправка текстового запроса")
                response = self._get_response(
                    prompt=f"{base_prompt} {request}",
                    role="system"
                )
            
            logger.info("Форматирование ответа")
            # Форматируем ответ для Telegram
            formatted_response = self.format.format_response_for_telegram(response)
            
            logger.info("Обработка запроса завершена")
            return formatted_response
            
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса: {str(e)}")
            # В случае ошибки возвращаем сообщение об ошибке
            return f"Произошла ошибка при запросе к ChatGPT: {str(e)}"

    # Загрузка переменных окружения
    load_dotenv()
    load_dotenv('.env.local', override=True)  # Приоритет локальным настройкам
