import math
import tkinter as tk
from tkinter import font as tkfont
from decimal import Decimal, getcontext, localcontext, ROUND_DOWN, ROUND_HALF_UP

class CalculatorEngine:
    def __init__(self):
        getcontext().prec = 14  # 정밀도 설정
        self.rounding_mode = 'F'
        self.decimal_places = 4
        self.reset_state()
        self.memory_gt_clear()
        self.memory_m_clear()

    def clear_current(self):
        self.input_buffer = ""
        self.current_value = Decimal('0')

    def reset_state(self):
        # 계산기 상태 초기화
        self.input_buffer = ""
        self.current_value = Decimal('0')
        self.previous_value = None
        self.operation = None
        self.last_button = None
        self.last_operand = None
        self.last_operator = None
        self.last_other_operand = None
        self.constant_calculation = False
        self.count_click = 0

    def format_number(self, number: Decimal) -> str:
        if self.rounding_mode == 'F':
            return f"{number:.14f}".rstrip('0').rstrip('.')
        
        places = 2 if self.decimal_places == 'Add2' else int(self.decimal_places)
        
        if self.rounding_mode in ['Cut', '5/4']:
            return f"{number.quantize(Decimal('1.' + '0' * places)):.{places}f}"

    def calculate(self):
        if self.operation and self.previous_value is not None:
            operations = {'+': self.add, '-': self.subtract, '×': self.multiply, '÷': self.divide}
            self.current_value = operations[self.operation](Decimal(str(self.previous_value)), Decimal(str(self.current_value)))
            self.previous_value = self.current_value
            self.operation = None
            self.input_buffer = ""

    def add(self, a: Decimal, b: Decimal) -> Decimal:
        return a + b

    def subtract(self, a: Decimal, b: Decimal) -> Decimal:
        return a - b

    def multiply(self, a: Decimal, b: Decimal) -> Decimal:
        return a * b

    def divide(self, a: Decimal, b: Decimal) -> Decimal:
        if b != 0:
            return a / b
        else:
            raise ValueError("Cannot divide by zero")

    def calculate_reciprocal(self, value: Decimal) -> Decimal: 
        if value != 0:
            return Decimal('1') / Decimal(str(value))
        else:
            raise ValueError("Cannot divide by zero")

    def square_root(self, value: Decimal) -> Decimal:
        with localcontext() as ctx:
            ctx.prec = getcontext().prec
            result = value.sqrt()
            if self.rounding_mode == 'F':
                return result
            elif self.rounding_mode == 'Cut':
                return result.quantize(Decimal('1.' + '0' * int(self.decimal_places)), rounding=ROUND_DOWN)
            elif self.rounding_mode == '5/4':
                return result.quantize(Decimal('1.' + '0' * int(self.decimal_places)), rounding=ROUND_HALF_UP)

    def apply_percentage(self):
        if self.operation is None:
            # 연산자가 없는 경우, 아무 동작도 하지 않음
            return

        if self.operation == '+':
            self.current_value = self.previous_value + (self.previous_value * self.current_value / Decimal('100'))
        elif self.operation == '-':
            self.current_value = self.previous_value - (self.previous_value * self.current_value / Decimal('100'))
        elif self.operation == '×':
            self.current_value = self.previous_value * (self.current_value / Decimal('100'))
        elif self.operation == '÷':
            if self.current_value != 0:
                self.current_value = (self.previous_value / self.current_value) * Decimal('100')
            else:
                raise ValueError("Cannot divide by zero")

        # 연산 완료 후 상태 재설정
        self.operation = None
        self.input_buffer = ""

    def change_sign(self):
        if self.input_buffer:
            self.input_buffer = str(-Decimal(self.input_buffer))
        self.current_value = -self.current_value

    def memory_m_add(self, value: Decimal):
        self.memory_m += value

    def memory_m_subtract(self, value: Decimal):
        self.memory_m -= value

    def memory_m_recall(self):
        return self.memory_m

    def memory_m_clear(self):
        self.memory_m = Decimal('0')

    def memory_gt_clear(self):
        self.memory_gt = Decimal('0')

    def memory_gt_add(self, value: Decimal):
        self.memory_gt += value

    def memory_gt_recall(self):
        return self.memory_gt    

    def constant_calculate(self):
        if self.last_operator == '×':
            result = self.calculate_binary(self.last_other_operand, self.last_operator, self.current_value)
        elif self.last_operator in ['+', '-', '÷']:
            if self.last_operator == '÷' and self.last_operand == 0:
                raise ValueError("Cannot divide by zero")
            result = self.calculate_binary(self.current_value, self.last_operator, Decimal(str(self.last_operand)))
        self.current_value = result
        return result


    def calculate_binary(self, a: Decimal, op: str, b: Decimal) -> Decimal:
        operations = {'+': self.add, '-': self.subtract, '×': self.multiply, '÷': self.divide}
        return operations[op](a, b)

    def backspace(self):
        if self.input_buffer:
            self.input_buffer = self.input_buffer[:-1]
            self.current_value = Decimal(self.input_buffer or '0')
        elif self.current_value != 0:
            str_value = str(self.current_value)[:-1] or '0'
            self.current_value = Decimal(str_value)

    def set_precision_mode(self, mode: str):
        getcontext().prec = int(mode)

    def set_rounding_mode(self, mode: str):
        self.rounding_mode = mode

    def set_decimal_places(self, places: str):
        self.decimal_places = places

    def should_reset_input(self):
        return self.last_button in ['+', '-', '×', '÷', '=', '√', 'M+', 'M-'] or self.constant_calculation

    def reset_input(self):
        self.input_buffer = ""
        self.constant_calculation = False

    def append_to_input(self, key):
        self.input_buffer += key
        try:
            self.current_value = Decimal(self.input_buffer)
        except ValueError:
            self.input_buffer = self.input_buffer[:-1]

    def set_operator(self, key):
        self.constant_calculation = False
        if self.previous_value is None:
            self.previous_value = self.current_value
        elif self.input_buffer and not self.constant_calculation:
            self.calculate()
        self.last_operator = key
        self.last_operand = self.current_value
        self.operation = key
        self.input_buffer = "" 

    def update_after_equals(self):
        self.previous_value = None
        self.operation = None
        self.input_buffer = str(self.current_value)

