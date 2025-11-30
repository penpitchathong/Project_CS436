import sqlite3

import tkinter as tk

from tkinter import messagebox

from datetime import datetime


# ---  Database Management (Data Storage & Retrieval) ---

DB_NAME = 'bmi_records.db'

def create_table():

    """... (คำอธิบายเหมือนเดิม) ..."""

    # เปลี่ยนจากการเปิด/ปิดแบบเดิม มาใช้ 'with'

    with sqlite3.connect(DB_NAME) as conn:

        cursor = conn.cursor()

        # 1. สร้างตาราง records หากยังไม่มี

        cursor.execute("""

            CREATE TABLE IF NOT EXISTS records (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                timestamp TEXT NOT NULL,

                name TEXT NOT NULL,

                weight REAL NOT NULL,

                height REAL NOT NULL,

                bmi REAL NOT NULL,

                category TEXT NOT NULL

            )

        """)

        #  ตรวจสอบและเพิ่มคอลัมน์ 'name' ถ้ายังไม่มี (Schema Migration)

        try:

            # ใช้ PRAGMA table_info

            cursor.execute("PRAGMA table_info(records)")

            columns = [col[1] for col in cursor.fetchall()]

           

            if 'name' not in columns:

                print("Adding 'name' column to existing records table (Migration)...")

                cursor.execute("ALTER TABLE records ADD COLUMN name TEXT NOT NULL DEFAULT 'ไม่ระบุชื่อ'")

        except sqlite3.Error as e:

            print(f"Error during schema migration: {e}")

