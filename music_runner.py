"""
Music-driven Runner Game
Integrates audio analysis with pygame runner mechanics
"""

import pygame
import json
import random
from pathlib import Path

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
LANES = 3
LANE_WIDTH = SCREEN_WIDTH // LANES

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
BLUE = (50, 100, 200)
GREEN = (50, 200, 50)


class Player(pygame.sprite.Sprite):
    """Player character that moves between lanes"""
    
    def __init__(self):
        super().__init__()
        self.surface = pygame.Surface((40, 40))
        self.surface.fill(RED)
        self.lane = 1  # Start in middle lane (0, 1, or 2)
        self.rect = self.surface.get_rect()
        self.rect.centerx = LANE_WIDTH * self.lane + LANE_WIDTH // 2
        self.rect.centery = SCREEN_HEIGHT - 100
        self.speed = 5
        
    def move_left(self):
        if self.lane > 0:
            self.lane -= 1
            self.update_position()
    
    def move_right(self):
        if self.lane < LANES - 1:
            self.lane += 1
            self.update_position()
    
    def update_position(self):
        """Smoothly move to target lane"""
        target_x = LANE_WIDTH * self.lane + LANE_WIDTH // 2
        if abs(self.rect.centerx - target_x) > 2:
            if self.rect.centerx < target_x:
                self.rect.centerx += self.speed
            elif self.rect.centerx > target_x:
                self.rect.centerx -= self.speed
        else:
            self.rect.centerx = target_x
    
    def update(self):
        self.update_position()


class Obstacle(pygame.sprite.Sprite):
    """Obstacle spawned from level data"""
    
    def __init__(self, lane, obstacle_type, spawn_y=-50):
        super().__init__()
        # Size based on type
        sizes = {'small': 30, 'medium': 40, 'large': 50}
        size = sizes.get(obstacle_type, 40)
        
        self.surface = pygame.Surface((size, size))
        self.surface.fill(BLUE)
        self.rect = self.surface.get_rect()
        self.rect.centerx = LANE_WIDTH * lane + LANE_WIDTH // 2
        self.rect.y = spawn_y
        self.speed = 5
        self.type = obstacle_type
        
    def update(self, game_speed_multiplier=1.0):
        self.rect.y += self.speed * game_speed_multiplier
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()





class MusicRunner:
    """Main game class that integrates music with gameplay"""
    
    def __init__(self, level_data_path, music_path=None):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Longi-Tunal - Music Runner")
        self.clock = pygame.time.Clock()
        
        # Load level data
        with open(level_data_path, 'r') as f:
            self.level_data = json.load(f)
        
        # Game state
        self.running = True
        self.score = 0
        self.game_time = 0.0
        self.base_speed = 1.0
        self.current_speed = self.base_speed
        
        # Score calculation
        self.current_bpm = self.level_data.get('bpm', 100)  # Get BPM from level data
        self.frame_count = 0
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        
        # Player
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # Level data indices
        self.obstacle_index = 0
        self.speed_change_index = 0
        
        # Music
        self.music_path = music_path
        if music_path and Path(music_path).exists():
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play()
        
        # Font for UI
        self.font = pygame.font.Font(None, 36)
        
    def get_background_color(self):
        """Get background color based on music intensity"""
        bg_data = self.level_data.get('background_intensity', [])
        
        # Find closest intensity point
        for i, point in enumerate(bg_data):
            if point['time'] >= self.game_time:
                intensity = point['intensity']
                # Interpolate color based on intensity
                color_value = int(255 * (1 - intensity * 0.3))
                return (color_value, color_value, 255)
        
        return (220, 220, 255)  # Default light blue
    
    def spawn_obstacles(self):
        """Spawn obstacles based on current game time"""
        obstacles_data = self.level_data.get('obstacles', [])
        
        while (self.obstacle_index < len(obstacles_data) and 
               obstacles_data[self.obstacle_index]['time'] <= self.game_time):
            
            obs_data = obstacles_data[self.obstacle_index]
            obstacle = Obstacle(
                lane=obs_data['lane'],
                obstacle_type=obs_data['type']
            )
            self.obstacles.add(obstacle)
            self.all_sprites.add(obstacle)
            self.obstacle_index += 1
    

    
    def update_speed(self):
        """Update game speed based on music"""
        speed_changes = self.level_data.get('speed_changes', [])
        
        while (self.speed_change_index < len(speed_changes) and 
               speed_changes[self.speed_change_index]['time'] <= self.game_time):
            
            self.current_speed = speed_changes[self.speed_change_index]['speed']
            self.speed_change_index += 1
    
    def handle_events(self):
        """Handle keyboard input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    self.player.move_left()
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    self.player.move_right()
    
    def check_collisions(self):
        """Check for collisions with obstacles"""
        # Obstacles
        hit = pygame.sprite.spritecollide(self.player, self.obstacles, False)
        if hit:
            self.running = False
            print(f"Game Over! Final Score: {self.score}")
    
    def draw_ui(self):
        """Draw score and other UI elements"""
        # Score with formula display
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        # Score formula
        actual_fps = self.clock.get_fps()
        formula_font = pygame.font.Font(None, 24)
        formula_text = formula_font.render(f"({self.current_bpm:.0f} BPM / {actual_fps:.1f} FPS) x 1000", True, (100, 100, 100))
        self.screen.blit(formula_text, (10, 45))
        
        # Time
        time_text = self.font.render(f"Time: {self.game_time:.1f}s", True, BLACK)
        self.screen.blit(time_text, (10, 80))
        
        # Speed
        speed_text = self.font.render(f"Speed: {self.current_speed:.2f}x", True, BLACK)
        self.screen.blit(speed_text, (SCREEN_WIDTH - 200, 10))
        
        # BPM indicator
        bpm_text = self.font.render(f"BPM: {self.current_bpm:.0f}", True, BLACK)
        self.screen.blit(bpm_text, (SCREEN_WIDTH - 200, 50))
        
        # Draw lane dividers
        for i in range(1, LANES):
            x = LANE_WIDTH * i
            pygame.draw.line(self.screen, (200, 200, 200), (x, 0), (x, SCREEN_HEIGHT), 2)
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Delta time
            dt = self.clock.tick(FPS) / 1000.0
            self.game_time += dt
            self.frame_count += 1
            
            # Calculate score: BPM / Frame Rate
            actual_fps = self.clock.get_fps()
            if actual_fps > 0:
                self.score = int((self.current_bpm / actual_fps) * 1000)  # Multiply by 1000 for better readability
            
            # Handle events
            self.handle_events()
            
            # Update game speed based on music
            self.update_speed()
            
            # Spawn entities
            self.spawn_obstacles()
            
            # Update sprites
            self.player.update()
            self.obstacles.update(self.current_speed)
            
            # Check collisions
            self.check_collisions()
            
            # Draw everything
            bg_color = self.get_background_color()
            self.screen.fill(bg_color)
            
            # Draw all sprites
            for sprite in self.all_sprites:
                self.screen.blit(sprite.surface, sprite.rect)
            
            # Draw UI
            self.draw_ui()
            
            # Update display
            pygame.display.flip()
        
        pygame.quit()


if __name__ == "__main__":
    # Example usage
    level_data_path = "level_data.json"
    music_path = "DEAF KEV - Invincible [NCS Release].mp3"  # Optional
    
    # Check if files exist
    if not Path(level_data_path).exists():
        print(f"Error: {level_data_path} not found!")
        print("Please generate level data first using the audio analyzer.")
        exit(1)
    
    # Start game
    game = MusicRunner(level_data_path, music_path)
    game.run()
