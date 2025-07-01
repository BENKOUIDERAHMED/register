import sqlite3
import pandas as pd
import json
from tkinter import ttk, messagebox, filedialog
def connectToDb(fileName):
    conn = sqlite3.connect(fileName)
    return conn ,conn.cursor()
    
# Database class for managing patients
class Hospital:
    def __init__(self, db_file="patients.db"):
        self.db_file = db_file
        self.setup_database()
        
    def setup_database(self):
        conn , cursor = connectToDb(self.db_file)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                FirstName TEXT NOT NULL,
                LastName TEXT NOT NULL,
                Age INTEGER NOT NULL,
                Gender TEXT NOT NULL,   
                Condition TEXT,
                Contact TEXT,
                Photos TEXT,
                AppointmentDate TEXT,
                DateAdded TEXT DEFAULT CURRENT_TIMESTAMP,
                LastModified TEXT DEFAULT CURRENT_TIMESTAMP,
                Deleted INTEGER DEFAULT 0
            )
        ''')
        # Check if Photos and AppointmentDate columns exist, if not add them
        cursor.execute("PRAGMA table_info(patients)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'Photos' not in columns:
            cursor.execute("ALTER TABLE patients ADD COLUMN Photos TEXT")
        if 'AppointmentDate' not in columns:
            cursor.execute("ALTER TABLE patients ADD COLUMN AppointmentDate TEXT")
        
        conn.commit()
        conn.close()
    
    def get_all_patients(self):
        try:
            conn= connectToDb(self.db_file)[0]
            # Order by ID DESC to show newest first
            df = pd.read_sql_query("SELECT * FROM patients WHERE Deleted = 0 ORDER BY ID DESC LIMIT 3000", conn)
            conn.close()
            return df
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحميل المرضى: {e}")
            return pd.DataFrame()
    
    def get_total_patients(self):
        conn , cursor = connectToDb(self.db_file)
        cursor.execute("SELECT COUNT(*) FROM patients WHERE Deleted = 0")
        total = cursor.fetchone()[0]
        conn.close()
        return total
    
    def search_patients(self, search_term, page=1, per_page=50):
        query = "SELECT * FROM patients WHERE Deleted = 0"
        params = []
        
        if search_term:
            query += " AND (LOWER(FirstName) LIKE ? OR LOWER(LastName) LIKE ? OR LOWER(Condition) LIKE ? OR LOWER(Contact) LIKE ?)"
            params.extend([f'%{search_term.lower()}%'] * 4)
        
        # Order by ID DESC to show newest first
        query += " ORDER BY ID DESC LIMIT ? OFFSET ?"
        offset = (page - 1) * per_page
        params.extend([per_page, offset])
        
        try:
            conn  = connectToDb(self.db_file)[0]
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            return df
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء البحث: {e}")
            return pd.DataFrame()
    
    def add_patient(self, data):
        try:
            # Convert Age to integer
            try:
                age = int(data["Age"])
            except ValueError:
                messagebox.showerror("خطأ", "العمر يجب أن يكون رقماً صحيحاً")
                return None

            # Convert photos list to JSON string
            photos_json = json.dumps(data.get("Photos", []))
            conn , cursor = connectToDb(self.db_file)
            cursor.execute("""
                INSERT INTO patients (FirstName, LastName, Age, Gender, Condition, Contact, Photos, AppointmentDate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (data["FirstName"], data["LastName"], age, data["Gender"], 
                  data.get("Condition", None), data.get("Contact", None), 
                  photos_json, data.get("AppointmentDate", None)))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return new_id
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في إضافة المريض: {e}")
            return None
    
    def update_patient(self, patient_id, new_data):
        try:
            # Convert Age to integer
            try:
                age = int(new_data["Age"])
            except ValueError:
                messagebox.showerror("خطأ", "العمر يجب أن يكون رقماً صحيحاً")
                return False

            # Convert photos list to JSON string
            photos_json = json.dumps(new_data.get("Photos", []))
            conn , cursor = connectToDb(self.db_file)
            cursor.execute("""
                UPDATE patients 
                SET FirstName=?, LastName=?, Age=?, Gender=?, Condition=?, Contact=?, Photos=?, AppointmentDate=?, LastModified=CURRENT_TIMESTAMP
                WHERE ID=?
            """, (new_data["FirstName"], new_data["LastName"], age, new_data["Gender"], 
                  new_data.get("Condition", None), new_data.get("Contact", None), 
                  photos_json, new_data.get("AppointmentDate", None), patient_id))
            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()
            return rows_affected > 0
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء التحديث: {e}")
            return False
    
    def delete_patient(self, patient_id):
        try:
            conn , cursor = connectToDb(self.db_file)
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
            conn , cursor = connectToDb(self.db_file)
            expected_columns = ["FirstName", "LastName", "Age", "Gender", "Condition", "Contact"]
            if not all(col in df.columns for col in expected_columns[:4]):
                messagebox.showerror("خطأ", "يجب أن يحتوي ملف الإكسل على الأعمدة: الاسم الأول، اسم العائلة، العمر، الجنس")
                return False
            
            for _, row in df.iterrows():
                # Ensure Age is an integer
                try:
                    age = int(row["Age"])
                except (ValueError, TypeError):
                    continue  # Skip invalid rows
                cursor.execute("""
                    INSERT INTO patients (FirstName, LastName, Age, Gender, Condition, Contact, Photos, AppointmentDate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (row["FirstName"], row["LastName"], age, row["Gender"], 
                      row.get("Condition", None), row.get("Contact", None), 
                      json.dumps([]), row.get("AppointmentDate", None)))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الاستيراد: {e}")
            return False