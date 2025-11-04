# 🎵 Longi-Tunal - Music-Driven Runner Game<<<<<<< HEAD

# Longi-Tunal - Music-Driven Runner Game

BU Research Week Hackathon project. A runner game where levels are dynamically generated based on currently playing music.

BU research week Hackathon. Runner game in which levels are generated based on currently playing music.

## 🎮 How It Works

## Project Structure

1. **Audio Analysis** (`audio_analyzer/`) - Analyzes music files and extracts:

   - BPM and beat timing```

   - Intensity/energy levelslongi-tunal/

   - Frequency analysis├── audio_analyzer/          # Audio analysis and level generation module

   │   ├── __init__.py

2. **Level Generation** (`audio_analyzer/mapper.py`) - Converts audio features to:│   ├── analyzer.py         # Core audio analysis (BPM, beats, intensity)

   - Obstacles (spawned on beats)│   └── mapper.py           # Audio features → Game level data mapper

   - Speed changes (based on energy)├── examples/

   - Background effects (visual intensity)│   └── example_usage.py    # Demo script

├── tests/                   # Unit tests (TODO)

3. **Runner Game** (`music_runner.py`) - Pygame-based runner with:└── requirements.txt        # Python dependencies

   - 3-lane system```

   - Music-synced gameplay

   - Dynamic difficulty## Audio Analysis Module



## 🚀 Quick StartThis module serves as the **interface between audio and the runner game**. It:



### Installation1. **Analyzes music files** - Extracts BPM, beats, intensity, frequency data

```bash2. **Generates level data** - Converts audio features into game elements

pip install -r requirements.txt

```### Features Extracted



### Generate Level Data- **BPM (Tempo)** - For base game speed

```bash- **Beat Detection** - Primary timing for obstacles

python examples/example_usage.py "your_song.mp3" level_data.json medium- **Onset Strength** - Intensity over time for dynamic difficulty

```- **RMS Energy** - Overall loudness for speed variations

- **Spectral Features** - Frequency bands for varied game elements

### Play the Game

```bash### Level Data Output

python music_runner.py

```The mapper generates a JSON structure with:



## 🎯 Controls```json

{

- **Left Arrow** or **A** - Move left  "metadata": {

- **Right Arrow** or **D** - Move right      "duration": 180.5,

- **ESC** - Quit game    "bpm": 128.0,

    "difficulty": "medium"

## 📁 Project Structure  },

  "obstacles": [

```    {"time": 1.5, "type": "medium", "lane": 1, "intensity": 0.75}

longi-tunal/  ],

├── audio_analyzer/          # Audio analysis module  "speed_changes": [

│   ├── analyzer.py         # Extract music features    {"time": 5.0, "speed": 1.2}

│   └── mapper.py           # Generate level data  ],

├── examples/  "collectibles": [

│   └── example_usage.py    # Demo script    {"time": 2.3, "type": "coin", "lane": 0}

├── music_runner.py         # Main game (integrated)  ],

├── game.py                 # Original prototype  "background_intensity": [

└── level_data.json         # Generated level data    {"time": 0.0, "intensity": 0.5}

```  ]

}

## 🎵 Game Features```



### Music Integration## Installation

- **Beat-Synced Obstacles** - Obstacles spawn exactly on music beats

- **Dynamic Speed** - Game speed changes with music intensity=======

- **Visual Effects** - Background color pulses with music# 🎵 Longi-Tunal - Music-Driven Runner Game



### Difficulty LevelsBU Research Week Hackathon project. A runner game where levels are dynamically generated based on currently playing music.

- **Easy** - Fewer obstacles, more forgiving

- **Medium** - Balanced challenge## 🎮 How It Works

- **Hard** - Maximum obstacles, intense gameplay

1. **Audio Analysis** (`audio_analyzer/`) - Analyzes music files and extracts:

## 💡 For Developers   - BPM and beat timing

   - Intensity/energy levels

### Audio Analysis API   - Frequency analysis

```python   

from audio_analyzer import AudioAnalyzer, LevelDataMapper2. **Level Generation** (`audio_analyzer/mapper.py`) - Converts audio features to:

   - Obstacles (spawned on beats)

# Analyze audio   - Collectibles (coins between beats)

analyzer = AudioAnalyzer('song.mp3')   - Speed changes (based on energy)

features = analyzer.analyze_full()   - Background effects (visual intensity)



# Generate level3. **Runner Game** (`music_runner.py`) - Pygame-based runner with:

mapper = LevelDataMapper(features)   - 3-lane system

level_data = mapper.generate_level_data(difficulty='medium')   - Music-synced gameplay

```   - Dynamic difficulty



### Level Data Format## 🚀 Quick Start

```json

{### Installation

  "metadata": {>>>>>>> runner

    "duration": 273.07,```bash

    "bpm": 99.38,pip install -r requirements.txt

    "difficulty": "medium"```

  },

  "obstacles": [<<<<<<< HEAD

    {"time": 1.93, "type": "medium", "lane": 1}## Usage

  ],

  "speed_changes": [### Basic Analysis

    {"time": 0.0, "speed": 0.58}

  ]=======

}### Generate Level Data

``````bash

python examples/example_usage.py "your_song.mp3" level_data.json medium

## 📦 Dependencies```



- **pygame** - Game engine### Play the Game

- **librosa** - Audio analysis```bash

- **numpy** - Numerical processingpython music_runner.py

- **scipy** - Signal processing```

- **soundfile** - Audio I/O

## 🎯 Controls

## 🏆 Team

- **Left Arrow** or **A** - Move left

BU Research Week Hackathon Team- **Right Arrow** or **D** - Move right  

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
>>>>>>> runner
```python
from audio_analyzer import AudioAnalyzer, LevelDataMapper

# Analyze audio
analyzer = AudioAnalyzer('song.mp3')
features = analyzer.analyze_full()

<<<<<<< HEAD
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
=======
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
>>>>>>> runner
