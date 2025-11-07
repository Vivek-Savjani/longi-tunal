import pygame,random,threading,asyncio,websockets,json
from multiprocessing import Process, Queue
from queue import Empty
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
    QUIT,
)
screen_width, screen_height = 800, 600
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surface = pygame.Surface((50, 50))
        self.surface.fill((255, 0, 0))
        self.rect = self.surface.get_rect()
    def update(self,commands, pressed_keys):
        try:
            request = commands.get_nowait()
            movement = request["command"]
            print("Got from queue:", repr(request), type(request))
            print(movement)
            match  movement:
                case "up":
                    self.rect.move_ip(0, -8)
                case "down":
                    self.rect.move_ip(0, 8)
                case "left":
                    self.rect.move_ip(-8, 0)
                case "right":
                    self.rect.move_ip(8, 0)
        except Exception:
            pass
        match pressed_keys:
            case _ if pressed_keys[K_UP]:
                self.rect.move_ip(0, -8)
            case _ if pressed_keys[K_DOWN]:
                self.rect.move_ip(0, 8)
            case _ if pressed_keys[K_LEFT]:
                self.rect.move_ip(-8, 0)
            case _ if pressed_keys[K_RIGHT]:
                self.rect.move_ip(8, 0)
                
        match self.rect:
            case _ if self.rect.left < 0:
                self.rect.left = 0
            case _ if self.rect.right > screen_width:
                self.rect.right = 800
            case _ if self.rect.top < 0:
                self.rect.top = 0
            case _ if self.rect.bottom > screen_height:
                self.rect.bottom = 600
class Enemy(pygame.sprite.Sprite):
    def __init__(self,speed):
        super(Enemy, self).__init__()
        self.surface = pygame.Surface((30, 30))
        self.surface.fill((0, 0, 255))
        self.rect = self.surface.get_rect(
            center=(
                screen_width,
                random.randint(0, screen_height),)
        )
        self.speed = - speed     
    def update(self):
        self.rect.move_ip(self.speed, 0)
        if self.rect.right < 0:
            self.kill()
            
command = Queue()
async def controller_server(websocket,):
    global command
    async for message in websocket:
        print("Received:", message)
        data = json.loads(message)  # convert string to dict
        command.put(data)

async def start_server():
    async with websockets.serve(controller_server, "0.0.0.0", 8765) as server:
       await server.serve_forever()

# Run the WebSocket server in background thread
threading.Thread(target=lambda: asyncio.run(start_server()), daemon=True).start()

def get_background_color(amplitude, bpm):
    """Calculate background color based on music data"""
    try:
        amp = float(amplitude)
        tempo = float(bpm)
        
        # Map amplitude to intensity
        intensity = min(amp / 100.0, 1.0) * 0.6  # Scale down for pastel
        
        # Map BPM to color (60-180 BPM range)
        if tempo < 90:
            # Soft Purple/Lavender (slow)
            r = int(160 + intensity * 60)
            g = int(140 + intensity * 50)
            b = int(190 + intensity * 50)
        elif tempo < 120:
            # Soft Blue (medium)
            r = int(130 + intensity * 50)
            g = int(160 + intensity * 60)
            b = int(210 + intensity * 40)
        elif tempo < 150:
            # Soft Green (fast)
            r = int(150 + intensity * 50)
            g = int(190 + intensity * 50)
            b = int(160 + intensity * 40)
        else:
            # Soft Pink/Coral (very fast)
            r = int(210 + intensity * 40)
            g = int(150 + intensity * 50)
            b = int(150 + intensity * 50)
        
        return (r, g, b)
    except:
        return (180, 180, 200)  # default soft blue
  
class BackgroundParticle:
    """Floating particle for background effect"""
    def __init__(self):
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        self.size = random.randint(2, 6)
        self.speed_x = random.uniform(-0.5, 0.5)
        self.speed_y = random.uniform(-0.5, 0.5)
        self.alpha = random.randint(30, 100)
        self.pulse_speed = random.uniform(0.02, 0.05)
        self.pulse_offset = random.uniform(0, 6.28)  # 2*pi
    
    def update(self, intensity):
        self.x += self.speed_x * (1 + intensity)
        self.y += self.speed_y * (1 + intensity)
        
        # Wrap around screen
        if self.x < 0: self.x = screen_width
        if self.x > screen_width: self.x = 0
        if self.y < 0: self.y = screen_height
        if self.y > screen_height: self.y = 0
        
        self.pulse_offset += self.pulse_speed
    
    def draw(self, surface, color):
        import math
        pulse = (math.sin(self.pulse_offset) + 1) / 2  # 0 to 1
        alpha = int(self.alpha * pulse)
        size = int(self.size * (0.5 + pulse * 0.5))
        
        s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, alpha), (size, size), size)
        surface.blit(s, (int(self.x - size), int(self.y - size)))

