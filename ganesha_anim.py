"""
================================================================================
  LORD GANESHA COSMIC PARTICLE CONVERGENCE ANIMATION
  Libraries: OpenCV (cv2), Pygame, NumPy
================================================================================
  Features:
  - OpenCV pixel extraction & BGRA transparent image processing
  - High-performance vectorized NumPy particle physics (47,000+ particles)
  - Organic spiral vortex & spring-attractor convergence simulation
  - Multi-theme glowing bloom effects (Original, Divine Gold, Cosmic Neon, Flame)
  - Interactive mouse shockwave explosions & procedural audio feedback
  - On-screen Glassmorphic UI with controls & status indicators
================================================================================
"""

import sys
import os
import time
import math
import cv2
import numpy as np
import pygame

# Initialize Pygame & Audio Mixer
pygame.init()
try:
    pygame.mixer.init(44100, -16, 2, 512)
    AUDIO_ENABLED = True
except Exception:
    AUDIO_ENABLED = False

pygame.font.init()

# --- CONSTANTS & CONFIGURATION ---
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 900
FPS = 60

# Color Modes
MODE_ORIGINAL = 0
MODE_DIVINE_GOLD = 1
MODE_COSMIC_NEON = 2
MODE_CELESTIAL_FLAME = 3
COLOR_MODE_NAMES = ["Original Image", "Divine Gold", "Cosmic Neon", "Celestial Flame"]

# Animation States
STATE_SCATTERED = 0
STATE_CONVERGING = 1
STATE_FORMED = 2

class SoundManager:
    """Procedural audio sound generator using NumPy wave synthesis."""
    def __init__(self):
        self.sounds = {}
        if not AUDIO_ENABLED:
            return
        try:
            self.sounds['chime'] = self._create_chime_sound()
            self.sounds['shockwave'] = self._create_shockwave_sound()
            self.sounds['whoosh'] = self._create_whoosh_sound()
        except Exception as e:
            print(f"Warning: Could not synthesize procedural audio: {e}")

    def _create_chime_sound(self):
        sample_rate = 44100
        duration = 1.2
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        # Bell chime frequencies (harmonic harmonics: 528Hz, 1056Hz, 1584Hz)
        wave = (np.sin(2 * np.pi * 528 * t) * 0.4 +
                np.sin(2 * np.pi * 1056 * t) * 0.25 +
                np.sin(2 * np.pi * 1584 * t) * 0.15)
        envelope = np.exp(-3.5 * t)
        wave = wave * envelope * 0.3
        audio_data = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((audio_data, audio_data))
        return pygame.sndarray.make_sound(stereo)

    def _create_shockwave_sound(self):
        sample_rate = 44100
        duration = 0.4
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = 150 * np.exp(-6 * t) + 40
        wave = np.sin(2 * np.pi * freq * t) * 0.5
        noise = (np.random.rand(len(t)) * 2 - 1) * 0.2 * np.exp(-5 * t)
        sound_wave = (wave + noise) * np.exp(-4 * t)
        audio_data = (np.clip(sound_wave, -1.0, 1.0) * 32767).astype(np.int16)
        stereo = np.column_stack((audio_data, audio_data))
        return pygame.sndarray.make_sound(stereo)

    def _create_whoosh_sound(self):
        sample_rate = 44100
        duration = 0.6
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        noise = (np.random.rand(len(t)) * 2 - 1) * 0.3
        envelope = np.sin(np.pi * (t / duration)) ** 2
        audio_data = (noise * envelope * 32767).astype(np.int16)
        stereo = np.column_stack((audio_data, audio_data))
        return pygame.sndarray.make_sound(stereo)

    def play(self, sound_name):
        if AUDIO_ENABLED and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except Exception:
                pass


