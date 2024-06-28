import tkinter as tk
from typing import List, Union
import math

class CalculatorEngine:
    def __init__(self):
        self.memory = 0
        self.current_value = 0
        self.previous_value = None
        self.operation = None
        self.rounding_mode = 'F'  # F, Cut, or 5/4
        self.decimal_places = 4  # 4, 3, 2, 1, 0, or Add2        self.number_mode = 4  # 4, 3, 2, 1, 0, or Add2
        self.input_buffer = ""
        self.last_button = None
        self.last_operand = None
        self.last_operator = None
        self.last_other_operand = None
        self.constant_calculation = False

    def set_rounding_mode(self, mode: str):
        self.rounding_mode = mode

    def set_decimal_places(self, places: Union[int, str]):
        self.decimal_places = places

    def format_number(self, number: float) -> str:
        if self.rounding_mode == 'F':
            return f"{number:.14g}"
        
        if self.decimal_places == 'Add2':
            places = 2
        else:
            places = int(self.decimal_places)
        
        if self.rounding_mode == 'Cut':
            return f"{math.floor(number * 10**places) / 10**places:.{places}f}"
        elif self.rounding_mode == '5/4':
            return f"{round(number, places):.{places}f}"
        
    def clear(self):
        self.current_value = 0
        self.previous_value = None
        self.operation = None
        self.input_buffer = ""
        self.last_button = None

    def add(self, a: float, b: float):
        return a + b

    def subtract(self, a: float, b: float):
        return a - b

    def multiply(self, a: float, b: float):
        return a * b

    def divide(self, a: float, b: float):
        if b != 0:
            return a / b
        else:
            raise ValueError("Cannot divide by zero")

    def square_root(self, value: float):
        return math.sqrt(value)

    def percentage(self):
        self.current_value /= 100

    def change_sign(self):
        if self.input_buffer:
            self.input_buffer = str(-float(self.input_buffer))
        self.current_value = -self.current_value

    def memory_add(self, value: float):
        self.memory += value

    def memory_subtract(self, value: float):
        self.memory -= value

    def memory_recall(self):
        return self.memory

    def memory_clear(self):
        self.memory = 0
        self.current_value = 0
        self.previous_value = None
        self.operation = None
        self.input_buffer = ""
        self.last_button = None
        self.last_operand = None
        self.last_operator = None
        self.last_other_operand = None
        self.constant_calculation = False

    def set_mode(self, mode: str):
        self.mode = mode

    def set_number_mode(self, mode: int):
        self.number_mode = mode

    def calculate(self):
        if self.operation and self.previous_value is not None:
            if self.operation == '+':
                self.current_value = self.add(self.previous_value, self.current_value)
            elif self.operation == '-':
                self.current_value = self.subtract(self.previous_value, self.current_value)
            elif self.operation == '×':
                self.current_value = self.multiply(self.previous_value, self.current_value)
            elif self.operation == '÷':
                self.current_value = self.divide(self.previous_value, self.current_value)
            self.previous_value = None
            self.operation = None
            self.input_buffer = ""

    def constant_calculate(self):
        if self.last_operator in ['+', '-', '÷']:
            result = self.calculate_binary(self.current_value, self.last_operator, self.last_operand)
        elif self.last_operator == '×':
            result = self.calculate_binary(self.last_other_operand, self.last_operator, self.current_value)
        self.current_value = result
        return result

    def calculate_binary(self, a, op, b):
        if op == '+':
            return a + b
        elif op == '-':
            return a - b
        elif op == '×':
            return a * b
        elif op == '÷':
            if b != 0:
                return a / b
            else:
                raise ValueError("Cannot divide by zero")    

class CalculatorState:
    def __init__(self, engine: CalculatorEngine):
        self.engine = engine
        self.display_value = "0"
        self.status_display = "init"

    def update_display(self):
        if self.engine.input_buffer:
            self.display_value = self.engine.input_buffer
        else:
            self.display_value = self.engine.format_number(self.engine.current_value)
        
        if self.engine.operation: 
            self.status_display = f"{self.engine.previous_value} {self.engine.operation}"

