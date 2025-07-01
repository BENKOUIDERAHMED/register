import tkinter as tk
from HospitalGui import HospitalGUI
from home1 import AppointmentApp

# التطبيق الأساسي
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("1024x768")
        self.title("الرئيسية")
        # هذا الإطار يحتوي على كل الواجهات
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        self.frames = {}

        # إنشاء الواجهات وإضافتها
        for F in (HospitalGUI, AppointmentApp):
            page_name = F.__name__
            frame = F(container, self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("AppointmentApp")  

    def show_frame(self, page_name):
        if page_name == "HospitalGUI":
            self.title("نظام إدارة المستشفى")
        else:
            self.title("الرئيسية")
        frame = self.frames[page_name]
        frame.tkraise()


if __name__ == "__main__":
    app = App()
    app.mainloop()
