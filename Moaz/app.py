import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import mysql.connector
from hashlib import sha256

ctk.set_appearance_mode("white")
ctk.set_default_color_theme("dark-blue")

# ============================================
# DATABASE
# ============================================

class DatabaseMySQL:
    def __init__(self, host="localhost", user="root", password="Mysql@123", database="CarRental"):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.create_tables()
        self.seed()

    def cur(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    # ================= TABLES =================

    def create_tables(self):
        c = self.cur()

        c.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            User_ID INT AUTO_INCREMENT PRIMARY KEY,
            Email VARCHAR(100),
            Password_Hash VARCHAR(64),
            First_Name VARCHAR(50),
            Role VARCHAR(20)
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS Cars (
            Plate VARCHAR(20) PRIMARY KEY,
            Brand VARCHAR(50),
            Model VARCHAR(50),
            Price FLOAT,
            Status VARCHAR(20)
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS Reservations (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            User_ID INT,
            Plate VARCHAR(20),
            Start_Date DATE,
            End_Date DATE,
            Days INT,
            Total FLOAT,
            Date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS Invoices (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            Res_ID INT,
            Amount FLOAT,
            Created DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.commit()

    # ================= SEED =================

    def seed(self):
        c = self.cur()
        c.execute("SELECT COUNT(*) FROM Users")
        if c.fetchone()[0] == 0:
            admin = sha256("admin123".encode()).hexdigest()
            user = sha256("123".encode()).hexdigest()

            c.execute("INSERT INTO Users VALUES (NULL,%s,%s,'Admin','admin')",
                      ("admin@car.com", admin))

            c.execute("INSERT INTO Users VALUES (NULL,%s,%s,'User','customer')",
                      ("user@car.com", user))

            c.execute("INSERT INTO Cars VALUES ('AAA','Toyota','Corolla',500,'available')")
            c.execute("INSERT INTO Cars VALUES ('BBB','BMW','X5',1200,'available')")

            self.commit()

    # ================= AUTH =================

    def login(self, email, password):
        h = sha256(password.encode()).hexdigest()
        c = self.cur()
        c.execute("SELECT * FROM Users WHERE Email=%s AND Password_Hash=%s", (email, h))
        return c.fetchone()

    def cars(self):
        c = self.cur()
        c.execute("SELECT * FROM Cars")
        return c.fetchall()

    def reserve(self, uid, plate, start, end, price):
        days = (end - start).days
        total = days * price

        c = self.cur()
        c.execute("""
            INSERT INTO Reservations (User_ID, Plate, Start_Date, End_Date, Days, Total)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (uid, plate, start, end, days, total))

        self.commit()
        return total

# ============================================
# APP
# ============================================

db = DatabaseMySQL()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1100x650")
        self.title("Car Rental PRO MAX")
        self.show_login()

    def clear(self):
        for w in self.winfo_children(): w.destroy()

    def show_login(self):
        self.clear()
        Login(self).pack(fill="both", expand=True)

    def open_dashboard(self, user):
        self.clear()
        Dashboard(self, user, self.show_login).pack(fill="both", expand=True)

# ============================================
# LOGIN
# ============================================

class Login(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)

        ctk.CTkLabel(self, text="CAR RENTAL PRO", font=("Arial", 32)).pack(pady=30)

        self.email = ctk.CTkEntry(self, placeholder_text="Email")
        self.email.pack(pady=10)

        self.passw = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.passw.pack(pady=10)

        ctk.CTkButton(self, text="LOGIN", command=self.login).pack(pady=20)

    def login(self):
        user = db.login(self.email.get(), self.passw.get())
        if user:
            self.master.open_dashboard(user)
        else:
            messagebox.showerror("Error", "Invalid login")

# ============================================
# DASHBOARD
# ============================================

class Dashboard(ctk.CTkFrame):
    def __init__(self, root, user, logout):
        super().__init__(root)
        self.user = user

        self.left = ctk.CTkFrame(self, width=250)
        self.left.pack(side="left", fill="y")

        self.main = ctk.CTkFrame(self)
        self.main.pack(side="right", fill="both", expand=True)

        role = "ADMIN" if user[4] == "admin" else "CUSTOMER"

        ctk.CTkLabel(self.left, text=role, font=("Arial", 20)).pack(pady=20)
        ctk.CTkButton(self.left, text="Cars", command=self.show_cars).pack(pady=10)
        ctk.CTkButton(self.left, text="Book", command=self.book).pack(pady=10)
        ctk.CTkButton(self.left, text="Logout", command=logout).pack(pady=30)

        self.show_cars()

    def clear(self):
        for w in self.main.winfo_children(): w.destroy()

    def show_cars(self):
        self.clear()
        ctk.CTkLabel(self.main, text="CARS", font=("Arial", 26)).pack(pady=10)

        for c in db.cars():
            ctk.CTkLabel(self.main, text=f"{c[0]} | {c[1]} {c[2]} | {c[3]} EGP/day").pack()

    # ================= BOOK (UPDATED) =================

    def book(self):
        self.clear()

        ctk.CTkLabel(self.main, text="BOOK CAR", font=("Arial", 26)).pack(pady=10)

        plate = ctk.CTkEntry(self.main, placeholder_text="Plate")
        plate.pack(pady=5)

        start = ctk.CTkEntry(self.main, placeholder_text="Start Date YYYY-MM-DD")
        start.pack(pady=5)

        end = ctk.CTkEntry(self.main, placeholder_text="End Date YYYY-MM-DD")
        end.pack(pady=5)

        def reserve():
            try:
                s = datetime.strptime(start.get(), "%Y-%m-%d")
                e = datetime.strptime(end.get(), "%Y-%m-%d")

                for c in db.cars():
                    if c[0] == plate.get():
                        total = db.reserve(self.user[0], c[0], s, e, c[3])
                        messagebox.showinfo("Success", f"Total = {total} EGP")
                        return

                messagebox.showerror("Error", "Car not found")

            except:
                messagebox.showerror("Error", "Invalid dates")

        ctk.CTkButton(self.main, text="CONFIRM BOOKING", command=reserve).pack(pady=10)

# ============================================
# RUN
# ============================================

if __name__ == "__main__":
    App().mainloop()