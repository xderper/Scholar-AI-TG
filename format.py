class Format:
    def __init__(self):
        # Словарь для преобразования цифр в верхний индекс
        self.superscript_map = {
            '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
            '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
        }

    def _to_superscript(self, number):
        """
        Преобразует число в верхний индекс (суперскрипт)
        
        Args:
            number (str): Число для преобразования
            
        Returns:
            str: Число в виде верхнего индекса
        """
        return ''.join(self.superscript_map[digit] for digit in number)

    def format_response_for_telegram(self, text):
        """
        Форматирует текст для лучшего отображения в Telegram
        
        Args:
            text (str): Исходный текст от ChatGPT

        Returns:
            str: Отформатированный текст для Telegram   
        """
        try:
            import re

            # Базовая очистка
            text = text.removeprefix("Ответ: ")
            
            # Замена LaTeX команд
            text = text.replace("\\text", "")
            text = text.replace("\\textbf", "")
            text = text.replace("\\textit", "")
            text = text.replace("\\frac", "")
            text = text.replace("\\sqrt", "√")
            text = text.replace("\\theta", "θ")
            text = text.replace("\\alpha", "α")
            text = text.replace("\\beta", "β")
            text = text.replace("\\gamma", "γ")
            text = text.replace("\\delta", "δ")
            text = text.replace("\\epsilon", "ε")
            text = text.replace("\\zeta", "ζ")
            text = text.replace("\\eta", "η")
            text = text.replace("\\lambda", "λ")
            text = text.replace("\\mu", "μ")
            text = text.replace("\\pi", "π")
            text = text.replace("\\rho", "ρ")
            text = text.replace("\\sigma", "σ")
            text = text.replace("\\tau", "τ")
            text = text.replace("\\phi", "φ")
            text = text.replace("\\omega", "ω")
            
            # Замена математических символов
            text = text.replace("\\times", "×")
            text = text.replace("\\cdot", "·")
            text = text.replace("\\circ", "°")
            text = text.replace("\\approx", "≈")
            text = text.replace("\\geq", "≥")
            text = text.replace("\\leq", "≤")
            text = text.replace("\\neq", "≠")
            
            # Удаление специальных символов
            text = text.replace("*", "")
            text = text.replace("/", "")    
            text = text.replace("[", "")
            text = text.replace("]", "")
            text = text.replace("{", "")
            text = text.replace("}", "")
            text = text.replace("\\", "")
            text = text.replace("(", "")
            text = text.replace(")", "")
            
            # Обработка индексов
            text = re.sub(r'([A-Za-zА-Яа-я])_([A-Za-zА-Яа-я0-9]+)', r'\1₍\2₎', text)
            
            # Обработка степеней
            text = re.sub(r'(\d+)\^(\d+)', lambda m: f'{m.group(1)}{self._to_superscript(m.group(2))}', text)
            text = re.sub(r'([A-Za-zА-Яа-я])\^(\d+)', lambda m: f'{m.group(1)}{self._to_superscript(m.group(2))}', text)

            # Форматирование разделов
            section_headers = ["Дано:", "Найти:", "Решение:", "По закону сохранения энергии:", 
                              "Ответ:", "Вывод:", "Решим задачу:", "Вычисления:", "Пример:", 
                              "Примечание:", "Вопрос:", "Анализ:", "Проверка:"]
            
            for section in section_headers:
                text = text.replace(section, f"\n{section}\n")

            return text
            
        except Exception as e:
            # Улучшенное сообщение об ошибке с информацией о конкретной проблеме
            import traceback
            error_info = traceback.format_exc()
            return f"Ошибка форматирования: {str(e)}\nПодробности:\n{error_info[:200]}...\n\nИсходный текст:\n{text}"