class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("Allcalc Rice Calculator")
        master.geometry("450x650")

        self.engine = CalculatorEngine()
        self.state = CalculatorState(self.engine)

        # Status display

        self.status_display = tk.Entry(master, width=20, justify='right', font=('Arial', 10), relief='flat', bd=5)
        self.status_display.grid(row=0, column=0, columnspan=5, padx=0, pady=0, sticky='nsew')

        # Main display
        self.display = tk.Entry(master, width=20, justify='right', font=('DS-Digital', 72), relief='sunken', bd=5)
        self.display.grid(row=1, column=0, columnspan=5, padx=10, pady=10, sticky='nsew')

        # Switches
        self.switch_frame = tk.Frame(master)
        self.switch_frame.grid(row=2, column=0, columnspan=5, pady=5)

        self.rounding_switch = tk.IntVar(value=0)
        self.rounding_scale = tk.Scale(self.switch_frame, from_=0, to=2, orient=tk.HORIZONTAL, length=120, showvalue=0,
                                   tickinterval=1, resolution=1, variable=self.rounding_switch, command=self.change_rounding_mode)
        self.rounding_scale.pack(side=tk.LEFT, padx=5)
        
        self.rounding_labels = ["F", "Cut ", " 5/4"]
        for i, label in enumerate(self.rounding_labels):
            tk.Label(self.switch_frame, text=label).place(x=18 + i * 38, y=20)

        self.decimal_switch = tk.IntVar(value=0)
        self.decimal_scale = tk.Scale(self.switch_frame, from_=0, to=5, orient=tk.HORIZONTAL, length=280, showvalue=0,
                                     tickinterval=1, resolution=1, variable=self.decimal_switch, command=self.change_decimal_places)
        self.decimal_scale.pack(side=tk.LEFT, padx=5)
        
        self.decimal_labels = [" 4", " 3 ", " 2 ", " 1 ", " 0 ", "Add2"]
        for i, label in enumerate(self.decimal_labels):
            tk.Label(self.switch_frame, text=label).place(x=150 + i * 48, y=20)

        # Buttons
        buttons = [
            ('allcalc.org', 2, 0, 1, 3), ('TAX-', 2, 3), ('TAX+', 2, 4),  
            ('M/EX', 3, 0), ('%', 3, 1), ('√', 3, 2), ('▶', 3, 3), ('GT', 3, 4), 
            ('MC', 4, 0), ('MR', 4, 1), ('M-', 4, 2), ('M+', 4, 3), ('÷', 4, 4), 
            ('+/-', 5, 0), ('7', 5, 1), ('8', 5, 2), ('9', 5, 3),  ('×', 5, 4),
            ('C', 6, 0), ('4', 6, 1), ('5', 6, 2), ('6', 6, 3), ('-', 6, 4),
            ('AC', 7, 0), ('1', 7, 1), ('2', 7, 2), ('3', 7, 3), ('+', 7, 4, 2),
            ('0', 8, 0), ('00', 8, 1), ('.', 8, 2), ('=', 8, 3)
        ]

        for btn in buttons:
            if btn[0] in ['AC', 'C']:
                tk.Button(master, text=btn[0], width=10, height=2, font=('Arial', 16), bg='orange', 
                          command=lambda x=btn[0]: self.click(x)).grid(row=btn[1]+1, column=btn[2], sticky='nsew')
            elif btn[0].isdigit() or btn[0] == '.':
                tk.Button(master, text=btn[0], width=10, height=2, font=('DS-Digital Bold', 18, 'bold'), bg='grey',
                          command=lambda x=btn[0]: self.click(x)).grid(row=btn[1]+1, column=btn[2], sticky='nsew')
            elif len(btn) == 4:  # For the '+' button rowspan
                tk.Button(master, text=btn[0], width=10, height=4, font=('Arial', 16),
                          command=lambda x=btn[0]: self.click(x)).grid(row=btn[1]+1, column=btn[2], rowspan=btn[3], sticky='nsew')
            elif len(btn) == 5:  # For the 'allcalc.org ' button columnspan
                tk.Button(master, text=btn[0], width=10, height=2, font=('Arial', 16),
                          command=lambda x=btn[0]: self.click(x)).grid(row=btn[1]+1, column=btn[2], rowspan=btn[3], columnspan=btn[4], sticky='nsew')
            else:
                tk.Button(master, text=btn[0], width=10, height=2, font=('Arial', 16),
                          command=lambda x=btn[0]: self.click(x)).grid(row=btn[1]+1, column=btn[2], sticky='nsew')

        # Make the grid cells expandable
        for i in range(9):
            master.grid_rowconfigure(i, weight=1)
        for i in range(5):
            master.grid_columnconfigure(i, weight=1)

        self.update_display()

    def click(self, key: str):
        if key.isdigit() or key == '.':
            if self.engine.last_button in ['+', '-', '×', '÷', '=', '√'] or self.engine.constant_calculation:
                self.engine.input_buffer = ""
                self.engine.constant_calculation = False
            if key == '.' and '.' in self.engine.input_buffer:
                return  # 이미 소숫점이 있으면 무시
            self.engine.input_buffer += key
            try:
                self.engine.current_value = float(self.engine.input_buffer)
            except ValueError:
                # 잘못된 입력 처리 (예: 소숫점만 입력된 경우)
                self.engine.input_buffer = self.engine.input_buffer[:-1]  # 마지막 문자 제거
        elif key == '▶':
            if self.engine.input_buffer:
                self.engine.input_buffer = self.engine.input_buffer[:-1]  # 마지막 문자 제거
                if self.engine.input_buffer:
                    self.engine.current_value = float(self.engine.input_buffer)
                else:
                    self.engine.current_value = 0
            elif self.engine.current_value != 0:
                self.engine.current_value = float(str(self.engine.current_value)[:-1] or '0')
        elif key in ['+', '-', '÷']:
            if self.engine.previous_value is None:
                self.engine.previous_value = self.engine.current_value
            elif self.engine.input_buffer and not self.engine.constant_calculation:
                self.engine.calculate()
            self.engine.last_operator = key
            self.engine.last_operand = self.engine.current_value
            self.engine.operation = key
            self.engine.input_buffer = ""
            self.state.status_display = f"{self.engine.previous_value} {self.engine.operation}"
        elif key in ['×']:
            if self.engine.previous_value is None:
                self.engine.previous_value = self.engine.current_value
            elif self.engine.input_buffer and not self.engine.constant_calculation:
                self.engine.calculate()
            self.engine.last_operator = key
            self.engine.last_other_operand = self.engine.previous_value
            self.engine.last_operand = self.engine.previous_value 
            self.engine.operation = key
            self.engine.input_buffer = ""
            self.state.status_display = f"{self.engine.previous_value} {self.engine.operation}"
        elif key == '=':
            if self.engine.constant_calculation or (self.engine.previous_value is None and self.engine.last_operator):
                print(f'key=if : {self.state.status_display}')
                self.state.status_display = f"{self.engine.current_value} {self.engine.last_operator} {self.engine.last_operand} ="
                result = self.engine.constant_calculate()
            elif self.engine.previous_value is not None and self.engine.operation:
                self.engine.last_operand = self.engine.current_value
                self.engine.last_operator = self.engine.operation
                self.state.status_display = f"{self.engine.previous_value} {self.engine.operation} {self.engine.current_value} =" 
                print(f'key=elif : {self.state.status_display}')
                self.engine.calculate()
                self.engine.previous_value = None
                self.engine.operation = None
            self.engine.constant_calculation = True
        elif key == 'C':
            self.engine.clear()
            self.state.status_display = f"Display Cleared" 
        elif key == 'AC':
            self.engine.clear()
            self.engine.memory_clear()
            self.state.status_display = f"Display Cleared & Memory Cleared" 
        elif key == '+/-':
            self.engine.change_sign()
        elif key == '%':
            self.engine.percentage()
        elif key == '√':
            self.engine.current_value = self.engine.square_root(self.engine.current_value)
            self.engine.input_buffer = str(self.engine.current_value)
            self.state.status_display = f"√{self.engine.current_value}"
        elif key == 'M+':
            self.engine.memory_add(self.engine.current_value)
            self.state.status_display = f"M = {self.engine.memory} = {self.engine.memory - self.engine.current_value} + {self.engine.current_value}"
        elif key == 'M-':
            self.engine.memory_subtract(self.engine.current_value)
            self.state.status_display = f"M = {self.engine.memory} = {self.engine.memory + self.engine.current_value} - {self.engine.current_value}"
        elif key == 'MR':
            self.engine.current_value = self.engine.memory_recall()
            self.engine.input_buffer = str(self.engine.current_value)
        elif key == 'MC':
            self.engine.memory_clear()
        
        self.engine.last_button = key
        print(f"before update: {self.state.status_display}")
        self.update_display()

    def change_rounding_mode(self, value):
        modes = ['F', 'Cut', '5/4']
        self.engine.set_rounding_mode(modes[int(value)])
        self.update_display()

    def change_decimal_places(self, value):
        places = ['4', '3', '2', '1', '0', 'Add2']
        self.engine.set_decimal_places(places[int(value)])
        self.update_display()

    def update_display(self):
        self.state.update_display()
        self.display.delete(0, tk.END)
        self.display.insert(0, self.state.display_value)
        self.status_display.delete(0, tk.END)
        print(f'update_display() : {self.state.status_display}')
        self.status_display.insert(0, self.state.status_display)


def main():
    root = tk.Tk()
    my_calculator = Calculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()