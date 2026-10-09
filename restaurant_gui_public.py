
import tkinter as tk
from db_config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime

# DATABASE CONNECTION
def connect_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

root = tk.Tk()
root.title("Restaurant Management System")
root.geometry("900x600")
root.configure(bg="#f2f4f7")

title = tk.Label(
    root, text="RESTAURANT MANAGEMENT SYSTEM",
    font=("Arial", 22, "bold"),
    bg="#182235", fg="white", pady=20
)
title.pack(fill="x")

tk.Label(
    root, text="Restaurant POS",
    font=("Arial", 18, "bold"),
    bg="#f2f4f7"
).pack(pady=20)


def open_menu():
    win = tk.Toplevel(root)
    win.title("Manage Menu")
    win.geometry("600x400")

    table = ttk.Treeview(
        win, columns=("ID", "Name", "Price"),
        show="headings"
    )
    for col in ("ID", "Name", "Price"):
        table.heading(col, text=col)
        table.column(col, width=150)
    table.pack(fill="both", expand=True, padx=15, pady=15)

    try:
        db = connect_db()
        cur = db.cursor()
        cur.execute("SELECT ino, iname, iprice FROM hotel")
        for row in cur.fetchall():
            table.insert("", "end", values=row)
        cur.close()
        db.close()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))


def open_orders():
    win = tk.Toplevel(root)
    win.title("New Order - Billing")
    win.geometry("750x550")

    tk.Label(
        win, text="NEW ORDER / BILLING",
        font=("Arial", 20, "bold")
    ).pack(pady=12)

    try:
        db = connect_db()
        cur = db.cursor()
        cur.execute("SELECT ino, iname, iprice FROM hotel")
        menu = cur.fetchall()
        cur.close()
        db.close()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
        win.destroy()
        return

    if not menu:
        messagebox.showinfo("Menu", "Menu is empty.")
        win.destroy()
        return

    item_map = {
        f"{name} - Rs. {price}": (code, name, price)
        for code, name, price in menu
    }

    tk.Label(win, text="Select Item").pack()
    item_var = tk.StringVar(value=list(item_map.keys())[0])
    item_box = ttk.Combobox(
        win, textvariable=item_var,
        values=list(item_map.keys()),
        state="readonly", width=35
    )
    item_box.pack(pady=5)

    tk.Label(win, text="Quantity").pack()
    qty_entry = tk.Entry(win, justify="center")
    qty_entry.insert(0, "1")
    qty_entry.pack(pady=5)

    table = ttk.Treeview(
        win,
        columns=("Item", "Price", "Qty", "Total"),
        show="headings", height=12
    )
    for col in ("Item", "Price", "Qty", "Total"):
        table.heading(col, text=col)
        table.column(col, width=130)
    table.pack(fill="both", expand=True, padx=10, pady=10)

    total = [0]
    cart = []

    total_label = tk.Label(
        win, text="Grand Total: Rs. 0",
        font=("Arial", 16, "bold")
    )
    total_label.pack(pady=5)

    def add_item():
        try:
            qty = int(qty_entry.get())
            if qty <= 0:
                raise ValueError

            code, name, price = item_map[item_var.get()]
            amount = price * qty

            cart.append((code, name, price, qty, amount))
            table.insert(
                "", "end",
                values=(name, price, qty, amount)
            )
            total[0] += amount
            total_label.config(
                text=f"Grand Total: Rs. {total[0]}"
            )
        except ValueError:
            messagebox.showerror(
                "Invalid Quantity",
                "Quantity must be a positive whole number."
            )

    def clear_order():
        cart.clear()
        for row in table.get_children():
            table.delete(row)
        total[0] = 0
        total_label.config(text="Grand Total: Rs. 0")

    def generate_bill():
        if not cart:
            messagebox.showwarning(
                "Empty Order", "Please add an item first."
            )
            return

        try:
            db = connect_db()
            cur = db.cursor()
            order_no = "ORD-" + datetime.now().strftime(
                "%Y%m%d%H%M%S%f"
            )

            cur.execute(
                "INSERT INTO report (order_no, tot_amount) "
                "VALUES (%s, %s)",
                (order_no, total[0])
            )
            db.commit()
            cur.close()
            db.close()

            bill = (
                f"Order No: {order_no}\n\n"
                + "\n".join(
                    f"{name} x {qty} = Rs. {amount}"
                    for code, name, price, qty, amount in cart
                )
                + f"\n\nGrand Total: Rs. {total[0]}"
            )
            messagebox.showinfo("Bill Generated", bill)
            clear_order()

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))

    tk.Button(
        win, text="Add to Order",
        command=add_item, width=20
    ).pack(pady=4)

    tk.Button(
        win, text="Generate Bill",
        command=generate_bill, width=20
    ).pack(pady=4)

    tk.Button(
        win, text="Clear Order",
        command=clear_order, width=20
    ).pack(pady=4)


def open_sales():
    win = tk.Toplevel(root)
    win.title("Sales Report")
    win.geometry("600x400")

    table = ttk.Treeview(
        win, columns=("Order No", "Amount"),
        show="headings"
    )
    table.heading("Order No", text="Order No")
    table.heading("Amount", text="Amount (Rs.)")
    table.pack(fill="both", expand=True, padx=15, pady=15)

    try:
        db = connect_db()
        cur = db.cursor()
        cur.execute(
            "SELECT order_no, tot_amount FROM report"
        )
        rows = cur.fetchall()
        for row in rows:
            table.insert("", "end", values=row)

        cur.close()
        db.close()

        grand_total = sum(row[1] for row in rows)
        tk.Label(
            win,
            text=f"Total Sales: Rs. {grand_total}",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))


tk.Button(
    root, text="Manage Menu", width=25,
    command=open_menu
).pack(pady=8)

tk.Button(
    root, text="New Order", width=25,
    command=open_orders
).pack(pady=8)

tk.Button(
    root, text="Sales Report", width=25,
    command=open_sales
).pack(pady=8)

root.mainloop()
