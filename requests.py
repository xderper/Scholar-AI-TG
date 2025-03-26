import os
import httpx
import openai
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
load_dotenv('.env.local', override=True)  # Приоритет локальным настройкам

class Requests:
    def __init__(self):
        self.physic_query = os.getenv("Physic_query")
        
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
    
    def _get_response(self, prompt, role = "user"):
        """
        Отправляет запрос к ChatGPT и возвращает ответ
        
        Args:
            prompt (str): Текст запроса к модели
            role (str): Роль, которая будет использоваться в запросе
        Returns:
            str: Ответ от модели
        """
        try:
            # Отправка запроса к ChatGPT
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Используем модель GPT-4o
                messages=[
                    {"role": role, "content": prompt}
                ],
                temperature=0.2,  # Настройка креативности (0.0 - 1.0)
                max_tokens=2000,  # Максимальная длина ответа
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Возвращаем текст ответа
            return response.choices[0].message.content
        except Exception as e:
            # В случае ошибки возвращаем сообщение об ошибке
            return f"Произошла ошибка при запросе к ChatGPT: {str(e)}"
    
    def physic(self, text):
        system_message = "Вы опытный учитель физики, который помогает ученикам решать задачи."
        prompt = f"{self.physic_query} {text}"
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",  # Используем модель GPT-4o
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Настройка креативности (0.0 - 1.0)
            max_tokens=2000,  # Максимальная длина ответа
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        
        # Возвращаем текст ответа
        return response.choices[0].message.content