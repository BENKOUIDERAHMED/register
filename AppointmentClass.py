from tkinter import messagebox
import pandas as pd
from datetime import datetime
from utils import connectToDb

class Appointment:
    def __init__(self, db_file="patients.db"):
        self.db_file = db_file
        self.setup_database()

    def setup_database(self):
        conn, cursor = connectToDb(self.db_file)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                PatientID INTEGER NOT NULL,
                AppointmentDate TEXT NOT NULL,
                Condition TEXT,
                Treatment TEXT,
                Symptoms TEXT,
                Notes TEXT,
                NextAppointment TEXT,
                DateAdded TEXT DEFAULT CURRENT_TIMESTAMP,
                LastModified TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (PatientID) REFERENCES patients(ID) ON DELETE CASCADE
            )
        ''')
        conn.commit()
        conn.close()

    def add_appointment(self, patient_id, data):
        try:
            conn, cursor = connectToDb(self.db_file)
            cursor.execute("""
                INSERT INTO appointments (
                    PatientID, AppointmentDate, Condition, Treatment, Symptoms, Notes, NextAppointment
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                patient_id,
                data.get("AppointmentDate", datetime.now().strftime("%Y-%m-%d")),
                data.get("Condition", ""),
                data.get("Treatment", ""),
                data.get("Symptoms", ""),
                data.get("Notes", ""),
                data.get("NextAppointment", "")
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
            conn, _ = connectToDb(self.db_file)
            df = pd.read_sql_query(
                "SELECT * FROM appointments WHERE PatientID = ? ORDER BY AppointmentDate DESC",
                conn, params=(patient_id,)
            )
            conn.close()
            return df
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء جلب المواعيد: {e}")
            return pd.DataFrame()

    def update_appointment(self, appointment_id, new_data):
        try:
            conn, cursor = connectToDb(self.db_file)
            cursor.execute("""
                UPDATE appointments
                SET AppointmentDate=?, Condition=?, Treatment=?, Symptoms=?, Notes=?, NextAppointment=?, LastModified=CURRENT_TIMESTAMP
                WHERE ID=?
            """, (
                new_data.get("AppointmentDate", ""),
                new_data.get("Condition", ""),
                new_data.get("Treatment", ""),
                new_data.get("Symptoms", ""),
                new_data.get("Notes", ""),
                new_data.get("NextAppointment", ""),
                appointment_id
            ))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في تحديث الموعد: {e}")
            return False

    def delete_appointment(self, appointment_id):
        try:
            conn, cursor = connectToDb(self.db_file)
            cursor.execute("DELETE FROM appointments WHERE ID=?", (appointment_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في حذف الموعد: {e}")

    def get_all_appointments(self, limit=100):
        try:
            conn, _ = connectToDb(self.db_file)
            df = pd.read_sql_query(
                "SELECT * FROM appointments ORDER BY AppointmentDate DESC LIMIT ?",
                conn, params=(limit,)
            )
            conn.close()
            return df
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في تحميل المواعيد: {e}")
            return pd.DataFrame()
    def count(self):
        try:
            conn, cursor = connectToDb(self.db_file)
            cursor.execute("SELECT COUNT(*) FROM appointments WHERE Deleted = 0")
            total = cursor.fetchone()[0]
            conn.close()
            return total
        except:
            return 0
