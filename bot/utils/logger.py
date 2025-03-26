import logging
from logging.handlers import RotatingFileHandler
import os
import sys

def setup_logger(name="bot", level=logging.INFO):
    """
    Настройка логгера с ротацией файлов
    
    Args:
        name (str): Имя логгера
        level (int): Уровень логирования
        
    Returns:
        logging.Logger: Настроенный логгер
    """
    # Создаем директорию для логов, если её нет
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Настраиваем логгер
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Формат логов
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    
    # Обработчик для вывода в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Обработчик для записи в файл с ротацией
    # Максимальный размер файла - 10 МБ, максимальное количество файлов - 5
    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, f"{name}.log"),
        maxBytes=10*1024*1024,
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger
