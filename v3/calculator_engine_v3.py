import math
from decimal import Decimal, getcontext, localcontext, ROUND_DOWN, ROUND_HALF_UP

class CalculatorEngineV3:
    def __init__(self):
        # Default global precision for internal calculations. 
        # actual limits will be enforced by self.precision_limit
        getcontext().prec = 28  
        self.rounding_mode = 'F'
        self.decimal_places = 4
        self.calc_mode = 'NON_K'  # 'K' or 'NON_K'
        
        self.precision_limit = 12 # Default to 12 digits
        self.set_precision(12)
        
        # Initialize attributes
        self.memory_m = Decimal('0')
        self.memory_gt = Decimal('0')
        self.tax_rate = Decimal('10')
        
        self.display_value = Decimal('0')
        self.input_buffer = ""
        self.is_entering_number = True
        
        self.stack = [] 
        self.constant_op = None
        self.constant_val = None
        self.is_k_active = False
        
        self.last_operator = None
        self.last_button = None
        self.gt_updated = False 
        self.m_updated = False  
        self.percentage_base = None 
        self.last_percent_op = None 
        self.last_k_input = None 
        
        # Exchange rates
        self.exchange_rates = {
            'C1': Decimal('1'), 
            'C2': Decimal('1350'), 
            'C3': Decimal('160'), 
            'C4': Decimal('0.95')
        }
        self.currency_symbols = {'C1': '$', 'C2': '₩', 'C3': '¥', 'C4': '€'}
        self.mode = 'M'  # 'M' for Memory, 'EX' for Exchange

    def set_precision(self, digits):
        self.precision_limit = int(digits)
        # We set the context precision to the limit to force truncation/rounding
        # at the specified number of significant digits during arithmetic.
        getcontext().prec = self.precision_limit
        print(f"DEBUG: Precision set to {self.precision_limit}")

    def reset_state(self):
        self.display_value = Decimal('0')
        self.input_buffer = ""
        self.is_entering_number = True
        
        self.stack = [] 
        self.constant_op = None
        self.constant_val = None
        self.is_k_active = False
        
        self.last_operator = None
        self.last_button = None
        self.gt_updated = False 
        self.m_updated = False  
        self.percentage_base = None 
        self.last_percent_op = None 
        self.last_k_input = None 

    def format_number(self, number: Decimal) -> str:
        # Avoid scientific notation and handle trailing zeros
        if self.rounding_mode == 'F':
            formatted = format(number, 'f')
            if '.' in formatted:
                formatted = formatted.rstrip('0').rstrip('.')
            
            # Enforce Display Limit strictly (Simple Truncation for Display)
            # Physical calculators truncate digits that don't fit
            pure_digits = formatted.replace('.', '').replace('-', '')
            if len(pure_digits) > self.precision_limit:
                # We need to shorten it. 
                # If decimal exists, we can truncate decimals.
                if '.' in formatted:
                    # allowed len includes dot? No, strictly digits.
                    # allowed chars = limit + (1 if dot) + (1 if sign)
                    allowed = self.precision_limit
                    if '.' in formatted: allowed += 1
                    if '-' in formatted: allowed += 1
                    
                    # But we must be careful not to keep just "0."
                    formatted = formatted[:allowed]
                    if formatted.endswith('.'):
                        formatted = formatted[:-1]
            
            return formatted
        
        places = 2 if self.decimal_places == 'Add2' else int(self.decimal_places)
        
        with localcontext() as ctx:
            if self.rounding_mode == 'Cut':
                ctx.rounding = ROUND_DOWN
            elif self.rounding_mode == '5/4':
                ctx.rounding = ROUND_HALF_UP
            
            try:
                quantized = number.quantize(Decimal('1.' + '0' * places))
                formatted = format(quantized, 'f')
                return formatted
            except:
                return format(number, 'f')

    def get_display_text(self) -> str:
        """Returns the text that should be shown on the calculator display."""
        if self.is_entering_number and self.input_buffer:
            return self.input_buffer
        return self.format_number(self.display_value)

    def input_digit(self, digit: str):
        if not self.is_entering_number:
            self.input_buffer = ""
            self.is_entering_number = True
        
        if digit == '.' and '.' in self.input_buffer:
            return
        
        # Check buffer length limit against precision limit
        current_len = len(self.input_buffer.replace('.', ''))
        if current_len >= self.precision_limit:
            return

        if self.input_buffer == "0" and digit != ".":
            self.input_buffer = digit
        else:
            self.input_buffer += digit
        
        self.display_value = Decimal(self.input_buffer)
        self.last_button = digit  

    def _perform_op(self, a, op, b):
        try:
            if op == '+': return a + b
            if op == '-': return a - b
            if op == '×': return a * b
            if op == '÷': 
                if b == 0: raise ZeroDivisionError
                return a / b
        except (ZeroDivisionError, ValueError):
            return Decimal('NaN')
        return b

    def set_operator(self, op):
        print(f"DEBUG: set_operator('{op}') start. last_button='{self.last_button}', is_entering_number={self.is_entering_number}, stack={self.stack}")
        if self.calc_mode == 'K':
            if self.last_button == op:
                self.is_k_active = True
                self.constant_op = op
                self.constant_val = self.display_value
                self.is_entering_number = False
                self.last_button = op
                print(f"DEBUG: K-mode activated. constant_op='{op}', constant_val={self.constant_val}")
                return

        if self.is_entering_number:
            if self.stack:
                prev_val, prev_op = self.stack.pop()
                self.display_value = self._perform_op(prev_val, prev_op, self.display_value)
                print(f"DEBUG: Intermediate calculation. {prev_val} {prev_op} ... = {self.display_value}")
            self.is_entering_number = False
            
        self.stack = [(self.display_value, op)]
        self.is_k_active = False 
        
        if self.calc_mode == 'K' and self.percentage_base is not None and self.last_button == '%':
            if op in ['+', '-']:
                if self.last_percent_op == '×':
                    self.display_value = self._perform_op(self.percentage_base, op, self.display_value)
                elif self.last_percent_op == '+':
                    if op == '-':
                        self.display_value = self.percentage_base
                
                self.percentage_base = None 
                self.last_percent_op = None
                self.stack = [] 
                self.is_entering_number = False
                self.last_button = op
                print(f"DEBUG: CASIO % Chain (Resolved). Display={self.display_value}, Stack Cleared")
                return

        self.last_button = op
        print(f"DEBUG: set_operator() end. stack={self.stack}")

    def _resolve_pending_operation(self):
        if self.calc_mode == 'K' and self.is_k_active:
            if self.constant_op == '+':
                self.display_value = self.display_value + self.constant_val
            elif self.constant_op == '-':
                self.display_value = self.display_value - self.constant_val
            elif self.constant_op == '×':
                self.display_value = self.constant_val * self.display_value
            elif self.constant_op == '÷':
                if self.constant_val == 0: self.display_value = Decimal('NaN')
                else: self.display_value = self.display_value / self.constant_val
            return self.display_value
        
        if self.stack:
            prev_val, prev_op = self.stack.pop()
            self.constant_op = prev_op
            if self.calc_mode == 'NON_K' and prev_op == '×':
                self.constant_val = prev_val
            else:
                self.constant_val = self.display_value
            
            self.display_value = self._perform_op(prev_val, prev_op, self.display_value)
            print(f"DEBUG: Operation resolved. Result={self.display_value}, New constant={self.constant_val} ({prev_op})")
            return self.display_value
        elif self.constant_op:
            if self.calc_mode == 'NON_K':
                if self.last_button == '%' and self.constant_op in ['+%', '-%'] and self.percentage_base is not None:
                    res = self.percentage_base
                    self.percentage_base = None 
                    self.display_value = res 
                    self.constant_op = self.constant_op[0] 
                    print(f"DEBUG: Resolve Delta Display & Transition. Result={res}, New constant_op={self.constant_op}")
                    return res
                
                print(f"DEBUG: Resolve Constant Op. op={self.constant_op}, val={self.constant_val}, display={self.display_value}")
                
                if self.constant_op == '+%':
                    self.display_value = self.constant_val + (self.constant_val * self.display_value / 100)
                elif self.constant_op == '-%':
                    self.display_value = self.constant_val - (self.constant_val * self.display_value / 100)
                elif self.constant_op == '÷%':
                    self.display_value = (self.display_value / self.constant_val) * 100
                else:
                    self.display_value = self._perform_op(self.display_value, self.constant_op, self.constant_val)
                return self.display_value
        
        return self.display_value

    def percent(self):
        print(f"DEBUG: percent() start. mode={self.calc_mode}, stack={self.stack}, constant={self.constant_op}({self.constant_val}), display={self.display_value}")
        
        if self.last_button == '%' and self.calc_mode == 'NON_K':
            print("DEBUG: Repeated % in NON_K mode - Ignored")
            return

        if self.calc_mode == 'K' and self.is_k_active and self.constant_op == '-':
             if self.constant_val == 0:
                 self.display_value = Decimal('NaN')
             else:
                 self.display_value = (self.display_value - self.constant_val) / self.constant_val * 100
             
             self.is_entering_number = False
             self.last_button = '%'
             print(f"DEBUG: K-Mode Constant % Result={self.display_value}")
             return

        if self.last_button == '%' and self.calc_mode == 'K':
            return

        if not self.stack and self.calc_mode == 'NON_K' and self.constant_op in ['×', '÷%', '+%', '-%']:
            A = self.constant_val
            B = self.display_value
            op = self.constant_op[0] if len(self.constant_op) > 1 else self.constant_op
            
            if op == '×': result = A * B / 100
            elif op == '÷': result = (B / A) * 100 
            elif op == '+': result = A + (A * B / 100)
            elif op == '-': result = A - (A * B / 100)
            else: result = self.display_value
            
            self.display_value = result
            if not result.is_nan():
                self.memory_gt += result
                self.gt_updated = True
            self.is_entering_number = False
            self.last_button = '%'
            print(f"DEBUG: percent() chain end. Result={result}")
            return

        if not self.stack:
            self.display_value = self.display_value / 100
            self.is_entering_number = False
            return

        A, op = self.stack.pop()
        B = self.display_value
        result = self.display_value
        
        if self.calc_mode == 'NON_K':
            if op == '×':
                result = A * B / 100
                self.constant_op = '×'
                self.constant_val = A
            elif op == '÷':
                result = (A / B) * 100
                self.constant_op = '÷%' 
                self.constant_val = B
            elif op == '+':
                delta = A * B / 100
                result = A + delta
                self.constant_op = '+%'
                self.constant_val = A
                self.percentage_base = delta 
            elif op == '-':
                delta = A * B / 100
                result = A - delta
                self.constant_op = '-%'
                self.constant_val = A
                self.percentage_base = -delta 
        else:
            self.last_percent_op = op 
            if op == '×':
                result = A * B / 100
                self.percentage_base = A 
            elif op == '÷':
                result = (A / B) * 100
            elif op == '+':
                if B == 100: result = Decimal('NaN')
                else: result = A / (1 - B / 100)
                self.percentage_base = result - A 
                self.constant_val = A 
            elif op == '-':
                if B == 0: result = Decimal('NaN')
                else: result = (A - B) / B * 100

        self.display_value = result
        self.is_entering_number = False
        self.last_button = '%'
        
        if self.calc_mode == 'NON_K' and not result.is_nan():
            self.memory_gt += result
            self.gt_updated = True

        print(f"DEBUG: percent() end. Result={result}")

    def equals(self):
        print(f"DEBUG: equals() start. mode={self.calc_mode}, k_active={self.is_k_active}, display={self.display_value}")
        
        is_delta_case = (self.calc_mode == 'NON_K' and self.last_button == '%' and self.constant_op in ['+%', '-%'])

        result = self._resolve_pending_operation()
        self.display_value = result 
        
        if not is_delta_case and result is not None and not result.is_nan():
            self.memory_gt += result
            self.gt_updated = True
            print(f"DEBUG: GT updated. added {result}, total_gt {self.memory_gt}")
            
        self.is_entering_number = False
        self.last_button = '='
        self.input_buffer = ""

        self.percentage_base = None 
        self.last_percent_op = None

        print(f"DEBUG: equals() end. display={self.display_value}")

    def clear(self):
        self.input_buffer = ""
        self.display_value = Decimal('0')
        self.is_entering_number = True
        self.last_button = 'C'

    def all_clear(self):
        self.reset_state()
        self.memory_gt = Decimal('0')
        self.memory_m = Decimal('0')
        self.last_button = 'AC'

    def m_plus(self):
        if self.stack:
            self._resolve_pending_operation()
        self.memory_m += self.display_value
        self.m_updated = True
        print(f"DEBUG: M+ added {self.display_value}, total_m {self.memory_m}")
        self.is_entering_number = False

    def m_minus(self):
        if self.stack:
            self._resolve_pending_operation()
        self.memory_m -= self.display_value
        self.m_updated = True
        print(f"DEBUG: M- subtracted {self.display_value}, total_m {self.memory_m}")
        self.is_entering_number = False

    def m_recall(self):
        self.display_value = self.memory_m
        self.is_entering_number = False
        self.last_button = 'MR'

    def m_clear(self):
        self.memory_m = Decimal('0')
        self.last_button = 'MC'

    def gt_recall(self):
        if self.calc_mode == 'NON_K' and self.last_button == 'GT':
            self.memory_gt = Decimal('0')
            print("DEBUG: GT cleared via double-tap")

        print(f"DEBUG: GT recall. value={self.memory_gt}")
        self.display_value = self.memory_gt
        self.is_entering_number = False
        self.last_button = 'GT'

    def gt_clear(self):
        self.memory_gt = Decimal('0')
        self.last_button = 'GTC'

    def tax_plus(self):
        self.display_value = self.display_value * (1 + self.tax_rate / 100)
        self.is_entering_number = False
        self.last_button = 'TAX+'

    def tax_minus(self):
        self.display_value = self.display_value / (1 + self.tax_rate / 100)
        self.is_entering_number = False
        self.last_button = 'TAX-'

    def set_tax_rate(self, rate):
        self.tax_rate = Decimal(rate)

    def square_root(self):
        if self.display_value < 0:
            self.display_value = Decimal('NaN')
        else:
            self.display_value = self.display_value.sqrt()
        self.is_entering_number = False
        self.last_button = '√'

    def change_sign(self):
        self.display_value = -self.display_value
        self.input_buffer = str(self.display_value)
        self.last_button = '+/-'

    def backspace(self):
        if self.is_entering_number and self.input_buffer:
            self.input_buffer = self.input_buffer[:-1]
            if not self.input_buffer or self.input_buffer == "-":
                self.input_buffer = "0"
            self.display_value = Decimal(self.input_buffer)
        self.last_button = '▶'
