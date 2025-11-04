"""
Example script demonstrating audio analysis and level generation.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from audio_analyzer import AudioAnalyzer, LevelDataMapper


def analyze_and_generate_level(audio_path, output_path=None, difficulty='medium'):
    """
    Full pipeline: analyze audio and generate level data.
    
    Args:
        audio_path (str): Path to audio file
        output_path (str): Path to save JSON output (optional)
        difficulty (str): Game difficulty level
    """
    print(f"Analyzing audio file: {audio_path}")
    print("-" * 50)
    
    # Step 1: Analyze audio
    analyzer = AudioAnalyzer(audio_path)
    features = analyzer.analyze_full()
    
    print(f"Duration: {features['duration']:.2f} seconds")
    print(f"BPM: {features['bpm']:.1f}")
    print(f"Number of beats detected: {len(features['beats'])}")
    print("-" * 50)
    
    # Step 2: Generate level data
    mapper = LevelDataMapper(features)
    level_data = mapper.generate_level_data(difficulty=difficulty)
    
    print(f"Level data generated:")
    print(f"  - Obstacles: {len(level_data['obstacles'])}")
    print(f"  - Speed changes: {len(level_data['speed_changes'])}")
    print(f"  - Collectibles: {len(level_data['collectibles'])}")
    print(f"  - Background intensity points: {len(level_data['background_intensity'])}")
    print("-" * 50)
    
    # Step 3: Save to file if requested
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(level_data, f, indent=2)
        print(f"Level data saved to: {output_path}")
    else:
        # Print sample data
        print("\nSample obstacles (first 5):")
        for obs in level_data['obstacles'][:5]:
            print(f"  Time: {obs['time']:.2f}s, Type: {obs['type']}, Lane: {obs['lane']}")
        
        print("\nSample speed changes (first 3):")
        for speed in level_data['speed_changes'][:3]:
            print(f"  Time: {speed['time']:.2f}s, Speed: {speed['speed']:.2f}x")
    
    return level_data


if __name__ == '__main__':
    # Example usage
    if len(sys.argv) < 2:
        print("Usage: python example_usage.py <audio_file> [output_json] [difficulty]")
        print("\nExample:")
        print("  python example_usage.py song.mp3")
        print("  python example_usage.py song.mp3 level_data.json hard")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    difficulty = sys.argv[3] if len(sys.argv) > 3 else 'medium'
    
    try:
        analyze_and_generate_level(audio_file, output_file, difficulty)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
