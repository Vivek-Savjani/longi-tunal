# 🎵 Longi-Tunal - Music-Driven Runner Game

BU Research Week Hackathon project. A runner game where levels are dynamically generated based on currently playing music.

## 🎮 How It Works

1. **Audio Analysis** (`audio_analyzer/`) - Analyzes music files and extracts:
   - BPM and beat timing
   - Intensity/energy levels
   - Frequency analysis
   
2. **Level Generation** (`audio_analyzer/mapper.py`) - Converts audio features to:
   - Obstacles (spawned on beats)
   - Collectibles (coins between beats)
   - Speed changes (based on energy)
   - Background effects (visual intensity)

3. **Runner Game** (`music_runner.py`) - Pygame-based runner with:
   - 3-lane system
   - Music-synced gameplay
   - Dynamic difficulty

## 🚀 Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Generate Level Data
```bash
python examples/example_usage.py "your_song.mp3" level_data.json medium
```

### Play the Game
```bash
python music_runner.py
```

## 🎯 Controls

- **Left Arrow** or **A** - Move left
- **Right Arrow** or **D** - Move right  
- **ESC** - Quit game

## 📁 Project Structure

```
longi-tunal/
├── audio_analyzer/          # Audio analysis module
│   ├── analyzer.py         # Extract music features
│   └── mapper.py           # Generate level data
├── examples/
│   └── example_usage.py    # Demo script
├── music_runner.py         # Main game (integrated)
├── game.py                 # Original prototype
└── level_data.json         # Generated level data
```

## 🎵 Game Features

### Music Integration
- **Beat-Synced Obstacles** - Obstacles spawn exactly on music beats
- **Dynamic Speed** - Game speed changes with music intensity
- **Visual Effects** - Background color pulses with music
- **Collectible Timing** - Coins placed strategically between beats

### Difficulty Levels
- **Easy** - Fewer obstacles, more forgiving
- **Medium** - Balanced challenge
- **Hard** - Maximum obstacles, intense gameplay

## 💡 For Developers

### Audio Analysis API
```python
from audio_analyzer import AudioAnalyzer, LevelDataMapper

# Analyze audio
analyzer = AudioAnalyzer('song.mp3')
features = analyzer.analyze_full()

# Generate level
mapper = LevelDataMapper(features)
level_data = mapper.generate_level_data(difficulty='medium')
```

### Level Data Format
```json
{
  "metadata": {
    "duration": 273.07,
    "bpm": 99.38,
    "difficulty": "medium"
  },
  "obstacles": [
    {"time": 1.93, "type": "medium", "lane": 1}
  ],
  "collectibles": [
    {"time": 1.02, "type": "coin", "lane": 2}
  ],
  "speed_changes": [
    {"time": 0.0, "speed": 0.58}
  ]
}
```

## 📦 Dependencies

- **pygame** - Game engine
- **librosa** - Audio analysis
- **numpy** - Numerical processing
- **scipy** - Signal processing
- **soundfile** - Audio I/O

## 🏆 Team

BU Research Week Hackathon Team
