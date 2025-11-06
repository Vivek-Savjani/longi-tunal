import pygame,threading,asyncio,websockets,json
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
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surface = pygame.Surface((50, 50))
        self.surface.fill((255, 0, 255))
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
            self.surface = pygame.Surface((80,lane_height / 2 ))
            self.surface.fill((0, 0, 255))
        elif pitch <= 0.66:
            self.surface = pygame.Surface((160, lane_height / 2))
            self.surface.fill((0, 255, 0))
        else:
            self.surface = pygame.Surface((240, lane_height / 2))
            self.surface.fill((255, 0, 0))
        self.amplitude = amplitude
        lane_index =lanes - 1 - min(int(amplitude / screen_height * lanes), lanes - 1)
        self.speed = - speed
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

# Run the WebSocket server in background thread
threading.Thread(target=lambda: asyncio.run(start_server()), daemon=True).start()
  
def game(music_data):      
    pygame.init()
    clock = pygame.time.Clock()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    player = Player()
    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    running = True
    global command     

    while running:
        for event in pygame.event.get():
            if ((event.type == KEYDOWN) and (event.key == K_ESCAPE)) or (event.type == pygame.QUIT):
                pygame.quit()
                running = False
        player.update(command,pygame.key.get_pressed())
        enemies.update()
        screen.fill((255, 255, 255))

        for entity in all_sprites:
            screen.blit(entity.surface,entity.rect)
        if pygame.sprite.spritecollideany(player, enemies):
            ##player.kill()
            ##running = False
            pass
        pygame.display.flip()
        try:
            md = music_data.get_nowait()
            speed = (float(md['bpm'])/9)
            new_enemy = Enemy(speed,float(md['amplitude']),float(md['pitch']))
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)
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
    p1 = Process(target=get_music_data, args=(music_data,))
    p1.start()
    game(music_data)
    p1.join()