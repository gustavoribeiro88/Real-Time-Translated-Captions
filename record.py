import pyaudio
import wave
import assemblyai as aai
# Record audio from the microphone and save it to a WAV file
def record_audio(filename, duration=5):
    p = pyaudio.PyAudio()

    # Open a stream for recording
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    print("Recording...")

    frames = []

    # Record for the specified duration
    for _ in range(0, int(16000 / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)

    print("Recording stopped.")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded data to a WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(frames))

# Example usage
#if __name__ == "__main__":
    record_audio("output.wav", duration=5)  # Record for 5 seconds
    print("Audio recorded and saved to output.wav")

# Turn the recorded audio into text with AssemblyAI
def audio_to_text(audiofile, language):
    aai.settings.api_key = "d84a3e72de32424d84067fd3d65c3d23"

    transcriber = aai.Transcriber()
    config = aai.TranscriptionConfig(language_code=language)

    transcript = transcriber.transcribe(audiofile, config=config)
    return transcript.text

# Example usage of audio_to_text
if __name__ == "__main__":
    audiofile = "output.wav"
    language = "en"  # Specify the language code, e.g., 'en' for English
    text = audio_to_text(audiofile, language)
    print(f"Transcribed Text: {text}")