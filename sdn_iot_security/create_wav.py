import wave
import numpy as np

# Create a simple WAV file with audio samples
sample_rate = 44100
duration = 2  # 2 seconds
frequency = 440  # A4 note

# Generate sine wave
t = np.linspace(0, duration, int(sample_rate * duration))
audio_data = np.sin(2 * np.pi * frequency * t)

# Scale to 16-bit range
audio_data = (audio_data * 32767).astype(np.int16)

# Write to WAV file
output_path = 'input.wav'
with wave.open(output_path, 'wb') as wav_file:
    wav_file.setnchannels(1)  # Mono
    wav_file.setsampwidth(2)  # 2 bytes per sample
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(audio_data.tobytes())

print(f"Created input.wav with {len(audio_data)} samples")
