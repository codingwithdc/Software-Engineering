import math
import random
from array import array

import pygame
from game.color_button import ColorButton


# Tone frequency (Hz) for each color ID: C4, E4, G4, C5
TONE_FREQUENCIES = {
    0: 261.63,  # Red
    1: 329.63,  # Blue
    2: 392.00,  # Green
    3: 523.25,  # Yellow
}


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        pad_size = 130
        gap = 24
        start_x = width // 2 - pad_size - (gap // 2)
        start_y = 150

        self.buttons = [
            ColorButton(0, pygame.Rect(start_x, start_y, pad_size, pad_size), (110, 20, 20), (255, 50, 50)),                      # Red
            ColorButton(1, pygame.Rect(start_x + pad_size + gap, start_y, pad_size, pad_size), (15, 60, 150), (40, 170, 255)),   # Blue
            ColorButton(2, pygame.Rect(start_x, start_y + pad_size + gap, pad_size, pad_size), (15, 100, 30), (50, 255, 90)),    # Green
            ColorButton(3, pygame.Rect(start_x + pad_size + gap, start_y + pad_size + gap, pad_size, pad_size), (140, 110, 10), (255, 235, 40)), # Yellow
        ]

        self.sequence = []
        self.player_input = []
        self.score = 0

        self.state = "WATCH"
        self.showing_step = 0
        self.step_start_time = 0
        self.flash_duration = 450
        self.pause_duration = 200
        self.is_flashing = False

        self.player_lit_button = None
        self.player_lit_start = 0
        self.player_flash_duration = 150

        self.font_title = pygame.font.SysFont(None, 40)
        self.font_medium = pygame.font.SysFont(None, 28)

        self.round_lead_in = 600
        self.game_over_reason = None

        # Per-step countdown during PLAYER_TURN (resets after every correct click)
        self.step_time_limit = 3000
        self.step_deadline = 0

        self.sounds = self._init_sounds()

        self.start_next_round()

    # ------------------------------------------------------------------ audio

    def _init_sounds(self):
        """Build one synthesized tone per color. Falls back to silence if no audio device."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            return {cid: self._build_tone(freq) for cid, freq in TONE_FREQUENCIES.items()}
        except pygame.error:
            return {}

    def _build_tone(self, freq, duration_ms=1000, volume=0.35):
        """Synthesize a sine tone as signed 16-bit PCM using the built-in array module."""
        sample_rate, _size, channels = pygame.mixer.get_init()
        n_samples = int(sample_rate * duration_ms / 1000)
        ramp = max(1, int(sample_rate * 0.01))  # 10 ms attack/release to avoid clicks
        amplitude = int(32767 * volume)
        step = 2 * math.pi * freq / sample_rate

        samples = array("h")
        for i in range(n_samples):
            envelope = min(1.0, i / ramp, (n_samples - i) / ramp)
            value = int(amplitude * envelope * math.sin(step * i))
            samples.extend([value] * channels)  # duplicate per channel if mixer is stereo

        return pygame.mixer.Sound(buffer=samples)

    def play_tone(self, color_id):
        sound = self.sounds.get(color_id)
        if sound:
            sound.stop()
            sound.play()

    def stop_tone(self, color_id, fade_ms=40):
        sound = self.sounds.get(color_id)
        if sound:
            sound.fadeout(fade_ms)

    # ------------------------------------------------------------------ game flow

    def start_next_round(self):
        new_color = random.randint(0, 3)
        self.sequence.append(new_color)

        # Speed up playback as score rises, clamped to minimum thresholds
        self.flash_duration = max(180, 450 - self.score * 25)
        self.pause_duration = max(80, 200 - self.score * 10)
        self.step_time_limit = max(1500, 3000 - self.score * 100)

        self.player_input.clear()
        self.state = "WATCH"
        # Start in a lead-in pause; update() lights step 0 when it ends
        self.showing_step = -1
        self.is_flashing = False
        self.step_start_time = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()

        if self.player_lit_button is not None:
            if now - self.player_lit_start >= self.player_flash_duration:
                self.player_lit_button.is_lit = False
                self.stop_tone(self.player_lit_button.color_id)
                self.player_lit_button = None

        if self.state == "WATCH":
            if self.is_flashing:
                current_btn_id = self.sequence[self.showing_step]
                if now - self.step_start_time >= self.flash_duration:
                    self.buttons[current_btn_id].is_lit = False
                    self.stop_tone(current_btn_id)
                    self.is_flashing = False
                    self.step_start_time = now
            else:
                delay = self.round_lead_in if self.showing_step < 0 else self.pause_duration
                if now - self.step_start_time >= delay:
                    self.showing_step += 1
                    if self.showing_step < len(self.sequence):
                        next_id = self.sequence[self.showing_step]
                        self.buttons[next_id].is_lit = True
                        self.play_tone(next_id)
                        self.is_flashing = True
                        self.step_start_time = now
                    else:
                        self.state = "PLAYER_TURN"
                        self.step_deadline = now + self.step_time_limit

        elif self.state == "PLAYER_TURN":
            if now >= self.step_deadline:
                self.game_over_reason = "timeout"
                self.state = "GAME_OVER"

    def handle_event(self, event):
        if self.state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        if self.state == "PLAYER_TURN" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn.contains(event.pos):
                    btn.is_lit = True
                    self.player_lit_button = btn
                    self.player_lit_start = pygame.time.get_ticks()
                    self.play_tone(btn.color_id)

                    self.register_player_click(btn.color_id)
                    break

    def register_player_click(self, color_id):
        self.player_input.append(color_id)
        current_idx = len(self.player_input) - 1

        if self.player_input[current_idx] != self.sequence[current_idx]:
            self.game_over_reason = "wrong"
            self.state = "GAME_OVER"
            return

        if len(self.player_input) == len(self.sequence):
            self.score += 1
            self.start_next_round()
        else:
            self.step_deadline = pygame.time.get_ticks() + self.step_time_limit

    def reset(self):
        self.sequence.clear()
        self.player_input.clear()
        self.score = 0
        for btn in self.buttons:
            btn.is_lit = False
        self.player_lit_button = None
        self.start_next_round()

    def render_timer_bar(self, screen):
        remaining = max(0, self.step_deadline - pygame.time.get_ticks())
        frac = remaining / self.step_time_limit

        bar_w, bar_h = 260, 8
        x = self.width // 2 - bar_w // 2
        y = 124

        if frac > 0.5:
            color = (80, 240, 130)
        elif frac > 0.25:
            color = (255, 210, 60)
        else:
            color = (240, 70, 70)

        pygame.draw.rect(screen, (50, 54, 64), (x, y, bar_w, bar_h), border_radius=4)
        if remaining > 0:
            pygame.draw.rect(screen, color, (x, y, int(bar_w * frac), bar_h), border_radius=4)

    def render(self, screen):
        screen.fill((22, 24, 30))

        title_surf = self.font_title.render("Memory Pattern Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 20))

        score_surf = self.font_medium.render(f"Score: {self.score}", True, (255, 220, 80))
        screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, 60))

        status_text = "Watch the pattern..." if self.state == "WATCH" else "Your turn: Click the pattern!"
        status_color = (190, 195, 205) if self.state == "WATCH" else (80, 240, 130)
        status_surf = self.font_medium.render(status_text, True, status_color)
        screen.blit(status_surf, (self.width // 2 - status_surf.get_width() // 2, 95))

        if self.state == "PLAYER_TURN":
            self.render_timer_bar(screen)

        for btn in self.buttons:
            btn.render(screen)

        if self.state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))

            over_text = "TIME'S UP! GAME OVER" if self.game_over_reason == "timeout" else "WRONG PATTERN! GAME OVER"
            over_surf = self.font_title.render(over_text, True, (240, 70, 70))
            screen.blit(over_surf, (self.width // 2 - over_surf.get_width() // 2, self.height // 2 - 40))

            final_score_surf = self.font_medium.render(f"Final Score: {self.score}", True, (255, 255, 255))
            screen.blit(final_score_surf, (self.width // 2 - final_score_surf.get_width() // 2, self.height // 2 + 10))

            restart_surf = self.font_medium.render("Press [R] to Play Again", True, (200, 200, 200))
            screen.blit(restart_surf, (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 50))