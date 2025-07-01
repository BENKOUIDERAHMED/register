from tkinter import ttk, messagebox, filedialog
import tkinter as tk
from HospitalClass1 import Hospital

from tkcalendar import DateEntry
from datetime import datetime
from PIL import Image, ImageTk
import os
import json
class HospitalGUI(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.hospitals = {}
        self.current_hospital = None
        self.create_toolbar(controller)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)
        self.add_database("Default Database")

    def create_toolbar(self , controller):
        toolbar = ttk.Frame(self)
        toolbar.pack(side="top", fill="x")
        ttk.Button(toolbar, text="الرئيسية", command=lambda: controller.show_frame("AppointmentApp")).pack(side="left", padx=5, pady=5)
        ttk.Button(toolbar, text="تحديث", command=self.load_patients).pack(side="left", padx=5, pady=5)
        ttk.Button(toolbar, text="إضافة قاعدة بيانات", command=self.add_database_dialog).pack(side="left", padx=5, pady=5)
        self.search_entry = ttk.Entry(toolbar, width=30)
        self.search_entry.pack(side="left", padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", self.search_patients)
        ttk.Button(toolbar, text="إضافة مريض", command=self.open_add_patient_window).pack(side="left", padx=5, pady=5)
        self.delete_btn = ttk.Button(toolbar, text="حذف", command=self.delete_patient, state="disabled")
        self.delete_btn.pack(side="left", padx=5, pady=5)
        ttk.Button(toolbar, text="استيراد", command=self.import_data).pack(side="left", padx=5, pady=5)
        ttk.Button(toolbar, text="تصدير", command=self.backup_data).pack(side="left", padx=5, pady=5)

    def add_database_dialog(self):
        db_name = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("Database Files", "*.db")])
        if db_name:
            self.add_database(db_name)

    def add_database(self, db_name):
        hospital = Hospital(db_name)
        self.hospitals[db_name] = hospital
        self.current_hospital = hospital
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=db_name.replace("Default Database", "قاعدة البيانات الافتراضية"))
        self.notebook.select(tab_frame)
        self.create_treeview(tab_frame)
        self.add_close_button_to_tab(tab_frame, db_name)
        self.load_patients()

    def create_treeview(self, parent):
        self.tree = ttk.Treeview(parent, columns=(
            "Select", "DisplayID", "InternalID", "FirstName", "LastName", "Age", "Gender", "Condition", "Contact", "AppointmentDate", "DateAdded", "LastModified"
        ), show="headings", style="Treeview")
        self.tree.pack(fill="both", expand=True)
        self.tree.heading("Select", text="اختيار")
        self.tree.column("Select", width=50, anchor="center")
        self.tree.heading("DisplayID", text="رقم العرض")
        self.tree.column("DisplayID", width=50, anchor="center")
        self.tree.heading("InternalID", text="الرقم الداخلي")
        self.tree.column("InternalID", width=0, stretch=tk.NO)
        self.tree.heading("FirstName", text="الاسم الأول")
        self.tree.column("FirstName", width=120, anchor="center")
        self.tree.heading("LastName", text="اسم العائلة")
        self.tree.column("LastName", width=120, anchor="center")
        self.tree.heading("Age", text="العمر")
        self.tree.column("Age", width=50, anchor="center")
        self.tree.heading("Gender", text="الجنس")
        self.tree.column("Gender", width=80, anchor="center")
        self.tree.heading("Condition", text="الحالة")
        self.tree.column("Condition", width=150, anchor="center")
        self.tree.heading("Contact", text="رقم التواصل")
        self.tree.column("Contact", width=100, anchor="center")
        self.tree.heading("AppointmentDate", text="تاريخ الموعد")
        self.tree.column("AppointmentDate", width=100, anchor="center")
        self.tree.heading("DateAdded", text="تاريخ الإضافة")
        self.tree.column("DateAdded", width=120, anchor="center")
        self.tree.heading("LastModified", text="آخر تعديل")
        self.tree.column("LastModified", width=120, anchor="center")
        self.tree.tag_configure('oddrow', background='white')
        self.tree.tag_configure('evenrow', background='#f0f0f0')
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<<TreeviewSelect>>", self.on_patient_select)

    def add_close_button_to_tab(self, tab_frame, db_name):
        tab_index = self.notebook.index(tab_frame)
        tab_text = f"{db_name.replace('Default Database', 'قاعدة البيانات الافتراضية')}  ✖"
        self.notebook.tab(tab_index, text=tab_text)

        def close_tab(event):
            if "✖" in self.notebook.tab(tab_index, "text"):
                if messagebox.askyesno("تأكيد", f"إغلاق {db_name.replace('Default Database', 'قاعدة البيانات الافتراضية')}؟"):
                    self.notebook.forget(tab_frame)
                    del self.hospitals[db_name]
                    if self.hospitals:
                        self.current_hospital = next(iter(self.hospitals.values()))
                    else:
                        self.current_hospital = None
            return "break"

        self.notebook.bind("<Button-1>", lambda e: close_tab(e))

    def load_patients(self):
        if not self.current_hospital:
            messagebox.showerror("خطأ", "لم يتم اختيار قاعدة بيانات")
            return
        try:
            df = self.current_hospital.get_all_patients()
            for item in self.tree.get_children():
                self.tree.delete(item)
            for i, row in df.iterrows():
                display_id = i + 1
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                appointment_date = row.get("AppointmentDate", "")
                self.tree.insert("", "end", values=(
                    "", display_id, row["ID"], row["FirstName"], row["LastName"],
                    row["Age"], row["Gender"], "", row["Contact"],
                    appointment_date, row["DateAdded"], row["LastModified"]
                ), tags=(tag,))
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحميل المرضى: {e}")

    def search_patients(self, event=None):
        if not self.current_hospital:
            messagebox.showerror("خطأ", "لم يتم اختيار قاعدة بيانات")
            return
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.load_patients()
            return
        try:
            df = self.current_hospital.search_patients(search_term)
            for item in self.tree.get_children():
                self.tree.delete(item)
            for i, row in df.iterrows():
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                appointment_date = row.get("AppointmentDate", "")
                self.tree.insert("", "end", values=(
                    "", i + 1, row["ID"], row["FirstName"], row["LastName"],
                    row["Age"], row["Gender"], row["Condition"], row["Contact"],
                    appointment_date, row["DateAdded"], row["LastModified"]
                ), tags=(tag,))
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء البحث: {e}")

    def on_tree_click(self, event):
        item = self.tree.identify_row(event.y)
        current_value = self.tree.item(item, "values")[0]
        new_value = "✔" if current_value != "✔" else "x"
        self.tree.set(item, "Select", new_value)
    
    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.current_edit_id = int(self.tree.item(item, "values")[2])
            self.open_update_patient_window()
    
    def on_patient_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.current_edit_id = int(self.tree.item(selected[0], "values")[2])
            self.delete_btn["state"] = "normal"
        else:
            self.delete_btn["state"] = "disabled"
    
    def open_add_patient_window(self):
        add_window = tk.Toplevel(self.master)
        add_window.title("إضافة مريض")
        add_window.geometry("700x600")
        add_window.transient(self)
        add_window.grab_set()
        
        # Main container with scrollable frame
        main_frame = ttk.Frame(add_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side - form fields
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        fields = {
            "FirstName": {"label": "الاسم الأول:", "type": "entry"},
            "LastName": {"label": "اسم العائلة:", "type": "entry"},
            "Age": {"label": "العمر:", "type": "entry"},
            "Gender": {"label": "الجنس:", "type": "combobox", "values": ["ذكر", "أنثى"]},
            "Condition": {"label": "الحالة:", "type": "entry"},
            "Contact": {"label": "رقم التواصل:", "type": "entry"},
            "AppointmentDate": {"label": "تاريخ الموعد:", "type": "calendar"}
        }
        
        entries = {}
        
        for idx, (field, config) in enumerate(fields.items()):
            lbl = ttk.Label(left_frame, text=config["label"])
            lbl.grid(row=idx, column=0, padx=5, pady=5, sticky="e")
            
            if config["type"] == "entry":
                entry = ttk.Entry(left_frame, width=30)
                entry.grid(row=idx, column=1, padx=5, pady=5, sticky="ew")
                entries[field] = entry
            elif config["type"] == "combobox":
                cb = ttk.Combobox(left_frame, values=config["values"], state="readonly", width=28)
                cb.grid(row=idx, column=1, padx=5, pady=5, sticky="ew")
                entries[field] = cb
            elif config["type"] == "calendar":
                # Create a frame for the calendar and time entry
                calendar_frame = ttk.Frame(left_frame)
                calendar_frame.grid(row=idx, column=1, padx=5, pady=5, sticky="ew")
                
                # Add calendar widget
                cal = DateEntry(calendar_frame, width=12, background='darkblue',
                              foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
                cal.pack(side="left", padx=(0, 5))
                
                # Add time entry
                time_entry = ttk.Entry(calendar_frame, width=8)
                time_entry.insert(0, "HH:MM")
                time_entry.config(foreground='gray')
                
                def on_focus_in(event, e=time_entry):
                    if e.get() == "HH:MM":
                        e.delete(0, tk.END)
                        e.config(foreground='black')
                def on_focus_out(event, e=time_entry):
                    if e.get() == "":
                        e.insert(0, "HH:MM")
                        e.config(foreground='gray')
                
                time_entry.bind("<FocusIn>", on_focus_in)
                time_entry.bind("<FocusOut>", on_focus_out)
                time_entry.pack(side="left")
                
                entries[field] = (cal, time_entry)
        
        # Right side - photos section
        right_frame = ttk.LabelFrame(main_frame, text="صور المريض", padding=10)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Photos list and controls
        photos_frame = ttk.Frame(right_frame)
        photos_frame.pack(fill="both", expand=True)
        
        photos_listbox = tk.Listbox(photos_frame, height=8)
        photos_listbox.pack(fill="both", expand=True, pady=(0, 10))
        
        photos_list = []
        
        def add_photo():
            file_paths = filedialog.askopenfilenames(
                title="اختر الصور",
                filetypes=[("ملفات الصور", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            for file_path in file_paths:
                if file_path not in photos_list:
                    photos_list.append(file_path)
                    photos_listbox.insert(tk.END, os.path.basename(file_path))
        
        def remove_photo():
            selection = photos_listbox.curselection()
            if selection:
                index = selection[0]
                photos_listbox.delete(index)
                photos_list.pop(index)
        
        def view_photo():
            selection = photos_listbox.curselection()
            if selection:
                index = selection[0]
                photo_path = photos_list[index]
                self.show_photo_viewer(photo_path)
        
        # Photo control buttons
        photo_buttons_frame = ttk.Frame(photos_frame)
        photo_buttons_frame.pack(fill="x")
        
        ttk.Button(photo_buttons_frame, text="إضافة صور", command=add_photo).pack(side="left", padx=(0, 5))
        ttk.Button(photo_buttons_frame, text="حذف", command=remove_photo).pack(side="left", padx=(0, 5))
        ttk.Button(photo_buttons_frame, text="عرض", command=view_photo).pack(side="left")
        
        def save_patient():
            data = {}
            for field, entry in entries.items():
                if field == "AppointmentDate":
                    cal, time_entry = entry
                    date_str = cal.get_date().strftime("%Y-%m-%d")
                    time_str = time_entry.get()
                    if time_str == "HH:MM":
                        data[field] = date_str
                    else:
                        data[field] = f"{date_str} {time_str}"
                else:
                    data[field] = entry.get()
            
            data["Photos"] = photos_list
            errors = self.validate_fields(data)
            if errors:
                messagebox.showerror("خطأ", "\n".join(errors))
                return
            new_id = self.current_hospital.add_patient(data)
            if new_id:
                self.load_patients()
                add_window.destroy()
                messagebox.showinfo("نجاح", "تمت إضافة المريض بنجاح")
            else:
                messagebox.showerror("خطأ", "فشل في إضافة المريض")
        
        # Save button at the bottom
        ttk.Button(left_frame, text="حفظ المريض", command=save_patient).grid(row=len(fields), column=0, columnspan=2, pady=20)
    
    def open_update_patient_window(self):
        if not hasattr(self, 'current_edit_id'):
            messagebox.showerror("خطأ", "لم يتم اختيار مريض")
            return
        
        update_window = tk.Toplevel(self)
        update_window.title("تحديث بيانات المريض")
        update_window.geometry("700x600")
        update_window.transient(self)
        update_window.grab_set()
        
        # Main container
        main_frame = ttk.Frame(update_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side - form fields
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        fields = {
            "FirstName": {"label": "الاسم الأول:", "type": "entry"},
            "LastName": {"label": "اسم العائلة:", "type": "entry"},
            "Age": {"label": "العمر:", "type": "entry"},
            "Gender": {"label": "الجنس:", "type": "combobox", "values": ["ذكر", "أنثى"]},
            "Condition": {"label": "الحالة:", "type": "entry"},
            "Contact": {"label": "رقم التواصل:", "type": "entry"},
            "AppointmentDate": {"label": "تاريخ الموعد:", "type": "calendar"}
        }
        
        entries = {}
        df = self.current_hospital.get_all_patients()
        patient = df[df["ID"] == self.current_edit_id].iloc[0]
        
        for idx, (field, config) in enumerate(fields.items()):
            lbl = ttk.Label(left_frame, text=config["label"])
            lbl.grid(row=idx, column=0, padx=5, pady=5, sticky="e")
            
            if config["type"] == "entry":
                entry = ttk.Entry(left_frame, width=30)
                value = str(patient.get(field, ""))
                entry.insert(0, value)
                entry.grid(row=idx, column=1, padx=5, pady=5, sticky="ew")
                entries[field] = entry
            elif config["type"] == "combobox":
                cb = ttk.Combobox(left_frame, values=config["values"], state="readonly", width=28)
                cb.set(str(patient.get(field, "")))
                cb.grid(row=idx, column=1, padx=5, pady=5, sticky="ew")
                entries[field] = cb
            elif config["type"] == "calendar":
                # Create a frame for the calendar and time entry
                calendar_frame = ttk.Frame(left_frame)
                calendar_frame.grid(row=idx, column=1, padx=5, pady=5, sticky="ew")
                
                # Add calendar widget
                cal = DateEntry(calendar_frame, width=12, background='darkblue',
                              foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
                
                # Set the date if it exists
                appointment_date = patient.get("AppointmentDate", "")
                if appointment_date:
                    try:
                        date_obj = datetime.strptime(appointment_date, "%Y-%m-%d %H:%M")
                        cal.set_date(date_obj)
                    except ValueError:
                        pass
                
                cal.pack(side="left", padx=(0, 5))
                
                # Add time entry
                time_entry = ttk.Entry(calendar_frame, width=8)
                if appointment_date:
                    try:
                        date_obj = datetime.strptime(appointment_date, "%Y-%m-%d %H:%M")
                        time_entry.insert(0, date_obj.strftime("%H:%M"))
                    except ValueError:
                        time_entry.insert(0, "HH:MM")
                        time_entry.config(foreground='gray')
                else:
                    time_entry.insert(0, "HH:MM")
                    time_entry.config(foreground='gray')
                
                def on_focus_in(event, e=time_entry):
                    if e.get() == "HH:MM":
                        e.delete(0, tk.END)
                        e.config(foreground='black')
                def on_focus_out(event, e=time_entry):
                    if e.get() == "":
                        e.insert(0, "HH:MM")
                        e.config(foreground='gray')
                
                time_entry.bind("<FocusIn>", on_focus_in)
                time_entry.bind("<FocusOut>", on_focus_out)
                time_entry.pack(side="left")
                
                entries[field] = (cal, time_entry)
        
        # Right side - photos section
        right_frame = ttk.LabelFrame(main_frame, text="صور المريض", padding=10)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Photos list and controls
        photos_frame = ttk.Frame(right_frame)
        photos_frame.pack(fill="both", expand=True)
        
        photos_listbox = tk.Listbox(photos_frame, height=8)
        photos_listbox.pack(fill="both", expand=True, pady=(0, 10))
        
        # Load existing photos
        try:
            existing_photos = json.loads(patient.get("Photos", "[]"))
        except (json.JSONDecodeError, TypeError):
            existing_photos = []
        
        photos_list = existing_photos.copy()
        for photo_path in photos_list:
            photos_listbox.insert(tk.END, os.path.basename(photo_path))
        
        def add_photo():
            file_paths = filedialog.askopenfilenames(
                title="اختر الصور",
                filetypes=[("ملفات الصور", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            for file_path in file_paths:
                if file_path not in photos_list:
                    photos_list.append(file_path)
                    photos_listbox.insert(tk.END, os.path.basename(file_path))
        
        def remove_photo():
            selection = photos_listbox.curselection()
            if selection:
                index = selection[0]
                photos_listbox.delete(index)
                photos_list.pop(index)
        
        def view_photo():
            selection = photos_listbox.curselection()
            if selection:
                index = selection[0]
                photo_path = photos_list[index]
                self.show_photo_viewer(photo_path)
        
        # Photo control buttons
        photo_buttons_frame = ttk.Frame(photos_frame)
        photo_buttons_frame.pack(fill="x")
        
        ttk.Button(photo_buttons_frame, text="إضافة صور", command=add_photo).pack(side="left", padx=(0, 5))
        ttk.Button(photo_buttons_frame, text="حذف", command=remove_photo).pack(side="left", padx=(0, 5))
        ttk.Button(photo_buttons_frame, text="عرض", command=view_photo).pack(side="left")
        
        def save_update():
            data = {}
            for field, entry in entries.items():
                if field == "AppointmentDate":
                    cal, time_entry = entry
                    date_str = cal.get_date().strftime("%Y-%m-%d")
                    time_str = time_entry.get()
                    if time_str == "HH:MM":
                        data[field] = date_str
                    else:
                        data[field] = f"{date_str} {time_str}"
                else:
                    data[field] = entry.get()
            
            data["Photos"] = photos_list
            errors = self.validate_fields(data)
            if errors:
                messagebox.showerror("خطأ", "\n".join(errors))
                return
            if self.current_hospital.update_patient(self.current_edit_id, data):
                self.load_patients()
                update_window.destroy()
                messagebox.showinfo("نجاح", "تم تحديث بيانات المريض")
        
        # Save button at the bottom
        ttk.Button(left_frame, text="تحديث بيانات المريض", command=save_update).grid(row=len(fields), column=0, columnspan=2, pady=20)
    
    def show_photo_viewer(self, photo_path):
        """Display photo in a new window"""
        if not os.path.exists(photo_path):
            messagebox.showerror("خطأ", "ملف الصورة غير موجود")
            return
        
        photo_window = tk.Toplevel(self.root)
        photo_window.title(f"Photo: {os.path.basename(photo_path)}")
        photo_window.geometry("600x600")
        
        try:
            image = Image.open(photo_path)
            # Resize to fit window while maintaining aspect ratio
            image.thumbnail((550, 550), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            label = ttk.Label(photo_window, image=photo)
            label.image = photo  # Keep a reference
            label.pack(expand=True)
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن عرض الصورة: {e}")
            photo_window.destroy()
    
    def validate_fields(self, data):
        errors = []
        if not data["FirstName"].strip():
            errors.append("الاسم الأول مطلوب")
        if not data["LastName"].strip():
            errors.append("اسم العائلة مطلوب")
        if not data["Age"].strip():
            errors.append("العمر مطلوب")
        else:
            try:
                int(data["Age"])
            except ValueError:
                errors.append("العمر يجب أن يكون رقماً")
        if not data["Gender"]:
            errors.append("الجنس مطلوب")
        
        # Validate appointment date format if provided
        if data.get("AppointmentDate"):
            try:
                # Try to parse as date only first
                datetime.strptime(data["AppointmentDate"], "%Y-%m-%d")
            except ValueError:
                try:
                    # If that fails, try with time
                    datetime.strptime(data["AppointmentDate"], "%Y-%m-%d %H:%M")
                except ValueError:
                    errors.append("تاريخ الموعد يجب أن يكون بالتنسيق YYYY-MM-DD أو YYYY-MM-DD HH:MM")
        
        return errors
    
    def delete_patient(self ):
        if  self.current_hospital is None:
            messagebox.showerror("خطأ", "لم يتم اختيار قاعدة بيانات")
            return
        #self.tree.item(selected[0], "values")[2]
        selected_items = [item for item in self.tree.get_children() if self.tree.item(item, "values")[0] == "✔"]
        if len(selected_items) > 0:
            if messagebox.askyesno("تأكيد", f"حذف {len(selected_items)} مريض؟"):
                for item in selected_items:
                    patient_id = int(self.tree.item(item, "values")[2])
                    self.current_hospital.delete_patient(patient_id)
                self.load_patients()
        else:
            messagebox.showinfo("معلومات", "لم يتم اختيار أي مريض للحذف")
    
    def backup_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if file_path:
            self.current_hospital.export_data(file_path)
            messagebox.showinfo("نجاح", "تم إنشاء النسخة الاحتياطية")
    
    def import_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            try:
                if self.current_hospital.import_data(file_path):
                    self.load_patients()
                    messagebox.showinfo("نجاح", "تم استيراد البيانات بنجاح")
                else:
                    messagebox.showerror("خطأ", "فشل في استيراد البيانات. يرجى التحقق من تنسيق الملف.")
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ أثناء الاستيراد: {e}")
