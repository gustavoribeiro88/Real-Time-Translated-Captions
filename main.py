import os
import pandas as pd
import numpy as np
import langdetect as ld
import pyaudio
import assemblyai as aai
import app
import record
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
from queue import Queue
import app
import record

# Start recording and transcribing in a separate thread
def start_recording_and_transcribing(queue, language):
    while True:
        record.record_audio("output.wav", duration=5)  # Record for 5 seconds
        text = record.audio_to_text("output.wav", language)
        queue.put(text)
    
# Update the GUI with the transcribed text
def update_gui(queue, text_widget):
    while True:
        if not queue.empty():
            text = queue.get()
            text_widget.insert(tk.END, text + '\n')
            text_widget.see(tk.END)  # Scroll to the end
        text_widget.update_idletasks()
# Create the main application window
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

    # Create a text widget to display transcribed text
    text_widget = tk.Text(input_frame, wrap=tk.WORD, height=10)
    text_widget.pack(fill=tk.BOTH, expand=True, pady=10)

    return root, text_widget
# Run the application
def run_app():
    root, text_widget = create_main_window()

    queue = Queue()

    # Detect language once
    record.record_audio("output.wav", duration=5)
    text = record.audio_to_text("output.wav", language='en')
    language = ld.detect(text)
    text_widget.insert(tk.END, f"Detected language: {language}\n{text}\n")
    text_widget.see(tk.END)

    # Start recording and transcribing with detected language
    Thread(target=start_recording_and_detect_language, args=(queue,), daemon=True).start()
    Thread(target=transcribe_loop, daemon=True).start()
    Thread(target=update_gui, args=(queue, text_widget), daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    run_app()