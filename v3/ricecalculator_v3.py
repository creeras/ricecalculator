import tkinter as tk
from tkinter import font as tkfont
from decimal import Decimal
import os
import sys

# Assume engine is in the same directory
from calculator_engine_v3 import CalculatorEngineV3

class RiceCalculatorV3:
    def __init__(self, master):
        self.master = master
        master.title("Rice Calculator V3 (K/Non-K)")
        # Set a fixed size initially to avoid jumping
        master.geometry("720x750")
        
        self.engine = CalculatorEngineV3()
        self.active_flashes = {} # Track active timers for flashing buttons
        
        self.setup_ui()
        # Initialize default settings from UI vars
        self.update_settings()
        self.update_display()

    def setup_ui(self):
        # 1. Mode Switch Frame
        self.mode_frame = tk.Frame(self.master)
        self.mode_frame.grid(row=0, column=0, columnspan=5, pady=5, sticky='ew')
        
        tk.Label(self.mode_frame, text="Calculator Type:").pack(side=tk.LEFT, padx=5)
        self.calc_type_var = tk.StringVar(value="NON_K")
        tk.Radiobutton(self.mode_frame, text="Non-K", variable=self.calc_type_var, value="NON_K", command=self.update_engine_mode).pack(side=tk.LEFT)
        tk.Radiobutton(self.mode_frame, text="K-Type (CASIO)", variable=self.calc_type_var, value="K", command=self.update_engine_mode).pack(side=tk.LEFT)

        # 2. Status Display (History/State)
        self.status_display = tk.Entry(self.master, width=60, justify='right', font=('Arial', 12), relief='flat', bd=2)
        self.status_display.grid(row=1, column=0, columnspan=5, padx=10, sticky='ew')

        # 3. Main Result Display
        self.display_frame = tk.Frame(self.master, bg='black', bd=5, relief='sunken')
        self.display_frame.grid(row=2, column=0, columnspan=5, padx=10, pady=10, sticky='nsew')
        
        self.display = tk.Text(self.display_frame, height=1, width=20, font=('DS-Digital', 72), bg='black', fg='#00FF00', relief='flat', bd=0)
        self.display.pack(expand=True, fill='both')
        self.display.tag_configure("right", justify='right')
        
        self.k_indicator = tk.Label(self.display_frame, text="", font=('Arial', 14, 'bold'), bg='black', fg='#00FF00')
        self.k_indicator.place(x=5, y=5)

        # 4. Settings Switch Frame (Precision, Rounding, Decimal)
        self.switch_frame = tk.Frame(self.master)
        self.switch_frame.grid(row=3, column=0, columnspan=5, pady=5, sticky='ew')
        
        self.setup_precision_switch()
        self.setup_rounding_switch()
        self.setup_decimal_switch()

        # 5. Buttons Setup
        self.setup_buttons()

        # Configure weights
        for i in range(12): # Rows
            self.master.grid_rowconfigure(i, weight=1)
        for i in range(5): # Columns
            self.master.grid_columnconfigure(i, weight=1)

    def setup_precision_switch(self):
        f = tk.Frame(self.switch_frame)
        f.pack(side=tk.LEFT, padx=10)
        tk.Label(f, text="PREC").pack()
        # 0 -> 10, 1 -> 12, 2 -> 14
        self.prec_var = tk.IntVar(value=1) # Default to 12
        s = tk.Scale(f, from_=0, to=2, orient=tk.HORIZONTAL, showvalue=0, length=80, variable=self.prec_var, command=self.update_settings)
        s.pack()
        tk.Label(f, text="10  12  14", font=('Arial', 8)).pack()

    def setup_rounding_switch(self):
        f = tk.Frame(self.switch_frame)
        f.pack(side=tk.LEFT, padx=10)
        tk.Label(f, text="ROUND").pack()
        self.round_var = tk.IntVar(value=0)
        s = tk.Scale(f, from_=0, to=2, orient=tk.HORIZONTAL, showvalue=0, length=80, variable=self.round_var, command=self.update_settings)
        s.pack()
        tk.Label(f, text="F  Cut  5/4", font=('Arial', 8)).pack()

    def setup_decimal_switch(self):
        f = tk.Frame(self.switch_frame)
        f.pack(side=tk.LEFT, padx=10)
        tk.Label(f, text="DECIMAL").pack()
        self.dec_var = tk.IntVar(value=0)
        s = tk.Scale(f, from_=0, to=5, orient=tk.HORIZONTAL, showvalue=0, length=200, variable=self.dec_var, command=self.update_settings)
        s.pack()
        tk.Label(f, text="4  3  2  1  0  Add2", font=('Arial', 8)).pack()

    def setup_buttons(self):
        # layout (text, row, col, rowspan, colspan)
        buttons = [
            ('TAX-', 0, 3, 1, 1), ('TAX+', 0, 4, 1, 1),
            ('M/EX', 1, 0, 1, 1), ('%', 1, 1, 1, 1), ('√', 1, 2, 1, 1), ('▶', 1, 3, 1, 1), ('GT', 1, 4, 1, 1),
            ('MC', 2, 0, 1, 1), ('MR', 2, 1, 1, 1), ('M-', 2, 2, 1, 1), ('M+', 2, 3, 1, 1), ('÷', 2, 4, 1, 1),
            ('+/-', 3, 0, 1, 1), ('7', 3, 1, 1, 1), ('8', 3, 2, 1, 1), ('9', 3, 3, 1, 1), ('×', 3, 4, 1, 1),
            ('C', 4, 0, 1, 1), ('4', 4, 1, 1, 1), ('5', 4, 2, 1, 1), ('6', 4, 3, 1, 1), ('-', 4, 4, 1, 1),
            ('AC', 5, 0, 1, 1), ('1', 5, 1, 1, 1), ('2', 5, 2, 1, 1), ('3', 5, 3, 1, 1), ('+', 5, 4, 2, 1),
            ('0', 6, 0, 1, 1), ('00', 6, 1, 1, 1), ('.', 6, 2, 1, 1), ('=', 6, 3, 1, 1)
        ]

        self.btn_objs = {}
        for b in buttons:
            text = b[0]
            row = b[1] + 4
            col = b[2]
            rs = b[3] if len(b) > 3 else 1
            cs = b[4] if len(b) > 4 else 1
            
            bg = '#f0f0f0'
            if text in ['AC', 'C']: bg = 'orange'
            elif text.isdigit() or text in ['.', '00']: bg = 'white'
            elif text in ['+', '-', '×', '÷', '=']: bg = '#e0e0e0'
            elif text in ['MR', 'GT']: bg = '#f0f0f0' # Explicitly gray functional buttons
            
            btn = tk.Button(self.master, text=text, font=('Arial', 14, 'bold'), 
                           bg=bg, relief='raised', bd=3,
                           command=lambda t=text: self.on_click(t))
            btn.grid(row=row, column=col, rowspan=rs, columnspan=cs, sticky='nsew', padx=2, pady=2)
            self.btn_objs[text] = btn

    def update_engine_mode(self):
        self.engine.all_clear()
        self.engine.calc_mode = self.calc_type_var.get()
        self.update_display()

    def update_settings(self, val=None):
        prec_map = [10, 12, 14]
        round_modes = ['F', 'Cut', '5/4']
        dec_modes = ['4', '3', '2', '1', '0', 'Add2']
        
        # KEY FIX: Pass precision limit to engine
        selected_prec = prec_map[self.prec_var.get()]
        self.engine.set_precision(selected_prec)

        self.engine.rounding_mode = round_modes[self.round_var.get()]
        self.engine.decimal_places = dec_modes[self.dec_var.get()]
        
        self.update_display()

    def on_click(self, key):
        if key.isdigit() or key in ['.', '00']:
            if key == '00':
                self.engine.input_digit('0')
                self.engine.input_digit('0')
            else:
                self.engine.input_digit(key)
        elif key in ['+', '-', '×', '÷']:
            self.engine.set_operator(key)
        elif key == '=':
            self.engine.equals()
        elif key == 'AC':
            self.engine.all_clear()
        elif key == 'C':
            self.engine.clear()
        elif key == '▶':
            self.engine.backspace()
        elif key == '+/-':
            self.engine.change_sign()
        elif key == '√':
            self.engine.square_root()
        elif key == 'M+':
            self.engine.m_plus()
        elif key == 'M-':
            self.engine.m_minus()
        elif key == 'MR':
            self.engine.m_recall()
        elif key == 'MC':
            self.engine.m_clear()
        elif key == 'GT':
            self.engine.gt_recall()
        elif key == 'TAX+':
            self.engine.tax_plus()
        elif key == 'TAX-':
            self.engine.tax_minus()
        elif key == '%':
            self.engine.percent()
        
        self.update_display()

    def flash_button(self, btn_name, color="#ffffff"):
        if btn_name in self.btn_objs:
            # Cancel existing timer for this button if it exists
            if btn_name in self.active_flashes:
                self.master.after_cancel(self.active_flashes[btn_name])
            
            # Apply flash color
            self.btn_objs[btn_name].config(bg=color)
            self.master.update_idletasks() # Force immediate rendering
            
            def end_flash():
                self.active_flashes.pop(btn_name, None)
                self.update_display()
            
            # Schedule restoration (Reduced to 200ms for snappier feedback)
            self.active_flashes[btn_name] = self.master.after(200, end_flash)

    def update_display(self):
        # 1. Indicator
        k_text = "K" if (getattr(self.engine, 'is_k_active', False)) else ""
        self.k_indicator.config(text=k_text)
        
        # 2. Main display - Use raw buffer if available
        raw_text = self.engine.get_display_text()
        
        if self.engine.is_entering_number:
            display_str = raw_text
            # No comma formatting while entering (prevents "1,0" issue)
        else:
            # Format finalized numbers with commas
            try:
                if 'NaN' not in raw_text and 'Error' not in raw_text:
                    if '.' in raw_text:
                        integer, decimal = raw_text.split('.')
                        integer = "{:,}".format(int(integer)) if integer not in ["", "-"] else integer
                        display_str = f"{integer}.{decimal}"
                    else:
                        display_str = "{:,}".format(int(raw_text))
                else:
                    display_str = raw_text
            except ValueError:
                display_str = raw_text

        self.display.delete('1.0', tk.END)
        self.display.insert('1.0', display_str, "right")

        # 3. Status/History
        op_text = ""
        if self.engine.stack:
            v, op = self.engine.stack[-1]
            op_text = f"{v} {op}"
        self.status_display.delete(0, tk.END)
        self.status_display.insert(0, op_text)

        # 4. Memory Change Logic (Flashing)
        if self.engine.gt_updated:
            self.engine.gt_updated = False
            self.flash_button('GT', "#ffffff") # White flash for maximum contrast
        
        if self.engine.m_updated:
            self.engine.m_updated = False
            self.flash_button('MR', "#ffffff") # White flash for maximum contrast

        # 5. Button highlighting (Only if NOT currently flashing)
        if 'MR' not in self.active_flashes:
            if self.engine.memory_m != 0:
                self.btn_objs['MR'].config(bg='#c8ffc8') # Light Green persistent
            else:
                self.btn_objs['MR'].config(bg='#f0f0f0') # Gray default
                
        if 'GT' not in self.active_flashes:
            if self.engine.memory_gt != 0:
                self.btn_objs['GT'].config(bg='#c8c8ff') # Light Blue persistent
            else:
                self.btn_objs['GT'].config(bg='#f0f0f0') # Gray default
        
        print(f"DEBUG: update_display finished. M={self.engine.memory_m}, GT={self.engine.memory_gt}, flashes={list(self.active_flashes.keys())}")

def main():
    root = tk.Tk()
    app = RiceCalculatorV3(root)
    root.mainloop()

if __name__ == "__main__":
    main()
