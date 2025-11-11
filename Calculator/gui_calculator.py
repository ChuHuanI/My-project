import tkinter as tk

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.geometry("400x600")
        self.resizable(0, 0)
        self.configure(bg="#1e1e1e")

        self.expression = ""
        self.input_text = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Configure the grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=4)
        self.grid_columnconfigure(0, weight=1)

        input_frame = tk.Frame(self, bg="#1e1e1e")
        input_frame.grid(row=0, column=0, sticky="nsew")
        input_frame.grid_columnconfigure(0, weight=1)

        input_field = tk.Entry(input_frame, font=('Segoe UI', 24, 'bold'), textvariable=self.input_text, bg="#1e1e1e", fg="white", bd=0, justify=tk.RIGHT)
        input_field.grid(row=0, column=0, sticky="nsew", padx=10, pady=20)

        btns_frame = tk.Frame(self, bg="#1e1e1e")
        btns_frame.grid(row=1, column=0, sticky="nsew")

        # Configure the button grid
        for i in range(4):
            btns_frame.grid_columnconfigure(i, weight=1)
        for i in range(5):
            btns_frame.grid_rowconfigure(i, weight=1)

        # Button styles
        btn_fg = "white"
        btn_font = ("Segoe UI", 19)
        num_bg = "#2c2c2c"
        op_bg = "#ff9f0a"
        clear_bg = "#a6a6a6"

        # First row
        tk.Button(btns_frame, text="C", fg=btn_fg, bg=clear_bg, cursor="hand2", font=btn_font, command=self.clear_input).grid(row=0, column=0, columnspan=2, sticky="nsew", padx=1, pady=1)
        tk.Button(btns_frame, text="/", fg=btn_fg, bg=op_bg, cursor="hand2", font=btn_font, command=lambda: self.add_to_expression("/")).grid(row=0, column=2, sticky="nsew", padx=1, pady=1)
        tk.Button(btns_frame, text="*", fg=btn_fg, bg=op_bg, cursor="hand2", font=btn_font, command=lambda: self.add_to_expression("*")).grid(row=0, column=3, sticky="nsew", padx=1, pady=1)

        # Second row
        tk.Button(btns_frame, text="7", fg=btn_fg, bg=num_bg, cursor="hand2", font=btn_font, command=lambda: self.add_to_expression(7)).grid(row=1, column=0, sticky="nsew", padx=1, pady=1)
        tk.Button(btns_frame, text="8", fg=btn_fg, bg=num_bg, cursor="hand2", font=btn_font, command=lambda: self.add_to_expression(8)).grid(row=1, column=1, sticky="nsew", padx=1, pady=1)
        tk.Button(btns_frame, text="9", fg=btn_fg, bg=num_bg, cursor="hand2", font=btn_font, command=lambda: self.add_to_expression(9)).grid(row=1, column=2, sticky="nsew", padx=1, pady=1)
        tk.Button(btns_frame, text="-", fg=btn_fg, bg=op_bg, cursor="hand2", font=btn_font, command=lambda: self.add_to_expression("-")).grid(row=1, column=3, sticky="nsew", padx=1, pady=1)

        # Third row
        tk.Button(btns_frame, text="4", fg=btn_fg, bg=num_bg, cursor="hand2", font=btn_font, command=lambda: self.add_to_expression(4)).grid(row=2, column=0, sticky="nsew", padx=1, pady=1)
        tk.Button(btns_frame, text="5", fg=btn_fg, bg=num_bg, cursor="hand2", font=btn_font, command=lambda: self.add_to_expression(5)).grid(row=2, column=1, sticky="nsew", padx=1, pady=1)
        tk.Button(btns_frame, text="6", fg=btn_fg, bg=num_bg, cursor="hand2", font=btn_font, command=lambda: self.add_to_expression(6)).grid(row=2, column=2, sticky="nsew", padx=1, pady=1)
        tk.Button(btns_frame, text="+", fg=btn_fg, bg=op_bg, cursor="hand2", font=btn_font, command=lambda: self.add_to_expression("+")).grid(row=2, column=3, sticky="nsew", padx=1, pady=1)

        # Fourth row
        tk.Button(btns_frame, text="1", fg=btn_fg, bg=num_bg, cursor="hand2", font=btn_font, command=lambda: self.add_to_expression(1)).grid(row=3, column=0, sticky="nsew", padx=1, pady=1)
        tk.Button(btns_frame, text="2", fg=btn_fg, bg=num_bg, cursor="hand2", font=btn_font, command=lambda: self.add_to_expression(2)).grid(row=3, column=1, sticky="nsew", padx=1, pady=1)
        tk.Button(btns_frame, text="3", fg=btn_fg, bg=num_bg, cursor="hand2", font=btn_font, command=lambda: self.add_to_expression(3)).grid(row=3, column=2, sticky="nsew", padx=1, pady=1)
        tk.Button(btns_frame, text="=", fg=btn_fg, bg=op_bg, cursor="hand2", font=btn_font, command=self.calculate).grid(row=3, column=3, rowspan=2, sticky="nsew", padx=1, pady=1)

        # Fifth row
        tk.Button(btns_frame, text="0", fg=btn_fg, bg=num_bg, cursor="hand2", font=btn_font, command=lambda: self.add_to_expression(0)).grid(row=4, column=0, columnspan=2, sticky="nsew", padx=1, pady=1)
        tk.Button(btns_frame, text=".", fg=btn_fg, bg=num_bg, cursor="hand2", font=btn_font, command=lambda: self.add_to_expression(".")).grid(row=4, column=2, sticky="nsew", padx=1, pady=1)

    def add_to_expression(self, value):
        if "=" in self.input_text.get():
            if str(value) in "+-*/":
                self.input_text.set(self.expression)
            else:
                self.expression = ""
                self.input_text.set("")

        self.expression = self.expression + str(value)
        self.input_text.set(self.expression)

    def clear_input(self):
        self.expression = ""
        self.input_text.set("")

    def calculate(self):
        try:
            calculation = self.expression
            result = str(eval(calculation))
            self.input_text.set(calculation + " = " + result)
            self.expression = result
        except:
            self.input_text.set("Error")
            self.expression = ""

if __name__ == "__main__":
    app = Calculator()
    app.mainloop()