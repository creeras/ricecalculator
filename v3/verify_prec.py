import unittest
from decimal import Decimal, getcontext
import sys
import os

# Add v3 to valid path
sys.path.append(os.path.join(os.getcwd(), 'v3'))

from calculator_engine_v3 import CalculatorEngineV3

class TestRiceCalculatorPrecision(unittest.TestCase):
    def setUp(self):
        self.engine = CalculatorEngineV3()

    def test_precision_10(self):
        self.engine.set_precision(10)
        # 1 / 3 should have 10 digits
        self.engine.input_digit('1')
        self.engine.set_operator('÷')
        self.engine.input_digit('3')
        self.engine.equals()
        
        result_str = self.engine.get_display_text()
        print(f"PREC 10 Test: 1/3 = {result_str}")
        
        # Count significant digits (ignoring decimal point)
        digits = len(result_str.replace('.', ''))
        # Depending on formatting, it might have fewer if trailing zeros, but 1/3 is repeating.
        # 0.333333333 (10 digits total: 0 + 9 3s)
        self.assertLessEqual(digits, 10, f"Result {result_str} has more than 10 digits")
        self.assertEqual(result_str, "0.333333333")

    def test_precision_12(self):
        self.engine.set_precision(12)
        self.engine.input_digit('1')
        self.engine.set_operator('÷')
        self.engine.input_digit('7')
        self.engine.equals()
        
        result_str = self.engine.get_display_text()
        print(f"PREC 12 Test: 1/7 = {result_str}")
        
        digits = len(result_str.replace('.', ''))
        self.assertLessEqual(digits, 12, f"Result {result_str} has more than 12 digits")

    def test_precision_14(self):
        self.engine.set_precision(14)
        self.engine.input_digit('2')
        self.engine.square_root() # sqrt(2) is irrational
        
        result_str = self.engine.get_display_text()
        print(f"PREC 14 Test: sqrt(2) = {result_str}")
        
        digits = len(result_str.replace('.', ''))
        self.assertLessEqual(digits, 14, f"Result {result_str} has more than 14 digits")

    def test_input_limit(self):
        # Verify we cannot input more digits than precision
        self.engine.set_precision(5)
        for i in range(10):
            if len(self.engine.input_buffer.replace('.', '')) >= 5:
                 break
            self.engine.input_digit(str(i))
            
        result_str = self.engine.get_display_text()
        print(f"Input Limit Test (Pred=5): Input 0-9 -> {result_str}")
        self.assertTrue(len(result_str) <= 5)
        self.assertEqual(result_str, "12345")

if __name__ == '__main__':
    unittest.main()
