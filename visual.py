import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3

class StudentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Mahasiswa")
        self.root.geometry("600x400")
        self.root.configure(bg='white')
        
        # Initialize database
        self.init_database()
        
        self.create_widgets()
        self.load_data()
    
    def init_database(self):
        self.db_path = "students.db"
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                nama TEXT NOT NULL,
                nim TEXT NOT NULL
            )
        ''')
        self.conn.commit()
    
    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg='white', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        input_frame = tk.Frame(main_frame, bg='white')
        input_frame.pack(fill='x', pady=(0, 20))
        
        # ID
        tk.Label(input_frame, text="ID :", font=('Arial', 12), bg='white')\
            .grid(row=0, column=0, sticky='e', padx=(0, 10), pady=5)
        self.id_entry = tk.Entry(input_frame, font=('Arial', 12), width=40, relief='solid', bd=2)
        self.id_entry.grid(row=0, column=1, pady=5, sticky='w')

        # Nama
        tk.Label(input_frame, text="NAMA :", font=('Arial', 12), bg='white')\
            .grid(row=1, column=0, sticky='e', padx=(0, 10), pady=5)
        self.name_entry = tk.Entry(input_frame, font=('Arial', 12), width=40, relief='solid', bd=2)
        self.name_entry.grid(row=1, column=1, pady=5, sticky='w')

        # NIM
        tk.Label(input_frame, text="NIM :", font=('Arial', 12), bg='white')\
            .grid(row=2, column=0, sticky='e', padx=(0, 10), pady=5)
        self.nim_entry = tk.Entry(input_frame, font=('Arial', 12), width=40, relief='solid', bd=2)
        self.nim_entry.grid(row=2, column=1, pady=5, sticky='w')

        # Tombol
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill='x', pady=(0, 20))
        
        tk.Button(button_frame, text="Tambah", font=('Arial', 10), relief='solid', bd=2,
                  padx=20, command=self.tambah_data).grid(row=0, column=0, padx=(0, 10))
        tk.Button(button_frame, text="Update", font=('Arial', 10), relief='solid', bd=2,
                  padx=20, command=self.update_data).grid(row=0, column=1, padx=(0, 10))
        tk.Button(button_frame, text="Hapus", font=('Arial', 10), relief='solid', bd=2,
                  padx=20, command=self.hapus_data).grid(row=0, column=2)

        # Area Tabel
        display_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=2)
        display_frame.pack(fill='both', expand=True)

        tk.Label(display_frame, text="TAMPILKAN DATA", font=('Arial', 12, 'bold'),
                 bg='white', pady=10).pack()

        columns = ('ID', 'Nama', 'NIM')
        self.tree = ttk.Treeview(display_frame, columns=columns, show='headings', height=8)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor='center')

        scrollbar = ttk.Scrollbar(display_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
    
    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.cursor.execute("SELECT id, nama, nim FROM students ORDER BY id")
        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', values=row)

    def tambah_data(self):
        id_val = self.id_entry.get().strip()
        name_val = self.name_entry.get().strip()
        nim_val = self.nim_entry.get().strip()

        if not all([id_val, name_val, nim_val]):
            messagebox.showwarning("Peringatan", "Semua field harus diisi!")
            return
        try:
            self.cursor.execute("INSERT INTO students (id, nama, nim) VALUES (?, ?, ?)",
                                (id_val, name_val, nim_val))
            self.conn.commit()
            self.load_data()
            self.clear_entries()
            messagebox.showinfo("Sukses", "Data berhasil ditambahkan!")
        except sqlite3.IntegrityError:
            messagebox.showwarning("Peringatan", "ID sudah ada! Gunakan ID yang berbeda.")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

    def update_data(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih data yang akan diupdate!")
            return
        id_val = self.id_entry.get().strip()
        name_val = self.name_entry.get().strip()
        nim_val = self.nim_entry.get().strip()
        if not all([id_val, name_val, nim_val]):
            messagebox.showwarning("Peringatan", "Semua field harus diisi!")
            return

        old_id = self.tree.item(selected[0], 'values')[0]
        try:
            self.cursor.execute("UPDATE students SET id=?, nama=?, nim=? WHERE id=?",
                                (id_val, name_val, nim_val, old_id))
            self.conn.commit()
            self.load_data()
            self.clear_entries()
            messagebox.showinfo("Sukses", "Data berhasil diupdate!")
        except sqlite3.IntegrityError:
            messagebox.showwarning("Peringatan", "ID sudah ada! Gunakan ID yang berbeda.")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

    def hapus_data(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih data yang akan dihapus!")
            return
        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus data ini?"):
            id_to_delete = self.tree.item(selected[0], 'values')[0]
            try:
                self.cursor.execute("DELETE FROM students WHERE id=?", (id_to_delete,))
                self.conn.commit()
                self.load_data()
                self.clear_entries()
                messagebox.showinfo("Sukses", "Data berhasil dihapus!")
            except Exception as e:
                messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], 'values')
            self.clear_entries()
            self.id_entry.insert(0, values[0])
            self.name_entry.insert(0, values[1])
            self.nim_entry.insert(0, values[2])

    def clear_entries(self):
        self.id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.nim_entry.delete(0, tk.END)

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentApp(root)
    def on_closing():
        app.__del__()  # ensure DB connection closed
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
