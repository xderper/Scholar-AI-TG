import matplotlib.pyplot as plt
import numpy as np
import io
from sympy import sympify, symbols, parse_expr
# Добавляем явный импорт lambdify
from sympy.utilities.lambdify import lambdify
import re

def clean_function_input(input_str):
    """
    Очищает и нормализует пользовательский ввод.
    """
    # Удаляем лишние пробелы и переводим в нижний регистр
    text = input_str.lower().strip()
    
    # Удаляем 'y = ' и 'f(x) = ' в начале выражения
    text = re.sub(r'^y\s*=\s*', '', text)
    text = re.sub(r'^f\s*\(\s*x\s*\)\s*=\s*', '', text)
    
    # Удаляем общие фразы и предлоги
    common_phrases = [
        "построй", "построить", "нарисуй", "нарисовать", 
        "график", "функция", "функции", "функцию"
    ]
    for phrase in common_phrases:
        text = text.replace(phrase, "").strip()
    
    # Замена распространенных математических выражений
    replacements = {
        "^": "**",  # Степень
        "корень": "sqrt",
        "квадрат": "**2",
        "куб": "**3",
        "синус": "sin",
        "косинус": "cos",
        "тангенс": "tan",
        "котангенс": "cot",
        "экспонента": "exp",
        "логарифм": "log",
        "модуль": "abs",
        "в квадрате": "**2",
        "в кубе": "**3",
        " х ": " x ",  # Замена русской х на английскую
        "пи": "pi",
        # Добавляем варианты для гиперболы
        "гипербола": "1/x",
        "обратная пропорциональность": "1/x",
        "k/x": "1/x",  # для случаев с коэффициентом k будет заменено на k*1/x
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Заменяем русскую 'х' на английскую 'x' (в любом контексте)
    text = text.replace('х', 'x')
    
    # Добавляем умножение между числом и x
    text = re.sub(r'(\d)([x])', r'\1*\2', text)
    text = re.sub(r'([x])(\d)', r'\1*\2', text)
    
    # Обработка степеней без пробелов (например, 2^2 -> 2**2)
    text = re.sub(r'(\d+)\^(\d+)', r'\1**\2', text)
    text = re.sub(r'([x])\^(\d+)', r'\1**\2', text)
    
    # Обработка гиперболы с коэффициентом (например, 2/x -> 2*(1/x))
    text = re.sub(r'(\d+)/x', r'\1*(1/x)', text)
    
    # Удаляем лишние пробелы
    text = text.replace(" ", "")
    
    return text

def generate_function_plot(function_str):
    try:
        # Очищаем текущий график
        plt.clf()
        
        # Очищаем и нормализуем ввод
        cleaned_function = clean_function_input(function_str)
        
        # Создаем переменную x для sympy
        x = symbols('x')
        
        try:
            # Парсим строку функции в математическое выражение
            expr = parse_expr(cleaned_function)
        except Exception as parse_error:
            raise ValueError(
                f"Не удалось распознать функцию. Пожалуйста, проверьте синтаксис.\n"
                f"Исходный ввод: {function_str}\n"
                f"Обработанный ввод: {cleaned_function}\n"
                f"Ошибка: {str(parse_error)}"
            )
        
        # Конвертируем sympy выражение в numpy функцию
        f = lambdify(x, expr, modules=['numpy'])
        
        # Создаем массив значений x
        x_vals = np.linspace(-10, 10, 1000)
        
        try:
            # Вычисляем значения y
            y_vals = f(x_vals)
            
            # Отфильтровываем бесконечные значения и NaN
            mask = np.isfinite(y_vals)
            x_vals = x_vals[mask]
            y_vals = y_vals[mask]
            
            # Если все значения отфильтрованы, выбрасываем ошибку
            if len(x_vals) == 0:
                raise ValueError("График содержит только бесконечные значения")
            
            # Создаем график
            plt.figure(figsize=(10, 6))
            plt.plot(x_vals, y_vals, 'b-', label=f'f(x) = {cleaned_function}')
            plt.grid(True)
            plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            plt.xlabel('x')
            plt.ylabel('y')
            plt.title(f'График функции: {cleaned_function}')
            plt.legend()
            
            # Устанавливаем разумные пределы для оси y
            y_min, y_max = np.percentile(y_vals[np.isfinite(y_vals)], [5, 95])
            y_range = y_max - y_min
            plt.ylim(y_min - 0.1 * y_range, y_max + 0.1 * y_range)
            
            # Сохраняем график в байтовый буфер
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            buf.seek(0)
            
            return buf, cleaned_function
            
        except Exception as calc_error:
            raise ValueError(f"Ошибка при вычислении значений функции: {str(calc_error)}")
            
    except Exception as e:
        raise ValueError(f"Ошибка при построении графика: {str(e)}")
    finally:
        plt.close('all')