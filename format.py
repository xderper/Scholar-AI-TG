import re
import html

class Format:

    def replace_subscript(self, text):
        self.superscript_map = {
            '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
            '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'
        }
        def subscript(match):
            # Преобразуем каждый символ в нижний индекс
            subscript_text = ''
            for char in match.group(1):
                if char.isdigit():
                    # Если это цифра, используем superscript_map
                    subscript_text += self.superscript_map[char]
                else:
                    # Для других символов используем специальные символы
                    subscript_map = {
                        # Латинские буквы
                        'a': 'ₐ', 'b': 'ᵦ', 'c': 'ᵣ', 'd': 'ᵈ', 'e': 'ₑ',
                        'f': 'ᶠ', 'g': 'ᵧ', 'h': 'ₕ', 'i': 'ᵢ', 'j': 'ⱼ',
                        'k': 'ₖ', 'l': 'ₗ', 'm': 'ₘ', 'n': 'ₙ', 'o': 'ₒ',
                        'p': 'ₚ', 'q': 'ᵩ', 'r': 'ᵣ', 's': 'ₛ', 't': 'ₜ',
                        'u': 'ᵤ', 'v': 'ᵥ', 'w': 'ʷ', 'x': 'ₓ', 'y': 'ᵧ',
                        'z': '₂',
                        'A': 'ₐ', 'B': 'ᵦ', 'C': 'ᵣ', 'D': 'ᵈ', 'E': 'ₑ',
                        'F': 'ᶠ', 'G': 'ᵧ', 'H': 'ₕ', 'I': 'ᵢ', 'J': 'ⱼ',
                        'K': 'ₖ', 'L': 'ₗ', 'M': 'ₘ', 'N': 'ₙ', 'O': 'ₒ',
                        'P': 'ₚ', 'Q': 'ᵩ', 'R': 'ᵣ', 'S': 'ₛ', 'T': 'ₜ',
                        'U': 'ᵤ', 'V': 'ᵥ', 'W': 'ʷ', 'X': 'ₓ', 'Y': 'ᵧ',
                        'Z': '₂',

                        # Русские буквы
                        'а': 'ₐ', 'б': 'ᵦ', 'в': 'ᵥ', 'г': 'ᵧ', 'д': 'ᵈ',
                        'е': 'ₑ', 'ё': 'ₑ', 'ж': 'ⱼ', 'з': '₂', 'и': 'ᵢ',
                        'й': 'ᵢ', 'к': 'ₖ', 'л': 'ₗ', 'м': 'ₘ', 'н': 'ₙ',
                        'о': 'ₒ', 'п': 'ₚ', 'р': 'ᵣ', 'с': 'ₛ', 'т': 'ₜ',
                        'у': 'ᵤ', 'ф': 'ᵣ', 'х': 'ₕ', 'ц': 'ₕ', 'ч': 'ₕ',
                        'ш': 'ₕ', 'щ': 'ₕ', 'ъ': 'ₕ', 'ы': 'ₕ', 'ь': 'ₕ',
                        'э': 'ₑ', 'ю': 'ᵤ', 'я': 'ₕ',

                        'А': 'ₐ', 'Б': 'ᵦ', 'В': 'ᵥ', 'Г': 'ᵧ', 'Д': 'ᵈ',
                        'Е': 'ₑ', 'Ё': 'ₑ', 'Ж': 'ⱼ', 'З': '₂', 'И': 'ᵢ',
                        'Й': 'ᵢ', 'К': 'ₖ', 'Л': 'ₗ', 'М': 'ₘ', 'Н': 'ₙ',
                        'О': 'ₒ', 'П': 'ₚ', 'Р': 'ᵣ', 'С': 'ₛ', 'Т': 'ₜ',
                        'У': 'ᵤ', 'Ф': 'ᵣ', 'Х': 'ₕ', 'Ц': 'ₕ', 'Ч': 'ₕ',
                        'Ш': 'ₕ', 'Щ': 'ₕ', 'Ъ': 'ₕ', 'Ы': 'ₕ', 'Ь': 'ₕ',
                        'Э': 'ₑ', 'Ю': 'ᵤ', 'Я': 'ₕ'
                    }
                    subscript_text += subscript_map.get(char, char)
            return subscript_text

        pattern = r'\{\{(.*?)\}\}'
        return re.sub(pattern, subscript, text)

    def safe_html_code(self, code_content):
        """
        Безопасно обрабатывает содержимое блока кода, экранируя HTML-теги
        
        Args:
            code_content (str): Содержимое блока кода
            
        Returns:
            str: Безопасное содержимое с экранированными HTML-тегами
        """
        # Экранируем HTML-теги, заменяя < на &lt; и > на &gt;
        return html.escape(code_content)

    def format_response_for_telegram(self, text):
        """
        Форматирует текст для лучшего отображения в Telegram
        
        Args:
            text (str): Исходный текст от ChatGPT

        Returns:
            str: Отформатированный текст для Telegram   
        """
        try:
            start_text = text
            # Check if text is None and handle accordingly
            if text is None:
                return "Не удалось получить ответ от сервера. Пожалуйста, попробуйте еще раз."
            
            # # Замена LaTeX команд
            text = text.replace("\\text", "")
            text = text.replace("\\textbf", "")
            text = text.replace("\\textit", "")
            
            # Форматирование ### заголовков в жирный шрифт
            text = re.sub(r'###\s*(.*?)($|\n)', r'<b>\1</b>\2', text)
            
            # Замена блоков кода с тройными обратными кавычками на HTML теги
            # С экранированием HTML-тегов внутри кода
            
            # Функция для обработки и экранирования кода
            def replace_code_block(match):
                lang = match.group(1) if len(match.groups()) > 1 else ""
                code = match.group(2) if len(match.groups()) > 1 else match.group(1)
                # Экранируем HTML в коде
                safe_code = self.safe_html_code(code)
                return f"<pre><code>{safe_code}</code></pre>"
            
            # Блоки кода с указанием языка
            text = re.sub(r'```([a-zA-Z0-9]*)\n(.*?)\n```', replace_code_block, text, flags=re.DOTALL)
            # Блоки кода без указания языка
            text = re.sub(r'```\n(.*?)\n```', replace_code_block, text, flags=re.DOTALL)
            # Однострочные блоки кода
            text = re.sub(r'```(.*?)```', replace_code_block, text, flags=re.DOTALL)
            
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
            text = text.replace("\\varphi", "φ")
            text = text.replace("varphi1", "φ₁")
            text = text.replace("\\omega", "ω")
            
            # Замена математических символов
            text = text.replace("\\times", "×")
            text = text.replace("\\cdot", "·")
            text = text.replace("\\left", "")
            text = text.replace("\\right", "")
            text = text.replace("\\frac", "")
            text = text.replace("\\dfrac", "")
            text = text.replace("\\tfrac", "")
            text = text.replace("\\circ", "°")
            text = text.replace("\\approx", "≈")
            text = text.replace("\\geq", "≥")
            text = text.replace("\\leq", "≤")
            text = text.replace("\\neq", "≠")
            
            # Общие правила форматирования математических формул
            text = text.replace("pm", "±")  # Плюс-минус
            text = text.replace("mp", "∓")  # Минус-плюс
            text = text.replace("cdot", "·")  # Точка умножения
            text = text.replace("times", "×")  # Крестик умножения
            text = text.replace("div", "÷")  # Знак деления
            text = text.replace("sqrt", "√")  # Корень квадратный
            text = text.replace("infty", "∞")  # Бесконечность
            text = text.replace("propto", "∝")  # Пропорционально
            text = text.replace("partial", "∂")  # Частная производная
            text = text.replace("nabla", "∇")  # Набла
            text = text.replace("exists", "∃")  # Существует
            text = text.replace("forall", "∀")  # Для всех
            text = text.replace("notin", "∉")  # Не принадлежит
            text = text.replace("subset", "⊂")  # Подмножество
            text = text.replace("supset", "⊃")  # Надмножество
            text = text.replace("cup", "∪")  # Объединение
            text = text.replace("cap", "∩")  # Пересечение
            text = text.replace("emptyset", "∅")  # Пустое множество
            text = text.replace("angle", "∠")  # Угол
            text = text.replace("perp", "⊥")  # Перпендикулярно
            text = text.replace("parallel", "∥")  # Параллельно
            text = text.replace("therefore", "∴")  # Следовательно
            text = text.replace("because", "∵")  # Потому что
            
            # Physics notation
            text = text.replace('⇒', '⇒')
            # Формула дискриминанта
            text = text.replace("x = -b ± √b² - 4ac2a", "x = (-b ± √(b² - 4ac))/(2a)")
            text = text.replace("x = -b pm √b² - 4ac2a", "x = (-b ± √(b² - 4ac))/(2a)")
            text = text.replace("ratic equation", "quadratic equation")
            text = text.replace("ratic formula", "quadratic formula")
            
            # Замена LaTeX-блоков на HTML код-блоки
            text = text.replace("\\[", "<pre><code>")
            text = text.replace("\\]", "</code></pre>")
            text = text.replace("\\(", "<code>")
            text = text.replace("\\)", "</code>") 
            
            # Замена frac на HTML дробь
            def replace_frac(match):
                numerator = match.group(1)
                denominator = match.group(2)
                return f'<code>{numerator}/{denominator}</code>'
            
            text = re.sub(r'frac\{([^\}]+)\}\{([^\}]+)\}', replace_frac, text)
            
            # Замена ^2 на верхний индекс
            text = text.replace("^2", "²")
            
            # Замена E_кин на Eₖᵢₙ
            text = text.replace("E_к", "Eₖ")
            text = text.replace("E_ки", "Eₖᵢ")
            text = text.replace("E_кин", "Eₖᵢₙ")
            
            text = self.replace_subscript(text)

            # Замена ** на <b> и </b>
            f = text.find("**")
            c = 0
            while f != -1:
                if c % 2 == 0:
                    text = text[:f] + "<b>" + text[f+2:]
                else:
                    text = text[:f] + "</b>" + text[f+2:]
                f = text.find("**")
                c += 1

            
            # Обработка степеней
            text = re.sub(r'(\\d+)\^(\\d+)', lambda m: f'{m.group(1)}<sup>{m.group(2)}</sup>', text)
            text = re.sub(r'([A-Za-zА-Яа-я])\^(\\d+)', lambda m: f'{m.group(1)}<sup>{m.group(2)}</sup>', text)

            # Замена стандартных заголовков на жирный шрифт
            text = text.replace("Дано:", "<b>Дано:</b>")
            text = text.replace("Найти:", "<b>Найти:</b>")
            text = text.replace("Решение:", "<b>Решение:</b>")
            text = text.replace("Ответ:", "<b>Ответ:</b>")

            text = text.replace("\\", "")
            text = text.replace("{", "")
            text = text.replace("}", "")
            text = text.replace("_", "")

            # Замена векторных обозначений
            text = text.replace("\\overrightarrow", "⃗")
            text = text.replace("overrightarrow", "⃗")
            text = text.replace("\\vec", "⃗")
            text = text.replace("vec", "⃗")

            # Замена матричных обозначений
            text = text.replace("\\beginvmatrix", "│")
            text = text.replace("beginvmatrix", "│")
            text = text.replace("\\endvmatrix", "│")
            text = text.replace("endvmatrix", "│")
            text = text.replace("&", " ")
            text = text.replace("\\quad", " ")
            text = text.replace("quad", " ")
            
            # Замена стрелок
            text = text.replace("\\Rightarrow", "⇒")
            text = text.replace("Rightarrow", "⇒")
           # Замена математических множеств и символов
            text = text.replace("\\mathbb{Z}", "ℤ")
            text = text.replace("\\mathbb{R}", "ℝ")
            text = text.replace("\\mathbb{N}", "ℕ")
            text = text.replace("\\mathbb{Q}", "ℚ")
            text = text.replace("\\in", "∈")
            text = text.replace("\\pi", "π")
            text = text.replace("\\sum", "∑")
            return text
            
        except Exception as e:
            # Улучшенное сообщение об ошибке с информацией о конкретной проблеме
            import traceback
            error_info = traceback.format_exc()
            logger.error(f"Error in format_response_for_telegram: {str(e)}")
            return start_text
