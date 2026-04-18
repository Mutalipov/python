import pygame
import os

# --- Configuration ---
MUSIC_DIR = r"C:\Users\Admin\Desktop\python\w3school_examples\prac7\mp3_player\music"
SCREEN_SIZE = (600, 320)
BG_COLOR = (25, 25, 35)
TEXT_COLOR = (240, 240, 240)
ACCENT_COLOR = (0, 200, 150)
ERR_COLOR = (255, 80, 80)

class MusicPlayer:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("Pro Music Player")
        
        self.font_main = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_small = pygame.font.SysFont("Segoe UI", 16)
        
        if not os.path.exists(MUSIC_DIR):
            os.makedirs(MUSIC_DIR)
            
        self.playlist = [f for f in os.listdir(MUSIC_DIR) if f.endswith(('.mp3', '.wav'))]
        self.current_index = 0
        self.playing = False
        self.error_msg = ""
        self.volume = 0.5
        
        # Track position management
        self.current_pos_sec = 0 
        
        pygame.mixer.music.set_volume(self.volume)
        self.running = True
        self.clock = pygame.time.Clock()

    def play_track(self, start_time=0, attempts=0):
        if not self.playlist:
            self.error_msg = "No music files found!"
            return

        if attempts >= len(self.playlist):
            self.error_msg = "Critical: All files unplayable."
            self.playing = False
            return

        try:
            track_path = os.path.join(MUSIC_DIR, self.playlist[self.current_index])
            pygame.mixer.music.load(track_path)
            # start_time is in seconds
            pygame.mixer.music.play(start=start_time)
            self.current_pos_sec = start_time
            self.playing = True
            self.error_msg = "" 
        except pygame.error as e:
            print(f"Error loading {self.playlist[self.current_index]}: {e}")
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.play_track(attempts=attempts + 1)

    def seek(self, seconds):
        """
        Adjusts the playback position. 
        Note: MP3 seeking via set_pos is often buggy, 
        so we restart the track from a specific time.
        """
        if self.playing:
            # Get current time (ms) and convert to seconds, then add offset
            new_pos = max(0, self.current_pos_sec + (pygame.mixer.music.get_pos() / 1000) + seconds)
            self.play_track(start_time=new_pos)

    def stop_track(self):
        pygame.mixer.music.stop()
        self.playing = False

    def next_track(self):
        if self.playlist:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.play_track(start_time=0)

    def prev_track(self):
        if self.playlist:
            self.current_index = (self.current_index - 1) % len(self.playlist)
            self.play_track(start_time=0)

    def update_volume(self, delta):
        self.volume = min(1.0, max(0.0, self.volume + delta))
        pygame.mixer.music.set_volume(self.volume)

    def draw_ui(self):
        self.screen.fill(BG_COLOR)
        
        title_text = self.playlist[self.current_index] if self.playlist else "Empty"
        title_surf = self.font_main.render(title_text, True, TEXT_COLOR)
        self.screen.blit(title_surf, (30, 50))

        if self.error_msg:
            err_surf = self.font_small.render(self.error_msg, True, ERR_COLOR)
            self.screen.blit(err_surf, (30, 85))

        status = "PLAYING" if self.playing else "STOPPED"
        curr_time = int(self.current_pos_sec + (pygame.mixer.music.get_pos() / 1000)) if self.playing else 0
        info_str = f"Status: {status}  |  Time: {curr_time}s  |  Vol: {int(self.volume * 100)}%"
        vol_surf = self.font_small.render(info_str, True, ACCENT_COLOR)
        self.screen.blit(vol_surf, (30, 120))

        # Progress Bar
        pygame.draw.rect(self.screen, (60, 60, 60), (30, 170, 540, 10))
        if self.playing:
            bar_width = (curr_time * 5) % 540 # Visual approximation
            pygame.draw.rect(self.screen, ACCENT_COLOR, (30, 170, bar_width, 10))

        controls = "[P] Play [S] Stop [N] Next [B] Back [L/R Arrows] -10/+10s [Q] Quit"
        help_surf = self.font_small.render(controls, True, (150, 150, 150))
        self.screen.blit(help_surf, (30, 260))

        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:      self.play_track()
                    elif event.key == pygame.K_s:    self.stop_track()
                    elif event.key == pygame.K_n:    self.next_track()
                    elif event.key == pygame.K_b:    self.prev_track()
                    elif event.key == pygame.K_LEFT:  self.seek(-10)  # Rewind 10s
                    elif event.key == pygame.K_RIGHT: self.seek(10)   # Fast Forward 10s
                    elif event.key == pygame.K_UP:   self.update_volume(0.1)
                    elif event.key == pygame.K_DOWN: self.update_volume(-0.1)
                    elif event.key == pygame.K_q:    self.running = False

            if self.playing and not pygame.mixer.music.get_busy():
                self.next_track()

            self.draw_ui()
            self.clock.tick(30)

        pygame.quit()

if __name__ == "__main__":
    player = MusicPlayer()
    player.run()