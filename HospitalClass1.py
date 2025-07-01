import pandas as pd
import json
from tkinter import messagebox
from utils import connectToDb


class Hospital:
    def __init__(self, db_file="patients.db"):
        self.db_file = db_file
        self.setup_database()

    def setup_database(self):
        conn, cursor = connectToDb(self.db_file)

        # جدول المرضى
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                FirstName TEXT NOT NULL,
                LastName TEXT NOT NULL,
                Age INTEGER NOT NULL,
                Gender TEXT NOT NULL,
                Contact TEXT,
                Photos TEXT,
                DateAdded TEXT DEFAULT CURRENT_TIMESTAMP,
                LastModified TEXT DEFAULT CURRENT_TIMESTAMP,
                Deleted INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()

    # ------------------ المرضى ------------------

    def get_all_patients(self):
        try:
            conn = connectToDb(self.db_file)[0]
            df = pd.read_sql_query("SELECT * FROM patients WHERE Deleted = 0 ORDER BY ID DESC", conn)
            conn.close()
            return df
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحميل المرضى: {e}")
            return pd.DataFrame()

    def get_total_patients(self):
        conn, cursor = connectToDb(self.db_file)
        cursor.execute("SELECT COUNT(*) FROM patients WHERE Deleted = 0")
        total = cursor.fetchone()[0]
        conn.close()
        return total

    def search_patients(self, search_term, page=1, per_page=50):
        query = "SELECT * FROM patients WHERE Deleted = 0"
        params = []

        if search_term:
            query += " AND (LOWER(FirstName) LIKE ? OR LOWER(LastName) LIKE ? OR LOWER(Contact) LIKE ?)"
            params.extend([f'%{search_term.lower()}%'] * 3)

        query += " ORDER BY ID DESC LIMIT ? OFFSET ?"
        offset = (page - 1) * per_page
        params.extend([per_page, offset])

        try:
            conn = connectToDb(self.db_file)[0]
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            return df
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء البحث: {e}")
            return pd.DataFrame()

    def add_patient(self, data):
        try:
            age = int(data["Age"])
            photos_json = json.dumps(data.get("Photos", []))
            conn, cursor = connectToDb(self.db_file)
            cursor.execute("""
                INSERT INTO patients (FirstName, LastName, Age, Gender, Contact, Photos)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (data["FirstName"], data["LastName"], age, data["Gender"],
                  data.get("Contact", None), photos_json))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return new_id
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في إضافة المريض: {e}")
            return None

    def update_patient(self, patient_id, new_data):
        try:
            age = int(new_data["Age"])
            photos_json = json.dumps(new_data.get("Photos", []))
            conn, cursor = connectToDb(self.db_file)
            cursor.execute("""
                UPDATE patients
                SET FirstName=?, LastName=?, Age=?, Gender=?, Contact=?, Photos=?, LastModified=CURRENT_TIMESTAMP
                WHERE ID=?
            """, (new_data["FirstName"], new_data["LastName"], age, new_data["Gender"],
                  new_data.get("Contact", None), photos_json, patient_id))
            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()
            return rows_affected > 0
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء التحديث: {e}")
            return False

    def delete_patient(self, patient_id):
        try:
            conn, cursor = connectToDb(self.db_file)
            cursor.execute("UPDATE patients SET Deleted = 1 WHERE ID=?", (patient_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحذف: {e}")

    def export_data(self, file_path):
        df = self.get_all_patients()
        df.to_excel(file_path, index=False)

    def import_data(self, file_path):
        try:
            df = pd.read_excel(file_path)
            conn, cursor = connectToDb(self.db_file)
            expected_columns = ["FirstName", "LastName", "Age", "Gender"]

            if not all(col in df.columns for col in expected_columns):
                messagebox.showerror("خطأ", "يجب أن يحتوي ملف الإكسل على الأعمدة المطلوبة")
                return False

            for _, row in df.iterrows():
                try:
                    age = int(row["Age"])
                except (ValueError, TypeError):
                    continue
                cursor.execute("""
                    INSERT INTO patients (FirstName, LastName, Age, Gender, Contact, Photos)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (row["FirstName"], row["LastName"], age, row["Gender"],
                      row.get("Contact", None), json.dumps([])))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الاستيراد: {e}")
            return False

    # ------------------ المواعيد ------------------

    def add_appointment(self, patient_id, data):
        try:
            conn, cursor = connectToDb(self.db_file)
            cursor.execute('''
                INSERT INTO appointments 
                (PatientID, AppointmentDate, Condition, Treatment, Symptoms, Notes, NextAppointment)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                patient_id,
                data.get("AppointmentDate"),
                data.get("Condition"),
                data.get("Treatment"),
                data.get("Symptoms"),
                data.get("Notes"),
                data.get("NextAppointment")
            ))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return new_id
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في إضافة الموعد: {e}")
            return None

    def get_appointments_by_patient(self, patient_id):
        try:
            conn = connectToDb(self.db_file)[0]
            df = pd.read_sql_query(
                "SELECT * FROM appointments WHERE PatientID = ? ORDER BY AppointmentDate DESC",
                conn,
                params=(patient_id,)
            )
            conn.close()
            return df
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في جلب المواعيد: {e}")
            return pd.DataFrame()

    def update_appointment(self, appointment_id, new_data):
        try:
            conn, cursor = connectToDb(self.db_file)
            cursor.execute('''
                UPDATE appointments
                SET AppointmentDate=?, Condition=?, Treatment=?, Symptoms=?, Notes=?, NextAppointment=?, LastModified=CURRENT_TIMESTAMP
                WHERE ID=?
            ''', (
                new_data.get("AppointmentDate"),
                new_data.get("Condition"),
                new_data.get("Treatment"),
                new_data.get("Symptoms"),
                new_data.get("Notes"),
                new_data.get("NextAppointment"),
                appointment_id
            ))
            conn.commit()
            result = cursor.rowcount
            conn.close()
            return result > 0
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في تحديث الموعد: {e}")
            return False

    def delete_appointment(self, appointment_id):
        try:
            conn, cursor = connectToDb(self.db_file)
            cursor.execute("DELETE FROM appointments WHERE ID = ?", (appointment_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء حذف الموعد: {e}")
    
    def find_patient_by_contact_or_lastname(self, contact, last_name):
        try:
            patients = self.get_all_patients()
            filtered = patients[
                (patients['Contact'] == contact) | (patients['LastName'] == last_name)
            ]

            if filtered.empty:
                return pd.DataFrame({})  # لم يتم العثور على مريض

            return filtered.iloc[0]  # إرجاع أول مريض مطابق
        except Exception as e:
            print("Error:", e)
            return pd.DataFrame({})




