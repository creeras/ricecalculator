import math
from decimal import Decimal, getcontext, localcontext, ROUND_DOWN, ROUND_HALF_UP

class CalculatorEngineV2:
    def __init__(self):
        getcontext().prec = 28  # Higher internal precision
        self.rounding_mode = 'F'
        self.decimal_places = 4
        self.calc_mode = 'NON_K'  # 'K' or 'NON_K'
        
        self.reset_state()
        self.memory_m = Decimal('0')
        self.memory_gt = Decimal('0')
        self.tax_rate = Decimal('10')
        
        # Exchange rates
        self.exchange_rates = {
            'C1': Decimal('1'), 
            'C2': Decimal('1350'), 
            'C3': Decimal('160'), 
            'C4': Decimal('0.95')
        }
        self.currency_symbols = {'C1': '$', 'C2': '₩', 'C3': '¥', 'C4': '€'}
        self.mode = 'M'  # 'M' for Memory, 'EX' for Exchange

    def reset_state(self):
        self.display_value = Decimal('0')
        self.input_buffer = ""
        self.is_entering_number = True
        
        # Stack concept
        self.stack = [] # Stores (value, operator)
        self.constant_op = None
        self.constant_val = None
        self.is_k_active = False
        
        self.last_operator = None
        self.last_button = None
        self.gt_updated = False # Flag for UI to flash GT button
        self.m_updated = False  # Flag for UI to flash MR button
        self.percentage_base = None # Track principal or profit amount
        self.last_percent_op = None # Track if last % was from *, /, +, or -

    def format_number(self, number: Decimal) -> str:
        # Avoid scientific notation and handle trailing zeros
        if self.rounding_mode == 'F':
            # Use normalize to remove trailing zeros, but avoid scientific notation
            formatted = format(number, 'f')
            if '.' in formatted:
                formatted = formatted.rstrip('0').rstrip('.')
            return formatted
        
        places = 2 if self.decimal_places == 'Add2' else int(self.decimal_places)
        
        with localcontext() as ctx:
            if self.rounding_mode == 'Cut':
                ctx.rounding = ROUND_DOWN
            elif self.rounding_mode == '5/4':
                ctx.rounding = ROUND_HALF_UP
            
            quantized = number.quantize(Decimal('1.' + '0' * places))
            return format(quantized, 'f')

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
        
        if self.input_buffer == "0" and digit != ".":
            self.input_buffer = digit
        else:
            self.input_buffer += digit
        
        self.display_value = Decimal(self.input_buffer)
        self.last_button = digit  # Track digit input to prevent accidental K-mode

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
            # K-type logic: Double tap operator sets constant
            if self.last_button == op:
                self.is_k_active = True
                self.constant_op = op
                self.constant_val = self.display_value
                self.is_entering_number = False
                self.last_button = op
                print(f"DEBUG: K-mode activated. constant_op='{op}', constant_val={self.constant_val}")
                return

        # Normal operation or operator change
        if self.is_entering_number:
            if self.stack:
                prev_val, prev_op = self.stack.pop()
                self.display_value = self._perform_op(prev_val, prev_op, self.display_value)
                print(f"DEBUG: Intermediate calculation. {prev_val} {prev_op} ... = {self.display_value}")
            self.is_entering_number = False
            
        self.stack = [(self.display_value, op)]
        self.is_k_active = False # New operator always clears K unless it's a double-tap
        
        # CASIO special: chain operations after % 
        if self.calc_mode == 'K' and self.percentage_base is not None and self.last_button == '%':
            if op in ['+', '-']:
                if self.last_percent_op == '×':
                    # Add-on/Discount: A + (A*B/100) or A - (A*B/100)
                    self.display_value = self._perform_op(self.percentage_base, op, self.display_value)
                elif self.last_percent_op == '+':
                    # Markup result: pressing '-' shows profit (already stored in percentage_base)
                    if op == '-':
                        self.display_value = self.percentage_base
                
                self.percentage_base = None # Consume it
                self.last_percent_op = None
                self.stack = [] # Terminate chain: result is final for this sequence
                self.is_entering_number = False
                self.last_button = op
                print(f"DEBUG: CASIO % Chain (Resolved). Display={self.display_value}, Stack Cleared")
                return

        self.last_button = op
        print(f"DEBUG: set_operator() end. stack={self.stack}")

    def _resolve_pending_operation(self):
        """Internal helper to resolve pending stack or constant operations without touching GT."""
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
            # SHARP (Non-K) constant rules
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
                    self.percentage_base = None # Consume it
                    self.display_value = res 
                    print(f"DEBUG: Resolve Delta Display. Result={res}")
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
        
        # If no stack but we have a constant op (SHARP style chain)
        if not self.stack and self.calc_mode == 'NON_K' and self.constant_op in ['×', '÷%', '+%', '-%']:
            # Handle continuous % chain in SHARP mode
            A = self.constant_val
            B = self.display_value
            op = self.constant_op[0] if len(self.constant_op) > 1 else self.constant_op
            
            if op == '×': result = A * B / 100
            elif op == '÷': result = (B / A) * 100 # In SHARP, divisor is constant
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
            # No base, just convert display to percentage
            self.display_value = self.display_value / 100
            self.is_entering_number = False
            return

        A, op = self.stack.pop()
        B = self.display_value
        result = self.display_value
        
        if self.calc_mode == 'NON_K':
            # SHARP Style
            if op == '×':
                result = A * B / 100
                self.constant_op = '×'
                self.constant_val = A
            elif op == '÷':
                result = (A / B) * 100
                self.constant_op = '÷%' # Special label for repeated % div
                self.constant_val = B
            elif op == '+':
                delta = A * B / 100
                result = A + delta
                self.constant_op = '+%'
                self.constant_val = A
                self.percentage_base = delta # Store delta for '=' key
            elif op == '-':
                delta = A * B / 100
                result = A - delta
                self.constant_op = '-%'
                self.constant_val = A
                self.percentage_base = -delta # Store negative delta for '=' key
        else:
            # CASIO Style
            self.last_percent_op = op # Store the trigger op
            if op == '×':
                result = A * B / 100
                self.percentage_base = A # Store principal for subsequent + or -
            elif op == '÷':
                result = (A / B) * 100
            elif op == '+':
                # Markup: A / (1 - B/100)
                if B == 100: result = Decimal('NaN')
                else: result = A / (1 - B / 100)
                self.percentage_base = result - A # Profit amount for subsequent -
                self.constant_val = A # Base for verification
            elif op == '-':
                # Margin: (A - B) / B * 100
                if B == 0: result = Decimal('NaN')
                else: result = (A - B) / B * 100

        self.display_value = result
        self.is_entering_number = False
        self.last_button = '%'
        
        # Note: Non-K mode % acts as a terminator like =, adding to GT.
        if self.calc_mode == 'NON_K' and not result.is_nan():
            self.memory_gt += result
            self.gt_updated = True

        print(f"DEBUG: percent() end. Result={result}")

    def equals(self):
        print(f"DEBUG: equals() start. mode={self.calc_mode}, k_active={self.is_k_active}, display={self.display_value}")
        
        # Check if this is a special delta display case for Non-K
        is_delta_case = (self.calc_mode == 'NON_K' and self.last_button == '%' and self.constant_op in ['+%', '-%'])

        # Calculate result
        result = self._resolve_pending_operation()
        self.display_value = result # EXPLICITLY ensuring display is updated
        
        # Update GT ONLY if it's NOT just a delta inspection
        if not is_delta_case and result is not None and not result.is_nan():
            self.memory_gt += result
            self.gt_updated = True
            print(f"DEBUG: GT updated. added {result}, total_gt {self.memory_gt}")
            
        self.is_entering_number = False
        self.last_button = '='
        self.input_buffer = ""

        # Clear percentage related states ONLY AFTER resolution
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

    # Memory functions
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
        # Non-K mode: Double tap GT clears it
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

    # Tax functions
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

    # Root
    def square_root(self):
        if self.display_value < 0:
            self.display_value = Decimal('NaN')
        else:
            self.display_value = self.display_value.sqrt()
        self.is_entering_number = False
        self.last_button = '√'

    # Sign change
    def change_sign(self):
        self.display_value = -self.display_value
        self.input_buffer = str(self.display_value)
        self.last_button = '+/-'

    # Backspace
    def backspace(self):
        if self.is_entering_number and self.input_buffer:
            self.input_buffer = self.input_buffer[:-1]
            if not self.input_buffer or self.input_buffer == "-":
                self.input_buffer = "0"
            self.display_value = Decimal(self.input_buffer)
        self.last_button = '▶'
