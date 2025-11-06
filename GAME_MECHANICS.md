"""
GAME MECHANICS - Longi-Tunal Music Runner
==========================================

## Core Gameplay Loop

The game continuously monitors elapsed time and spawns game elements 
based on timestamps from the pre-analyzed level data JSON file.

### 1. Music-Synced Obstacle Spawning

**Mechanism:**
- Obstacles are spawned when `game_time >= obstacle['time']`
- Each obstacle is positioned in one of 3 lanes (0, 1, or 2)
- Obstacle size varies based on music intensity:
  - `small`: 30x30px (low intensity < 0.3)
  - `medium`: 40x40px (medium intensity 0.3-0.7)
  - `large`: 50x50px (high intensity > 0.7)

**Technical Implementation:**
```python
while obstacle_index < len(obstacles) and obstacles[obstacle_index]['time'] <= game_time:
    spawn_obstacle(obstacles[obstacle_index])
    obstacle_index += 1
```

### 2. Dynamic Speed System

**Mechanism:**
- Base game speed is 1.0x
- Speed multiplier ranges from 0.7x to 1.3x based on music energy
- Speed changes are interpolated from RMS (Root Mean Square) audio energy
- Changes occur gradually at predefined timestamps

**Formula:**
```
speed = base_speed * (0.7 + intensity * 0.6)
where intensity is normalized RMS energy (0-1)
```

### 3. Collectible Generation

**Mechanism:**
- Coins spawn at timestamps between beat markers
- Placed strategically to reward risk-taking and lane changes
- 40% spawn probability per beat interval
- Positioned in random lanes to encourage movement

**Algorithm:**
```python
for i in range(len(beats) - 1):
    coin_time = (beats[i] + beats[i+1]) / 2  # Midpoint
    if random() < 0.4:
        spawn_coin(coin_time, random_lane())
```

### 4. Background Visual Feedback

**Mechanism:**
- Background color intensity mapped to onset strength envelope
- Samples taken every ~0.23 seconds from audio analysis
- Color interpolation formula:
  ```
  RGB = (base_value * (1 - intensity * 0.3), 
         base_value * (1 - intensity * 0.3), 
         255)
  ```
- Creates a pulsing blue gradient effect synchronized with music peaks

### 5. Lane-Based Movement System

**Player Mechanics:**
- 3-lane discrete positioning (not continuous horizontal movement)
- Instant lane switching on input
- Smooth visual transition with interpolation
- Lane boundaries enforced (cannot move beyond lanes 0-2)

**Movement Logic:**
```python
target_x = lane_width * current_lane + lane_width / 2
if player.x != target_x:
    player.x += sign(target_x - player.x) * transition_speed
```

### 6. Collision Detection

**Two collision types:**

a) **Obstacle Collision (Failure Condition)**
   - Rectangle-based collision detection
   - Game over on any obstacle hit
   - No health system - one-hit failure

b) **Collectible Collision (Score System)**
   - Rectangle intersection check
   - Collectible removed on collision
   - Score incremented (+10 points per coin)

### 7. Timing Synchronization

**Delta Time System:**
```python
dt = clock.tick(FPS) / 1000.0  # Convert to seconds
game_time += dt
```

- Fixed 60 FPS target for consistent gameplay
- Time accumulation independent of frame rate
- All spawning decisions based on accumulated `game_time`
- Ensures music sync regardless of performance variations

### 8. Difficulty Scaling

**Three difficulty modes affect obstacle density:**

- **Easy**: 30% spawn chance per beat
- **Medium**: 60% spawn chance per beat  
- **Hard**: 90% spawn chance per beat

Spawn chance is further modulated by music intensity:
```python
if random() < (difficulty_multiplier * intensity):
    spawn_obstacle()
```

## Data Flow Architecture

```
Audio File → AudioAnalyzer → Features (BPM, beats, intensity)
                ↓
         LevelDataMapper → level_data.json
                ↓
         MusicRunner.load() → Game State
                ↓
    Game Loop (60 FPS) → Continuous time checking
                ↓
    Spawn System → Create sprites at correct timestamps
                ↓
    Update Loop → Move sprites, check collisions
                ↓
    Render → Draw to screen with visual effects
```

## Performance Optimizations

1. **Indexed Scanning**: Each entity type (obstacles, collectibles, speed changes) 
   maintains its own index to avoid re-scanning entire arrays

2. **Sprite Culling**: Objects automatically removed when off-screen

3. **Pre-computed Data**: All timing decisions made during audio analysis phase,
   not during gameplay

4. **Fixed Update Rate**: 60 FPS cap prevents CPU overuse while maintaining smoothness

## Technical Specifications

- **Screen Resolution**: 800x600 pixels
- **Lane System**: 3 lanes, each 266.67px wide
- **Frame Rate**: 60 FPS (capped)
- **Coordinate System**: Origin at top-left
- **Sprite Movement**: Downward scrolling (positive Y direction)
- **Collision Tolerance**: Pixel-perfect rectangle intersection

## Future Enhancement Possibilities

1. **Power-ups**: Special collectibles with temporary effects
2. **Combo System**: Score multipliers for consecutive collections
3. **Visual Effects**: Particle systems on beat hits
4. **Multi-track Support**: Different instrument layers affecting different gameplay elements
5. **Procedural Background**: Animated visualizations based on frequency spectrum
6. **Leaderboard**: Score persistence and comparison system
