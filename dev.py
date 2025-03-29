import os
import sys
import time
import subprocess
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Путь к директории проекта
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

class BotRestartHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.restart_bot()
        self.last_modified = time.time()
    
    def restart_bot(self):
        """Перезапускает бота"""
        # Если процесс уже запущен, останавливаем его
        if self.process and self.process.poll() is None:
            logger.info("Останавливаем бота...")
            self.process.terminate()
            self.process.wait()  # Ждем завершения процесса
        
        # Запускаем бота
        logger.info("Запускаем бота...")
        self.process = subprocess.Popen(
            [sys.executable, "run.py"],
            cwd=PROJECT_DIR
        )
    
    def on_modified(self, event):
        """Обработчик события изменения файла"""
        # Игнорируем изменения в файлах .pyc и временных файлах
        if event.src_path.endswith((".pyc", ".tmp", ".log")) or "__pycache__" in event.src_path or "temp" in event.src_path:
            return
        
        # Добавляем задержку для предотвращения множественных перезапусков
        if time.time() - self.last_modified < 1:
            return
        
        self.last_modified = time.time()
        logger.info(f"Обнаружено изменение в файле: {event.src_path}")
        self.restart_bot()
    
    def on_created(self, event):
        """Обработчик события создания файла"""
        # Игнорируем создание файлов .pyc и временных файлов
        if event.src_path.endswith((".pyc", ".tmp", ".log")) or "__pycache__" in event.src_path or "temp" in event.src_path:
            return
        
        # Добавляем задержку для предотвращения множественных перезапусков
        if time.time() - self.last_modified < 1:
            return
        
        self.last_modified = time.time()
        logger.info(f"Обнаружен новый файл: {event.src_path}")
        self.restart_bot()

def main():
    """Основная функция для запуска наблюдателя за файлами"""
    logger.info("Запуск режима разработки с автоматическим перезапуском...")
    
    # Создаем обработчик событий
    event_handler = BotRestartHandler()
    
    # Создаем наблюдателя
    observer = Observer()
    
    # Добавляем пути для наблюдения
    observer.schedule(event_handler, os.path.join(PROJECT_DIR, "bot"), recursive=True)
    observer.schedule(event_handler, PROJECT_DIR, recursive=False)
    
    # Запускаем наблюдателя
    observer.start()
    
    try:
        # Бесконечный цикл для работы наблюдателя
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Останавливаем наблюдателя при нажатии Ctrl+C
        logger.info("Остановка режима разработки...")
        if event_handler.process and event_handler.process.poll() is None:
            event_handler.process.terminate()
        observer.stop()
    
    # Ждем завершения наблюдателя
    observer.join()

if __name__ == "__main__":
    main()
