import os
import sys
import json
from vosk import Model, KaldiRecognizer
import pyaudio

# Check if model is downloaded, if not download a small English model
if not os.path.exists("vosk-model-en-in-0.5"):
    print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'vosk-model-small-en-us-0.15' in the current folder.")
    sys.exit(1)

# Initialize Vosk model and recognizer
model = Model("vosk-model-en-in-0.5")
recognizer = KaldiRecognizer(model, 16000)
recognizer.SetWords(True)

# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                input=True, frames_per_buffer=4096)
stream.start_stream()

print("\nListening... (Press Ctrl+C to stop and save)\n")

try:
    full_text = []
    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            result_dict = json.loads(result)
            if 'text' in result_dict and result_dict['text']:
                print(result_dict['text'], end=' ', flush=True)  # Print live transcription
                full_text.append(result_dict['text'])
        else:
            partial_result = recognizer.PartialResult()
            partial_dict = json.loads(partial_result)
            if 'partial' in partial_dict:
                # Clear line and print partial result (for live typing effect)
                sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear the line
                sys.stdout.write(partial_dict['partial'])
                sys.stdout.flush()

except KeyboardInterrupt:
    print("\n\nStopping...")
    
    # Save the full text to file
    with open("listened.txt", "w") as f:
        f.write(" ".join(full_text))
    print(f"Transcript saved to 'listened.txt'")
    
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()