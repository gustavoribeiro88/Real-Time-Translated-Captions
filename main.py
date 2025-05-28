import os
import pandas as pd
import numpy as np
import langdetect as ld
import pyaudio
import assemblyai as aai
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
from queue import Queue
import time
import speech_recognition as sr
import wave

# Define API key for AssemblyAI
aai.settings.api_key = 'd84a3e72de32424d84067fd3d65c3d23'  # Replace with your AssemblyAI API key

# Record audio using PyAudio
def record_audio(filename, duration=5):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    frames = []

    print("Recording...")
    for _ in range(0, int(16000 / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)

    print("Recording finished.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Ensure audiocache directory exists
    if not os.path.exists("audiocache"):
        os.makedirs("audiocache")
    filepath = os.path.join("audiocache", filename)

    # Save as proper WAV file
    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(frames))

# Convert audio file to text using AssemblyAI
def audio_to_text(filename, language='en'):
    filepath = os.path.join("audiocache", filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Audio file {filepath} does not exist.")

    # Read the audio file
    with open(filepath, 'rb') as f:
        audio_data = f.read()
    
    # Set the language for transcription using TranscriptionConfig
    config = aai.TranscriptionConfig(language_code=language)

    # Upload the audio file to AssemblyAI
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe("audiocache/" + filename, config=config)
    
    # Poll for the transcription result
    while transcript.status != 'completed':
        time.sleep(5)  # Wait before checking again
        transcript = aai.Transcript.get(transcript.id)

    return transcript.text

# Start recording and transcribing in a separate thread
def start_recording_and_transcribing(queue, language):
    os.makedirs("audiocache", exist_ok=True)
    while True:
        filename = f"output_{int(time.time() * 1000)}.wav"
        record_audio(filename, duration=5)  # Record for 5 seconds
        text = audio_to_text(filename, language)
        queue.put(text)
        # Print the transcribed text to the console (optional)
        print(f"Transcribed Text: {text}")


# Detect language from an audio file AssemblyAI aai.TranscriptionConfig's language_detection set to True
def detect_language(filepath):
    audio_file = filepath
    transcriber = aai.Transcriber()
    config = aai.TranscriptionConfig(language_detection=True)
    transcript = transcriber.transcribe(audio_file, config=config)
    # Poll for the transcription result
    while transcript.status != 'completed':
        time.sleep(5)  # Wait before checking again
        transcript = aai.Transcript.get(transcript.id)
    if transcript.json_response["language_code"]:
        return transcript.json_response["language_code"]  # Return the detected language code


# Update the GUI with the transcribed text
def update_gui(queue, text_widget):
    while True:
        if not queue.empty():
            text = queue.get()
            text_widget.insert(tk.END, text + '\n')
            text_widget.see(tk.END)  # Scroll to the end
        text_widget.update_idletasks()

# Create the main application window
def create_main_window(detected_language='en'):
    root = tk.Tk()
    root.title("Real-Time Translated Captions")
    root.geometry("600x450")
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
    instructions.pack(pady=10)

    # Language selection
    languages = {
        "English": "en",
        "Spanish": "es",
        "French": "fr",
        "German": "de",
        "Italian": "it",
        "Portuguese": "pt",
        "Russian": "ru",
        "Chinese": "zh",
        "Japanese": "ja",
        "Korean": "ko"
    }

    # Default translation language logic
    if detected_language == "en":
        default_lang_code = "es"
    else:
        default_lang_code = "en"

    default_lang_name = [k for k, v in languages.items() if v == default_lang_code][0]

    lang_label = ttk.Label(input_frame, text="Translate to:")
    lang_label.pack(pady=(10, 0))

    lang_var = tk.StringVar(value=default_lang_name)
    lang_combo = ttk.Combobox(
        input_frame,
        textvariable=lang_var,
        values=list(languages.keys()),
        state="readonly"
    )
    lang_combo.pack(pady=(0, 10))

    # Create a text widget to display transcribed text
    text_widget = tk.Text(input_frame, wrap=tk.WORD, height=10)
    text_widget.pack(fill=tk.BOTH, expand=True, pady=10)

    # Return language selection variable as well
    return root, text_widget, lang_var, languages
# Run the application
def run_app():
    root, text_widget, lang_var, languages = create_main_window()

    queue = Queue()

    # Detect language once from a first audio file wich will be recorded
    language = 'en'  # Default language
    try:
        # Record a short audio clip to detect language
        filename = "temp.wav"
        record_audio(filename, duration=5)  # Record for 5 seconds
        language = detect_language("audiocache/" + filename)
        if not language:
            raise ValueError("Language detection failed.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to detect language: {e}")
        return

    print(f"Detected Language: {language}")

    # Start recording and transcribing with detected language
    Thread(target=start_recording_and_transcribing, args=(queue, language), daemon=True).start()


    Thread(target=update_gui, args=(queue, text_widget), daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    run_app()