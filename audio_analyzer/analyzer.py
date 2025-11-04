"""
Core audio analysis module.
Extracts musical features from audio files.
"""

import librosa
import numpy as np


class AudioAnalyzer:
    """
    Analyzes audio files and extracts musical features.
    
    Features extracted:
    - BPM (tempo)
    - Beat timestamps
    - Onset strength (intensity over time)
    - Spectral features (frequency distribution)
    """
    
    def __init__(self, audio_path):
        """
        Initialize the analyzer with an audio file.
        
        Args:
            audio_path (str): Path to the audio file
        """
        self.audio_path = audio_path
        self.y = None  # Audio time series
        self.sr = None  # Sample rate
        self.duration = None
        self._load_audio()
    
    def _load_audio(self):
        """Load the audio file."""
        self.y, self.sr = librosa.load(self.audio_path)
        self.duration = librosa.get_duration(y=self.y, sr=self.sr)
    
    def get_bpm(self):
        """
        Extract the tempo (BPM) of the audio.
        
        Returns:
            float: Beats per minute
        """
        tempo, _ = librosa.beat.beat_track(y=self.y, sr=self.sr)
        return float(tempo)
    
    def get_beats(self):
        """
        Detect beat timestamps in the audio.
        
        Returns:
            numpy.ndarray: Array of beat times in seconds
        """
        tempo, beat_frames = librosa.beat.beat_track(y=self.y, sr=self.sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=self.sr)
        return beat_times
    
    def get_onset_strength(self, hop_length=512):
        """
        Calculate onset strength envelope (intensity over time).
        
        Args:
            hop_length (int): Number of samples between frames
            
        Returns:
            tuple: (times, onset_strength_values)
        """
        onset_env = librosa.onset.onset_strength(y=self.y, sr=self.sr, hop_length=hop_length)
        times = librosa.frames_to_time(np.arange(len(onset_env)), sr=self.sr, hop_length=hop_length)
        return times, onset_env
    
    def get_spectral_features(self, n_bins=5):
        """
        Extract spectral features divided into frequency bands.
        Useful for mapping different frequencies to different game elements.
        
        Args:
            n_bins (int): Number of frequency bands to divide into
            
        Returns:
            dict: Dictionary with frequency bands and their energy over time
        """
        # Compute spectrogram
        S = np.abs(librosa.stft(self.y))
        
        # Divide into frequency bands
        freq_bands = np.array_split(S, n_bins, axis=0)
        
        result = {}
        for i, band in enumerate(freq_bands):
            # Calculate energy in each band over time
            energy = np.mean(band, axis=0)
            result[f'band_{i}'] = energy
        
        return result
    
    def get_rms_energy(self):
        """
        Get RMS (Root Mean Square) energy over time.
        Represents overall loudness/intensity.
        
        Returns:
            tuple: (times, rms_values)
        """
        rms = librosa.feature.rms(y=self.y)[0]
        times = librosa.frames_to_time(np.arange(len(rms)), sr=self.sr)
        return times, rms
    
    def analyze_full(self):
        """
        Perform full analysis and return all features.
        
        Returns:
            dict: Dictionary containing all extracted features
        """
        bpm = self.get_bpm()
        beats = self.get_beats()
        onset_times, onset_strength = self.get_onset_strength()
        rms_times, rms_energy = self.get_rms_energy()
        spectral_features = self.get_spectral_features()
        
        return {
            'duration': self.duration,
            'bpm': bpm,
            'beats': beats.tolist(),
            'onset_strength': {
                'times': onset_times.tolist(),
                'values': onset_strength.tolist()
            },
            'rms_energy': {
                'times': rms_times.tolist(),
                'values': rms_energy.tolist()
            },
            'spectral_features': {
                band: values.tolist() 
                for band, values in spectral_features.items()
            }
        }
