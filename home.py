import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkcalendar import DateEntry

class AppointmentApp(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller  # حفظ المرجع للتحكم في التنقل بين الواجهات

        # Style
        style = ttk.Style(self)
        style.theme_use('vista')
        style.configure("TLabel", font=("Arial", 11))
        style.configure("TButton", font=("Arial", 10))
        style.configure("TEntry", font=("Arial", 11))
        style.configure("TLabelframe.Label", font=("Arial", 12, "bold"))

        self.configure(bg="#e0e0e0")

        self.appointment_id = 1
        self.entry_widgets = {}

        self.create_top_bar(controller)
        self.create_main_content()
        self.update_time()

    def create_top_bar(self , controller):
        top_bar = tk.Frame(self, bg="#c5d6e2", height=40)
        ttk.Button(top_bar, text="ادارة", command=lambda: controller.show_frame("HospitalGUI")).pack(side="left", padx=5, pady=5)
        top_bar.pack(fill="x", side="top")
        self.time_label = tk.Label(top_bar, font=("Arial", 12), bg=top_bar['bg'])
        self.time_label.pack(side="left", padx=20, pady=5)
        title_label = tk.Label(top_bar, text="عيادة الأسنان", font=("Arial", 14, "bold"), bg=top_bar['bg'])
        title_label.pack(side="right", padx=20, pady=5)
        settings_button = ttk.Button(top_bar, text="الإعدادات")
        settings_button.pack(side="right", padx=5)

    def create_main_content(self):
        main_frame = tk.Frame(self, bg=self['bg'])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.columnconfigure(0, weight=3, minsize=400)
        main_frame.columnconfigure(1, weight=2, minsize=300)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=2)
        main_frame.rowconfigure(2, weight=0)
        patient_info_frame = self.create_frame(main_frame, "بيانات المريض")
        patient_info_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=5, pady=5)
        appointment_details_frame = self.create_frame(main_frame, "تفاصيل الموعد")
        appointment_details_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        notes_frame = self.create_frame(main_frame, "التشخيص والعلاج")
        notes_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        buttons_frame = tk.Frame(main_frame, bg=self['bg'])
        buttons_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        self.create_patient_info_widgets(patient_info_frame)
        self.create_appointment_details_widgets(appointment_details_frame)
        self.create_notes_widgets(notes_frame)
        self.create_buttons(buttons_frame)

    def create_frame(self, parent, text):
        return ttk.LabelFrame(parent, text=text, padding=10)

    def update_time(self):
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%I:%M:%S %p")
        day_str = now.strftime("%A")
        arabic_day = {
            "Saturday": "السبت", "Sunday": "الأحد", "Monday": "الإثنين",
            "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء", "Thursday": "الخميس", "Friday": "الجمعة"
        }
        day_str_ar = arabic_day.get(day_str, day_str)

        full_str = f"{day_str_ar} {date_str}   الوقت: {time_str}"
        self.time_label.config(text=full_str)
        self.after(1000, self.update_time)

    def save_appointment(self):
        print("جاري حفظ الموعد...")
        appointment_data = {}
        for name, widget_info in self.entry_widgets.items():
            widget = widget_info['widget']
            if widget_info['type'] == 'text':
                appointment_data[name] = widget.get("1.0", "end-1c")
            else:
                appointment_data[name] = widget.get()

        print(f"بيانات الموعد المحفوظة: {appointment_data}")
        self.appointment_id += 1
        self.appointment_id_var.set(str(self.appointment_id))
        self.clear_fields()

    def view_images(self):
        print("عرض الصور...")

    def right_align_text(self, event):
        widget = event.widget
        widget.tag_add("rtl", "1.0", "end")
        widget.see(tk.INSERT)

    def clear_fields(self):
        for name, widget_info in self.entry_widgets.items():
            if name == "رقم الموعد":
                continue
            widget = widget_info['widget']
            if widget_info['type'] == 'entry':
                widget.delete(0, 'end')
            elif widget_info['type'] == 'text':
                widget.delete('1.0', 'end')
            elif widget_info['type'] == 'date':
                widget.set_date(datetime.now())

    def create_patient_info_widgets(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=0)
        fields = ["رقم الموعد", "اسم المريض", "لقب المريض", "الجنس", "العمر", "رقم الهاتف", "المبلغ المدفوع", "المبلغ المتبقي"]

        self.appointment_id_var = tk.StringVar(value=str(self.appointment_id))
        self.add_widget(parent, fields[0], 'entry', 0,state='readonly',   textvariable=self.appointment_id_var)

        for i, field in enumerate(fields[1:], start=1):
            self.add_widget(parent, field, 'entry', i)

    def create_appointment_details_widgets(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=0)

        self.add_widget(parent, "تاريخ الموعد:", 'date', 0)
        self.add_widget(parent, "الوقت:", 'entry', 1)
        self.add_widget(parent, "تاريخ الموعد القادم:", 'date', 2)

    def create_notes_widgets(self, parent):
        parent.columnconfigure(0, weight=1)
        text_fields = ["ملاحظات:", "العلاج:", "الأعراض:"]
        for i, field in enumerate(text_fields):
            parent.rowconfigure(i*2, weight=0)
            parent.rowconfigure(i*2 + 1, weight=1)
            self.add_widget(parent, field, 'text', i, is_note=True)

    def add_widget(self, parent, field_name, widget_type, row, is_note=False, **kwargs):
        clean_name = field_name.replace(":", "")
        if is_note:
            label = ttk.Label(parent, text=field_name)
            label.grid(row=row*2, column=0, sticky="e", padx=5, pady=(10,0))
            widget_row = row*2 + 1
            widget_col = 0
            sticky = "nsew"
        else:
            label = ttk.Label(parent, text=f"{field_name}:")
            label.grid(row=row, column=1, sticky="w", padx=5, pady=5)
            widget_row = row
            widget_col = 0
            sticky = "ew"

        if widget_type == 'entry':
            widget = ttk.Entry(parent, justify='right', **kwargs)
        elif widget_type == 'date':
            widget = DateEntry(parent, width=18, background='darkblue', foreground='white',
                               borderwidth=2, date_pattern='yyyy-mm-dd', justify='right', locale='ar_SA')
        elif widget_type == 'text':
            widget = tk.Text(parent, height=3, relief="solid", borderwidth=1, font=("Tahoma", 11))
            widget.tag_configure("rtl", justify='right')
            widget.bind("<KeyRelease>", self.right_align_text)

        widget.grid(row=widget_row, column=widget_col, sticky=sticky, padx=5, pady=2)
        self.entry_widgets[clean_name] = {'widget': widget, 'type': widget_type}

    def create_buttons(self, parent):
        button_container = tk.Frame(parent, bg=self['bg'])
        button_container.pack()
        buttons_layout = [
            ("الموعد التالي", "الموعد السابق", "تعديل البيانات"),
            ("عرض الصور", "حذف موعد", "إنهاء")
        ]

        commands = {
            "عرض الصور": self.view_images,
            "إنهاء": self.controller.quit if hasattr(self.controller, 'quit') else self.quit
        }

        for row_idx, row_buttons in enumerate(buttons_layout):
            for col_idx, btn_text in enumerate(row_buttons):
                cmd = commands.get(btn_text)
                button = ttk.Button(button_container, text=btn_text, width=15, command=cmd)
                button.grid(row=row_idx, column=col_idx, padx=5, pady=5, ipady=5)
