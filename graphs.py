import matplotlib.pyplot as plt
import numpy as np
import io
from sympy import sympify, symbols, parse_expr, sin, cos, tan, cot, asin, acos, atan, acot, pi, sqrt, log, Abs, Piecewise, solve
from sympy.utilities.lambdify import lambdify
import re
from formula_utils import FormulaUtils

class Graphs:
    def __init__(self, request, section, solution):
        self.request = request
        self.formula_utils = FormulaUtils()

        if (section == "mathematics" and solution == "graph"):
            self.formula = self.formula_utils.get_formula(self.request)
            self.clean_formula()
            self.draw_graph_math()

    def draw_graph_math(self):
        try:
            # Очищаем текущий график
            plt.clf()
            
            # Очищаем и нормализуем ввод
            cleaned_function = self.clean_formula()
            
            # Создаем переменную x для sympy
            x = symbols('x')
            
            try:
                # Парсим строку функции в математическое выражение
                expr = parse_expr(cleaned_function)
            except Exception as parse_error:
                raise ValueError(
                    f"Не удалось распознать функцию. Пожалуйста, проверьте синтаксис.\n"
                    f"Исходный ввод: {self.formula}\n"
                    f"Обработанный ввод: {cleaned_function}\n"
                    f"Ошибка: {str(parse_error)}"
                )
            
            # Конвертируем sympy выражение в numpy функцию с поддержкой тригонометрических функций
            try:
                f = lambdify(x, expr, modules=['numpy', {'Abs': np.abs}])
            except Exception as lambdify_error:
                raise ValueError(f"Ошибка при конвертации функции: {str(lambdify_error)}")
            
            # Находим вершину параболы, если это квадратичная функция
            def find_parabola_vertex(expr):
                try:
                    # Проверяем, является ли функция квадратичной
                    if expr.as_poly(x).degree() == 2:
                        # Находим производную
                        derivative = expr.diff(x)
                        # Находим корень производной (x-координата вершины)
                        x_vertex = float(solve(derivative, x)[0])
                        # Находим y-координату вершины
                        y_vertex = float(expr.subs(x, x_vertex))
                        return x_vertex, y_vertex
                except:
                    pass
                return None
            
            # Получаем координаты вершины
            vertex = find_parabola_vertex(expr)
            
            # Создаем массив значений x
            if vertex is not None:
                # Если это парабола, центрируем график вокруг вершины
                x_vertex, y_vertex = vertex
                x_range = 5  # Диапазон по x в обе стороны от вершины
                x_vals = np.linspace(x_vertex - x_range, x_vertex + x_range, 1000)
            else:
                # Для других функций используем стандартный диапазон
                if any(func in cleaned_function for func in ['sin', 'cos', 'tan', 'cot']):
                    x_vals = np.linspace(-2*np.pi, 2*np.pi, 1000)
                else:
                    x_vals = np.linspace(-5, 5, 1000)
            
            try:
                # Вычисляем значения y
                y_vals = f(x_vals)
                
                # Проверяем тип результата
                if not isinstance(y_vals, np.ndarray):
                    y_vals = np.array(y_vals, dtype=float)
                
                # Проверяем, что все значения являются числами
                if not np.issubdtype(y_vals.dtype, np.number):
                    raise ValueError("Функция вернула нечисловые значения")
                
                # Отфильтровываем бесконечные значения и NaN
                mask = np.isfinite(y_vals)
                if not np.any(mask):
                    raise ValueError("Все значения функции являются бесконечными или NaN")
                
                x_vals = x_vals[mask]
                y_vals = y_vals[mask]
                
                # Создаем график
                fig = plt.figure(figsize=(10, 10))
                ax = fig.add_subplot(1, 1, 1)
                ax.set_aspect('equal', adjustable='datalim')
                
                # Настраиваем оси
                ax.spines['left'].set_position('zero')
                ax.spines['bottom'].set_position('zero')
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)
                
                # Рисуем график
                ax.plot(x_vals, y_vals, 'b-', label=f'f(x) = {self.formula}')
                ax.grid(True, which='major', color='#cccccc', linestyle='--', linewidth=0.7, alpha=0.7)
                
                # Добавляем дополнительные линии сетки для единичных отрезков
                if vertex is not None:
                    # Для параболы делаем диапазон по x шире, по y уже
                    x_range = 5
                    y_range = 7
                    plt.xlim(x_vertex - x_range, x_vertex + x_range)
                    plt.ylim(y_vertex - y_range, y_vertex + y_range)
                    # Сетка и подписи через 1
                    ax.set_xticks(np.arange(int(x_vertex - x_range), int(x_vertex + x_range) + 1, 1))
                    ax.set_yticks(np.arange(int(y_vertex - y_range), int(y_vertex + y_range) + 1, 1))
                else:
                    ax.set_xticks(np.arange(-5, 6, 1))
                    ax.set_yticks(np.arange(-5, 6, 1))
                
                # Добавляем стрелки на концах осей
                ax.plot((1), (0), '>k', transform=ax.get_yaxis_transform(), clip_on=False)
                ax.plot((0), (1), '^k', transform=ax.get_xaxis_transform(), clip_on=False)
                
                # Подписи осей
                ax.set_xlabel('x', x=1.0, horizontalalignment='left')
                ax.set_ylabel('y', y=1.0, horizontalalignment='left')
                
                # Заголовок и легенда
                plt.title(f'График функции: {self.formula}', fontsize=18, y=1.08)
                plt.legend(loc='upper left')
                
                # Определяем пределы для осей
                if vertex is not None:
                    # Для параболы делаем диапазон по x шире, по y уже
                    x_range = 5
                    y_range = 7
                    plt.xlim(x_vertex - x_range, x_vertex + x_range)
                    plt.ylim(y_vertex - y_range, y_vertex + y_range)
                elif any(func in cleaned_function for func in ['sin', 'cos']):
                    limit = 2*np.pi
                    plt.xlim(-limit, limit)
                    plt.ylim(-limit, limit)
                else:
                    # Находим максимальные значения по обеим осям
                    max_abs_x = min(5, np.max(np.abs(x_vals)))
                    max_abs_y = min(5, np.max(np.abs(y_vals[np.isfinite(y_vals)])))
                    limit = max(max_abs_x, max_abs_y)
                    plt.xlim(-limit, limit)
                    plt.ylim(-limit, limit)
                
                # Сохраняем график в байтовый буфер с увеличенным DPI для четкости
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', pad_inches=0.1)
                buf.seek(0)
                
                return buf, self.formula
                
            except Exception as calc_error:
                raise ValueError(f"Ошибка при вычислении значений функции: {str(calc_error)}")
        
        except Exception as e:
            raise ValueError(f"Ошибка при построении графика: {str(e)}")
        finally:
            plt.close('all')

    def clean_formula(self):
        """Очищает формулу от лишних символов и HTML-тегов"""
        formula = self.formula.replace("<b>", "").replace("</b>", "")  # удаляем HTML теги
        
        # Заменяем надстрочные цифры на **n
        formula = formula.replace("²", "**2")
        formula = formula.replace("³", "**3")
        formula = formula.replace("⁴", "**4")
        formula = formula.replace("⁵", "**5")
        formula = formula.replace("⁶", "**6")
        formula = formula.replace("⁷", "**7")
        formula = formula.replace("⁸", "**8")
        formula = formula.replace("⁹", "**9")
        
        # Заменяем ^ на **
        formula = formula.replace("^", "**")
        
        # Обработка модулей
        # Заменяем |x| на Abs(x)
        formula = re.sub(r'\|([^|]+)\|', r'Abs(\1)', formula)
        
        # Добавляем умножение между числом и x, если его нет
        formula = re.sub(r'(\d)x', r'\1*x', formula)
        
        formula = formula.strip()
        self.formula = formula
        return formula