class CalculatorState:
    def __init__(self, engine: CalculatorEngine):
        self.engine = engine
        self.display_value = "0"
        self.status_display = ""
        self.calculation_history = []
        self.current_entry = ""
        self.history_index = -1
        self.last_calculation = ""
        self.constant_calculation_count = 0
        
    def update_display(self):
        if self.engine.input_buffer:
            self.display_value = self.engine.input_buffer
        else:
            self.display_value = self.engine.format_number(self.engine.current_value)
        
        self.status_display = self.current_entry if self.current_entry else self.last_calculation

    def add_to_history(self):
        if self.current_entry:
            self.calculation_history.append(self.current_entry)
            self.history_index = len(self.calculation_history) - 1
            self.last_calculation = self.current_entry  # 마지막 계산 저장
            self.current_entry = ""
        print(f'Calculation History: {self.calculation_history}')


    def reset(self):
        self.display_value = "0"
        self.status_display = ""
        self.calculation_history = []
        self.current_entry = ""
        self.last_calculation = ""  # 초기화 시 마지막 계산도 초기화
        self.history_index = -1
        
import tkinter as tk
from tkinter import font as tkfont
from decimal import Decimal

class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("Allcalc Rice Calculator (nonK)")
        master.geometry("720x650")
        self.gt_button = None
        self.mr_button = None

        self.engine = CalculatorEngine()
        self.state = CalculatorState(self.engine)

        self.setup_ui()
        self.update_display()
        print(f"#{self.engine.count_click:4}#, 【key】 , last_operand, last_operator, previous_value, current_value, input_buffer")

    def setup_ui(self):
        # Status display frame
        self.status_frame = tk.Frame(self.master)
        self.status_frame.grid(row=0, column=0, columnspan=5, sticky='nsew')

        # Previous button
        self.prev_button = tk.Button(self.status_frame, text="<", command=self.show_previous_entry)
        self.prev_button.pack(side=tk.LEFT)

        # Status display
        self.status_display = tk.Entry(self.status_frame, width=60, justify='center', font=('Arial', 10), relief='flat', bd=5)
        self.status_display.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Next button
        self.next_button = tk.Button(self.status_frame, text=">", command=self.show_next_entry)
        self.next_button.pack(side=tk.RIGHT)
        
        # Main display
        self.display_height = 1
        self.display = tk.Text(self.master, height=self.display_height, width=20, font=('DS-Digital', 72), relief='sunken', bd=5)
        self.display.grid(row=1, column=0, columnspan=5, padx=10, pady=10, sticky='nsew')
        self.display.configure(height=self.display_height)
        self.display.tag_configure("right", justify='right')
        self.display.tag_configure("separator", foreground='#888888')

        self.display_font = tkfont.Font(family='DS-Digital', size=72)
        self.display.configure(font=self.display_font)
        
        # Switches setup
        self.setup_switches()

        # Buttons setup
        self.setup_buttons()

        # Make the grid cells expandable
        for i in range(9):
            self.master.grid_rowconfigure(i, weight=1)
        for i in range(5):
            self.master.grid_columnconfigure(i, weight=1)

    def setup_switches(self):
        self.switch_frame = tk.Frame(self.master)
        self.switch_frame.grid(row=2, column=0, columnspan=5, pady=5)

        self.setup_precision_switch()
        self.setup_rounding_switch()
        self.setup_decimal_switch()

    def setup_precision_switch(self):
        self.precision_switch = tk.IntVar(value=3)
        self.precision_scale = tk.Scale(self.switch_frame, from_=0, to=2, orient=tk.HORIZONTAL, length=120, showvalue=0,
                                   tickinterval=1, resolution=1, variable=self.precision_switch, command=self.change_precision_mode)
        self.precision_scale.pack(side=tk.LEFT, padx=5)        

        precision_labels = ["10 ", " 12 ", "  14 "]
        for i, label in enumerate(precision_labels):
            tk.Label(self.switch_frame, text=label).place(x=13 + i * 38, y=20)

    def setup_rounding_switch(self):
        self.rounding_switch = tk.IntVar(value=0)
        self.rounding_scale = tk.Scale(self.switch_frame, from_=0, to=2, orient=tk.HORIZONTAL, length=120, showvalue=0,
                                   tickinterval=1, resolution=1, variable=self.rounding_switch, command=self.change_rounding_mode)
        self.rounding_scale.pack(side=tk.LEFT, padx=5)
        
        rounding_labels = [" F", "Cut ", " 5/4"]
        for i, label in enumerate(rounding_labels):
            tk.Label(self.switch_frame, text=label).place(x=150 + i * 38, y=20)

    def setup_decimal_switch(self):
        self.decimal_switch = tk.IntVar(value=0)
        self.decimal_scale = tk.Scale(self.switch_frame, from_=0, to=5, orient=tk.HORIZONTAL, length=280, showvalue=0,
                                     tickinterval=1, resolution=1, variable=self.decimal_switch, command=self.change_decimal_places)
        self.decimal_scale.pack(side=tk.LEFT, padx=5)
        
        decimal_labels = [" 4", " 3 ", " 2 ", " 1 ", " 0 ", "Add2"]
        for i, label in enumerate(decimal_labels):
            tk.Label(self.switch_frame, text=label).place(x=285 + i * 48, y=20)

    def setup_buttons(self):
        buttons = [
            ('allcalc.org', 0, 0, 1, 3), ('TAX-', 0, 3), ('TAX+', 0, 4),  
            ('M/EX', 1, 0), ('%', 1, 1), ('√', 1, 2), ('▶', 1, 3), ('GT', 1, 4), 
            ('MC', 2, 0), ('MR', 2, 1), ('M-', 2, 2), ('M+', 2, 3), ('÷', 2, 4), 
            ('+/-', 3, 0), ('7', 3, 1), ('8', 3, 2), ('9', 3, 3),  ('×', 3, 4),
            ('C', 4, 0), ('4', 4, 1), ('5', 4, 2), ('6', 4, 3), ('-', 4, 4),
            ('AC', 5, 0), ('1', 5, 1), ('2', 5, 2), ('3', 5, 3), ('+', 5, 4, 2),
            ('0', 6, 0), ('00', 6, 1), ('.', 6, 2), ('=', 6, 3)
        ]

        for btn in buttons:
            self.create_button(btn)

    def create_button(self, btn):
        if btn[0] in ['AC', 'C']:
            button = tk.Button(self.master, text=btn[0], width=10, height=2, font=('Arial', 16), bg='orange', 
                      command=lambda x=btn[0]: self.click(x))
        elif btn[0].isdigit() or btn[0] == '.':
            button = tk.Button(self.master, text=btn[0], width=10, height=2, font=('DS-Digital Bold', 18, 'bold'), bg='grey',
                      command=lambda x=btn[0]: self.click(x))
        elif len(btn) == 5:  # For the 'allcalc.org' button
            button = tk.Button(self.master, text=btn[0], width=10, height=2, font=('Arial', 16),
                      command=lambda x=btn[0]: self.click(x))
        elif len(btn) == 4:  # For the '+' button
            button = tk.Button(self.master, text=btn[0], width=10, height=4, font=('Arial', 16),
                      command=lambda x=btn[0]: self.click(x))
        else:
            button = tk.Button(self.master, text=btn[0], width=10, height=2, font=('Arial', 16),
                      command=lambda x=btn[0]: self.click(x))
        
        button.grid(row=btn[1]+3, column=btn[2], sticky='nsew', rowspan=btn[3] if len(btn) > 3 else 1, columnspan=btn[4] if len(btn) > 4 else 1)
        
        if btn[0] == 'GT':
            self.gt_button = button
        elif btn[0] == 'MR':
            self.mr_button = button


    def update_memory_buttons(self):
        gt_memory = self.engine.memory_gt_recall()
        m_memory = self.engine.memory_m_recall()

        if gt_memory != 0:
            self.gt_button.config(bg='#E6E6FA')  # Light lavender
        else:
            self.gt_button.config(bg='SystemButtonFace')  # Default button color

        if m_memory != 0:
            self.mr_button.config(bg='#F0FFF0')  # Light honeydew
        else:
            self.mr_button.config(bg='SystemButtonFace')  # Default button color

    def click(self, key):
        self.engine.count_click += 1
        print(f"#{self.engine.count_click:4}-1#, 【{key}】 , {self.engine.last_operand}, {self.engine.last_operator}, {self.engine.previous_value}, {self.engine.current_value},'{self.engine.input_buffer}'")
        if key == 'allcalc.org':
            self.copy_history_to_clipboard()
            self.engine.count_click -=1
        if key.isdigit() or key == '.':
            self.handle_number_input(key)
        elif key == '▶':
            self.engine.backspace()
        elif key in ['+', '-', '×', '÷']:
            self.handle_operator(key)
        elif key == '=':
            self.handle_equals()
        elif key == 'GT':
            self.handle_gt()
        elif key in ['C', 'AC']:
            self.handle_clear(key)
        elif key == '+/-':
            self.engine.change_sign()
        elif key == '%':
            self.handle_percentage()
        elif key == '√':
            self.handle_square_root()
        elif key in ['M+', 'M-', 'MR', 'MC']:
            self.handle_memory_m(key)
        
        self.engine.last_button = key
        print(f"#{self.engine.count_click:4}-2#, 【{key}】 , {self.engine.last_operand}, {self.engine.last_operator}, {self.engine.previous_value}, {self.engine.current_value},'{self.engine.input_buffer}'")
        self.update_display()

    def handle_number_input(self, key):
        if self.engine.should_reset_input():
            self.engine.reset_input()
            if self.state.current_entry.endswith('='):
                self.state.current_entry = ""
        if self.engine.input_buffer == "" and key == '.':
            self.engine.input_buffer = "0"
        if key == '.' and '.' in self.engine.input_buffer:
            return
        self.engine.append_to_input(key)
        self.state.update_display()

    def handle_operator(self, key):
        if self.engine.input_buffer:
            current_value = Decimal(self.engine.input_buffer)
            self.state.current_entry += f" {self.engine.input_buffer}"
        else:
            current_value = self.engine.current_value
            if not self.state.current_entry:
                self.state.current_entry = str(current_value)

        # Check if the last operation was also an operator
        if self.engine.last_button in ['+', '-', '×', '÷']:
            # Remove the last operator from the current entry
            self.state.current_entry = self.state.current_entry.rsplit(' ', 1)[0]
        else:
            # If not, perform the calculation for the previous operation
            if self.engine.operation:
                result = self.engine.calculate_binary(self.engine.previous_value, self.engine.operation, current_value)
                self.engine.current_value = result
                self.state.current_entry += f" → {result}"

        # Update the current entry with the new operator
        self.state.current_entry += f" {key}"
        
        # Update the engine state
        self.engine.previous_value = self.engine.current_value
        self.engine.operation = key
        self.engine.input_buffer = ""
        
        # Update last_operand and last_other_operand for multiplication
        if key == '×':
            self.engine.last_other_operand = self.engine.current_value
            self.engine.last_operand = current_value
        else:
            self.engine.last_operand = current_value
        
        self.engine.last_operator = key
        self.state.update_display()

    def handle_equals(self):
        if self.engine.input_buffer:
            current_value = Decimal(self.engine.input_buffer)
            self.state.current_entry += f" {self.engine.input_buffer}"
        else:
            current_value = self.engine.current_value
        print(f"last_button: {self.engine.last_button}")
        if self.engine.last_operator == '÷' and self.engine.last_button == '÷':
            print(f"역수 계산")
            try:
                reciprocal = self.engine.calculate_reciprocal(self.engine.last_operand)
                self.engine.current_value = reciprocal
                self.state.current_entry += f" = 1 ÷ {self.engine.last_operand} = {reciprocal}"
            except ValueError:
                self.state.current_entry += " = Error (Division by zero)"
                self.engine.current_value = Decimal('0')
        elif self.engine.operation:

            # 루트 연산이 포함된 경우를 처리
            if "√" in self.state.current_entry:
                parts = self.state.current_entry.split()
                if len(parts) >= 3 and parts[-2] == '=':
                    # 루트 계산 결과가 이미 있는 경우
                    root_result = Decimal(parts[-1])
                    self.state.current_entry = f"{self.engine.previous_value} {self.engine.operation} {root_result}"

            result = self.engine.calculate_binary(self.engine.previous_value, self.engine.operation, current_value)
            self.engine.current_value = result
            self.state.current_entry += f" = {result}"
            
            # 다음 상수 계산을 위해 마지막 연산자와 피연산자 저장
            self.engine.last_operator = self.engine.operation
            if self.engine.operation == '×':
                self.engine.last_other_operand = self.engine.previous_value
            else:
                self.engine.last_operand = current_value
        elif self.engine.last_operator:
            self.handle_constant_calculation()
        else:
            self.state.current_entry += f" = {self.engine.current_value}"

        self.engine.memory_gt_add(self.engine.current_value)
        self.update_memory_buttons()
        
        self.state.status_display = self.state.current_entry
        self.state.add_to_history()
        
        self.engine.update_after_equals()
        self.engine.input_buffer = ""
        self.state.constant_calculation_count = 0
        print(f"state.current_entry: {self.state.current_entry}")
        print(f"state.last_calculation: {self.state.last_calculation}")

    def handle_percentage(self):
        if self.engine.input_buffer:
            self.engine.current_value = Decimal(self.engine.input_buffer)
        
        try:
            if self.engine.operation is None:
                # If there's no operation, just convert the current value to a percentage
                result = self.engine.current_value / Decimal('100')
                self.state.current_entry = f"{self.engine.current_value}% = {result}"
            else:
                previous_value = self.engine.previous_value
                current_value = self.engine.current_value
                operation = self.engine.operation

                if operation == '+':
                    result = previous_value + (previous_value * current_value / Decimal('100'))
                    self.state.current_entry = f"{previous_value} *(1+ {current_value}%) = {result}"
                elif operation == '-':
                    result = previous_value - (previous_value * current_value / Decimal('100'))
                    self.state.current_entry = f"{previous_value} *(1- {current_value}%) = {result}"
                elif operation == '×':
                    result = previous_value * (current_value / Decimal('100'))
                    self.state.current_entry = f"{previous_value} × {current_value}% = {result}"
                elif operation == '÷':
                    if current_value != 0:
                        result = (previous_value / current_value) * Decimal('100')
                        self.state.current_entry = f"{previous_value} ÷ {current_value} × 100 = {result} (%)"
                    else:
                        raise ValueError("Cannot divide by zero")

            self.engine.current_value = result
        except ValueError as e:
            self.state.current_entry += f" Error: {str(e)}"
        
        self.engine.operation = None
        self.engine.previous_value = None
        self.engine.input_buffer = ""
        self.state.add_to_history()
        self.update_display()

    def handle_constant_calculation(self):
        self.state.constant_calculation_count += 1
        if self.engine.last_operator and self.engine.last_operand is not None:
            try:
                result = self.engine.constant_calculate()
                operator_str = self.engine.last_operator
                if self.engine.last_operator == '×':
                    operand_str = str(self.engine.last_other_operand)
                else:
                    operand_str = str(self.engine.last_operand)
                if self.state.constant_calculation_count == 1:
                    self.state.current_entry += f" {operator_str} {operand_str}"
                self.state.current_entry += f" = {result}"
                self.engine.current_value = result
            except ValueError:
                self.state.current_entry += " = Error (Division by zero)"
                self.engine.current_value = Decimal('0')
        else:
            self.state.current_entry += f" = {self.engine.current_value}"

        
    def handle_gt(self):
        self.engine.current_value = self.engine.memory_gt_recall()
        self.state.current_entry += f" Recall GT = {self.engine.current_value}"
        self.engine.input_buffer = ""
        self.state.add_to_history()
        self.update_display()        



    def handle_clear(self, key):
        if key == 'C':
            self.engine.clear_current()
            self.state.status_display = f"【C】 화면 지우기"
        elif key == 'AC':
            # 계산기마다 AC 작동 범위가 다르므로 호출하는 함수를 구분하여 적용함.
            self.engine.reset_state()
            self.engine.memory_gt_clear()
            self.engine.memory_m_clear()
            self.state.reset()
            self.state.status_display = f"【AC】화면 지우기 & 메모리 초기화"
        self.update_memory_buttons()

    def handle_square_root(self):
        if self.engine.input_buffer:
            value = Decimal(self.engine.input_buffer)
        else:
            value = self.engine.current_value
        result = self.engine.square_root(value)
        self.engine.current_value = result
        self.engine.input_buffer = ""
        self.state.current_entry += f" (√{value} = {result})"
        self.state.add_to_history()
        self.update_display()

    def handle_memory_m(self, key):
        if key == 'M+':
            self.engine.memory_m_add(self.engine.current_value)
            self.state.current_entry += f" M += {self.engine.current_value}"
        elif key == 'M-':
            self.engine.memory_m_subtract(self.engine.current_value)
            self.state.current_entry += f" M -= {self.engine.current_value}"
        elif key == 'MR':
            self.engine.current_value = self.engine.memory_m_recall()
            self.state.current_entry += f" Recall M = {self.engine.current_value}"
            self.engine.input_buffer = ""
        elif key == 'MC':
            self.engine.memory_m_clear()
            self.state.current_entry += " MC"
        self.state.add_to_history()
        self.update_display()
        self.update_memory_buttons()


    def perform_calculation(self):
        if self.engine.operation and self.engine.previous_value is not None:
            if self.engine.input_buffer:
                current_value = Decimal(self.engine.input_buffer)
            else:
                current_value = self.engine.current_value
            result = self.engine.calculate_binary(self.engine.previous_value, self.engine.operation, current_value)
            self.engine.current_value = result
            self.engine.input_buffer = ""

    def update_display(self):
        self.state.update_display()
        self.display.delete('1.0', tk.END)
        
        display_value = self.engine.format_number(self.engine.current_value)
        parts = display_value.split('.')
        integer_part = parts[0].lstrip('0') or '0'
        decimal_part = parts[1] if len(parts) > 1 else ""

        for i, char in enumerate(reversed(integer_part)):
            if i > 0 and i % 3 == 0:
                self.display.insert('1.0', ',', 'separator')
            self.display.insert('1.0', char)

        if decimal_part:
            self.display.insert(tk.END, '.')
            for char in decimal_part:
                self.display.insert(tk.END, char, "small")
        
        self.display.tag_add("right", "1.0", "end")
        self.display.tag_config("small", font=('DS-Digital', 65))

        self.adjust_font_size()

        self.status_display.delete(0, tk.END)
        self.status_display.insert(0, self.state.status_display)
        print(f'self.state.status_display: "{self.state.status_display}", self.engine.current_value: "{self.engine.current_value}"')

        # Add this line to update memory display
        self.update_memory_indicator()

    def update_memory_indicator(self):
        # This method should update any visual indicator of memory status
        # For example, if you have a label or icon for memory status:
        memory_value = self.engine.memory_m_recall()
        if memory_value != 0:
            # Update your memory indicator to show that memory is not empty
            pass
        else:
            # Update your memory indicator to show that memory is empty
            pass


    def show_previous_entry(self):
        entry = self.state.get_previous_entry()
        if entry:
            self.status_display.delete(0, tk.END)
            self.status_display.insert(0, entry)

    def show_next_entry(self):
        entry = self.state.get_next_entry()
        if entry:
            self.status_display.delete(0, tk.END)
            self.status_display.insert(0, entry)

    def adjust_font_size(self):
        current_width = self.display.winfo_width()
        text_width = self.display_font.measure(self.display.get('1.0', 'end-1c'))
        
        if text_width > current_width:
            current_size = self.display_font['size']
            while text_width > current_width and current_size > 10:
                current_size -= 1
                self.display_font.configure(size=current_size)
                text_width = self.display_font.measure(self.display.get('1.0', 'end-1c'))
        else:
            self.display_font.configure(size=72)
        
        self.display.configure(font=self.display_font)
        self.display.configure(height=self.display_height)

    def change_precision_mode(self, value):
        modes = ['10', '12', '14']
        self.engine.set_precision_mode(modes[int(value)])
        self.update_display()

    def change_rounding_mode(self, value):
        modes = ['F', 'Cut', '5/4']
        self.engine.set_rounding_mode(modes[int(value)])
        self.update_display()

    def change_decimal_places(self, value):
        modes = ['4', '3', '2', '1', '0', 'Add2']
        self.engine.set_decimal_places(modes[int(value)])
        self.update_display()

    def copy_history_to_clipboard(self):
        history_text = "\n".join(self.state.calculation_history)
        self.master.clipboard_clear()
        self.master.clipboard_append(history_text)
        self.master.update()  # 클립보드 작업이 완료되도록 보장합니다
        self.state.status_display = "계산 기록이 클립보드에 복사되었습니다."
        self.update_display()

def main():
    root = tk.Tk()
    my_calculator = Calculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()