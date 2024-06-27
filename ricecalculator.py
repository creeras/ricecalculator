import tkinter as tk

class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("Allcalc Rice Calculator")
        master.geometry("450x620")

        # 디스플레이 
        # 폰트 다운로드 주소 : https://www.dafont.com/ds-digital.font
        self.display = tk.Entry(master, width=20, justify='right', font=('DS-Digital', 72), relief='sunken', bd=5)
        self.display.grid(row=0, column=0, columnspan=5, padx=10, pady=10, sticky='nsew')

        # 스위치
        self.switch_frame = tk.Frame(master)
        self.switch_frame.grid(row=1, column=0, columnspan=5, pady=5)

        self.mode_switch = tk.IntVar(value=0)
        self.mode_scale = tk.Scale(self.switch_frame, from_=0, to=2, orient=tk.HORIZONTAL, length=120, showvalue=0,
                                   tickinterval=1, resolution=1, variable=self.mode_switch)
        self.mode_scale.pack(side=tk.LEFT, padx=5)
        
        self.mode_labels = ["F", "Cut ", " 5/4"]
        for i, label in enumerate(self.mode_labels):
            tk.Label(self.switch_frame, text=label).place(x=18 + i * 38, y=20)

        self.number_switch = tk.IntVar(value=0)
        self.number_scale = tk.Scale(self.switch_frame, from_=0, to=5, orient=tk.HORIZONTAL, length=280, showvalue=0,
                                     tickinterval=1, resolution=1, variable=self.number_switch)
        self.number_scale.pack(side=tk.LEFT, padx=5)
        
        self.number_labels = [" 4", " 3 ", " 2 ", " 1 ", " 0 ", "Add2"]
        for i, label in enumerate(self.number_labels):
            tk.Label(self.switch_frame, text=label).place(x=150 + i * 48, y=20)

        # 버튼 생성 및 배치
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
            if (btn[0] == 'AC' or btn[0] == 'C') :  # 'AC' 'C' 버튼에 대해서만 배경색을 빨간색으로 설정
                tk.Button(master, text=btn[0], width=10, height=2, font=('Arial', 16), bg='orange').grid(row=btn[1], column=btn[2], sticky='nsew')
            elif (btn[0].isdigit() or btn[0] == '.') :  # 숫자 or Dot 버튼에 대해서 배경색을 회색으로 설정
                tk.Button(master, text=btn[0], width=10, height=2, font=('DS-Digital', 18, 'bold'), bg='grey').grid(row=btn[1], column=btn[2], sticky='nsew')
            elif len(btn) == 4:  # For the '+' button rowspan
                tk.Button(master, text=btn[0], width=10, height=4, font=('Arial', 16)).grid(row=btn[1], column=btn[2], rowspan=btn[3], sticky='nsew')
            elif len(btn) == 5:  # For the 'allcalc.org ' button columnspan
                tk.Button(master, text=btn[0], width=10, height=2, font=('Arial', 16)).grid(row=btn[1], column=btn[2], rowspan=btn[3], columnspan=btn[4], sticky='nsew')
            else:
                tk.Button(master, text=btn[0], width=10, height=2, font=('Arial', 16)).grid(row=btn[1], column=btn[2], sticky='nsew')

        # Make the grid cells expandable
        for i in range(9):
            master.grid_rowconfigure(i, weight=1)
        for i in range(5):
            master.grid_columnconfigure(i, weight=1)

    def click(self, key):
        # 버튼 클릭 기능은 여기에 구현됩니다
        pass

root = tk.Tk()
my_calculator = Calculator(root)
root.mainloop()