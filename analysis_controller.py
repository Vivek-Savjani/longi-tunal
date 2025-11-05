import json
import os
import sys

# IMPORTANT: This line tells the controller where to find your files in the subfolder.
try:
    from analysis_package.analyzer import AudioAnalyzer
    from analysis_package.mapper import LevelDataMapper
except ImportError as e:
    print(f"\nFATAL IMPORT ERROR: Could not find analyzer/mapper. Did you forget __init__.py?", file=sys.stderr)
    sys.exit(1)

# --- CONFIGURATION (YOUR INPUTS) ---
# 🚨🚨🚨 Change this file name to your actual song! 🚨🚨🚨
INPUT_AUDIO_FILE = "test_song.mp3" 
JSON_OUTPUT_FILE = 'game_audio_data.json'
DEFAULT_DIFFICULTY = 'medium'

def run_full_analysis_and_save():
    """ Runs the full music-to-level pipeline. """
    
    if not os.path.exists(INPUT_AUDIO_FILE):
        print(f"\nERROR: Input audio file '{INPUT_AUDIO_FILE}' not found.", file=sys.stderr)
        print("Please place your song file in this same folder.")
        sys.exit(1)

    try:
        # 1. RUN AUDIO ANALYSIS: Creates the analyzer object and gets all the math data.
        print(f"Starting analysis for {INPUT_AUDIO_FILE}...")
        analyzer = AudioAnalyzer(audio_path=INPUT_AUDIO_FILE)
        raw_audio_features = analyzer.analyze_full() 
        print("Audio features extracted.")

        # 2. RUN LEVEL MAPPING: Takes the math data and turns it into game objects.
        print(f"Generating level data with difficulty: {DEFAULT_DIFFICULTY}...")
        mapper = LevelDataMapper(audio_features=raw_audio_features)
        final_level_data = mapper.generate_level_data(difficulty=DEFAULT_DIFFICULTY) 
        
        # 3. SAVE FINAL DATA: Writes the game data to the JSON file.
        with open(JSON_OUTPUT_FILE, 'w') as f:
            json.dump(final_level_data, f, indent=2)
        
        print("\n--- LEVEL GENERATION SUCCESS! ---")
        print(f"Data saved to '{JSON_OUTPUT_FILE}' for the game runner.")

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    run_full_analysis_and_save()
