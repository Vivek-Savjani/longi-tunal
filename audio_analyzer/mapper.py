"""
Level Data Mapper Module.
Converts audio analysis features into game-ready level data.
"""

import numpy as np


class LevelDataMapper:
    """
    Maps audio features to runner game elements.
    
    This is the interface between audio analysis and the runner game.
    Takes raw audio features and converts them into actionable game data.
    """
    
    def __init__(self, audio_features):
        """
        Initialize mapper with audio features.
        
        Args:
            audio_features (dict): Output from AudioAnalyzer.analyze_full()
        """
        self.features = audio_features
        self.duration = audio_features['duration']
        self.bpm = audio_features['bpm']
        self.beats = audio_features['beats']
    
    def generate_level_data(self, difficulty='medium'):
        """
        Generate complete level data for the runner game.
        
        Args:
            difficulty (str): Difficulty level ('easy', 'medium', 'hard')
            
        Returns:
            dict: Complete level data structure
        """
        obstacles = self._generate_obstacles(difficulty)
        speed_changes = self._generate_speed_changes()
        collectibles = self._generate_collectibles()
        background_intensity = self._generate_background_intensity()
        
        return {
            'metadata': {
                'duration': self.duration,
                'bpm': self.bpm,
                'difficulty': difficulty
            },
            'obstacles': obstacles,
            'speed_changes': speed_changes,
            'collectibles': collectibles,
            'background_intensity': background_intensity
        }
    
    def _generate_obstacles(self, difficulty):
        """
        Generate obstacle positions based on beats and intensity.
        
        Args:
            difficulty (str): Difficulty level
            
        Returns:
            list: List of obstacle definitions
        """
        obstacles = []
        
        # Use beats as primary timing for obstacles
        beats = np.array(self.beats)
        onset_values = np.array(self.features['onset_strength']['values'])
        
        # Normalize onset strength
        onset_normalized = (onset_values - onset_values.min()) / (onset_values.max() - onset_values.min())
        
        # Difficulty multipliers
        difficulty_map = {'easy': 0.3, 'medium': 0.6, 'hard': 0.9}
        spawn_chance = difficulty_map.get(difficulty, 0.6)
        
        for beat_time in beats:
            # Add some randomness but based on music intensity
            beat_idx = int(beat_time * len(onset_normalized) / self.duration)
            beat_idx = min(beat_idx, len(onset_normalized) - 1)
            
            intensity = onset_normalized[beat_idx]
            
            # Spawn obstacle based on intensity and difficulty
            if np.random.random() < spawn_chance * intensity:
                obstacle_type = self._choose_obstacle_type(intensity)
                lane = np.random.randint(0, 3)  # Assuming 3 lanes
                
                obstacles.append({
                    'time': float(beat_time),
                    'type': obstacle_type,
                    'lane': lane,
                    'intensity': float(intensity)
                })
        
        return obstacles
    
    def _choose_obstacle_type(self, intensity):
        """
        Choose obstacle type based on intensity.
        
        Args:
            intensity (float): Normalized intensity value (0-1)
            
        Returns:
            str: Obstacle type
        """
        if intensity < 0.3:
            return 'small'
        elif intensity < 0.7:
            return 'medium'
        else:
            return 'large'
    
    def _generate_speed_changes(self):
        """
        Generate speed change events based on BPM and intensity.
        
        Returns:
            list: List of speed change events
        """
        speed_changes = []
        rms_times = np.array(self.features['rms_energy']['times'])
        rms_values = np.array(self.features['rms_energy']['values'])
        
        # Normalize RMS
        rms_normalized = (rms_values - rms_values.min()) / (rms_values.max() - rms_values.min())
        
        # Calculate base speed from BPM
        base_speed = 1.0 + (self.bpm - 120) / 120  # Normalized around 120 BPM
        
        # Sample speed changes at regular intervals
        sample_interval = int(len(rms_times) / 20)  # ~20 speed changes per song
        
        for i in range(0, len(rms_times), sample_interval):
            intensity = rms_normalized[i]
            speed_multiplier = 0.7 + (intensity * 0.6)  # Range: 0.7 - 1.3
            
            speed_changes.append({
                'time': float(rms_times[i]),
                'speed': float(base_speed * speed_multiplier)
            })
        
        return speed_changes
    
    def _generate_collectibles(self):
        """
        Generate collectible items (power-ups, coins, etc.).
        Places them between obstacles.
        
        Returns:
            list: List of collectible definitions
        """
        collectibles = []
        
        # Place collectibles at half-beats (between main beats)
        beats = np.array(self.beats)
        
        for i in range(len(beats) - 1):
            # Place collectible halfway between beats
            collect_time = (beats[i] + beats[i + 1]) / 2
            
            # 40% chance to spawn collectible
            if np.random.random() < 0.4:
                collectibles.append({
                    'time': float(collect_time),
                    'type': 'coin',
                    'lane': np.random.randint(0, 3)
                })
        
        return collectibles
    
    def _generate_background_intensity(self):
        """
        Generate background visual intensity data for effects.
        
        Returns:
            list: List of time/intensity pairs for background effects
        """
        times = self.features['onset_strength']['times']
        values = self.features['onset_strength']['values']
        
        # Normalize
        values_normalized = (values - np.min(values)) / (np.max(values) - np.min(values))
        
        # Sample at regular intervals for performance
        sample_rate = 10  # Sample every 10th point
        
        return [
            {'time': float(times[i]), 'intensity': float(values_normalized[i])}
            for i in range(0, len(times), sample_rate)
        ]
    
    def export_json(self, filepath):
        """
        Export level data to JSON file.
        
        Args:
            filepath (str): Path to output JSON file
        """
        import json
        
        level_data = self.generate_level_data()
        
        with open(filepath, 'w') as f:
            json.dump(level_data, f, indent=2)
        
        print(f"Level data exported to {filepath}")
