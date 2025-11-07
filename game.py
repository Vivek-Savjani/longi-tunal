import pygame,threading,asyncio,websockets,json,random,math,time,numpy as np
from multiprocessing import Process, Queue
from queue import Queue as queue, Empty
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)
screen_width, screen_height = 800, 600
lanes = 3
lane_height = screen_height / lanes
lane_centres = [int((i * lane_height) + (lane_height / 2)) for i in range(lanes)]

score = 0
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        points = [(0, 0), (50, 25), (0, 50)]
        pygame.draw.polygon(self.surface, theme['player'], points)
        self.current_lane = lanes // 2
        self.rect = self.surface.get_rect(
            center=(100, lane_centres[self.current_lane])
            )
        self.key_pressed = False
        
    def update(self,commands, pressed_keys):
        try:
            request = commands.get_nowait()
            movement = request["command"]
            print("Got from queue:", repr(request), type(request))
            print(movement)
            if movement == "up" and self.current_lane > 0:
                self.current_lane -= 1
                self.key_pressed = True
            elif movement == "down" and self.current_lane < lanes - 1:
                self.current_lane += 1
                self.key_pressed = True
        except Exception:
            pass
        if self.key_pressed == False: 
            if pressed_keys[K_UP] and self.current_lane > 0:
                    self.current_lane -= 1
                    self.key_pressed = True
            elif pressed_keys[K_DOWN] and self.current_lane < lanes - 1:
                    self.current_lane += 1
                    self.key_pressed = True
        if not (pressed_keys[K_UP] or pressed_keys[K_DOWN]):
            self.key_pressed = False
        match self.rect:
            case _ if self.rect.left < 0:
                    self.rect.left = 0
            case _ if self.rect.right > screen_width:
                    self.rect.right = 800
            case _ if self.rect.top < 0:
                    self.rect.top = 0
            case _ if self.rect.bottom > screen_height:
                    self.rect.bottom = 600
        self.rect.center = (100,lane_centres[self.current_lane])
    
class Enemy(pygame.sprite.Sprite):
    def __init__(self,speed,amplitude,pitch):
        super(Enemy, self).__init__()
        if pitch <= 0.33:
            size = (80,lane_height / 2 )
            colour = theme["enemy_low"]
        elif pitch <= 0.66:
            size = (160,lane_height / 2 )
            colour = theme["enemy_mid"]
        else:
            size = (240,lane_height / 2 )
            colour = theme["enemy_high"]
        self.amplitude = amplitude
        lane_index =lanes - 1 - min(int(amplitude / screen_height * lanes), lanes - 1)
        self.speed = - speed
        self.surface = pygame.Surface(size, pygame.SRCALPHA)
        shape = pygame.Rect((0, 0), size)
        pygame.draw.rect(self.surface, colour,shape, border_radius=10)
        self.rect = self.surface.get_rect(
            center=(
                screen_width,
                lane_centres[lane_index])
        )
         
    def update(self):
        self.rect.move_ip(self.speed, 0)
        if self.rect.right < 0:
            self.kill()
        if self.speed == 0: self.kill()
class background:
    def __init__(self,screen,theme):
        self.screen = screen
        self.theme = theme
        self.screen_width, self.screen_height = screen.get_size()
        self.center_x, self.center_y = self.screen_width // 2, self.screen_width // 2
        self.beat_flash_timer = 0
    def on_beat(self):
        self.beat_flash_timer = 5
    def update(self):
        if self.beat_flash_timer > 0:
            self.beat_flash_timer -= 1
    def draw(self):
        if self.beat_flash_timer > 0:
            self.screen.fill(self.theme["bg_flash"])
        else:
            self.screen.fill(self.theme["bg"])
