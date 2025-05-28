import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Initialize the main application window
def create_main_window():
    root = tk.Tk()
    root.title("Real-Time Translated Captions")
    root.geometry("600x400")
    root.configure(bg="#222831")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#222831")
    style.configure("TLabel", background="#222831", foreground="#eeeeee", font=("Segoe UI", 12))
    style.configure("TButton", background="#00adb5", foreground="#eeeeee", font=("Segoe UI", 11, "bold"))
    style.map("TButton",
              background=[("active", "#393e46")],
              foreground=[("active", "#00adb5")])

    # Create a frame for the input area
    input_frame = ttk.Frame(root, padding="20")
    input_frame.pack(fill=tk.BOTH, expand=True)

    # Create a label for instructions
    instructions = ttk.Label(
        input_frame,
        text="Press 'Start' to begin real-time translation.",
        anchor="center"
    )
    instructions.pack(pady=20)

    # Create a button to start the translation process
    start_button = ttk.Button(
        input_frame,
        text="Start",
        command=lambda: messagebox.showinfo("Info", "Starting translation...")
    )
    start_button.pack(pady=20, ipadx=10, ipady=5)

    return root
# Run the application
def run_app():
    app = create_main_window()
    app.mainloop()
if __name__ == "__main__":
    run_app()