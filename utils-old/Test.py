import tkinter as tk

class Sliders:
    def __init__(self, master):
        self.slider1 = tk.Scale(master, from_=0, to=30, orient="horizontal", width=20, length=300, label="Blur1",
                                bg="white", troughcolor="lightgray",
                                highlightthickness=0, sliderrelief="flat",
                                command=self.update_value)
        self.slider1.pack(pady=20)
        self.slider1.set(15)

        self.slider2 = tk.Scale(master, from_=0, to=30, orient="horizontal", width=20, length=300, label="Blur2",
                                bg="white", troughcolor="lightgray",
                                highlightthickness=0, sliderrelief="flat",
                                command=self.update_value)
        self.slider2.pack(pady=20)
        self.slider2.set(25)

        self.slider3 = tk.Scale(master, from_=0, to=300, orient="horizontal", width=20, length=300, label="Tresh1",
                                bg="white", troughcolor="lightgray",
                                highlightthickness=0, sliderrelief="flat",
                                command=self.update_value)
        self.slider3.pack(pady=20)
        self.slider3.set(100)

        self.slider4 = tk.Scale(master, from_=0, to=300, orient="horizontal", width=20, length=300, label="Tresh2",
                                bg="white", troughcolor="lightgray",
                                highlightthickness=0, sliderrelief="flat",
                                command=self.update_value)
        self.slider4.pack(pady=20)
        self.slider4.set(255)

    def update_value(self, value):
        self.value1 = int(self.slider1.get())
        self.value2 = int(self.slider2.get())
        self.value3 = int(self.slider3.get())
        self.value4 = int(self.slider4.get())