def load_ganesha_pixels(image_path, scale=1.3, win_w=WINDOW_WIDTH, win_h=WINDOW_HEIGHT):
    """
    Reads 'ganesha.png' with OpenCV (IMREAD_UNCHANGED for BGRA transparent pixels).
    Extracts non-transparent pixel coordinates and RGB color values.
    Returns centered screen target positions and RGB colors.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image '{image_path}' not found at path: {os.path.abspath(image_path)}")

    # Read image using OpenCV keeping alpha channel
    img_bgra = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img_bgra is None:
        raise ValueError(f"Failed to decode image '{image_path}'. Check file integrity.")

    # Ensure 4 channels (BGRA)
    if img_bgra.shape[2] == 3:
        b, g, r = cv2.split(img_bgra)
        gray = cv2.cvtColor(img_bgra, cv2.COLOR_BGR2GRAY)
        alpha = np.where(gray > 240, 0, 255).astype(np.uint8)
        img_bgra = cv2.merge([b, g, r, alpha])

    orig_h, orig_w = img_bgra.shape[:2]

    # Resize for high resolution display if scale != 1.0
    if scale != 1.0:
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)
        img_bgra = cv2.resize(img_bgra, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

    h, w = img_bgra.shape[:2]

    # Extract non-transparent pixels (Alpha > 20)
    alpha = img_bgra[:, :, 3]
    y_idx, x_idx = np.where(alpha > 20)

    # Extract BGR and convert to RGB
    b_val = img_bgra[y_idx, x_idx, 0]
    g_val = img_bgra[y_idx, x_idx, 1]
    r_val = img_bgra[y_idx, x_idx, 2]
    colors_rgb = np.column_stack((r_val, g_val, b_val)).astype(np.float32)

    # Calculate centered target screen coordinates
    offset_x = (win_w - w) // 2
    offset_y = (win_h - h) // 2 + 10  # Slightly offset for header title space

    target_x = (x_idx + offset_x).astype(np.float32)
    target_y = (y_idx + offset_y).astype(np.float32)

    return target_x, target_y, colors_rgb, (w, h)


class ParticleSystem:
    """Vectorized particle physics & rendering engine using NumPy."""
    def __init__(self, target_x, target_y, colors_rgb, win_w=WINDOW_WIDTH, win_h=WINDOW_HEIGHT):
        self.num_particles = len(target_x)
        self.win_w = win_w
        self.win_h = win_h

        self.target_x = target_x
        self.target_y = target_y
        self.orig_colors = colors_rgb.copy()
        self.active_colors = colors_rgb.copy()

        # Current state arrays
        self.pos_x = np.zeros(self.num_particles, dtype=np.float32)
        self.pos_y = np.zeros(self.num_particles, dtype=np.float32)
        self.vel_x = np.zeros(self.num_particles, dtype=np.float32)
        self.vel_y = np.zeros(self.num_particles, dtype=np.float32)

        self.phases = np.random.uniform(0, 2 * np.pi, self.num_particles).astype(np.float32)
        self.particle_size = 1  # 1px default, adjustable up to 3px

        # Physics tuning parameters
        self.attraction_stiffness = 0.08
        self.damping = 0.84
        self.swirl_enabled = True
        self.swirl_strength = 1.8

        self.state = STATE_SCATTERED
        self.color_mode = MODE_ORIGINAL
        self.convergence_progress = 0.0  # 0.0 to 1.0

        # Pre-create background starfield particles
        self.num_stars = 120
        self.star_x = np.random.uniform(0, win_w, self.num_stars).astype(np.float32)
        self.star_y = np.random.uniform(0, win_h, self.num_stars).astype(np.float32)
        self.star_speeds = np.random.uniform(0.1, 0.4, self.num_stars).astype(np.float32)
        self.star_brightness = np.random.uniform(50, 180, self.num_stars).astype(np.float32)

        # Scatter initial positions
        self.scatter_particles()

    def scatter_particles(self):
        """Randomly scatters particles across the entire window canvas."""
        # Random positions across canvas with radial expansion
        cx, cy = self.win_w / 2.0, self.win_h / 2.0
        angles = np.random.uniform(0, 2 * np.pi, self.num_particles)
        radii = np.random.uniform(50, max(self.win_w, self.win_h) * 0.7, self.num_particles)

        self.pos_x = (cx + np.cos(angles) * radii).astype(np.float32)
        self.pos_y = (cy + np.sin(angles) * radii).astype(np.float32)

        # Give random initial blast velocities
        self.vel_x = (np.cos(angles) * np.random.uniform(2, 12, self.num_particles)).astype(np.float32)
        self.vel_y = (np.sin(angles) * np.random.uniform(2, 12, self.num_particles)).astype(np.float32)

        self.state = STATE_SCATTERED
        self.convergence_progress = 0.0

    def trigger_convergence(self):
        """Initiates the particle convergence transition."""
        self.state = STATE_CONVERGING

    def trigger_shockwave(self, center_x, center_y, power=25.0, radius=220.0):
        """Applies a radial explosive shockwave force away from (center_x, center_y)."""
        dx = self.pos_x - center_x
        dy = self.pos_y - center_y
        dist_sq = dx * dx + dy * dy
        dist = np.sqrt(dist_sq) + 1e-4

        mask = dist < radius
        if np.any(mask):
            force = (1.0 - dist[mask] / radius) * power
            self.vel_x[mask] += (dx[mask] / dist[mask]) * force
            self.vel_y[mask] += (dy[mask] / dist[mask]) * force

    def set_color_mode(self, mode):
        """Applies distinct color transformations to the particle system."""
        self.color_mode = mode
        if mode == MODE_ORIGINAL:
            self.active_colors = self.orig_colors.copy()
        elif mode == MODE_DIVINE_GOLD:
            # Gold theme: Shimmering gold, amber, and warm saffron
            intensity = (self.orig_colors[:, 0] * 0.3 + self.orig_colors[:, 1] * 0.59 + self.orig_colors[:, 2] * 0.11) / 255.0
            r = np.clip(intensity * 255 + 40, 0, 255)
            g = np.clip(intensity * 200 + 20, 0, 240)
            b = np.clip(intensity * 50, 0, 150)
            self.active_colors = np.column_stack((r, g, b)).astype(np.float32)
        elif mode == MODE_COSMIC_NEON:
            # Neon Electric Blue / Purple
            r = np.clip(self.orig_colors[:, 2] * 0.8 + 20, 0, 255)
            g = np.clip(self.orig_colors[:, 1] * 0.5 + 40, 0, 255)
            b = np.clip(self.orig_colors[:, 0] * 0.9 + 100, 0, 255)
            self.active_colors = np.column_stack((r, g, b)).astype(np.float32)
        elif mode == MODE_CELESTIAL_FLAME:
            # Radiant fiery red/orange glow
            intensity = (self.orig_colors[:, 0] + self.orig_colors[:, 1] + self.orig_colors[:, 2]) / (3 * 255.0)
            r = np.clip(intensity * 255 + 50, 0, 255)
            g = np.clip(intensity * 140, 0, 200)
            b = np.clip(intensity * 30, 0, 100)
            self.active_colors = np.column_stack((r, g, b)).astype(np.float32)

    def update(self, dt_sec):
        """Updates particle position physics and state simulation."""
        # Floating background starfield animation
        self.star_y += self.star_speeds
        mask_stars = self.star_y > self.win_h
        self.star_y[mask_stars] = 0
        self.star_x[mask_stars] = np.random.uniform(0, self.win_w, np.count_nonzero(mask_stars))

        # Vectorized spring attraction force towards target position
        dx = self.target_x - self.pos_x
        dy = self.target_y - self.pos_y
        dist = np.sqrt(dx * dx + dy * dy) + 1e-4

        if self.state == STATE_SCATTERED:
            # Floating Brownian drift in scattered state
            self.phases += dt_sec * 2.0
            drift_x = np.cos(self.phases) * 0.4
            drift_y = np.sin(self.phases * 1.3) * 0.4
            self.vel_x = (self.vel_x + drift_x) * 0.95
            self.vel_y = (self.vel_y + drift_y) * 0.95
        else:
            # Convergence physics
            attract_fx = dx * self.attraction_stiffness
            attract_fy = dy * self.attraction_stiffness

            # Swirl vortex force perpendicular to distance vector
            if self.swirl_enabled:
                swirl_factor = np.clip(dist / 250.0, 0.0, 1.0) * self.swirl_strength
                tangent_x = -dy / dist
                tangent_y = dx / dist
                swirl_fx = tangent_x * swirl_factor * 2.5
                swirl_fy = tangent_y * swirl_factor * 2.5
            else:
                swirl_fx, swirl_fy = 0.0, 0.0

            self.vel_x = (self.vel_x + attract_fx + swirl_fx) * self.damping
            self.vel_y = (self.vel_y + attract_fy + swirl_fy) * self.damping

        # Integrate positions
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y

        # Calculate overall convergence percentage
        mean_error = np.mean(dist)
        if mean_error < 3.0:
            self.state = STATE_FORMED
            self.convergence_progress = 1.0
        else:
            self.convergence_progress = float(np.clip(1.0 - (mean_error / 300.0), 0.0, 1.0))

    def render(self, surface):
        """Renders particle system to Pygame display surface with high speed."""
        # 1. Clear background with deep cosmic midnight gradient
        surface.fill((8, 4, 20))

        # Render floating starfield
        for i in range(self.num_stars):
            b_val = int(self.star_brightness[i])
            surface.set_at((int(self.star_x[i]), int(self.star_y[i])), (b_val, b_val, int(b_val * 1.2)))

        # Render subtle divine background radial aura bloom when converging/formed
        if self.convergence_progress > 0.2:
            center_x, center_y = int(self.win_w // 2), int(self.win_h // 2)
            aura_radius = int(220 * self.convergence_progress)
            aura_surf = pygame.Surface((aura_radius * 2, aura_radius * 2), pygame.SRCALPHA)

            # Golden/warm ambient aura
            alpha_val = int(35 * self.convergence_progress)
            pygame.draw.circle(aura_surf, (255, 180, 50, alpha_val), (aura_radius, aura_radius), aura_radius)
            pygame.draw.circle(aura_surf, (255, 220, 120, int(alpha_val * 0.6)), (aura_radius, aura_radius), int(aura_radius * 0.6))
            surface.blit(aura_surf, (center_x - aura_radius, center_y - aura_radius), special_flags=pygame.BLEND_ADD)

        # Fast NumPy integer position clipping
        ix = np.clip(np.round(self.pos_x).astype(np.int32), 0, self.win_w - 1)
        iy = np.clip(np.round(self.pos_y).astype(np.int32), 0, self.win_h - 1)

        # 2. Direct high-speed NumPy surfarray pixel mapping
        pixel_array = pygame.surfarray.pixels3d(surface)
        pixel_array[ix, iy] = self.active_colors.astype(np.uint8)
        del pixel_array  # Unlock surface

        # 3. Additive bloom glow layer for bright particles if size > 1 or formed
        if self.particle_size > 1:
            glow_surf = pygame.Surface((self.win_w, self.win_h), pygame.SRCALPHA)
            px_array_glow = pygame.surfarray.pixels3d(glow_surf)
            # Offset positions for 2x2 particle rendering
            ix_r = np.clip(ix + 1, 0, self.win_w - 1)
            iy_b = np.clip(iy + 1, 0, self.win_h - 1)
            px_array_glow[ix_r, iy] = (self.active_colors * 0.7).astype(np.uint8)
            px_array_glow[ix, iy_b] = (self.active_colors * 0.7).astype(np.uint8)
            px_array_glow[ix_r, iy_b] = (self.active_colors * 0.5).astype(np.uint8)
            del px_array_glow
            surface.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_ADD)


class UIOverlay:
    """Glassmorphic User Interface Overlay with Title, Status & Interactive Panel."""
    def __init__(self, win_w=WINDOW_WIDTH, win_h=WINDOW_HEIGHT):
        self.win_w = win_w
        self.win_h = win_h

        # Attempt to load elegant fonts
        self.font_title = self._get_font(["Segoe UI", "Calibri", "Arial"], 28, bold=True)
        self.font_sub = self._get_font(["Segoe UI", "Calibri", "Arial"], 16, bold=True)
        self.font_body = self._get_font(["Consolas", "Courier New", "Arial"], 13)

        self.show_help = True
        self.status_msg = "Press [SPACE] or Click to Converge / Explode"

    def _get_font(self, font_names, size, bold=False):
        for fname in font_names:
            try:
                font = pygame.font.SysFont(fname, size, bold=bold)
                if font:
                    return font
            except Exception:
                continue
        return pygame.font.Font(None, size)

    def draw(self, surface, ps, fps):
        # 1. Header Title Banner
        title_str = "॥ ॐ श्री गणेशाय नमः ॥"
        title_sub = "LORD GANESHA COSMIC PARTICLE RE-CREATION"

        # Header Glass Container
        hdr_w, hdr_h = 520, 65
        hdr_x = (self.win_w - hdr_w) // 2
        hdr_y = 12

        hdr_bg = pygame.Surface((hdr_w, hdr_h), pygame.SRCALPHA)
        pygame.draw.rect(hdr_bg, (15, 10, 35, 180), (0, 0, hdr_w, hdr_h), border_radius=12)
        pygame.draw.rect(hdr_bg, (255, 190, 60, 120), (0, 0, hdr_w, hdr_h), width=1, border_radius=12)
        surface.blit(hdr_bg, (hdr_x, hdr_y))

        # Title Text with Golden Glow
        txt_title = self.font_title.render(title_str, True, (255, 215, 90))
        txt_shadow = self.font_title.render(title_str, True, (200, 100, 10))
        surface.blit(txt_shadow, (hdr_x + (hdr_w - txt_title.get_width()) // 2 + 1, hdr_y + 8))
        surface.blit(txt_title, (hdr_x + (hdr_w - txt_title.get_width()) // 2, hdr_y + 7))

        txt_sub = self.font_sub.render(title_sub, True, (220, 220, 250))
        surface.blit(txt_sub, (hdr_x + (hdr_w - txt_sub.get_width()) // 2, hdr_y + 38))

        # 2. Bottom Status Bar & Help Controls
        if self.show_help:
            panel_w, panel_h = 420, 160
            panel_x = 15
            panel_y = self.win_h - panel_h - 15

            panel_bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(panel_bg, (12, 8, 28, 200), (0, 0, panel_w, panel_h), border_radius=10)
            pygame.draw.rect(panel_bg, (100, 120, 200, 80), (0, 0, panel_w, panel_h), width=1, border_radius=10)
            surface.blit(panel_bg, (panel_x, panel_y))

            state_names = ["SCATTERED", "CONVERGING...", "FORMED & GLOWING"]
            curr_state = state_names[ps.state]
            color_name = COLOR_MODE_NAMES[ps.color_mode]

            lines = [
                f"Status: {curr_state} ({ps.convergence_progress*100:.1f}%)",
                f"Particles: {ps.num_particles:,}  |  FPS: {fps:.0f}",
                f"Color Theme: {color_name}",
                "----------------------------------------",
                "[SPACE / Click] : Converge / Explode Shockwave",
                "[C] : Cycle Color Theme   [S] : Swirl Toggle",
                "[R] : Scatter / Reset     [+/-] : Particle Size",
                "[H] : Toggle Help Overlay [ESC] : Quit",
            ]

            for i, line in enumerate(lines):
                col = (255, 200, 80) if i == 0 else ((180, 220, 255) if i < 3 else (190, 190, 210))
                txt = self.font_body.render(line, True, col)
                surface.blit(txt, (panel_x + 12, panel_y + 10 + i * 18))


def main():
    if "--test-run" in sys.argv:
        os.environ["SDL_VIDEODRIVER"] = "dummy"

    print("================================================================================")
    print("  Starting Lord Ganesha Particle Convergence Animation")
    print("================================================================================")
    
    # Image filepath
    img_filename = "ganesh.png"
    if not os.path.exists(img_filename):
        print(f"Error: '{img_filename}' was not found in current directory ({os.getcwd()}).")
        return

    # Set window position center
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    # Create Pygame Display Window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("|| ॐ श्री गणेशाय नमः || - Lord Ganesha Cosmic Particle Animation")
    clock = pygame.time.Clock()

    # Load sound manager & image pixels via OpenCV
    sounds = SoundManager()

    print(f"Reading '{img_filename}' with OpenCV...")
    target_x, target_y, colors_rgb, img_size = load_ganesha_pixels(img_filename, scale=1.3)
    print(f"Successfully extracted {len(target_x):,} non-transparent pixel particles.")

    # Initialize Particle System & UI Overlay
    ps = ParticleSystem(target_x, target_y, colors_rgb, WINDOW_WIDTH, WINDOW_HEIGHT)
    ui = UIOverlay(WINDOW_WIDTH, WINDOW_HEIGHT)

    running = True
    auto_converge_timer = time.time() + 0.2  # Quick start for test run
    test_frames = 0

    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        current_fps = clock.get_fps()
        test_frames += 1

        if "--test-run" in sys.argv and test_frames > 60:
            print("Test run completed 60 frames successfully.")
            break

        # Check auto-start convergence
        if auto_converge_timer and time.time() > auto_converge_timer:
            ps.trigger_convergence()
            sounds.play('whoosh')
            auto_converge_timer = None

        # --- EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False

                elif event.key == pygame.K_SPACE:
                    if ps.state == STATE_SCATTERED:
                        ps.trigger_convergence()
                        sounds.play('whoosh')
                    elif ps.state in (STATE_CONVERGING, STATE_FORMED):
                        # Explode particles outward
                        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
                        ps.trigger_shockwave(cx, cy, power=35.0, radius=350.0)
                        sounds.play('shockwave')

                elif event.key == pygame.K_r:
                    ps.scatter_particles()
                    sounds.play('whoosh')
                    auto_converge_timer = time.time() + 1.5

                elif event.key == pygame.K_c:
                    next_mode = (ps.color_mode + 1) % 4
                    ps.set_color_mode(next_mode)
                    sounds.play('chime')

                elif event.key == pygame.K_s:
                    ps.swirl_enabled = not ps.swirl_enabled

                elif event.key == pygame.K_h:
                    ui.show_help = not ui.show_help

                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    ps.particle_size = min(3, ps.particle_size + 1)

                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    ps.particle_size = max(1, ps.particle_size - 1)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if event.button == 1:  # Left Click
                    if ps.state == STATE_SCATTERED:
                        ps.trigger_convergence()
                        sounds.play('whoosh')
                    else:
                        # Shockwave at mouse click coordinates
                        ps.trigger_shockwave(mx, my, power=30.0, radius=250.0)
                        sounds.play('shockwave')

        # Previous state check for chime sound on completion
        prev_state = ps.state

        # Update Physics & Render
        ps.update(dt)

        if prev_state == STATE_CONVERGING and ps.state == STATE_FORMED:
            sounds.play('chime')

        ps.render(screen)
        ui.draw(screen, ps, current_fps)

        pygame.display.flip()

    pygame.quit()
    print("Animation closed gracefully.")

if __name__ == "__main__":
    main()
