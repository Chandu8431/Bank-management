import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    mysql = None
    Error = Exception


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",       # WAMP default is often blank
    "database": "bank_mng",
    "port": 3306
}

TABLES = {
    "Account Details": {
        "table": "account",
        "columns": ["Account_No", "Customer_ID", "Account_Type", "Balance", "Opening_Date"],
        "primary": "Account_No"
    },
    "Customer Details": {
        "table": "customer",
        "columns": ["Customer_ID", "Name", "Address", "Phone", "Email", "Date_of_Birth"],
        "primary": "Customer_ID"
    },
    "Employees Details": {
        "table": "employee",
        "columns": ["Employee_ID", "Name", "Position", "Phone", "Salary"],
        "primary": "Employee_ID"
    },
    "Loan Details": {
        "table": "loan",
        "columns": ["Loan_ID", "Loan_Type", "Loan_Amount", "Interest_Rate", "Loan_Date"],
        "primary": "loan_ID"
    },
    "Transaction Details":{
        "table": "transactions",
        "columns": ["Transaction_ID", "Account_No", "Transaction_Type", "Amount", "Transaction_Date"],
        "primary": "Transaction_ID"
    },
 }
    


class BankDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Bank Management System | Dashboard")
        self.root.geometry("1180x720")
        self.root.minsize(950, 600)
        self.root.configure(bg="#f3f6fb")

        self.connection = None
        self.current_section = "Dashboard"
        self.search_var = tk.StringVar()

        self.setup_style()
        self.build_layout()
        self.connect_database()
        self.show_dashboard()

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=29, font=("Segoe UI", 10),
                        background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=7)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=(14, 8))

    def build_layout(self):
        header = tk.Frame(self.root, bg="#142d4e", height=72)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="🏦  BANK MANAGEMENT SYSTEM", bg="#142d4e",
                 fg="yellow", font=("Segoe UI", 19, "bold")).pack(side="left", padx=24)
        self.status_label = tk.Label(header, text="Connecting to database...",
                                     bg="#142d4e", fg="#d8e6f7",
                                     font=("Segoe UI", 10))
        self.status_label.pack(side="right", padx=22)

        body = tk.Frame(self.root, bg="#f3f6fb")
        body.pack(fill="both", expand=True)

        sidebar = tk.Frame(body, bg="#1d3b61", width=205)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="MAIN MENU", bg="#1d3b61", fg="#9db6d2",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=20, pady=(24, 12))

        menu_items = [
            ("▦   Dashboard", self.show_dashboard),
            ("👥   Account Details", lambda: self.show_table("Account Details")),
            ("💳   Customer Details", lambda: self.show_table("Customer Details")),
            ("🧑   Employees Details", lambda: self.show_table("Employees Details")),
            ("$    Loan Details", lambda: self.show_table("Loan Details")),
            ("📄   Transaction Details", lambda: self.show_table("Transaction Details")),
        ]
        for label, command in menu_items:
            btn = tk.Button(sidebar, text=label, command=command, anchor="w",
                            bg="#1d3b61", fg="white", activebackground="#2c5685",
                            activeforeground="white", relief="flat", bd=0,
                            font=("Segoe UI", 11), padx=20, pady=13, cursor="hand2")
            btn.pack(fill="x")

        tk.Label(sidebar, text="Database: bank_mng", bg="#1d3b61", fg="#b8cbe0",
                 font=("Segoe UI", 9)).pack(side="bottom", pady=18)

        self.content = tk.Frame(body, bg="#f3f6fb")
        self.content.pack(side="left", fill="both", expand=True, padx=24, pady=22)

    def connect_database(self):
        if mysql is None:
            self.status_label.config(text="Missing mysql-connector-python")
            messagebox.showerror(
                "Missing package",
                "Install the MySQL connector first:\n\npy -m pip install mysql-connector-python"
            )
            return
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            self.status_label.config(text="● Connected to bank_mng")
        except Error as exc:
            self.connection = None
            self.status_label.config(text="● Database connection failed")
            messagebox.showerror(
                "MySQL connection error",
                "Could not connect to MySQL.\n\n"
                f"{exc}\n\n"
                "Check that WAMP/MySQL is running and DB_CONFIG has the correct "
                "username, password, port and database name."
            )

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def query(self, sql, params=None):
        if self.connection is None or not self.connection.is_connected():
            self.connect_database()
        if self.connection is None:
            return []
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(sql, params or ())
            if cursor.with_rows:
                return cursor.fetchall()
            self.connection.commit()
            return []
        finally:
            cursor.close()

    def scalar(self, sql):
        rows = self.query(sql)
        if rows:
            return next(iter(rows[0].values()))
        return 0

    def show_dashboard(self):
        self.current_section = "Dashboard"
        self.clear_content()

        tk.Label(self.content, text="Dashboard", bg="#f3f6fb", fg="#142d4e",
                 font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(self.content, text="Overview of your bank database",
                 bg="#f3f6fb", fg="#6b7c93", font=("Segoe UI", 11)).pack(anchor="w", pady=(3, 20))

        cards_frame = tk.Frame(self.content, bg="#f3f6fb")
        cards_frame.pack(fill="x")

        cards = [
            ("Total Accounts", "SELECT COUNT(*) AS total FROM account", "#2878b5"),
            ("Total Customers", "SELECT COUNT(*) AS total FROM customer", "#218c74"),
            ("Total Employees", "SELECT COUNT(*) AS total FROM employee", "#2878b5"),
            ("Total Loans Issued", "SELECT COUNT(*) AS total FROM loan ", "#8064a2"),
            ("Total Salary", "SELECT COALESCE(SUM(Salary),0) AS total FROM employee", "#397a9e"),
        ]

        for index, (title, sql, color) in enumerate(cards):
            try:
                value = self.scalar(sql)
                if title == "Total Salary":
                    value_text = f"₹ {float(value):,.2f}"
                else:
                    value_text = str(value)
            except Exception:
                value_text = "—"

            card = tk.Frame(cards_frame, bg="white", highlightbackground="#e1e8f0",
                            highlightthickness=1, padx=18, pady=16)
            card.grid(row=index // 3, column=index % 3, sticky="nsew",
                      padx=7, pady=7)
            tk.Frame(card, bg=color, height=4).pack(fill="x", pady=(0, 13))
            tk.Label(card, text=title, bg="white", fg="#68788d",
                     font=("Segoe UI", 10, "bold")).pack(anchor="w")
            tk.Label(card, text=value_text, bg="white", fg="#142d4e",
                     font=("Segoe UI", 21, "bold")).pack(anchor="w", pady=(8, 2))

        for col in range(3):
            cards_frame.grid_columnconfigure(col, weight=1)

        quick = tk.Frame(self.content, bg="white", padx=20, pady=18,
                         highlightbackground="#e1e8f0", highlightthickness=1)
        quick.pack(fill="both", expand=True, padx=7, pady=(18, 5))
        tk.Label(quick, text="Quick Access", bg="white", fg="#142d4e",
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 12))
        row = tk.Frame(quick, bg="white")
        row.pack(anchor="w")
        for name in TABLES:
            ttk.Button(row, text=f"View {name}",
                       command=lambda n=name: self.show_table(n)).pack(side="left", padx=(0, 9))

        tk.Label(quick, text="Choose a section from the left menu to view and search records.",
                 bg="white", fg="#6b7c93", font=("Segoe UI", 10)).pack(anchor="w", pady=(20, 0))

    def show_table(self, section):
        self.current_section = section
        self.clear_content()
        info = TABLES[section]
        table = info["table"]
        columns = info["columns"]

        top = tk.Frame(self.content, bg="#f3f6fb")
        top.pack(fill="x")
        tk.Label(top, text=section, bg="#f3f6fb", fg="#142d4e",
                 font=("Segoe UI", 23, "bold")).pack(side="left")
        ttk.Button(top, text="↻ Refresh",
                   command=lambda: self.load_table_rows(section)).pack(side="right")

        searchbar = tk.Frame(self.content, bg="#f3f6fb")
        searchbar.pack(fill="x", pady=16)
        tk.Label(searchbar, text="Search:", bg="#f3f6fb",
                 fg="#40536b", font=("Segoe UI", 10, "bold")).pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(searchbar, textvariable=self.search_var, width=35)
        search_entry.pack(side="left", padx=10)
        search_entry.bind("<Return>", lambda event: self.load_table_rows(section))
        ttk.Button(searchbar, text="Search",
                   command=lambda: self.load_table_rows(section)).pack(side="left")
        ttk.Button(searchbar, text="Show All",
                   command=lambda: (self.search_var.set(""), self.load_table_rows(section))).pack(side="left", padx=7)

        tree_frame = tk.Frame(self.content, bg="white")
        tree_frame.pack(fill="both", expand=True)
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.active_tree = tree
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=max(115, min(180, len(col) * 12)), anchor="center")
        yscroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        xscroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        bottom = tk.Frame(self.content, bg="#f3f6fb")
        bottom.pack(fill="x", pady=12)
        self.table_count = tk.Label(bottom, text="", bg="#f3f6fb",
                                    fg="#68788d", font=("Segoe UI", 10))
        self.table_count.pack(side="left")
        ttk.Button(bottom, text="Delete Selected",
                   command=lambda: self.delete_selected(section)).pack(side="right")

        self.load_table_rows(section)

    def load_table_rows(self, section):
        if not hasattr(self, "active_tree") or not self.active_tree.winfo_exists():
            return
        info = TABLES[section]
        table = info["table"]
        columns = info["columns"]
        search_text = self.search_var.get().strip()

        try:
            if search_text:
                where = " OR ".join(f"CAST(`{col}` AS CHAR) LIKE %s" for col in columns)
                sql = f"SELECT * FROM `{table}` WHERE {where} LIMIT 500"
                params = tuple([f"%{search_text}%"] * len(columns))
                rows = self.query(sql, params)
            else:
                rows = self.query(f"SELECT * FROM `{table}` LIMIT 500")

            for item in self.active_tree.get_children():
                self.active_tree.delete(item)
            for row in rows:
                self.active_tree.insert("", "end",
                    values=[row.get(col) for col in columns])
            self.table_count.config(text=f"{len(rows)} record(s) shown (maximum 500)")
        except Exception as exc:
            messagebox.showerror("Table error", f"Could not load {table}:\n{exc}")

    def delete_selected(self, section):
        selected = self.active_tree.selection()
        if not selected:
            messagebox.showwarning("Select a record", "Please select a row to delete.")
            return

        info = TABLES[section]
        primary = info["primary"]
        columns = info["columns"]
        primary_index = columns.index(primary)
        values = self.active_tree.item(selected[0], "values")
        record_id = values[primary_index]

        if not messagebox.askyesno("Confirm delete",
                                   f"Delete {section[:-1] if section.endswith('s') else section} "
                                   f"record {record_id}?"):
            return
        try:
            self.query(
                f"DELETE FROM `{info['table']}` WHERE `{primary}` = %s",
                (record_id,)
            )
            self.load_table_rows(section)
            messagebox.showinfo("Deleted", "Record deleted successfully.")
        except Exception as exc:
            messagebox.showerror(
                "Delete failed",
                f"{exc}\n\nIf another table refers to this record, MySQL may prevent deletion."
            )

    def on_close(self):
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
        except Exception:
            pass
        self.root.destroy()


if __name__ == "__main__":
    app_root = tk.Tk()
    app = BankDashboard(app_root)
    app_root.protocol("WM_DELETE_WINDOW", app.on_close)
    app_root.mainloop()

