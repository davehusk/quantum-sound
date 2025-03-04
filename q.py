
import numpy as np
import pyaudio

# Parameters
N = 20
sample_rate = 44100  # Standard audio rate
buffer_size = 512    # Common buffer size

# Initialize quantum state
frequencies = np.logspace(np.log10(100), np.log10(10000), N)
amplitudes = np.random.rand(N) * np.exp(1j * np.random.rand(N) * 2 * np.pi)
H = np.diag(np.ones(N)) + 0.1 * (np.eye(N, k=1) + np.eye(N, k=-1))

# Precompute matrix exponential for exact evolution
dt = buffer_size / sample_rate
H_complex = -1j * H * dt
expH = np.linalg.matrix_exp(H_complex)

def quantum_audio_callback(in_data, frame_count, time_info, status):
    global amplitudes
    
    # Exact time evolution using matrix exponential
    amplitudes = expH @ amplitudes
    
    # Normalize amplitudes to preserve quantum state norm
    norm = np.linalg.norm(amplitudes)
    if norm > 0:
        amplitudes /= norm
    
    # Synthesize sound using squared magnitudes (probabilities)
    t = np.linspace(0, dt, buffer_size, endpoint=False)
    signal = np.zeros(buffer_size)
    for i in range(N):
        signal += np.abs(amplitudes[i])**2 * np.sin(2 * np.pi * frequencies[i] * t)
    
    # Stereo output
    signal = np.repeat(signal[:, None], 2, axis=1)
    signal = np.clip(signal, -1, 1).astype(np.float32).tobytes()
    
    return (signal, pyaudio.paContinue)

# Start audio stream
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32,
                channels=2,
                rate=sample_rate,
                output=True,
                frames_per_buffer=buffer_size,
                stream_callback=quantum_audio_callback)

stream.start_stream()
input("Press Enter to stop...")
stream.stop_stream()
stream.close()
p.terminate()