class synthwave_bg(background):
    def __init__(self,screen,theme):
        super().__init__(screen,theme)
        self.sun_y = int(self.screen_height * 0.95)
        
        self.sun_core_r = 145
        self.sun_glow_r = 150
        self.sun_core_colour = self.theme["enemy_high"]
        self.sun_glow_colour = self.theme["player"] + (40,)
        
        self.beat_pulse = 0
        
        self.scan_line_y = 0
        self.scan_line_speed = 0.1
        self.scan_line_colour = self.theme["enemy_low"] + (10,)
        
      
        self.ray_alpha = 40
        
    def on_beat(self):
        super().on_beat()
        self.beat_pulse = 30
    
    def update(self):
        super().update()
        self.beat_pulse *= 0.85
        if self.beat_pulse < 0.1: self.beat_pulse = 0
        
        self.scan_line_y = (self.scan_line_y + self.scan_line_speed)
        self.scan_line_y += self.scan_line_speed
        if self.scan_line_y >= 8:  # line spacing
            self.scan_line_y -= 8  
        scan_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        line_spacing = 8
        y = -line_spacing + self.scan_line_y
        while y < self.screen_height:
            pygame.draw.line(scan_surf, self.scan_line_colour, (0, int(y)), (self.screen_width, int(y)), 2)
            y += line_spacing
        self.screen.blit(scan_surf, (0, 0))
        
    def draw(self):
        super().draw()
        current_core_r = int(self.sun_core_r+ self.beat_pulse)
        current_glow_r = int(self.sun_glow_r + self.beat_pulse * 1.5)

        glow_surf = pygame.Surface((current_glow_r * 2, current_glow_r * 2), 
                                   pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, 
                           self.sun_glow_colour, 
                           (current_glow_r, current_glow_r), 
                           current_glow_r)
        
        self.screen.blit(glow_surf, (self.center_x - current_glow_r, 
                                     self.sun_y - current_glow_r))
        

        sun_surf_size = current_core_r * 2
        sun_surf = pygame.Surface((sun_surf_size, sun_surf_size), pygame.SRCALPHA)
        color_top = pygame.Color(*self.sun_core_colour)
        color_bottom = pygame.Color(*self.theme["player"])

        solid_top_height = 80 
        
        base_line_spacing = 20
        
        for y in range(0, sun_surf_size, base_line_spacing):
            y_ratio = y / sun_surf_size
            current_color = color_top.lerp(color_bottom, y_ratio)
            current_line_thickness = 0 
            
            if y < solid_top_height:
                current_line_thickness = 20 
     
            else:
                aggressive_y_ratio = (y - solid_top_height) / (sun_surf_size - solid_top_height)
                
                current_line_thickness = int(12 - (aggressive_y_ratio * 4)) 
                current_line_thickness = max(1, current_line_thickness) 
                
            pygame.draw.line(sun_surf, 
                             current_color, 
                             (0, y),
                             (sun_surf_size, y), 
                             current_line_thickness) 

        # Now, create a circular mask
        mask_surf = pygame.Surface((sun_surf_size, sun_surf_size), pygame.SRCALPHA)
        pygame.draw.circle(mask_surf, 
                           (255, 255, 255), 
                           (current_core_r, current_core_r),
                           current_core_r)
        sun_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        self.screen.blit(sun_surf, (self.center_x - current_core_r, 
                                     self.sun_y - current_core_r))
        
     
        scan_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        for y in range(int(self.scan_line_y), self.screen_height, 8):
            pygame.draw.line(
                scan_surf,
                self.scan_line_colour, 
                (0, y),
                (self.screen_width, y),
                2)
        self.screen.blit(scan_surf, (0, 0))

class ice_bg(background):
    def __init__(self, screen, theme):
        super().__init__(screen, theme)
        
        self.beat_pulse = 0
        self.particle_count = 100
        self.particles = []
        
        for i in range(self.particle_count):
            self.particles.append({
                "x": random.randint(0, self.screen_width),
                "y": random.randint(0, self.screen_height),
                "speed": random.uniform(1, 3)
            })
        
    def on_beat(self):
        super().on_beat()
        
        # Trigger the particle pulse
        self.beat_pulse = 1.5 
        
    def update(self):
        super().update()
            
        # Decay for the snow particle pulse
        self.beat_pulse *= 0.90 # Fades over time
        if self.beat_pulse < 0.1:
            self.beat_pulse = 0
        
        # Update particles
        for p in self.particles:
            p['y'] += p['speed'] + self.beat_pulse
            p['x'] += math.sin(time.time() + p['x']) * 0.5
            if p['y'] > self.screen_height:
                p['y'] = 0
                p['x'] = random.randint(0, self.screen_width)

    def draw(self):
        # 1. Draw base background
        super().draw()
        
        # 2. Draw Particles
        for p in self.particles:
            pygame.draw.circle(self.screen, self.theme['lane_divider'], (p['x'], p['y']), 2)
