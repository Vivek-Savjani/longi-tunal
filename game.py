import pygame,random,threading,asyncio,websockets,json
from multiprocessing import Process, Queue
from queue import Empty
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
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
    def __init__(self,speed,amplitude):
        super(Enemy, self).__init__()
        self.surface = pygame.Surface((30, 30))
        self.surface.fill((0, 0, 255))
        self.amplitude = amplitude
        self.speed = - speed
        self.rect = self.surface.get_rect(
            center=(
                screen_width,
                self.amplitude,)
        )
         
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
  
def game(music_data):      
    pygame.init()
    clock = pygame.time.Clock()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    player = Player()
    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player,enemies)
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
        pygame.draw.circle(screen, (0, 0, 0), (750, 300), 15)
        for entity in all_sprites:
            screen.blit(entity.surface,entity.rect)
        if pygame.sprite.spritecollideany(player, enemies):
            player.kill()
            ##running = False
            pass
        pygame.display.flip()
        try:
            md = music_data.get_nowait()
            speed = (float(md['bpm'])/30) + 1
            new_enemy = Enemy(speed,float(md['amplitude']))
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
    PITCH_LOW,PITCH_HIGH = 150,2000
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
        raise RuntimeError("VB Cable not found. Make sure it's installed and enabled.")

    def get_amplitude(indata):
        mono = np.mean(indata, axis=1)
        amplitude = (np.sqrt(np.mean(mono ** 2))) * 100
        mapped_value = np.interp(amplitude, [-10, 50], [10, 590])
        return f"{mapped_value:.0f}"
    
    def get_bass_amp(indata):
        mono = np.mean(indata, axis=1)
        spectrum = np.fft.rfft(mono)
        freqs = np.fft.rfftfreq(len(mono), 1/SR)
        bass_range = (freqs >= BASS_LOW) & (freqs <= BASS_HIGH)
        return np.mean(np.abs(spectrum[bass_range]))

    def get_pitch(indata):
        mono = np.mean(indata, axis=1)
        spectrum = np.fft.rfft(mono)
        freqs = np.fft.rfftfreq(len(mono), 1/SR)
        pitch_range = (freqs >= PITCH_LOW) & (freqs <= PITCH_HIGH)
        if np.any(pitch_range):
            pitch_freq = freqs[pitch_range][np.argmax(np.abs(spectrum[pitch_range]))]
        else:
            pitch_freq = 0
        return f"{pitch_freq:.0f}"
    with sd.InputStream(channels=2, samplerate=SR, blocksize=BLOCK_SIZE, device=device_index) as stream:
        while True:
            indata, _ = stream.read(BLOCK_SIZE)
            bass_amp = get_bass_amp(indata)
            if len(beat_times) > 1:
                intervals = np.diff(beat_times)
                bpm = 60 / np.mean(intervals)
            else:
                bpm = 0
            now = time.time()
            if bass_amp > prev_bass_amp * THRESHOLD_MULT and bass_amp > 0.2:
                amplitude = get_amplitude(indata)
                pitch = get_pitch(indata)
                if len(beat_times) == 0 or now - beat_times[-1] > 0.2:  # avoid double-counting
                    beat_times.append(now)
                    music_data.put({'amplitude': amplitude, 'bpm': bpm,'pitch' : pitch})
            prev_bass_amp = bass_amp
            while beat_times and now - beat_times[0] > WINDOW_SEC:
                beat_times.popleft()

    
                

if __name__ == "__main__":
    music_data = Queue()
    p1 = Process(target=get_music_data, args=(music_data,))
    p1.start()
    game(music_data)
    p1.join()