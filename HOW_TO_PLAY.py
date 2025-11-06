"""
Quick Start Guide for Music Runner
"""

# How to Play:
# 1. Generate level data from music:
#    python examples/example_usage.py "your_song.mp3" level_data.json medium

# 2. Run the game:
#    python music_runner.py

# Controls:
# - Left Arrow / A: Move left
# - Right Arrow / D: Move right
# - ESC: Quit

# Game Features:
# ✅ Music-synced obstacles (appear on beats)
# ✅ Dynamic speed changes (follows music energy)
# ✅ Collectibles (coins between beats)
# ✅ Background color intensity (visual feedback)
# ✅ Score tracking

print("""
🎮 LONGI-TUNAL MUSIC RUNNER 🎵
================================

📋 SETUP:
1. Install requirements:
   pip install -r requirements.txt

2. Generate level from music:
   python examples/example_usage.py "song.mp3" level_data.json medium

3. Run the game:
   python music_runner.py

🎯 CONTROLS:
   ← / A  : Move Left
   → / D  : Move Right
   ESC    : Quit

🎮 GAMEPLAY:
   - Avoid blue obstacles (spawned on beats)
   - Collect yellow coins (spawned between beats)
   - Speed changes with music intensity
   - Background pulses with music

Good luck! 🚀
""")