themes = {
    "synthwave": {
        "player": (255, 50, 200),
        "enemy_low": (0, 180, 255),
        "enemy_mid": (57, 255, 20),
        "enemy_high": (255, 0, 255),
        "bg": (40, 40, 40),
        "bg_flash": (70, 70, 70),
        "lane_divider": (255, 0, 255),
        "background_class": synthwave_bg
    },
"ice": {
    "player": (200, 255, 255),
    "enemy_low": (0, 150, 255),
    "enemy_mid": (0, 220, 255),
    "enemy_high": (180, 255, 255),
    "bg": (5, 15, 40),
    "bg_flash": (100, 200, 255),
    "lane_divider": (180, 255, 255),
    "background_class": ice_bg
}
}
theme = themes["ice"]
 
command = queue()
async def controller_server(websocket,):
    global command
    async for message in websocket:
        print("Received:", message)
        data = json.loads(message)  # convert string to dict
        command.put(data)

async def start_server():
    async with websockets.serve(controller_server, "0.0.0.0", 8765) as server:
       await server.serve_forever()
def draw_text(screen,text,font,colour,center_pos):
    img = font.render(text,True,colour)
    rect = img.get_rect(center = center_pos)
    screen.blit(img,rect)

def game_start (screen,font_large,font_small):
    while True:
        screen.fill(theme["bg"])
        draw_text(screen,"LONGI - TUNAL",font_large,theme["player"],(screen_width // 2, screen_height // 3))
        draw_text(screen, "Press any key to Start", font_small, theme['lane_divider'], (screen_width // 2, screen_height // 2))
        draw_text(screen, "UP/DOWN to Move", font_small, theme['lane_divider'], (screen_width // 2, screen_height // 2 + 50))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return "QUIT"
            elif event.type == KEYDOWN:
                return "RUNNING"
        try:
            command.get_nowait()
            return "RUNNING"
        except Exception:
            pass
def game_over(screen,font_large,font_small,final_score):
    while True:
            screen.fill(theme['bg'])
            draw_text(screen, "GAME OVER", font_large, theme['enemy_high'], (screen_width // 2, screen_height // 3))
            draw_text(screen, f"Score: {final_score}", font_small, theme['player'], (screen_width // 2, screen_height // 2))
            draw_text(screen, "Press any key to restart", font_small, theme['lane_divider'], (screen_width // 2, screen_height // 2 + 50))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return "QUIT"
                elif event.type == KEYDOWN:
                    return "RUNNING"
            try:
                command.get_nowait()
                return "RUNNING"
            except:
                pass
            
        
        
def game_main(music_data):
    pygame.init()
    pygame.font.init() 
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Rythm Rush")

    try:
        font_large = pygame.font.SysFont('Consolas', 72)
        font_small = pygame.font.SysFont('Consolas', 30)
    except:
        font_large = pygame.font.Font(None, 80)
        font_small = pygame.font.Font(None, 36)
        print("Consolas not found")
    game_state = "START"
    while True:
        if game_state == 'START':
            result = game_start(screen, font_large, font_small)
            if result == 'QUIT':
                break # Exit the main loop
            game_state = result
        elif game_state == "RUNNING":
            result = game(music_data,screen,font_large,font_small)
            if result == "QUIT":
                break
            final_score = result
            game_state = "GAME_OVER"
        elif game_state == "GAME_OVER":
            result = game_over(screen,font_large,font_small,final_score)
            if result == "QUIT":
                break
            game_state = result
    pygame.quit()
  
def game(music_data,screen,font_large,font_small):      
    clock = pygame.time.Clock()  
    try:
        BgClass = theme['background_class']
        background = BgClass(screen, theme)
    except KeyError:
        print(f"Warning: No 'background_class' for theme. Using BaseBackground.")
        background = background(screen, theme)
    except Exception as e:
        print(e)
    player = Player()
    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    running = True    
    score = 0
    while running:
        for event in pygame.event.get():
            if ((event.type == KEYDOWN) and (event.key == K_ESCAPE)) or (event.type == pygame.QUIT):
                return "QUIT"
        player.update(command,pygame.key.get_pressed())
        enemies.update()
        background.update()
        background.draw()
        lane_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

        for i in range(1, lanes):
            pygame.draw.line(
                lane_surface,
                (*theme["lane_divider"], 80), 
                (0, i * lane_height),
                (screen_width, i * lane_height),
                2
            )
        screen.blit(lane_surface, (0, 0))
        for entity in all_sprites:
            screen.blit(entity.surface,entity.rect)
        draw_text(screen, f"Score: {score:.0f}", font_small, theme['player'], (screen_width - 100, 30))
        if pygame.sprite.spritecollideany(player, enemies):
            player.kill()
            return round(score)
        pygame.display.flip()
        try:
            md = music_data.get_nowait()
            speed = (float(md['bpm'])/9)
            new_enemy = Enemy(speed,float(md['amplitude']),float(md['pitch']))
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)
            score += float(md["bpm"]/240) 
        except Empty:
            ##print("Empty Queue")
            pass
        except Exception as e:
            print(f"analysis failed {e}")
      
        clock.tick(120) ## cap the frame rate to 120 FPS (useful for timing with the sound wave form in furture)

def get_music_data(music_data):
    import sounddevice as sd
    import numpy as np
    from collections import deque
    import time
    BASS_LOW,BASS_HIGH = 20,150
    PITCH_LOW,PITCH_HIGH = 150,1500
    WINDOW_SEC = 5
    bass_history = deque(maxlen=50)
    bass_history.extend([0] * 22)
    amplitude_history = deque(maxlen=22)
    threshold_multiplier = 1.1
    bpm = 0
    beat_times = deque()
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
        raise RuntimeError("VB Cable not found. Make sure it's installed and enabled.")
    
    def get_amplitude(mono):
        nonlocal amplitude_history
        amplitude = (np.sqrt(np.mean(mono ** 2))) 
        amplitude_history.append(amplitude)
        min_amplitude = min(amplitude_history)
        max_amplitude = max(amplitude_history)
        if max_amplitude - min_amplitude < 1e-5:
            mapped_value = 0
        else:
            mapped_value = np.interp(amplitude, [min_amplitude, max_amplitude], [0, 600])
        return f"{mapped_value:.0f}"
    
    def get_bass_amp(spectrum,freqs):
        bass_range = (freqs >= BASS_LOW) & (freqs <= BASS_HIGH)
        return np.mean(np.abs(spectrum[bass_range]))

    def get_pitch(spectrum,freqs):
        pitch_range = (freqs >= PITCH_LOW) & (freqs <= PITCH_HIGH)
        if np.any(pitch_range):
            pitch_freq = freqs[pitch_range][np.argmax(np.abs(spectrum[pitch_range]))]
            scale = (pitch_freq - PITCH_LOW) / (PITCH_HIGH - PITCH_LOW)
            pitch = np.clip(scale, 0.0, 1.0)
        else:
            pitch = 0
        return pitch
    with sd.InputStream(channels=2, samplerate=SR, blocksize=BLOCK_SIZE, device=device_index) as stream:
        while True:
            indata, _ = stream.read(BLOCK_SIZE)
            mono = np.mean(indata, axis=1)
            spectrum = np.fft.rfft(mono)
            freqs = np.fft.rfftfreq(len(mono), 1/SR)
            bass_amp = get_bass_amp(spectrum,freqs)
    
            now = time.time()   
            threshold = np.mean(bass_history) *threshold_multiplier
            if bass_amp > threshold and bass_amp > 0.2:
                if len(beat_times) == 0 or now - beat_times[-1] > 0.2:  # avoid double-counting
                    beat_times.append(now)      
                    amplitude = get_amplitude(mono)
                    pitch = get_pitch(spectrum,freqs)
                    music_data.put({'amplitude': amplitude, 'bpm': bpm,'pitch' : pitch})
            if len(beat_times) > 1:
                intervals = np.diff(beat_times)
                bpm = 60 / np.mean(intervals)
            bass_history.append(bass_amp)
            while beat_times and now - beat_times[0] > WINDOW_SEC:
                beat_times.popleft()

    
                

if __name__ == "__main__":
    music_data = Queue()
    threading.Thread(target=lambda: asyncio.run(start_server()), daemon=True).start()
    p1 = Process(target=get_music_data, args=(music_data,))
    p1.start()
    game_main(music_data)
    p1.join()