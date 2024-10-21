import random
import sqlite3
from tkinter import *
from tkinter import messagebox

# Function to initialize the database
def init_db():
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY,
            application TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Function to generate a random password
def generate_password(length, allow_repetition):
    character_pool = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

    if allow_repetition:
        password = ''.join(random.choice(character_pool) for _ in range(length))
    else:
        if length > len(character_pool):
            return None  # Prevents repetition from exceeding available characters
        password = ''.join(random.sample(character_pool, length))

    return password

# Function to save password to the database
def save_password(application_name, password):
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute("INSERT INTO passwords (application, password) VALUES (?, ?)", (application_name, password))
    conn.commit()
    conn.close()

# Function to load all saved passwords
def load_passwords():
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute("SELECT * FROM passwords")
    passwords = c.fetchall()
    conn.close()
    return passwords

# Function to delete a password by ID
def delete_password(password_id):
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute("DELETE FROM passwords WHERE id = ?", (password_id,))
    conn.commit()
    conn.close()

# Function to clear all saved passwords
def clear_passwords():
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute("DELETE FROM passwords")
    conn.commit()
    conn.close()

# Function to generate and display the password
def on_generate():
    try:
        length = int(length_entry.get())
        allow_repetition = repetition_var.get()
        application_name = app_name_entry.get()

        password = generate_password(length, allow_repetition)
        if password:
            # Display the generated password in the password_label
            password_label.config(text=f"Generated Password: {password}")
            password_entry.delete(0, END)
            password_entry.insert(0, password)
            # Append password as not saved initially
            all_generated_passwords.append({
                'application': application_name,
                'password': password,
                'saved': False
            })
        else:
            messagebox.showerror("Error", "Password length exceeds available characters without repetition.")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid length.")

# Function to save the generated password
def on_save():
    application_name = app_name_entry.get()
    password = password_entry.get()
    if application_name and password:
        save_password(application_name, password)
        app_name_entry.delete(0, END)
        password_entry.delete(0, END)
        messagebox.showinfo("Saved", "Password saved successfully!")

        # Update generated password status to saved
        for p in all_generated_passwords:
            if p['password'] == password and p['application'] == application_name:
                p['saved'] = True
                break
    else:
        messagebox.showerror("Error", "Please enter an application name and password.")

# Function to refresh the saved passwords display
def refresh_saved_passwords_display(passwords_window):
    for widget in passwords_window.winfo_children():
        widget.destroy()  # Clear previous contents

    # Create header for the table
    header = Frame(passwords_window)
    header.pack(fill=X, padx=5, pady=5)

    Label(header, text="Application", font=('bold', 12), width=20).pack(side=LEFT)
    Label(header, text="Password", font=('bold', 12), width=20).pack(side=LEFT)
    Label(header, text="Created At", font=('bold', 12), width=20).pack(side=LEFT)
    Label(header, text="", font=('bold', 12), width=10).pack(side=LEFT)

    # Load saved passwords from the database
    passwords = load_passwords()

    # Display each saved password in the table format
    for password in passwords:
        password_item = Frame(passwords_window)
        password_item.pack(fill=X, padx=5, pady=5)

        Label(password_item, text=password[1], width=20).pack(side=LEFT)
        Label(password_item, text=password[2], width=20).pack(side=LEFT)
        Label(password_item, text=password[3], width=20).pack(side=LEFT)
        Button(password_item, text="Delete", command=lambda id=password[0]: delete_password(id) or refresh_saved_passwords_display(passwords_window)).pack(side=LEFT)

# Function to open a new window to display saved passwords
def open_saved_passwords_window():
    passwords_window = Toplevel(root)
    passwords_window.title("Saved Passwords")
    passwords_window.geometry("600x400")
    refresh_saved_passwords_display(passwords_window)  # Display current passwords

# Function to load and display all passwords
def open_all_passwords_window():
    all_passwords_window = Toplevel(root)
    all_passwords_window.title("All Passwords")
    all_passwords_window.geometry("600x400")

    for widget in all_passwords_window.winfo_children():
        widget.destroy()  # Clear previous contents

    Label(all_passwords_window, text="All Generated Passwords", font=('bold', 14)).pack(pady=10)

    # Display saved passwords in a structured format with delete options
    for password in load_passwords():
        password_item = Frame(all_passwords_window)
        password_item.pack(fill=X, padx=5, pady=5)

        Label(password_item, text=password[1], width=20).pack(side=LEFT)
        Label(password_item, text=password[2], width=20).pack(side=LEFT)
        Label(password_item, text=password[3], width=20).pack(side=LEFT)
        Button(password_item, text="Delete", command=lambda id=password[0]: delete_password(id) or open_all_passwords_window()).pack(side=LEFT)

    # Show all previously generated passwords, including those not saved
    Label(all_passwords_window, text="Previously Generated Passwords", font=('bold', 12)).pack(pady=10)

    for password_entry in all_generated_passwords:
        password_item = Frame(all_passwords_window)
        password_item.pack(fill=X, padx=5, pady=5)

        Label(password_item, text=password_entry['application'], width=20).pack(side=LEFT)
        Label(password_item, text=password_entry['password'], width=20).pack(side=LEFT)
        status = "Saved" if password_entry['saved'] else "Not Saved"
        Label(password_item, text=status, width=20).pack(side=LEFT)
        if password_entry['saved']:
            Button(password_item, text="Delete", command=lambda p=password_entry: messagebox.showinfo("Info", "Use the 'Saved Passwords' view to delete saved passwords.")).pack(side=LEFT)
        else:
            Button(password_item, text="Delete", command=lambda p=password_entry: all_generated_passwords.remove(p) or open_all_passwords_window()).pack(side=LEFT)

# Function to clear all saved and generated passwords
def on_clear():
    if messagebox.askyesno("Confirm", "Are you sure you want to clear ALL passwords?"):
        clear_passwords()  # Clear all saved passwords from the database
        all_generated_passwords.clear()  # Clear all generated passwords (unsaved ones)
        messagebox.showinfo("Success", "All passwords cleared!")

# Initialize a list to store all generated passwords
all_generated_passwords = []

# Set up the main application window
root = Tk()
root.title("Password Generator")
root.geometry("600x600")

# Entry fields for password generation
length_label = Label(root, text="Password Length:")
length_label.pack(pady=5)
length_entry = Entry(root)
length_entry.pack(pady=5)

# Checkboxes for repetition
repetition_var = BooleanVar(value=True)
Checkbutton(root, text="Allow Repetition", variable=repetition_var).pack(anchor="w")

# Field for application name
app_name_label = Label(root, text="Application Name:")
app_name_label.pack(pady=5)
app_name_entry = Entry(root)
app_name_entry.pack(pady=5)

# Label to display generated password
password_label = Label(root, text="Generated Password: ")
password_label.pack(pady=5)

# Buttons to generate and save passwords
generate_button = Button(root, text="Generate Password", command=on_generate)
generate_button.pack(pady=5)

password_entry = Entry(root)
password_entry.pack(pady=5)

save_button = Button(root, text="Save Password", command=on_save)
save_button.pack(pady=5)

# View all passwords button
view_all_button = Button(root, text="View All Passwords", command=open_all_passwords_window)
view_all_button.pack(pady=5)

# View saved passwords button
view_saved_button = Button(root, text="View Saved Passwords", command=open_saved_passwords_window)
view_saved_button.pack(pady=5)

# Clear all passwords button
clear_button = Button(root, text="Clear All Passwords", command=on_clear)
clear_button.pack(pady=5)

# Initialize the database
init_db()

# Start the main loop
root.mainloop()
