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
from typing import Optional, Tuple, Union, Dict, Any, BinaryIO, List

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
    
    def _transcribe_audio(self, audio_file_path: str) -> str:
        """
        Транскрибирует аудио файл с помощью OpenAI Whisper API
        
        Args:
            audio_file_path (str): Путь к аудио файлу
            
        Returns:
            str: Транскрипция аудио или пустая строка в случае ошибки
        """
        try:
            logger.info(f"Отправка аудио на транскрипцию: {audio_file_path}")
            
            # Проверяем существование файла
            if not os.path.exists(audio_file_path):
                logger.error(f"Аудио файл не найден: {audio_file_path}")
                return ""
                
            # Открываем файл для отправки в Whisper API
            with open(audio_file_path, "rb") as audio_file:
                # Используем модель whisper для транскрипции
                transcript_response = self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            
            # Получаем текст транскрипции
            transcript_text = transcript_response.text
            
            if transcript_text and len(transcript_text.strip()) > 0:
                logger.info(f"Аудио успешно транскрибировано: {transcript_text[:100]}...")
                return transcript_text
            else:
                logger.warning("Аудио файл транскрибирован, но текст пустой")
                return ""
                
        except Exception as e:
            logger.error(f"Ошибка при транскрипции аудио: {str(e)}", exc_info=True)
            return ""
    
    def _get_response(self, prompt, image_data=None, audio_data=None):
        """
        Отправляет запрос к OpenAI API
        
        Args:
            prompt (str): Текстовый запрос
            image_data (str, optional): URL изображения для обработки
            audio_data (str, optional): Аудио данные для обработки
            
        Returns:
            str: Ответ от модели
        """
        try:
            logger.info(f"Отправка запроса к OpenAI. Текст: {prompt[:50]}...")
            
            # Подготовка содержимого сообщения
            content: List[Dict[str, Any]] = [{"type": "text", "text": prompt}]
            
            # Добавляем изображение, если оно есть
            if image_data:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image_data
                    }
                })
                logger.info("Добавлено изображение к запросу")
            
            # Добавляем аудио, если оно есть - исправленный формат
            if audio_data:
                # Используем правильный тип 'file' или 'audio' вместо 'audio_url'
                content.append({
                    "type": "file",  # или "audio" в зависимости от версии API
                    "file_id": {
                        "file_id": audio_data
                    }
                })
                logger.info("Добавлено аудио к запросу")
                
            # Формируем сообщение с мультимедиа контентом
            messages = [{"role": "user", "content": content}]
            
            # Удаляем поддержку аудио, пока не будет доступна официальная поддержка от OpenAI
            if audio_data:
                logger.warning("Поддержка аудио временно отключена - отправляем только текст и изображение")
                # Создаем новый content только с текстом и изображением
                filtered_content = [item for item in content if item["type"] in ["text", "image_url"]]
                messages = [{"role": "user", "content": filtered_content}]
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=2000,
                temperature=0.2
            )
            
            logger.info(f"Получен ответ от OpenAI. Длина ответа: {len(response.choices[0].message.content)} символов")
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Ошибка при запросе к OpenAI: {str(e)}", exc_info=True)
            # Если ошибка связана с аудио, попробуем запрос без аудио
            if audio_data and "audio" in str(e).lower():
                logger.info("Повторная попытка без аудио данных")
                return self._get_response(prompt, image_data=image_data)
            raise
    
    def main(self, request: str = None, subject: str = None, photo=None, audio=None, solution: str = None) -> Union[str, Tuple[BinaryIO, str]]:
        """
        Основной метод для обработки запросов по различным предметам
        
        Args:
            request (str): Запрос пользователя
            subject (str): Предмет (physics, chemistry, math)
            photo: Данные изображения в формате base64 или None
            audio: Путь к аудио файлу или данные аудио в формате base64
            solution (str): Тип решения (например, "graph" для построения графика)
            
        Returns:
            Union[str, Tuple[BinaryIO, str]]: Отформатированный ответ для Telegram или кортеж (изображение, подпись)
        """
        try:
            # Сначала проверяем, не является ли это запросом только с аудио 
            # для транскрипции без других параметров
            if audio and not subject and not photo and not request:
                # Это запрос только на транскрипцию аудио
                transcript = self._transcribe_audio(audio)
                if transcript:
                    return transcript
                else:
                    return "Не удалось расшифровать аудиозапись. Пожалуйста, убедитесь, что запись содержит речь на понятном языке."
            
            # Если есть аудио и это файл, то сначала транскрибируем его
            if audio and isinstance(audio, str) and os.path.exists(audio):
                transcript = self._transcribe_audio(audio)
                if transcript:
                    # Если это первый запрос и транскрипция получена, возвращаем ее напрямую
                    if not request:
                        return transcript
                    # Если есть запрос, добавляем транскрипцию к запросу
                    request = f"{request}\n\nТранскрипция аудио: {transcript}"
                    logger.info(f"Добавлена транскрипция аудио к запросу: {transcript[:50]}...")
            
            # Проверка на пустой запрос
            if not request:
                request = "Помоги мне с этим заданием."
                
            # Если предмет не указан, используем chatgpt по умолчанию
            if not subject:
                subject = 'chatgpt'
                
            has_media = photo is not None or audio is not None
            logger.info(f"Обработка запроса. Предмет: {subject}, Решение: {solution}, Фото: {'Да' if photo else 'Нет'}, Аудио: {'Да' if audio else 'Нет'}")
            
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

            prompt = f"{query}\n{request}" if query else request
            # Получаем ответ от модели
            logger.info(f"Финальный запрос: {prompt[:100]}...")
            
            # Отправляем запрос только с изображением, аудио уже обработано отдельно
            response = self._get_response(prompt, image_data=photo, audio_data=None)
            
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