def show_menu(screen):
    """Display modern start menu"""
    screen_width, screen_height = 800, 600
    clock = pygame.time.Clock()
    
    # Menu animation
    menu_alpha = 0
    pulse_offset = 0
    
    waiting = True
    while waiting:
        import math
        pulse_offset += 0.05
        pulse = (math.sin(pulse_offset) + 1) / 2  # 0 to 1
        
        # Fade in effect
        menu_alpha = min(255, menu_alpha + 5)
        
        # Gradient background
        for y in range(screen_height):
            color_value = int(100 + (y / screen_height) * 100)
            pygame.draw.line(screen, (color_value - 50, color_value - 30, color_value + 50), 
                           (0, y), (screen_width, y))
        
        # Animated particles in background
        for i in range(20):
            x = (i * 40 + pulse_offset * 20) % screen_width
            y = (i * 30 + pulse_offset * 15) % screen_height
            size = int(3 + pulse * 2)
            s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, 80), (size, size), size)
            screen.blit(s, (int(x), int(y)))
        
        # Main box
        box_width, box_height = 600, 400
        box_x = (screen_width - box_width) // 2
        box_y = (screen_height - box_height) // 2
        
        # Outer glow with pulse
        for i in range(3):
            glow_alpha = int((60 - i * 15) * (0.7 + pulse * 0.3))
            glow_surf = pygame.Surface((box_width + i*10, box_height + i*10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (100, 150, 255, glow_alpha), 
                           (0, 0, box_width + i*10, box_height + i*10), border_radius=25)
            screen.blit(glow_surf, (box_x - i*5, box_y - i*5))
        
        # Main menu box
        box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        box_surf.set_alpha(menu_alpha)
        pygame.draw.rect(box_surf, (25, 30, 45, 240), (0, 0, box_width, box_height), border_radius=25)
        pygame.draw.rect(box_surf, (100, 150, 255), (0, 0, box_width, box_height), 4, border_radius=25)
        screen.blit(box_surf, (box_x, box_y))
        
        # Title with glow
        font_title = pygame.font.Font(None, 100)
        font_subtitle = pygame.font.Font(None, 50)
        font_instruction = pygame.font.Font(None, 35)
        
        title_color = (100 + int(pulse * 100), 150 + int(pulse * 50), 255)
        title = font_title.render("LONGI-TUNAL", True, title_color)
        title.set_alpha(menu_alpha)
        
        subtitle = font_subtitle.render("Music Reactive Runner", True, (200, 200, 220))
        subtitle.set_alpha(menu_alpha)
        
        # Pulsing instruction
        instruction_alpha = int(menu_alpha * (0.5 + pulse * 0.5))
        instruction = font_instruction.render("Press SPACE to Start", True, (150, 200, 255))
        instruction.set_alpha(instruction_alpha)
        
        controls1 = font_instruction.render("Controls: Arrow Keys / WASD", True, (180, 180, 200))
        controls1.set_alpha(menu_alpha)
        
        controls2 = font_instruction.render("Avoid the obstacles!", True, (180, 180, 200))
        controls2.set_alpha(menu_alpha)
        
        # Position text
        title_rect = title.get_rect(center=(screen_width // 2, screen_height // 2 - 100))
        subtitle_rect = subtitle.get_rect(center=(screen_width // 2, screen_height // 2 - 30))
        instruction_rect = instruction.get_rect(center=(screen_width // 2, screen_height // 2 + 60))
        controls1_rect = controls1.get_rect(center=(screen_width // 2, screen_height // 2 + 120))
        controls2_rect = controls2.get_rect(center=(screen_width // 2, screen_height // 2 + 160))
        
        screen.blit(title, title_rect)
        screen.blit(subtitle, subtitle_rect)
        screen.blit(instruction, instruction_rect)
        screen.blit(controls1, controls1_rect)
        screen.blit(controls2, controls2_rect)
        
        pygame.display.flip()
        clock.tick(60)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    return True
                elif event.key == K_ESCAPE:
                    return False
    
    return False

def game(music_data):      
    pygame.init()
    pygame.mixer.init()  # Explicitly initialize mixer
    clock = pygame.time.Clock()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    
    # Show menu first
    if not show_menu(screen):
        return  # Exit if menu returns False
    
    player = Player()
    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player,enemies)
    running = True
    global command
    
    # Background color state
    current_bg = (180, 180, 200)
    target_bg = (180, 180, 200)
    
    # Create background particles
    particles = [BackgroundParticle() for _ in range(50)]
    
    # Wave animation
    wave_offset = 0
    current_intensity = 0
    
    # Score system
    score = 0
    current_bpm = 0
    game_time = 0

    while running:
        dt = clock.tick(120) / 1000.0  # Delta time in seconds
        game_time += dt
        
        # Calculate score: BPM / Frame Rate
        actual_fps = clock.get_fps()
        if actual_fps > 0 and current_bpm > 0:
            score = int((current_bpm / actual_fps) * 1000)
        for event in pygame.event.get():
            if ((event.type == KEYDOWN) and (event.key == K_ESCAPE)) or (event.type == pygame.QUIT):
                pygame.quit()
                running = False
        player.update(command,pygame.key.get_pressed())
        enemies.update()
        
        # Smooth background transition
        current_bg = tuple(
            int(current_bg[i] + (target_bg[i] - current_bg[i]) * 0.1)
            for i in range(3)
        )
        screen.fill(current_bg)
        
        # Draw animated waves at bottom (speed based on music intensity)
        import math
        wave_speed = 0.02 + (current_intensity * 0.08)  # Faster with louder music
        wave_offset += wave_speed
        wave_amplitude = 10 + (current_intensity * 20)  # Higher waves with louder music
        wave_color = tuple(max(0, c - 30) for c in current_bg)  # Darker shade
        
        num_waves = int(2 + current_intensity * 3)  # More waves with louder music
        for i in range(num_waves):
            y_base = screen_height - 100 + i * 30
            points = []
            for x in range(0, screen_width + 10, 10):
                y = y_base + math.sin((x / 50) + wave_offset + i) * wave_amplitude
                points.append((x, y))
            points.append((screen_width, screen_height))
            points.append((0, screen_height))
            if len(points) > 2:
                s = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                wave_alpha = int((30 + i * 20) * (0.5 + current_intensity * 0.5))
                pygame.draw.polygon(s, (*wave_color, wave_alpha), points)
                screen.blit(s, (0, 0))
        
        # Update and draw particles (more active with music)
        num_active_particles = int(30 + current_intensity * 20)  # Show more particles when loud
        for idx, particle in enumerate(particles[:num_active_particles]):
            particle.update(current_intensity)
            # Particle color based on background
            particle_color = tuple(min(255, c + 50) for c in current_bg)
            particle.draw(screen, particle_color)
        
        # Draw radial glow in center (pulsing with music)
        glow_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        glow_intensity = int(30 + current_intensity * 120)  # Stronger glow with louder music
        glow_size = 1.0 + (current_intensity * 0.8)  # Bigger glow with louder music
        for i in range(5, 0, -1):
            radius = int(150 * (i / 5) * glow_size)
            alpha = int(glow_intensity / i)
            pygame.draw.circle(glow_surface, (*current_bg, alpha), 
                             (screen_width // 2, screen_height // 2), radius)
        screen.blit(glow_surface, (0, 0))
        
        # Draw score UI (only Score and Time)
        font_large = pygame.font.Font(None, 48)
        
        score_text = font_large.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))
        
        time_text = font_large.render(f"Time: {game_time:.1f}s", True, (0, 0, 0))
        screen.blit(time_text, (10, 60))
        
        pygame.draw.circle(screen, (0, 0, 0), (750, 300), 15)
        for entity in all_sprites:
            screen.blit(entity.surface,entity.rect)
        
        # Check collision
        if pygame.sprite.spritecollideany(player, enemies):
            # Modern Game Over screen
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))  # Dark semi-transparent
            screen.blit(overlay, (0, 0))
            
            # Draw animated box
            box_width, box_height = 500, 350
            box_x = (screen_width - box_width) // 2
            box_y = (screen_height - box_height) // 2
            
            # Outer glow
            for i in range(3):
                glow_surf = pygame.Surface((box_width + i*10, box_height + i*10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (255, 70, 70, 40-i*10), 
                               (0, 0, box_width + i*10, box_height + i*10), border_radius=20)
                screen.blit(glow_surf, (box_x - i*5, box_y - i*5))
            
            # Main box
            box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            pygame.draw.rect(box_surf, (30, 30, 40, 250), (0, 0, box_width, box_height), border_radius=20)
            pygame.draw.rect(box_surf, (255, 70, 70), (0, 0, box_width, box_height), 3, border_radius=20)
            screen.blit(box_surf, (box_x, box_y))
            
            # Text
            font_title = pygame.font.Font(None, 90)
            font_subtitle = pygame.font.Font(None, 45)
            font_score = pygame.font.Font(None, 55)
            font_small = pygame.font.Font(None, 35)
            
            title = font_title.render("GAME OVER", True, (255, 90, 90))
            subtitle = font_subtitle.render("You Hit an Obstacle!", True, (220, 220, 220))
            final_score = font_score.render(f"Final Score: {score}", True, (100, 200, 255))
            instruction = font_small.render("Press ESC to Exit", True, (180, 180, 180))
            
            title_rect = title.get_rect(center=(screen_width // 2, screen_height // 2 - 80))
            subtitle_rect = subtitle.get_rect(center=(screen_width // 2, screen_height // 2 - 10))
            score_rect = final_score.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
            instruction_rect = instruction.get_rect(center=(screen_width // 2, screen_height // 2 + 110))
            
            screen.blit(title, title_rect)
            screen.blit(subtitle, subtitle_rect)
            screen.blit(final_score, score_rect)
            screen.blit(instruction, instruction_rect)
            
            pygame.display.flip()
            
            # Wait for ESC to exit
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        running = False
                    elif event.type == KEYDOWN and event.key == K_ESCAPE:
                        waiting = False
                        running = False
                        pygame.quit()
                        return  # Exit the function completely
            
        pygame.display.flip()
        try:
            md = music_data.get_nowait()
            
            # Update intensity for effects
            current_intensity = min(float(md['amplitude']) / 100.0, 1.0)
            
            # Update BPM for score calculation
            current_bpm = float(md['bpm'])
            
            # Update target background color
            target_bg = get_background_color(md['amplitude'], md['bpm'])
            
            if random.randint(0, 100) < int(float(md['amplitude'])):
                speed = (float(md['bpm'])/25) + 1
                ##print("Spawning enemy with speed:", speed)
                new_enemy = Enemy(speed)
                enemies.add(new_enemy)
                all_sprites.add(new_enemy)
        except Empty:
            ##print("Empty Queue")
            pass
        except Exception as e:
            print(f"analysis failed {e}")

def get_music_data(music_data):
    import sounddevice as sd
    import numpy as np
    from collections import deque
    import time
    BASS_LOW = 20
    BASS_HIGH = 150
    WINDOW_SEC = 5
    THRESHOLD_MULT = 1.5 
    beat_times = deque()
    prev_bass_amp = 0 
    SR = 44100
    BLOCK_SIZE = 1024  # Number of frames per read

    # Find VB Cable device
    devices = sd.query_devices()
    device_index = None
    for i, d in enumerate(devices):
        if "cable output" in d["name"].lower():
            print("Found VB Cable device:", d["name"])
            device_index = i
            break

    if device_index is None:
        print("VB Cable not found, using default input device")
        device_index = None

    def get_amplitude(indata):
        mono = np.mean(indata, axis=1)
        amplitude = np.sqrt(np.mean(mono ** 2)) * 100
        return f"{amplitude:.2f}"

    def get_current_bpm(indata):
        nonlocal prev_bass_amp, beat_times
        mono = np.mean(indata, axis=1)

        spectrum = np.fft.rfft(mono)
        freqs = np.fft.rfftfreq(len(mono), 1/SR)
        bass_range = (freqs >= BASS_LOW) & (freqs <= BASS_HIGH)
        bass_amp = np.mean(np.abs(spectrum[bass_range]))

        now = time.time()

        if bass_amp > prev_bass_amp * THRESHOLD_MULT and bass_amp > 0.2:
            if len(beat_times) == 0 or now - beat_times[-1] > 0.2:  # avoid double-counting
                beat_times.append(now)

        prev_bass_amp = bass_amp

        while beat_times and now - beat_times[0] > WINDOW_SEC:
            beat_times.popleft()

        if len(beat_times) > 1:
            intervals = np.diff(beat_times)
            bpm = 60 / np.mean(intervals)
        else:
            bpm = 0

        return f"{bpm:.0f}"

    with sd.InputStream(channels=2, samplerate=SR, blocksize=BLOCK_SIZE, device=device_index) as stream:
        while True:
            indata, _ = stream.read(BLOCK_SIZE)
            amplitude = get_amplitude(indata)
            bpm = get_current_bpm(indata)
            music_data.put({'amplitude': amplitude, 'bpm': bpm})

if __name__ == "__main__":
    music_data = Queue()
    p1 = Process(target=get_music_data, args=(music_data,))
    p1.start()
    game(music_data)
    p1.join()