def save_record(name, weight, height, bmi, category):

    """บันทึกข้อมูลการวัด BMI ลงในฐานข้อมูล"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(DB_NAME) as conn:

        cursor = conn.cursor()

        cursor.execute("INSERT INTO records (timestamp, name, weight, height, bmi, category) VALUES (?, ?, ?, ?, ?, ?)",

                       (timestamp, name, weight, height, bmi, category))

def get_all_records():

    """ดึงข้อมูลประวัติการวัดทั้งหมดจากฐานข้อมูล พร้อม ID สำหรับการลบ"""

    with sqlite3.connect(DB_NAME) as conn:

        cursor = conn.cursor()

        cursor.execute("SELECT id, timestamp, name, weight, height, bmi, category FROM records ORDER BY timestamp DESC")

        records = cursor.fetchall()

        return records # คืนค่าก่อน conn.close()

def delete_record(record_id):

    """ลบข้อมูลการวัด BMI ตาม ID ที่ระบุ"""

    with sqlite3.connect(DB_NAME) as conn:

        cursor = conn.cursor()

        cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))

        # *** แก้ไข: ต้องเรียก .rowcount จาก cursor ไม่ใช่ conn ***

        deleted_count = cursor.rowcount  # <--- แก้ไขตรงนี้

        # conn.commit() ถูกจัดการโดย 'with' แล้ว

        return deleted_count

# ---  Simple Business Logic & Reporting (เหมือนเดิม) ---

def calculate_bmi(weight_kg, height_cm):

    """คำนวณ BMI"""

    height_m = height_cm / 100

    if height_m <= 0: return 0

    bmi = weight_kg / (height_m ** 2)

    return round(bmi, 2)


def get_bmi_category(bmi):
    """แปลผลค่า BMI เป็นหมวดหมู่ (ตามเกณฑ์ขององค์การอนามัยโลกสำหรับชาวเอเชีย และเพิ่ม Obese III)"""
    # Morbidly Obese / Obese Class III (ค่า BMI ที่ถือเป็นโรคอ้วนรุนแรง)
    if bmi >= 40.0:
        return "Obese III (โรคอ้วนระดับ 3/รุนแรง)"
    # Obese Class II (อ้วนระดับ 2)
    elif 30.0 <= bmi < 40.0:
        return "Obese II (อ้วนระดับ 2)"
    # Obese Class I (อ้วนระดับ 1)
    elif 25.0 <= bmi < 30.0:
        return "Obese I (อ้วนระดับ 1)"
    # Overweight (น้ำหนักเกิน) - เกณฑ์เอเชีย
    elif 23.0 <= bmi < 25.0:
        return "Overweight (น้ำหนักเกิน)"
    # Normal weight (ปกติ) - เกณฑ์เอเชีย
    elif 18.5 <= bmi < 23.0:
        return "Normal weight (ปกติ)"
    # Underweight (ผอม)
    else: # bmi < 18.5
        return "Underweight (ผอม)"
# ---  Input Validation and GUI (Tkinter) ---

class BMICalculatorApp:

    def __init__(self, master):

        self.master = master

        master.title("BMI Tracker & Calculator")

        master.geometry("650x550") # ขยายขนาดหน้าต่างรองรับส่วนลบข้อมูล

        self.name_var = tk.StringVar(value="ผู้ใช้ 1") # New: สำหรับชื่อผู้บันทึก

        self.weight_var = tk.DoubleVar()

        self.height_var = tk.DoubleVar()

        self.delete_id_var = tk.IntVar() # New: สำหรับ ID ที่จะลบ

        create_table() # ตรวจสอบและสร้างตารางฐานข้อมูลเมื่อเริ่มแอป

        # สร้าง UI

        self.create_widgets()

        self.update_history_display()

    def create_widgets(self):

        # Frame หลักสำหรับ Input และ Delete

        top_frame = tk.Frame(self.master)

        top_frame.pack(pady=10)

        # ----------------------------------------------------

        # Input & Calculate Frame

        # ----------------------------------------------------

        input_frame = tk.LabelFrame(top_frame, text="บันทึกข้อมูลใหม่", padx=10, pady=10)

        input_frame.grid(row=0, column=0, padx=10, sticky='n')

        # Input - ชื่อผู้บันทึก (New)

        tk.Label(input_frame, text="Name (ชื่อ):").grid(row=0, column=0, padx=5, pady=5, sticky='w')

        self.name_entry = tk.Entry(input_frame, textvariable=self.name_var)

        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Input - น้ำหนัก

        tk.Label(input_frame, text="Weight (kg):").grid(row=1, column=0, padx=5, pady=5, sticky='w')

        self.weight_entry = tk.Entry(input_frame, textvariable=self.weight_var)

        self.weight_entry.grid(row=1, column=1, padx=5, pady=5)

        # Input - ส่วนสูง

        tk.Label(input_frame, text="Height (cm):").grid(row=2, column=0, padx=5, pady=5, sticky='w')

        self.height_entry = tk.Entry(input_frame, textvariable=self.height_var)

        self.height_entry.grid(row=2, column=1, padx=5, pady=5)

        # ปุ่มคำนวณและบันทึก

        self.calculate_button = tk.Button(input_frame, text="Calculate & Save BMI", command=self.process_bmi, bg='lightblue')

        self.calculate_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Label แสดงผลลัพธ์

        self.result_label = tk.Label(input_frame, text="BMI Result: -", font=('Arial', 12, 'bold'))

        self.result_label.grid(row=4, column=0, columnspan=2, pady=5)

        self.category_label = tk.Label(input_frame, text="Category: -", font=('Arial', 10))

        self.category_label.grid(row=5, column=0, columnspan=2, pady=2)      

        # ----------------------------------------------------

        #  Delete Frame (New)

        # ----------------------------------------------------

        delete_frame = tk.LabelFrame(top_frame, text="ลบข้อมูลประวัติ", padx=10, pady=10)

        delete_frame.grid(row=0, column=1, padx=10, sticky='n')      

        tk.Label(delete_frame, text="Record ID ที่ต้องการลบ:").grid(row=0, column=0, padx=5, pady=5, sticky='w')

        self.delete_entry = tk.Entry(delete_frame, textvariable=self.delete_id_var)

        self.delete_entry.grid(row=0, column=1, padx=5, pady=5)

        self.delete_button = tk.Button(delete_frame, text="Delete Record", command=self.delete_record_ui, bg='salmon', fg='white')

        self.delete_button.grid(row=1, column=0, columnspan=2, pady=10)      

        tk.Label(delete_frame, text="**ดู ID จากตารางประวัติ**", font=('Arial', 8, 'italic')).grid(row=2, column=0, columnspan=2)

        # ----------------------------------------------------

        #  History Display Frame

        # ----------------------------------------------------

        tk.Label(self.master, text="--- ประวัติการบันทึก (Latest 10 Records) ---", font=('Arial', 10, 'underline')).pack(pady=5)

        self.history_text = tk.Text(self.master, height=12, width=80, state=tk.DISABLED, wrap=tk.NONE)

        self.history_text.pack(padx=10)

        # เพิ่ม Scrollbar แนวนอน

        h_scroll = tk.Scrollbar(self.master, orient=tk.HORIZONTAL, command=self.history_text.xview)

        h_scroll.pack(fill=tk.X, padx=10)

        self.history_text.config(xscrollcommand=h_scroll.set)



    def process_bmi(self):

        """ดำเนินการคำนวณ ตรวจสอบความถูกต้อง และบันทึกข้อมูล"""

        try:

            # 1. Input Validation

            name = self.name_var.get().strip()

            weight = self.weight_var.get()

            height = self.height_var.get()

            if not name:

                name = "ไม่ระบุชื่อ"

            if not (isinstance(weight, (int, float)) and isinstance(height, (int, float))):

                 raise ValueError("Weight/Height must be numerical.")

            if weight <= 0 or height <= 0:

                raise ValueError("Weight and Height must be positive numbers (> 0).")          

            if height < 50 or height > 300:

                raise ValueError("Height seems unrealistic (50-300 cm).")

        except ValueError as e:

            messagebox.showerror("Invalid Input", str(e))

            self.update_result_labels(0, "Error")

            return

        # 2. Simple Business Logic

        bmi = calculate_bmi(weight, height)

        category = get_bmi_category(bmi)

        # 3. Save and Update UI

        save_record(name, weight, height, bmi, category) # ส่งชื่อเข้าไปด้วย

        self.update_result_labels(bmi, category)

        self.update_history_display()

        messagebox.showinfo("Success", f"BMI Calculated ({bmi}) and record saved successfully!")

   

    def delete_record_ui(self):

        """ดำเนินการลบข้อมูลตาม ID ที่ผู้ใช้ป้อน"""

        try:

            record_id = self.delete_id_var.get()

           

            if record_id <= 0:

                raise ValueError("กรุณาใส่ ID ที่ถูกต้อง (> 0)")

            # ยืนยันการลบ

            confirm = messagebox.askyesno("ยืนยันการลบ", f"คุณต้องการลบ Record ID {record_id} ใช่หรือไม่?")

            if not confirm:

                return

            deleted_count = delete_record(record_id)

        
            if deleted_count > 0:

                messagebox.showinfo("ลบสำเร็จ", f"ลบ Record ID {record_id} เรียบร้อยแล้ว")

                self.update_history_display()

            else:

                messagebox.showwarning("ลบไม่สำเร็จ", f"ไม่พบ Record ID {record_id} ในฐานข้อมูล")

            self.delete_id_var.set(0) # เคลียร์ input field



        except tk.TclError:

            messagebox.showerror("Input Error", "กรุณาใส่ ID เป็นตัวเลข")

        except ValueError as e:

            messagebox.showerror("Input Error", str(e))

        except Exception as e:

            messagebox.showerror("Database Error", f"เกิดข้อผิดพลาดในการลบ: {e}")



 #"""อัปเดต Label แสดงผล BMI ล่าสุด"""

    def update_result_labels(self, bmi, category):

        self.result_label.config(text=f"BMI Result: {bmi}")

        self.category_label.config(text=f"Category: {category}")

        # เปลี่ยนสีตาม Category

        if "Normal" in category:

            self.result_label.config(fg='green')

        elif "Underweight" in category or "Overweight" in category:

            self.result_label.config(fg='orange')

        else:

            self.result_label.config(fg='red')



    def update_history_display(self):

        records = get_all_records()

        self.history_text.config(state=tk.NORMAL)

        self.history_text.delete('1.0', tk.END) # เคลียร์ข้อมูลเก่า

        # ปรับ Header ให้รวม ID และ Name

        header = f"{'ID':<4} {'Date/Time':<18} {'Name':<15} {'Weight (kg)':<12} {'Height (cm)':<15} {'BMI':<6} {'Category':<20}\n"

        self.history_text.insert(tk.END, header)
        
        self.history_text.insert(tk.END, "-" * 95 + "\n")



        for i, record in enumerate(records[:10]): # แสดง 10 รายการล่าสุด

            record_id, timestamp, name, weight, height, bmi, category = record
           
            # จัดรูปแบบ Name, Weight, Height, BMI และ Category

            line = f"{record_id:<4} {timestamp[:16]:<18} {name[:18]:<20} {weight:<12.2f} {height:<12.2f} {bmi:<6.2f} {category:<20}\n"

            self.history_text.insert(tk.END, line)

        self.history_text.config(state=tk.DISABLED)


# --- Main Execution ---

if __name__ == "__main__":
    root = tk.Tk()
    app = BMICalculatorApp(root)   
    root.mainloop()