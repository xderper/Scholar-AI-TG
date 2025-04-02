import re
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

    def format_response_for_telegram(self, text):
        """
        Форматирует текст для лучшего отображения в Telegram
        
        Args:
            text (str): Исходный текст от ChatGPT

        Returns:
            str: Отформатированный текст для Telegram   
        """
        try:


            # # Базовая очистка
            # text = text.removeprefix("Ответ: ")
            
            # # Замена LaTeX команд
            text = text.replace("\\text", "")
            text = text.replace("\\textbf", "")
            text = text.replace("\\textit", "")
            


            
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
            text = text.replace("\\circ", "°")
            text = text.replace("\\approx", "≈")
            text = text.replace("\\geq", "≥")
            text = text.replace("\\leq", "≤")
            text = text.replace("\\neq", "≠")
            
            # Physics notation
            text = text.replace('⇒', '⇒')
            
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


            return text
            
        except Exception as e:
            # Улучшенное сообщение об ошибке с информацией о конкретной проблеме
            import traceback
            error_info = traceback.format_exc()
            return f"Ошибка форматирования: {str(e)}\nПодробности:\n{error_info[:200]}...\n\nИсходный текст:\n{text}"
