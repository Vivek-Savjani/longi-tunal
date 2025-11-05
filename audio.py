import librosa
import numpy as np
import json
import os

# --- Configuration ---
# You can adjust these parameters to change how smooth or detailed the platform is.
# Higher frame_rate gives finer detail but larger data.
FRAME_RATE = 30  # Data points per second, controlling the visual resolution of the platform
FFT_WINDOW_SIZE = 2048 # Standard Fast Fourier Transform size

def analyze_music_file(filepath):
    """
    Loads an audio file, analyzes its magnitude spectrum (waveform energy),
    and detects beats.

    Args:
        filepath (str): Path to the audio file (e.g., 'user_song.mp3').

    Returns:
        dict: A dictionary containing the list of waveform magnitudes and beat timestamps.
    """
    try:
        # 1. Load the audio file
        # 'sr=None' uses the file's native sampling rate
        print(f"Loading and analyzing: {os.path.basename(filepath)}")
        y, sr = librosa.load(filepath, sr=None)
        
        # Calculate hop length based on the desired visual frame rate
        # This determines how many audio samples correspond to one visual data point
        hop_length = sr // FRAME_RATE
        
        # 2. Get the Short-Time Fourier Transform (STFT)
        # This converts the audio signal into a sequence of magnitude frames (like a spectrogram).
        stft_magnitude = np.abs(librosa.stft(y, n_fft=FFT_WINDOW_SIZE, hop_length=hop_length))
        
        # 3. Aggregate Energy (Waveform Height)
        # Sum the energy across all frequency bins for each time frame. 
        # This gives us a single value representing the overall loudness/energy at that moment.
        # This array will be the Y-height of your runner platform.
        waveform_magnitudes = np.sum(stft_magnitude, axis=0)

        # Normalize the magnitudes to a 0-1 range for easy scaling in the game
        max_mag = np.max(waveform_magnitudes)
        if max_mag == 0:
            normalized_magnitudes = np.zeros_like(waveform_magnitudes)
        else:
            normalized_magnitudes = waveform_magnitudes / max_mag

        # 4. Beat Detection (for Obstacle Spawning)
        # Use librosa's built-in beat tracker for reliable beat detection.
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop_length, units='frames')
        
        # Convert beat frames (indices in the normalized_magnitudes array) to a list
        beat_indices = beat_frames.tolist()

        print(f"Analysis complete. Detected Tempo: {tempo:.2f} BPM.")
        print(f"Total data points (frames): {len(normalized_magnitudes)}")
        print(f"Total beats detected: {len(beat_indices)}")

        # 5. Prepare data for the game loop
        game_data = {
            "waveform_magnitudes": normalized_magnitudes.tolist(),
            "beat_indices": beat_indices,
            "sample_rate": sr,
            "frame_rate": FRAME_RATE,
            "hop_length": hop_length,
            "duration": librosa.get_duration(y=y, sr=sr),
            # The game loop will need to play the audio back synchronously
            "audio_file": filepath # The game must load and play this file
        }
        
        return game_data

    except Exception as e:
        print(f"An error occurred during audio analysis: {e}")
        return None

if __name__ == '__main__':
    # --- EXAMPLE USAGE ---
    # NOTE: You MUST have a sound file named 'test_song.mp3' or similar in the same directory
    # or replace the path below with a valid path to an MP3 or WAV file.
    
    # Create a dummy file path for demonstration purposes since we can't upload assets here
    # Replace this with the path to the user's actual uploaded music file in your final game!
    # E.g., user_file_path = "C:/Users/User/Downloads/my_epic_song.wav"
    user_file_path = "test_song.mp3" 

    if os.path.exists(user_file_path):
        data = analyze_music_file(user_file_path)
        if data:
            # Save the analyzed data to a JSON file. This is often the best way to 
            # decouple the analysis phase from the game execution phase.
            with open('game_audio_data.json', 'w') as f:
                json.dump(data, f)