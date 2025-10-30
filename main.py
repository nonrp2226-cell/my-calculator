import operator
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.utils import get_color_from_hex


class SafeCalculator:
    operators = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv
    }

    @staticmethod
    def calculate(expr):
        tokens = []
        num = ''
        for c in expr:
            if c.isdigit() or c == '.':
                num += c
            elif c in SafeCalculator.operators:
                if num == '':
                    return None
                tokens.append(float(num))
                tokens.append(c)
                num = ''
            else:
                return None
        if num != '':
            tokens.append(float(num))
        if not tokens:
            return None

        result = tokens[0]
        i = 1
        while i < len(tokens):
            op = tokens[i]
            num = tokens[i + 1]
            try:
                result = SafeCalculator.operators[op](result, num)
            except ZeroDivisionError:
                return 'Ошибка'
            i += 2

        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        return str(result)


class ModernSamsungCalculator(App):
    def build(self):
        Window.clearcolor = get_color_from_hex("#1E1E1E")
        self.expression = ""
        self.error_state = False

        main_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Дисплей с фиксированным размером текста
        self.display = Label(
            text="",
            font_size=120,  # всегда стандартный размер
            halign="right",
            valign="center",
            size_hint=(1, 0.25),
            color=(1, 1, 1, 1),
        )
        self.display.bind(size=self._update_text_size)
        main_layout.add_widget(self.display)

        # Кнопки
        buttons = [
            ["C", "%", "÷", "У"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["+/-", "0", ",", "="]
        ]

        button_grid = GridLayout(cols=4, spacing=5, size_hint=(1, 0.75))

        for row in buttons:
            for char in row:
                bg_color = get_color_from_hex("#333333")
                fg_color = (1, 1, 1, 1)
                if char == "C":
                    fg_color = get_color_from_hex("#FF5C5C")
                elif char == "У":
                    fg_color = get_color_from_hex("#AAAAAA")
                elif char in "÷×-+%=":
                    fg_color = get_color_from_hex("#00E676")

                btn = Button(
                    text=char,
                    background_normal="",
                    background_color=bg_color,
                    color=fg_color,
                    font_size="32sp",
                    bold=True,
                    on_release=lambda instance, ch=char: self.on_click(ch)
                )
                button_grid.add_widget(btn)

        main_layout.add_widget(button_grid)
        return main_layout

    def _update_text_size(self, *args):
        self.display.text_size = self.display.size

    def format_number(self, text):
        """Добавляет пробелы для чисел"""
        if not text:
            return ""
        formatted = ""
        temp = ""
        for c in text:
            if c.isdigit() or c == '.':
                temp += c
            else:
                if temp:
                    formatted += self.add_spaces(temp)
                    temp = ""
                formatted += c
        if temp:
            formatted += self.add_spaces(temp)
        return formatted

    @staticmethod
    def add_spaces(num_str):
        if "." in num_str:
            integer, fractional = num_str.split(".")
        else:
            integer, fractional = num_str, ""
        integer = integer.replace(" ", "")
        integer_formatted = ""
        for i, digit in enumerate(reversed(integer)):
            if i != 0 and i % 3 == 0:
                integer_formatted = " " + integer_formatted
            integer_formatted = digit + integer_formatted
        if fractional:
            return integer_formatted + "." + fractional
        return integer_formatted

    def update_display(self):
        text = self.format_number(self.expression)
        self.display.text = text

    def on_click(self, char):
        # Пасхалка: 3914+×=
        if self.expression.endswith("3914+×") and char == "=":
            self.expression = "Шалунишка"
            self.error_state = True
            self.update_display()
            return

        if char == "C":
            self.expression = ""
            self.error_state = False
            self.update_display()
        elif char == "У":
            if not self.error_state:
                self.expression = self.expression[:-1]
                self.update_display()
        elif char == "=":
            if not self.error_state and self.expression.strip() != "":
                safe_expr = self.expression.replace("÷", "/").replace("×", "*").replace(",", ".")
                result = SafeCalculator.calculate(safe_expr)
                if result is None:
                    self.expression = "Ошибка"
                    self.error_state = True
                else:
                    self.expression = result
                self.update_display()
        elif char == "+/-":
            if not self.error_state and any(c.isdigit() for c in self.expression):
                if self.expression.startswith("-"):
                    self.expression = self.expression[1:]
                else:
                    self.expression = "-" + self.expression
                self.update_display()
        else:
            if not self.error_state:
                if char in "÷×-+%" and not any(c.isdigit() for c in self.expression):
                    return
                if len(self.expression) < 23 and (char.isdigit() or char in ".,÷×-+%"):
                    if char == ",":
                        char = "."
                    self.expression += char
                    self.update_display()


if __name__ == "__main__":
    ModernSamsungCalculator().run()
