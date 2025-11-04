# Longi-Tunal - Music-Driven Runner Game

BU research week Hackathon. Runner game in which levels are generated based on currently playing music.

## Project Structure

```
longi-tunal/
├── audio_analyzer/          # Audio analysis and level generation module
│   ├── __init__.py
│   ├── analyzer.py         # Core audio analysis (BPM, beats, intensity)
│   └── mapper.py           # Audio features → Game level data mapper
├── examples/
│   └── example_usage.py    # Demo script
├── tests/                   # Unit tests (TODO)
└── requirements.txt        # Python dependencies
```

## Audio Analysis Module

This module serves as the **interface between audio and the runner game**. It:

1. **Analyzes music files** - Extracts BPM, beats, intensity, frequency data
2. **Generates level data** - Converts audio features into game elements

### Features Extracted

- **BPM (Tempo)** - For base game speed
- **Beat Detection** - Primary timing for obstacles
- **Onset Strength** - Intensity over time for dynamic difficulty
- **RMS Energy** - Overall loudness for speed variations
- **Spectral Features** - Frequency bands for varied game elements

### Level Data Output

The mapper generates a JSON structure with:

```json
{
  "metadata": {
    "duration": 180.5,
    "bpm": 128.0,
    "difficulty": "medium"
  },
  "obstacles": [
    {"time": 1.5, "type": "medium", "lane": 1, "intensity": 0.75}
  ],
  "speed_changes": [
    {"time": 5.0, "speed": 1.2}
  ],
  "collectibles": [
    {"time": 2.3, "type": "coin", "lane": 0}
  ],
  "background_intensity": [
    {"time": 0.0, "intensity": 0.5}
  ]
}
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Analysis

```python
from audio_analyzer import AudioAnalyzer, LevelDataMapper

# Analyze audio
analyzer = AudioAnalyzer('song.mp3')
features = analyzer.analyze_full()

# Generate level data
mapper = LevelDataMapper(features)
level_data = mapper.generate_level_data(difficulty='medium')

# Export to JSON
mapper.export_json('level_output.json')
```

### Command Line

```bash
python examples/example_usage.py song.mp3 output.json medium
```

## Integration Guide for Runner Game Team

### Input Format
Your runner game should load the generated JSON file containing:
- `obstacles`: When and where to spawn obstacles
- `speed_changes`: Game speed adjustments over time
- `collectibles`: Power-ups/coins placement
- `background_intensity`: Visual effects intensity

### Timing
All time values are in **seconds** from the start of the song.

### Lanes
Obstacles and collectibles use `lane` field (0-2 for 3 lanes, adjust as needed).

### Difficulty
Available: `'easy'`, `'medium'`, `'hard'` - affects obstacle density.

## Development Status

- [x] Audio analysis module
- [x] Level data mapper
- [x] JSON export functionality
- [ ] Unit tests
- [ ] Runner game integration (in progress by other team members)

## Dependencies

- `librosa` - Audio analysis
- `numpy` - Numerical operations
- `scipy` - Signal processing
- `soundfile` - Audio file I/O

## License

Educational project for BU Research Week Hackathon
