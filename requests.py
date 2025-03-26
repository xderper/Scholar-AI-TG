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
        """
        Метод для обработки запросов по физике
        
        Args:
            text (str): Текст запроса пользователя
            
        Returns:
            str: Отформатированный ответ для Telegram
        """
        system_message = "Вы опытный учитель физики, который помогает ученикам решать задачи."
        prompt = f"{self.physic_query} {text}"
        
        try:
            # Отправляем запрос к ChatGPT
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
            
            # Получаем текст ответа
            response_text = response.choices[0].message.content
            
            # Форматируем ответ для Telegram
            formatted_response = self.format_response_for_physic_telegram(response_text)
            
            return formatted_response
            
        except Exception as e:
            # В случае ошибки возвращаем сообщение об ошибке
            return f"Произошла ошибка при запросе к ChatGPT: {str(e)}"

    def format_response_for_physic_telegram(self, text):
        """
        Форматирует текст для лучшего отображения в Telegram
        
        Args:
            text (str): Исходный текст от ChatGPT
    
        Returns:
            str: Отформатированный текст для Telegram   
        """
        try:
            # Используем более простой подход к форматированию
            # Telegram поддерживает только <b>, <i>, <code>, <pre>, <a>
            
            # Сначала удалим все LaTeX-разметки
            text = text.replace('\\(', '').replace('\\)', '')
            text = text.replace('\\{', '{').replace('\\}', '}')
            text = text.replace('\\text{', '').replace('}', '')
            text = text.replace('\\frac{', '').replace('}{', '/').replace('}', '')
            text = text.replace('\\theta', 'θ')
            text = text.replace('\\circ', '°')
            text = text.replace('\\approx', '≈')
            text = text.replace('\\sqrt{', '√(').replace('}', ')')
            
            # Заменяем другие математические символы
            text = text.replace('\\times', '×')
            text = text.replace('\\cdot', '·')
            text = text.replace('\\pi', 'π')
            text = text.replace('\\alpha', 'α')
            text = text.replace('\\beta', 'β')
            text = text.replace('\\gamma', 'γ')
            text = text.replace('\\Delta', 'Δ')
            text = text.replace('\\delta', 'δ')
            text = text.replace('\\lambda', 'λ')
            text = text.replace('\\omega', 'ω')
            text = text.replace('\\infty', '∞')
            text = text.replace('\\pm', '±')
            text = text.replace('\\geq', '≥')
            text = text.replace('\\leq', '≤')
            text = text.replace('\\neq', '≠')
        
            # Заменим ** на <b></b> только если они идут парами
            parts = text.split('**')
            if len(parts) > 1 and len(parts) % 2 == 1:  # Проверяем, что ** идут парами
                for i in range(1, len(parts), 2):
                    parts[i] = f"<b>{parts[i]}</b>"
                text = ''.join(parts)
            
            import re
            
            # Добавляем переносы строк для лучшей читаемости
            text = text.replace('. ', '.\n')
            
            # Выделяем заголовки жирным шрифтом
            for section in ["Дано:", "Найти:", "Решение:", "По закону сохранения энергии:", "Ответ:"]:
                text = text.replace(section, f"\n<b>{section}</b>\n")
            
            # Разделяем пункты решения пустыми строками, но оставляем цифру на той же строке
            for i in range(1, 10):
                # Заменяем формат "1. Текст" на "\n1. Текст"
                text = text.replace(f"\n{i}. ", f"\n{i}. ")
                # Заменяем формат "1. Текст" на "1. Текст" (без переноса между цифрой и текстом)
                text = text.replace(f"{i}. ", f"<b>{i}.</b> ")
            
            # Заменяем формулы энергии на более читаемый формат
            text = text.replace('E_{пот}', 'E пот')
            text = text.replace('E_{кин}', 'E кин')
            text = text.replace('F_{разр}', 'F разр')
            
            # Заменяем подстрочные индексы на обычный текст
            text = re.sub(r'([A-Za-z])_([A-Za-z0-9]+)', r'\1\2', text)
            
            # Заменяем надстрочные индексы
            text = re.sub(r'([A-Za-z0-9])(\^)([0-9])', r'\1\3', text)
            
            # Удаляем лишние пробелы и переносы строк
            text = re.sub(r'\n\s*\n', '\n\n', text)
            
            # Удаляем все оставшиеся HTML-теги, кроме <b> и <i>
            text = re.sub(r'<(?!/?b>|/?i>)[^>]+>', '', text)
            
            return text
        except Exception as e:
            # В случае ошибки форматирования возвращаем исходный текст
            return f"Ошибка форматирования: {str(e)}\n\n{text}"