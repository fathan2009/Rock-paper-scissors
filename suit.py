"""
=============================================================================
GAME BATU, GUNTING, KERTAS - 2D FULL COLOR ARENA (TAWURAN JARI)
Fitur Unggulan:
1. Grafis 2D Full Color dengan 7 Skin Tangan Karakter Unik.
2. Mode VS AI (Komputer Cerdas) dan Mode 2 Player (1 Laptop bersama).
3. Kontrol Rahasia Anti-Intip untuk 2 Player (Keyboard + Tombol On-Screen).
4. Animasi NONJOK YANG KALAH: Tangan pemenang melesat menonjok tangan yang kalah!
5. Efek Komik Visual: POW!, BAM!, Screen Shake, Bintang Pusing, Percikan Api.
6. Sistem Nyawa (HP Bar Bertransisi Halus + Hati Merah/Hitam) hingga K.O.
7. Sound FX Asinkron bawaan Windows (Winsound) tanpa lag & tombol Mute.
=============================================================================
"""

import math
import random
import threading
import tkinter as tk
from tkinter import messagebox

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

# ---------------------------------------------------------------------------
# DEFINISI 7 SKIN TANGAN (2D FULL COLOR & DETAIL VEKTOR)
# ---------------------------------------------------------------------------
SKINS = {
    "classic": {
        "id": "classic",
        "name": "Pendekar Klasik",
        "tagline": "Petarung jalanan legendaris dengan perban tinju merah",
        "base": "#f5b083",
        "shade": "#d97d4b",
        "cuff": "#e63946",
        "cuff_sub": "#ffffff",
        "accent": "#c1121f",
        "outline": "#2b1b17",
        "glow": "#ff9f68",
        "type": "human",
    },
    "cyborg": {
        "id": "cyborg",
        "name": "Cyber Mecha",
        "tagline": "Tangan robot titanium krom dengan sirkuit neon cyan",
        "base": "#90a4ae",
        "shade": "#546e7a",
        "cuff": "#263238",
        "cuff_sub": "#00e5ff",
        "accent": "#00e5ff",
        "outline": "#102027",
        "glow": "#00e5ff",
        "type": "mecha",
    },
    "boxer": {
        "id": "boxer",
        "name": "Juara Tinju",
        "tagline": "Sarung tinju kulit merah mengkilap dengan bintang emas",
        "base": "#e63946",
        "shade": "#9d0208",
        "cuff": "#f1faee",
        "cuff_sub": "#ffb703",
        "accent": "#ffd166",
        "outline": "#1d3557",
        "glow": "#ff477e",
        "type": "glove",
    },
    "magma": {
        "id": "magma",
        "name": "Monster Magma",
        "tagline": "Batu vulkanik hitam berurat lahar pijar membara",
        "base": "#2b1e1e",
        "shade": "#150c0c",
        "cuff": "#590d22",
        "cuff_sub": "#ff4d00",
        "accent": "#ff7b00",
        "outline": "#ff3c00",
        "glow": "#ff5400",
        "type": "magma",
    },
    "gold": {
        "id": "gold",
        "name": "Raja Emas",
        "tagline": "Emas murni 24 karat berkilau dengan cincin berlian mewah",
        "base": "#ffd700",
        "shade": "#b8860b",
        "cuff": "#4a0e4e",
        "cuff_sub": "#ffd700",
        "accent": "#ffffff",
        "outline": "#3a2e00",
        "glow": "#ffe066",
        "type": "gold",
    },
    "toxic": {
        "id": "toxic",
        "name": "Alien Toxic",
        "tagline": "Mutan alien hijau asam radioaktif berlendir",
        "base": "#70e000",
        "shade": "#38b000",
        "cuff": "#240046",
        "cuff_sub": "#ccff33",
        "accent": "#9ef01a",
        "outline": "#004b23",
        "glow": "#70e000",
        "type": "toxic",
    },
    "shadow": {
        "id": "shadow",
        "name": "Ninja Bayangan",
        "tagline": "Pendekar malam berselubung petir energi ungu gelap",
        "base": "#2b2d42",
        "shade": "#14151f",
        "cuff": "#480ca8",
        "cuff_sub": "#7209b7",
        "accent": "#b5179e",
        "outline": "#03071e",
        "glow": "#7209b7",
        "type": "shadow",
    },
}

SKIN_KEYS = list(SKINS.keys())

CHOICES = ["batu", "gunting", "kertas"]
CHOICE_INFO = {
    "batu": {"name": "Batu", "icon": "🪨", "desc": "Batu menumpulkan Gunting", "color": "#e76f51"},
    "gunting": {"name": "Gunting", "icon": "✂️", "desc": "Gunting memotong Kertas", "color": "#f4a261"},
    "kertas": {"name": "Kertas", "icon": "📄", "desc": "Kertas membungkus Batu", "color": "#2a9d8f"},
}


# ---------------------------------------------------------------------------
# AUDIO MANAGER (WINSOUND ASINKRON BACKGROUND THREAD)
# ---------------------------------------------------------------------------
class SoundManager:
    def __init__(self):
        self.enabled = True

    def play(self, s_type):
        if not self.enabled or not HAS_WINSOUND:
            return

        def _worker():
            try:
                if s_type == "punch":
                    winsound.Beep(180, 80)
                    winsound.Beep(90, 160)
                elif s_type == "clash":
                    winsound.Beep(520, 70)
                    winsound.Beep(380, 90)
                elif s_type == "select":
                    winsound.Beep(750, 45)
                elif s_type == "ready":
                    winsound.Beep(523, 80)
                elif s_type == "countdown":
                    winsound.Beep(660, 70)
                elif s_type == "shoot":
                    winsound.Beep(988, 120)
                elif s_type == "ko":
                    winsound.Beep(349, 120)
                    winsound.Beep(262, 140)
                    winsound.Beep(196, 300)
                elif s_type == "victory":
                    for note in [523, 659, 784, 1046]:
                        winsound.Beep(note, 90)
            except Exception:
                pass

        threading.Thread(target=_worker, daemon=True).start()


# ---------------------------------------------------------------------------
# HAND RENDERER 2D PROCEDURAL VECTOR (FULL COLOR)
# ---------------------------------------------------------------------------
class HandRenderer:
    @staticmethod
    def draw(canvas, cx, cy, gesture, direction, skin, state="normal", scale=1.0, hurt_intensity=0.0):
        base = skin["base"]
        shade = skin["shade"]
        outline = skin["outline"]
        cuff_col = skin["cuff"]
        cuff_sub = skin["cuff_sub"]
        accent = skin["accent"]
        glow = skin["glow"]
        stype = skin.get("type", "human")

        # Efek kedip merah saat terkena hantaman
        if state == "hurt" and int(hurt_intensity * 10) % 2 == 1:
            base = "#ff3333"
            shade = "#8b0000"
            outline = "#ffffff"

        def poly(pts, fill, out=outline, width=3):
            flat = []
            for lx, ly in pts:
                flat.extend([cx + direction * lx * scale, cy + ly * scale])
            return canvas.create_polygon(flat, fill=fill, outline=out, width=max(1, int(width * scale)), joinstyle="round")

        def oval(lx1, ly1, lx2, ly2, fill, out=outline, width=3):
            x1, y1 = cx + direction * lx1 * scale, cy + ly1 * scale
            x2, y2 = cx + direction * lx2 * scale, cy + ly2 * scale
            return canvas.create_oval(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2),
                                      fill=fill, outline=out, width=max(1, int(width * scale)))

        def line(pts, fill=outline, width=3):
            flat = []
            for lx, ly in pts:
                flat.extend([cx + direction * lx * scale, cy + ly * scale])
            return canvas.create_line(flat, fill=fill, width=max(1, int(width * scale)), capstyle="round")

        # 1. Bayangan Tangan di Lantai Arena
        canvas.create_oval(
            cx - 78 * scale, cy + 68 * scale,
            cx + 78 * scale, cy + 92 * scale,
            fill="#090d16", outline=""
        )

        # Efek Aura Cahaya saat Menyerang (Punch)
        if gesture == "punch":
            canvas.create_oval(
                cx - 90 * scale, cy - 70 * scale,
                cx + 90 * scale, cy + 70 * scale,
                fill="", outline=glow, width=int(4 * scale)
            )

        # 2. Lengan Bawah (Forearm)
        poly([(-125, -24), (-48, -27), (-48, 27), (-125, 24)], base)
        poly([(-125, 2), (-48, 2), (-48, 27), (-125, 24)], shade)
        line([(-125, -24), (-48, -27)])
        line([(-125, 24), (-48, 27)])

        # Detail Khusus pada Lengan Bawah sesuai Skin
        if stype == "mecha":
            line([(-112, -10), (-60, -10)], cuff_sub, 3)
            oval(-92, -15, -80, -5, cuff_sub, outline, 2)
            oval(-92, 5, -80, 15, cuff_sub, outline, 2)
        elif stype == "magma":
            poly([(-115, -6), (-95, -14), (-75, -6), (-95, 6)], accent, "", 0)
            poly([(-105, 10), (-85, 4), (-68, 12)], cuff_sub, "", 0)
        elif stype == "toxic":
            oval(-105, 4, -90, 16, accent, "", 0)
            oval(-85, -12, -72, -2, cuff_sub, "", 0)
        elif stype == "shadow":
            line([(-115, -6), (-60, -6)], accent, 2)
            line([(-105, 8), (-70, 8)], cuff_sub, 2)
        elif stype == "human":
            # Perban tinju putih melilit pergelangan
            line([(-110, -22), (-95, 22)], "#ffffff", 2)
            line([(-90, -23), (-75, 23)], "#ffffff", 2)

        # 3. Manset / Gelang Tangan (Wrist Cuff)
        poly([(-58, -35), (-30, -35), (-30, 35), (-58, 35)], cuff_col)
        line([(-44, -35), (-44, 35)], cuff_sub, 3)

        if stype == "gold":
            oval(-48, -12, -40, 12, "#ffffff", "#b8860b", 2)
        elif stype == "boxer":
            for ly in [-20, -8, 4, 16]:
                line([(-52, ly), (-36, ly)], "#ffffff", 2)

        # 4. Gambar Gestur Tangan (Batu / Gunting / Kertas / Punch)
        if gesture in ("batu", "punch"):
            # Telapak Tangan Kepal (Fist)
            poly([(-30, -28), (14, -30), (36, -20), (38, 20), (10, 30), (-30, 26)], base)
            poly([(-30, 6), (12, 6), (36, 18), (10, 30), (-30, 26)], shade)

            # 4 Buku Jari (Knuckles)
            oval(14, -30, 44, -13, base)
            oval(18, -14, 48, 4, base)
            oval(16, 3, 46, 20, base)
            oval(10, 18, 38, 32, shade)

            # Garis sendi lipatan buku jari
            line([(16, -14), (32, -14)], shade, 2)
            line([(18, 3), (34, 3)], shade, 2)
            line([(16, 19), (30, 19)], shade, 2)

            # Ibu Jari Mengunci Jari-Jari Lain
            poly([(-18, 2), (18, 6), (26, 16), (22, 26), (2, 26), (-18, 16)], base)
            line([(-10, 16), (18, 16)], shade, 2)

            # Detail Aksesoris Skin
            if stype == "gold":
                # Cincin berlian mewah di buku jari telunjuk
                oval(22, -26, 34, -17, "#ffffff", "#ffd700", 2)
                poly([(28, -29), (32, -26), (28, -23), (24, -26)], "#a0e7e5", outline, 1)
            elif stype == "boxer":
                # Bintang emas juara tinju
                poly([(2, -8), (7, 4), (18, 4), (9, 11), (13, 22), (2, 15), (-9, 22), (-5, 11), (-14, 4), (-3, 4)], accent, outline, 1)
                # Kilauan lengkung sarung tinju
                oval(-15, -24, 15, -14, "#ffffff", "", 0)
            elif stype == "mecha":
                oval(-10, -12, 6, 4, cuff_sub, outline, 2)
            elif stype == "toxic":
                poly([(6, 24), (10, 36), (2, 34)], accent, outline, 1)

            if gesture == "punch":
                # Garis kecepatan / wind speed lines melesat
                for sy in [-26, -10, 8, 24]:
                    line([(-140, sy), (-50, sy)], "#ffffff", 4)
                # Gelombang kejut angin di depan tinju
                oval(32, -40, 60, 40, "", glow, 3)

        elif gesture == "gunting":
            # Telapak Tangan Gunting
            poly([(-30, -28), (12, -26), (18, 0), (14, 26), (-30, 26)], base)
            poly([(-30, 6), (12, 6), (14, 26), (-30, 26)], shade)

            # Jari Manis & Kelingking terlipat
            oval(-2, 8, 28, 28, shade)
            poly([(-16, 2), (14, 6), (22, 14), (16, 22), (-16, 14)], base)

            # Bilah Jari Telunjuk (miring sedikit ke atas)
            poly([(10, -26), (84, -35), (88, -20), (16, -11)], base)
            line([(10, -26), (84, -35)])
            line([(88, -20), (16, -11)])
            oval(70, -33, 88, -20, shade)
            line([(45, -28), (45, -17)], shade, 2)

            # Bilah Jari Tengah (lurus ke depan)
            poly([(12, -9), (86, -2), (82, 14), (14, 9)], base)
            line([(12, -9), (86, -2)])
            line([(82, 14), (14, 9)])
            oval(68, -2, 84, 13, shade)
            line([(46, -4), (46, 7)], shade, 2)

            # Kilau tajam di ujung gunting
            line([(80, -28), (86, -10)], "#ffffff", 2)

            if stype == "gold":
                oval(-6, 6, 8, 18, "#ffffff", "#ffd700", 2)
            elif stype == "mecha":
                line([(20, -22), (70, -29)], cuff_sub, 2)
                line([(22, 1), (70, 5)], cuff_sub, 2)

        elif gesture == "kertas":
            # Telapak Tangan Membuka
            poly([(-30, -28), (8, -30), (14, 24), (-30, 26)], base)
            poly([(-30, 5), (10, 5), (14, 24), (-30, 26)], shade)

            # 4 Jari Membuka Menghadap Depan
            # Telunjuk
            poly([(8, -26), (86, -26), (86, -13), (8, -13)], base)
            oval(72, -26, 86, -13, shade)
            # Tengah
            poly([(10, -11), (94, -11), (94, 2), (10, 2)], base)
            oval(78, -11, 94, 2, shade)
            # Manis
            poly([(8, 4), (88, 4), (88, 16), (8, 16)], shade)
            oval(74, 4, 88, 16, base)
            # Kelingking
            poly([(6, 18), (76, 18), (76, 29), (6, 29)], shade)
            oval(64, 18, 76, 29, base)

            # Ibu Jari Membuka Menghadap Serong Bawah
            poly([(-16, 6), (16, 14), (42, 38), (30, 48), (-4, 26)], base)
            oval(28, 32, 42, 46, shade)

            if stype == "mecha":
                for fy in [-20, -5, 10]:
                    line([(20, fy), (65, fy)], cuff_sub, 2)
            elif stype == "magma":
                poly([(20, -8), (35, -16), (45, -8)], accent, "", 0)

        # 5. Efek Pusing & Bintang jika Terkena Hantaman (Hurt)
        if state == "hurt":
            star_offsets = [(-25, -60), (0, -75), (28, -60)]
            for so_x, so_y in star_offsets:
                sx = cx + so_x * scale
                sy = cy + so_y * scale
                canvas.create_text(sx, sy, text="⭐", font=("Arial", int(17 * scale)), fill="#ffd166")
            canvas.create_text(cx, cy - 45 * scale, text="💢", font=("Arial", int(19 * scale)), fill="#ff4d4d")


# ---------------------------------------------------------------------------
# SISTEM PARTIKEL & VISUAL FX (POW!, SCREEN SHAKE, DAMAGE TEXT)
# ---------------------------------------------------------------------------
class FXSystem:
    def __init__(self):
        self.particles = []
        self.comic_popups = []
        self.damage_numbers = []

    def clear(self):
        self.particles.clear()
        self.comic_popups.clear()
        self.damage_numbers.clear()

    def spawn_punch_impact(self, x, y, glow_col="#ffbe0b"):
        colors = ["#ff0054", "#ff5400", "#ffbd00", "#ffffff", glow_col]
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(6, 16)
            self.particles.append({
                "x": x,
                "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 2.5,
                "life": 1.0,
                "decay": random.uniform(0.04, 0.08),
                "radius": random.uniform(5, 10),
                "color": random.choice(colors),
            })

        comic_texts = ["POW!", "BAM!", "SMACK!", "CRUNCH!", "BOOM!"]
        self.comic_popups.append({
            "x": x,
            "y": y - 10,
            "text": random.choice(comic_texts),
            "scale": 0.5,
            "max_scale": 1.5,
            "life": 1.0,
            "decay": 0.035,
            "color": "#ffe600",
            "outline": "#d90429",
        })

    def spawn_clash(self, x, y):
        for _ in range(14):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(4, 12)
            self.particles.append({
                "x": x,
                "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": 1.0,
                "decay": 0.06,
                "radius": random.uniform(4, 8),
                "color": "#00f5d4",
            })
        self.comic_popups.append({
            "x": x,
            "y": y - 10,
            "text": "CLANG!",
            "scale": 0.5,
            "max_scale": 1.3,
            "life": 1.0,
            "decay": 0.04,
            "color": "#00f5d4",
            "outline": "#073b4c",
        })

    def spawn_damage(self, x, y, text="-1 NYAWA"):
        self.damage_numbers.append({
            "x": x,
            "y": y,
            "vy": -2.8,
            "text": text,
            "life": 1.0,
            "decay": 0.025,
            "color": "#ff3838",
        })

    def spawn_confetti(self, width, height):
        colors = ["#ff0054", "#9b5de5", "#f15bb5", "#fee440", "#00bbf9", "#00f5d4"]
        for _ in range(40):
            self.particles.append({
                "x": random.uniform(50, width - 50),
                "y": random.uniform(50, 180),
                "vx": random.uniform(-4, 4),
                "vy": random.uniform(2, 6),
                "life": 1.0,
                "decay": random.uniform(0.01, 0.02),
                "radius": random.uniform(6, 11),
                "color": random.choice(colors),
            })

    def update(self):
        for p in self.particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.35
            p["life"] -= p["decay"]
            if p["life"] <= 0:
                self.particles.remove(p)

        for cp in self.comic_popups[:]:
            if cp["scale"] < cp["max_scale"]:
                cp["scale"] += 0.16
            cp["y"] -= 0.6
            cp["life"] -= cp["decay"]
            if cp["life"] <= 0:
                self.comic_popups.remove(cp)

        for dn in self.damage_numbers[:]:
            dn["y"] += dn["vy"]
            dn["life"] -= dn["decay"]
            if dn["life"] <= 0:
                self.damage_numbers.remove(dn)

    def draw(self, canvas):
        for p in self.particles:
            r = p["radius"] * p["life"]
            canvas.create_oval(
                p["x"] - r, p["y"] - r, p["x"] + r, p["y"] + r,
                fill=p["color"], outline=""
            )

        for cp in self.comic_popups:
            sc = cp["scale"]
            cx, cy = cp["x"], cp["y"]
            r_outer = 48 * sc
            r_inner = 26 * sc
            pts = []
            for i in range(16):
                ang = i * (math.pi / 8)
                r = r_outer if i % 2 == 0 else r_inner
                pts.extend([cx + math.cos(ang) * r, cy + math.sin(ang) * r])
            canvas.create_polygon(pts, fill=cp["color"], outline=cp["outline"], width=3)
            font_size = max(10, int(19 * sc))
            canvas.create_text(
                cx, cy, text=cp["text"],
                font=("Impact", font_size, "bold"),
                fill=cp["outline"]
            )

        for dn in self.damage_numbers:
            alpha_font = max(12, int(22 * dn["life"]))
            canvas.create_text(
                dn["x"] + 2, dn["y"] + 2, text=dn["text"],
                font=("Arial Black", alpha_font, "bold"), fill="#200000"
            )
            canvas.create_text(
                dn["x"], dn["y"], text=dn["text"],
                font=("Arial Black", alpha_font, "bold"), fill=dn["color"]
            )


# ---------------------------------------------------------------------------
# KELAS UTAMA GAME (TKINTER 2D FULL COLOR ARENA)
# ---------------------------------------------------------------------------
class SuitGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Batu Gunting Kertas 2D - Arena Tawuran Jari Full Color")
        self.geometry("1140x730")
        self.minsize(1080, 700)
        self.configure(bg="#0b0f19")

        # Sound & FX
        self.sound = SoundManager()
        self.fx = FXSystem()

        # Pengaturan Default Permainan
        self.max_lives = 5
        self.p1_lives = self.max_lives
        self.p2_lives = self.max_lives
        self.p1_hp_display = float(self.max_lives)
        self.p2_hp_display = float(self.max_lives)

        self.p1_skin = "classic"
        self.p2_skin = "cyborg"
        self.ai_skin = "magma"

        # Game State
        self.mode = "ai"  # 'ai' atau 'pvp'
        self.state = "idle"  # 'idle', 'countdown', 'animating', 'game_over'
        self.round_num = 1
        self.match_wins = {"p1": 0, "p2": 0, "draw": 0}

        # Pilihan Ronde
        self.p1_choice = None
        self.p2_choice = None
        self.p1_locked = False
        self.p2_locked = False

        # Variabel Animasi Pukulan
        self.anim_frame = 0
        self.anim_type = None  # 'p1_punch', 'p2_punch', 'draw'
        self.p1_pos_x = 260
        self.p1_pos_y = 280
        self.p2_pos_x = 860
        self.p2_pos_y = 280
        self.screen_shake_x = 0
        self.screen_shake_y = 0
        self.shake_duration = 0

        # Breathing Bobbing Tick
        self.idle_tick = 0

        # UI Container
        self.main_container = tk.Frame(self, bg="#0b0f19")
        self.main_container.pack(fill="both", expand=True)

        # Bind Global Keyboard Shortcuts
        self.bind("<Key>", self.handle_key_press)

        # Tampilkan Menu Utama
        self.show_main_menu()

        # Mulai Main Loop Animasi
        self.run_loop()

    # -----------------------------------------------------------------------
    # ANIMATION LOOP (50-60 FPS)
    # -----------------------------------------------------------------------
    def run_loop(self):
        self.idle_tick += 1

        # Screen shake update
        if self.shake_duration > 0:
            self.shake_duration -= 1
            self.screen_shake_x = random.randint(-8, 8)
            self.screen_shake_y = random.randint(-8, 8)
        else:
            self.screen_shake_x = 0
            self.screen_shake_y = 0

        # Smooth HP transition
        if abs(self.p1_hp_display - self.p1_lives) > 0.05:
            self.p1_hp_display += (self.p1_lives - self.p1_hp_display) * 0.15
            self.update_hp_bars()
        if abs(self.p2_hp_display - self.p2_lives) > 0.05:
            self.p2_hp_display += (self.p2_lives - self.p2_hp_display) * 0.15
            self.update_hp_bars()

        # Update FX particles
        self.fx.update()

        # Jalankan animasi pertarungan jika aktif
        if self.state == "animating":
            self.update_battle_animation()

        # Render Canvas Arena jika sedang aktif
        if hasattr(self, "arena_canvas") and self.arena_canvas.winfo_exists():
            self.render_arena()

        self.after(20, self.run_loop)

    def clear_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # -----------------------------------------------------------------------
    # LAYAR: MENU UTAMA
    # -----------------------------------------------------------------------
    def show_main_menu(self):
        self.clear_container()
        self.state = "menu"

        menu_frame = tk.Frame(self.main_container, bg="#0b0f19")
        menu_frame.pack(fill="both", expand=True)

        title_box = tk.Frame(menu_frame, bg="#0b0f19")
        title_box.pack(pady=(35, 10))

        tk.Label(
            title_box,
            text="BATU • GUNTING • KERTAS",
            font=("Impact", 44),
            fg="#f72585",
            bg="#0b0f19",
        ).pack()

        tk.Label(
            title_box,
            text="⚔️ 2D FIGHTING ARENA - KALAH SUIT LANGSUNG DITONJOK! ⚔️",
            font=("Segoe UI", 14, "bold"),
            fg="#4cc9f0",
            bg="#0b0f19",
        ).pack(pady=(4, 0))

        # Preview Dua Tangan Berhadapan
        preview_canvas = tk.Canvas(menu_frame, width=720, height=200, bg="#121826", highlightthickness=2, highlightbackground="#3a0ca3")
        preview_canvas.pack(pady=15)
        self.draw_menu_preview(preview_canvas)

        # Tombol-tombol Menu
        btn_box = tk.Frame(menu_frame, bg="#0b0f19")
        btn_box.pack(pady=10)

        def make_btn(parent, text, color, hover, cmd):
            return tk.Button(
                parent,
                text=text,
                font=("Segoe UI", 14, "bold"),
                width=23,
                height=2,
                bg=color,
                fg="white",
                bd=0,
                cursor="hand2",
                activebackground=hover,
                activeforeground="white",
                command=cmd,
            )

        btn_ai = make_btn(btn_box, "🤖 MAIN LAWAN AI", "#4361ee", "#3a0ca3", self.start_vs_ai)
        btn_ai.grid(row=0, column=0, padx=15, pady=8)

        btn_pvp = make_btn(btn_box, "👥 2 PLAYER (1 LAPTOP)", "#f72585", "#b5179e", self.start_vs_pvp)
        btn_pvp.grid(row=0, column=1, padx=15, pady=8)

        btn_skin = make_btn(btn_box, "🎨 KOLEKSI SKIN TANGAN", "#7209b7", "#560bad", self.show_skin_menu)
        btn_skin.grid(row=1, column=0, padx=15, pady=8)

        btn_sett = make_btn(btn_box, "⚙️ ATURAN & NYAWA", "#2a9d8f", "#21867a", self.show_settings_modal)
        btn_sett.grid(row=1, column=1, padx=15, pady=8)

        # Bottom info bar
        bottom_bar = tk.Frame(menu_frame, bg="#0b0f19")
        bottom_bar.pack(side="bottom", pady=22)

        sound_text = "🔊 SUARA: ON" if self.sound.enabled else "🔇 SUARA: OFF"
        self.sound_btn = tk.Button(
            bottom_bar,
            text=sound_text,
            font=("Segoe UI", 11, "bold"),
            bg="#253248",
            fg="#ffd166",
            bd=0,
            padx=16,
            pady=5,
            cursor="hand2",
            command=self.toggle_sound,
        )
        self.sound_btn.pack(side="left", padx=15)

        exit_btn = tk.Button(
            bottom_bar,
            text="❌ KELUAR",
            font=("Segoe UI", 11, "bold"),
            bg="#d90429",
            fg="white",
            bd=0,
            padx=18,
            pady=5,
            cursor="hand2",
            command=self.destroy,
        )
        exit_btn.pack(side="left", padx=15)

    def draw_menu_preview(self, canvas):
        canvas.delete("all")
        for y in range(40, 200, 40):
            canvas.create_line(0, y, 720, y, fill="#1c2538")
        for x in range(40, 720, 50):
            canvas.create_line(x, 0, x, 200, fill="#1c2538")

        skin1 = SKINS.get(self.p1_skin, SKINS["classic"])
        skin2 = SKINS.get(self.p2_skin if self.mode == "pvp" else self.ai_skin, SKINS["cyborg"])

        HandRenderer.draw(canvas, 200, 100, "batu", 1, skin1, scale=1.05)
        HandRenderer.draw(canvas, 520, 100, "kertas", -1, skin2, scale=1.05)

        canvas.create_text(360, 100, text="VS", font=("Impact", 40), fill="#ffe600")

    def toggle_sound(self):
        self.sound.enabled = not self.sound.enabled
        txt = "🔊 SUARA: ON" if self.sound.enabled else "🔇 SUARA: OFF"
        if hasattr(self, "sound_btn") and self.sound_btn.winfo_exists():
            self.sound_btn.config(text=txt)
        if hasattr(self, "ingame_sound_btn") and self.ingame_sound_btn.winfo_exists():
            self.ingame_sound_btn.config(text="🔊" if self.sound.enabled else "🔇")
        self.sound.play("select")

    # -----------------------------------------------------------------------
    # LAYAR: KOLEKSI & PILIH SKIN TANGAN
    # -----------------------------------------------------------------------
    def show_skin_menu(self):
        self.clear_container()
        self.state = "skin_select"

        container = tk.Frame(self.main_container, bg="#0b0f19")
        container.pack(fill="both", expand=True, padx=25, pady=15)

        top = tk.Frame(container, bg="#0b0f19")
        top.pack(fill="x", pady=(0, 10))

        tk.Button(
            top,
            text="◀ KEMBALI KE MENU",
            font=("Segoe UI", 11, "bold"),
            bg="#3a0ca3",
            fg="white",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.show_main_menu,
        ).pack(side="left")

        tk.Label(
            top,
            text="🎨 PILIH SKIN TANGAN (7 KARAKTER)",
            font=("Impact", 28),
            fg="#4cc9f0",
            bg="#0b0f19",
        ).pack(side="left", padx=25)

        panels = tk.Frame(container, bg="#0b0f19")
        panels.pack(fill="both", expand=True)

        self.preview_gesture = "batu"

        # Kolom Kiri: Player 1
        p1_box = tk.LabelFrame(
            panels,
            text="  [ SKIN PLAYER 1 ]  ",
            font=("Segoe UI", 13, "bold"),
            fg="#4cc9f0",
            bg="#141923",
            bd=2,
            relief="groove",
        )
        p1_box.pack(side="left", fill="both", expand=True, padx=8, pady=5)

        self.p1_skin_canvas = tk.Canvas(p1_box, width=320, height=210, bg="#0e131d", highlightthickness=0)
        self.p1_skin_canvas.pack(pady=8)

        self.p1_skin_label = tk.Label(p1_box, text="", font=("Segoe UI", 13, "bold"), fg="#ffd166", bg="#141923")
        self.p1_skin_label.pack()
        self.p1_skin_desc = tk.Label(p1_box, text="", font=("Segoe UI", 9), fg="#a0aec0", bg="#141923", wraplength=280)
        self.p1_skin_desc.pack(pady=(0, 8))

        p1_grid = tk.Frame(p1_box, bg="#141923")
        p1_grid.pack(pady=4)
        for idx, sk_key in enumerate(SKIN_KEYS):
            sk = SKINS[sk_key]
            btn = tk.Button(
                p1_grid,
                text=sk["name"],
                font=("Segoe UI", 9, "bold"),
                bg=sk["cuff"],
                fg="white",
                bd=0,
                width=14,
                cursor="hand2",
                command=lambda k=sk_key: self.set_p1_skin(k),
            )
            btn.grid(row=idx // 2, column=idx % 2, padx=4, pady=3)

        # Kolom Kanan: Player 2 / AI
        p2_box = tk.LabelFrame(
            panels,
            text="  [ SKIN PLAYER 2 / AI ]  ",
            font=("Segoe UI", 13, "bold"),
            fg="#f72585",
            bg="#141923",
            bd=2,
            relief="groove",
        )
        p2_box.pack(side="right", fill="both", expand=True, padx=8, pady=5)

        self.p2_skin_canvas = tk.Canvas(p2_box, width=320, height=210, bg="#0e131d", highlightthickness=0)
        self.p2_skin_canvas.pack(pady=8)

        self.p2_skin_label = tk.Label(p2_box, text="", font=("Segoe UI", 13, "bold"), fg="#ffd166", bg="#141923")
        self.p2_skin_label.pack()
        self.p2_skin_desc = tk.Label(p2_box, text="", font=("Segoe UI", 9), fg="#a0aec0", bg="#141923", wraplength=280)
        self.p2_skin_desc.pack(pady=(0, 8))

        p2_grid = tk.Frame(p2_box, bg="#141923")
        p2_grid.pack(pady=4)
        for idx, sk_key in enumerate(SKIN_KEYS):
            sk = SKINS[sk_key]
            btn = tk.Button(
                p2_grid,
                text=sk["name"],
                font=("Segoe UI", 9, "bold"),
                bg=sk["cuff"],
                fg="white",
                bd=0,
                width=14,
                cursor="hand2",
                command=lambda k=sk_key: self.set_p2_skin(k),
            )
            btn.grid(row=idx // 2, column=idx % 2, padx=4, pady=3)

        # Bar Preview Uji Gerakan
        test_bar = tk.Frame(container, bg="#0b0f19")
        test_bar.pack(side="bottom", pady=8)

        tk.Label(test_bar, text="Tes Pose Skin:", font=("Segoe UI", 11, "bold"), fg="#ffd166", bg="#0b0f19").pack(side="left", padx=10)
        for gest, lbl in [("batu", "🪨 Batu"), ("gunting", "✂️ Gunting"), ("kertas", "📄 Kertas"), ("punch", "💥 Tonjokan")]:
            tk.Button(
                test_bar,
                text=lbl,
                font=("Segoe UI", 10, "bold"),
                bg="#253248",
                fg="white",
                bd=0,
                padx=10,
                pady=4,
                cursor="hand2",
                command=lambda g=gest: self.change_preview_gesture(g),
            ).pack(side="left", padx=5)

        self.refresh_skin_preview()

    def set_p1_skin(self, skin_id):
        self.p1_skin = skin_id
        self.sound.play("select")
        self.refresh_skin_preview()

    def set_p2_skin(self, skin_id):
        self.p2_skin = skin_id
        self.ai_skin = skin_id
        self.sound.play("select")
        self.refresh_skin_preview()

    def change_preview_gesture(self, gesture):
        self.preview_gesture = gesture
        self.sound.play("select")
        self.refresh_skin_preview()

    def refresh_skin_preview(self):
        if not hasattr(self, "p1_skin_canvas") or not self.p1_skin_canvas.winfo_exists():
            return
        if not hasattr(self, "p2_skin_canvas") or not self.p2_skin_canvas.winfo_exists():
            return

        sk1 = SKINS.get(self.p1_skin, SKINS["classic"])
        sk2 = SKINS.get(self.p2_skin, SKINS["cyborg"])

        self.p1_skin_canvas.delete("all")
        HandRenderer.draw(self.p1_skin_canvas, 160, 105, self.preview_gesture, 1, sk1, scale=1.1)
        if hasattr(self, "p1_skin_label") and self.p1_skin_label.winfo_exists():
            self.p1_skin_label.config(text=f"{sk1['name']}")
        if hasattr(self, "p1_skin_desc") and self.p1_skin_desc.winfo_exists():
            self.p1_skin_desc.config(text=sk1["tagline"])

        self.p2_skin_canvas.delete("all")
        HandRenderer.draw(self.p2_skin_canvas, 160, 105, self.preview_gesture, -1, sk2, scale=1.1)
        if hasattr(self, "p2_skin_label") and self.p2_skin_label.winfo_exists():
            self.p2_skin_label.config(text=f"{sk2['name']}")
        if hasattr(self, "p2_skin_desc") and self.p2_skin_desc.winfo_exists():
            self.p2_skin_desc.config(text=sk2["tagline"])

    # -----------------------------------------------------------------------
    # MODAL PENGATURAN & ATURAN NYAWA
    # -----------------------------------------------------------------------
    def show_settings_modal(self):
        modal = tk.Toplevel(self)
        modal.title("Pengaturan Game & Sistem Nyawa")
        modal.geometry("540x480")
        modal.configure(bg="#141923")
        modal.resizable(False, False)
        modal.transient(self)
        modal.grab_set()

        tk.Label(
            modal,
            text="⚙️ ATURAN & SISTEM NYAWA",
            font=("Impact", 22),
            fg="#4cc9f0",
            bg="#141923",
        ).pack(pady=(18, 8))

        content = (
            "📖 ATURAN SUIT BATU GUNTING KERTAS:\n"
            "• Batu mengalahkan Gunting 🪨 > ✂️\n"
            "• Gunting memotong Kertas ✂️ > 📄\n"
            "• Kertas membungkus Batu 📄 > 🪨\n\n"
            "🥊 SISTEM PUKULAN & NYAWA:\n"
            "• Tangan yang menang akan melompat dan MENONJOK tangan yang kalah!\n"
            "• Tangan yang terkena pukulan akan berkurang 1 NYAWA (HP).\n"
            "• Jika suit SERI, kedua tangan saling bentur tanpa ada yang terluka.\n"
            "• Pemain pertama yang nyawanya habis (0 HP) dinyatakan K.O.!\n\n"
            "👥 KONTROL 2 PLAYER DI 1 LAPTOP:\n"
            "• Player 1: Tombol [A] Batu, [S] Gunting, [D] Kertas\n"
            "• Player 2: Tombol [J] Batu, [K] Gunting, [L] Kertas (atau Panah ◄ ▼ ►)\n"
            "Pilihan pemain ditutup rahasia sampai kedua pemain selesai memilih!"
        )

        tk.Label(
            modal,
            text=content,
            font=("Segoe UI", 10),
            justify="left",
            fg="#e2e8f0",
            bg="#141923",
        ).pack(padx=25, pady=4)

        lives_box = tk.Frame(modal, bg="#141923")
        lives_box.pack(pady=12)

        tk.Label(
            lives_box,
            text="Pilih Jumlah Nyawa:",
            font=("Segoe UI", 12, "bold"),
            fg="#ffd166",
            bg="#141923",
        ).pack(side="left", padx=10)

        live_buttons = {}

        def select_lives(num):
            self.set_lives(num)
            for n, b in live_buttons.items():
                b.config(bg="#f72585" if n == num else "#253248")

        for num in [3, 5, 7]:
            bg_col = "#f72585" if self.max_lives == num else "#253248"
            b = tk.Button(
                lives_box,
                text=f"{num} Nyawa",
                font=("Segoe UI", 10, "bold"),
                bg=bg_col,
                fg="white",
                bd=0,
                padx=12,
                pady=4,
                cursor="hand2",
                command=lambda n=num: select_lives(n),
            )
            b.pack(side="left", padx=5)
            live_buttons[num] = b

        tk.Button(
            modal,
            text="TUTUP",
            font=("Segoe UI", 11, "bold"),
            bg="#3a0ca3",
            fg="white",
            bd=0,
            padx=20,
            pady=6,
            cursor="hand2",
            command=modal.destroy,
        ).pack(pady=8)

    def set_lives(self, num):
        self.max_lives = num
        self.p1_lives = num
        self.p2_lives = num
        self.p1_hp_display = float(num)
        self.p2_hp_display = float(num)
        self.sound.play("select")

    # -----------------------------------------------------------------------
    # MEMULAI PERMAINAN
    # -----------------------------------------------------------------------
    def start_vs_ai(self):
        self.mode = "ai"
        self.reset_match()
        self.show_arena_screen()

    def start_vs_pvp(self):
        self.mode = "pvp"
        self.reset_match()
        self.show_arena_screen()

    def reset_match(self):
        self.p1_lives = self.max_lives
        self.p2_lives = self.max_lives
        self.p1_hp_display = float(self.max_lives)
        self.p2_hp_display = float(self.max_lives)
        self.round_num = 1
        self.state = "idle"
        self.p1_choice = None
        self.p2_choice = None
        self.p1_locked = False
        self.p2_locked = False
        self.fx.clear()
        self.reset_hand_positions()

    def reset_hand_positions(self):
        self.p1_pos_x = 260
        self.p1_pos_y = 280
        self.p2_pos_x = 860
        self.p2_pos_y = 280

    # -----------------------------------------------------------------------
    # LAYAR: ARENA PERTANDINGAN
    # -----------------------------------------------------------------------
    def show_arena_screen(self):
        self.clear_container()

        arena_frame = tk.Frame(self.main_container, bg="#0b0f19")
        arena_frame.pack(fill="both", expand=True)

        # 1. Top HUD
        top_hud = tk.Frame(arena_frame, bg="#10141e", bd=1, relief="ridge")
        top_hud.pack(fill="x", padx=10, pady=(8, 0))

        # P1 Profil (Kiri)
        p1_prof = tk.Frame(top_hud, bg="#10141e")
        p1_prof.pack(side="left", padx=15, pady=8)

        tk.Label(
            p1_prof,
            text=f"PLAYER 1 ({SKINS[self.p1_skin]['name']})",
            font=("Segoe UI", 12, "bold"),
            fg="#4cc9f0",
            bg="#10141e",
        ).pack(anchor="w")

        self.p1_hearts_label = tk.Label(
            p1_prof,
            text=self.get_hearts_str(self.p1_lives),
            font=("Segoe UI", 15),
            fg="#ff3838",
            bg="#10141e",
        )
        self.p1_hearts_label.pack(anchor="w")

        self.p1_hp_canvas = tk.Canvas(p1_prof, width=220, height=18, bg="#1c2538", highlightthickness=1, highlightbackground="#4cc9f0")
        self.p1_hp_canvas.pack(pady=2)

        self.p1_hp_text = tk.Label(
            p1_prof,
            text=f"HP: {self.p1_lives} / {self.max_lives}",
            font=("Segoe UI", 10, "bold"),
            fg="#e2e8f0",
            bg="#10141e",
        )
        self.p1_hp_text.pack(anchor="w")

        # Center Status (Ronde & Tombol Aksi Cepat)
        center_box = tk.Frame(top_hud, bg="#10141e")
        center_box.pack(side="left", expand=True)

        self.round_label = tk.Label(
            center_box,
            text=f"ROUND {self.round_num}",
            font=("Impact", 22),
            fg="#ffd166",
            bg="#10141e",
        )
        self.round_label.pack()

        mode_title = "MODE: LAWAN AI 🤖" if self.mode == "ai" else "MODE: 2 PLAYER 👥"
        tk.Label(
            center_box,
            text=mode_title,
            font=("Segoe UI", 10, "bold"),
            fg="#a0aec0",
            bg="#10141e",
        ).pack()

        hud_nav = tk.Frame(center_box, bg="#10141e")
        hud_nav.pack(pady=3)

        sound_icon = "🔊" if self.sound.enabled else "🔇"
        self.ingame_sound_btn = tk.Button(
            hud_nav,
            text=sound_icon,
            font=("Segoe UI", 10, "bold"),
            bg="#253248",
            fg="white",
            bd=0,
            padx=10,
            cursor="hand2",
            command=self.toggle_sound,
        )
        self.ingame_sound_btn.pack(side="left", padx=4)

        tk.Button(
            hud_nav,
            text="Menu Utama",
            font=("Segoe UI", 10, "bold"),
            bg="#d90429",
            fg="white",
            bd=0,
            padx=12,
            cursor="hand2",
            command=self.show_main_menu,
        ).pack(side="left", padx=4)

        tk.Button(
            hud_nav,
            text="Ganti Skin",
            font=("Segoe UI", 10, "bold"),
            bg="#7209b7",
            fg="white",
            bd=0,
            padx=12,
            cursor="hand2",
            command=self.show_skin_menu,
        ).pack(side="left", padx=4)

        # P2 / AI Profil (Kanan)
        p2_prof = tk.Frame(top_hud, bg="#10141e")
        p2_prof.pack(side="right", padx=15, pady=8)

        p2_skin_key = self.p2_skin if self.mode == "pvp" else self.ai_skin
        p2_title = f"AI ({SKINS[p2_skin_key]['name']})" if self.mode == "ai" else f"PLAYER 2 ({SKINS[p2_skin_key]['name']})"
        tk.Label(
            p2_prof,
            text=p2_title,
            font=("Segoe UI", 12, "bold"),
            fg="#f72585",
            bg="#10141e",
        ).pack(anchor="e")

        self.p2_hearts_label = tk.Label(
            p2_prof,
            text=self.get_hearts_str(self.p2_lives),
            font=("Segoe UI", 15),
            fg="#ff3838",
            bg="#10141e",
        )
        self.p2_hearts_label.pack(anchor="e")

        self.p2_hp_canvas = tk.Canvas(p2_prof, width=220, height=18, bg="#1c2538", highlightthickness=1, highlightbackground="#f72585")
        self.p2_hp_canvas.pack(pady=2)

        self.p2_hp_text = tk.Label(
            p2_prof,
            text=f"HP: {self.p2_lives} / {self.max_lives}",
            font=("Segoe UI", 10, "bold"),
            fg="#e2e8f0",
            bg="#10141e",
        )
        self.p2_hp_text.pack(anchor="e")

        # 2. Main Combat Canvas (Arena 2D)
        self.arena_canvas = tk.Canvas(arena_frame, width=1120, height=440, bg="#0d111a", highlightthickness=0)
        self.arena_canvas.pack(fill="both", expand=True, padx=10, pady=5)

        # 3. Bottom Controls Panel
        self.controls_frame = tk.Frame(arena_frame, bg="#10141e", bd=1, relief="ridge")
        self.controls_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.build_controls_ui()
        self.update_hp_bars()

    def get_hearts_str(self, lives):
        red = "❤️" * max(0, lives)
        black = "🖤" * max(0, self.max_lives - lives)
        return red + black

    def update_hp_bars(self):
        if not hasattr(self, "p1_hp_canvas") or not self.p1_hp_canvas.winfo_exists():
            return
        if not hasattr(self, "p2_hp_canvas") or not self.p2_hp_canvas.winfo_exists():
            return

        # Update HP Bar Player 1
        self.p1_hp_canvas.delete("all")
        pct1 = max(0.0, self.p1_hp_display / self.max_lives)
        fill1 = "#06d6a0" if pct1 > 0.5 else ("#ffd166" if pct1 > 0.25 else "#ef233c")
        self.p1_hp_canvas.create_rectangle(0, 0, 220 * pct1, 18, fill=fill1, outline="")
        if hasattr(self, "p1_hearts_label") and self.p1_hearts_label.winfo_exists():
            self.p1_hearts_label.config(text=self.get_hearts_str(self.p1_lives))
        if hasattr(self, "p1_hp_text") and self.p1_hp_text.winfo_exists():
            self.p1_hp_text.config(text=f"HP: {self.p1_lives} / {self.max_lives}")

        # Update HP Bar Player 2 / AI
        self.p2_hp_canvas.delete("all")
        pct2 = max(0.0, self.p2_hp_display / self.max_lives)
        fill2 = "#06d6a0" if pct2 > 0.5 else ("#ffd166" if pct2 > 0.25 else "#ef233c")
        w2 = 220 * pct2
        self.p2_hp_canvas.create_rectangle(220 - w2, 0, 220, 18, fill=fill2, outline="")
        if hasattr(self, "p2_hearts_label") and self.p2_hearts_label.winfo_exists():
            self.p2_hearts_label.config(text=self.get_hearts_str(self.p2_lives))
        if hasattr(self, "p2_hp_text") and self.p2_hp_text.winfo_exists():
            self.p2_hp_text.config(text=f"HP: {self.p2_lives} / {self.max_lives}")

    # -----------------------------------------------------------------------
    # PANEL KONTROL SUIT (VS AI ATAU 2 PLAYER LOCAL)
    # -----------------------------------------------------------------------
    def build_controls_ui(self):
        if not hasattr(self, "controls_frame") or not self.controls_frame.winfo_exists():
            return
        for w in self.controls_frame.winfo_children():
            w.destroy()

        if self.mode == "ai":
            box = tk.Frame(self.controls_frame, bg="#10141e")
            box.pack(pady=8)

            tk.Label(
                box,
                text="PILIH TANGANMU (Klik Tombol atau Tekan Tombol Keyboard [A], [S], [D]):",
                font=("Segoe UI", 11, "bold"),
                fg="#ffd166",
                bg="#10141e",
            ).pack(pady=(0, 6))

            btn_row = tk.Frame(box, bg="#10141e")
            btn_row.pack()

            actions = [
                ("batu", "🪨 BATU [A]", "#e76f51"),
                ("gunting", "✂️ GUNTING [S]", "#f4a261"),
                ("kertas", "📄 KERTAS [D]", "#2a9d8f"),
            ]

            for key, lbl, col in actions:
                btn = tk.Button(
                    btn_row,
                    text=lbl,
                    font=("Segoe UI", 13, "bold"),
                    bg=col,
                    fg="white",
                    bd=0,
                    width=17,
                    height=2,
                    cursor="hand2",
                    activebackground="#ffffff",
                    activeforeground="#000000",
                    command=lambda k=key: self.on_p1_choose(k),
                )
                btn.pack(side="left", padx=12)

        else:
            dual_box = tk.Frame(self.controls_frame, bg="#10141e")
            dual_box.pack(fill="x", padx=20, pady=8)

            # Sisi Kiri: Player 1 (A, S, D)
            p1_ctrl = tk.Frame(dual_box, bg="#10141e")
            p1_ctrl.pack(side="left")

            p1_status_text = "🔒 SUDAH SIAP!" if self.p1_locked else "PILIH: [A] Batu | [S] Gunting | [D] Kertas"
            p1_status_color = "#06d6a0" if self.p1_locked else "#4cc9f0"
            tk.Label(
                p1_ctrl,
                text=f"PLAYER 1: {p1_status_text}",
                font=("Segoe UI", 11, "bold"),
                fg=p1_status_color,
                bg="#10141e",
            ).pack(anchor="w", pady=(0, 4))

            p1_row = tk.Frame(p1_ctrl, bg="#10141e")
            p1_row.pack(anchor="w")

            for k, sym in [("batu", "🪨 A"), ("gunting", "✂️ S"), ("kertas", "📄 D")]:
                tk.Button(
                    p1_row,
                    text=sym,
                    font=("Segoe UI", 11, "bold"),
                    bg="#4361ee" if not self.p1_locked else "#253248",
                    fg="white",
                    bd=0,
                    width=10,
                    height=1,
                    cursor="hand2",
                    command=lambda val=k: self.on_p1_choose(val),
                ).pack(side="left", padx=4)

            # Sisi Kanan: Player 2 (J, K, L / Panah)
            p2_ctrl = tk.Frame(dual_box, bg="#10141e")
            p2_ctrl.pack(side="right")

            p2_status_text = "🔒 SUDAH SIAP!" if self.p2_locked else "PILIH: [J] Batu | [K] Gunting | [L] Kertas"
            p2_status_color = "#06d6a0" if self.p2_locked else "#f72585"
            tk.Label(
                p2_ctrl,
                text=f"PLAYER 2: {p2_status_text}",
                font=("Segoe UI", 11, "bold"),
                fg=p2_status_color,
                bg="#10141e",
            ).pack(anchor="e", pady=(0, 4))

            p2_row = tk.Frame(p2_ctrl, bg="#10141e")
            p2_row.pack(anchor="e")

            for k, sym in [("batu", "🪨 J"), ("gunting", "✂️ K"), ("kertas", "📄 L")]:
                tk.Button(
                    p2_row,
                    text=sym,
                    font=("Segoe UI", 11, "bold"),
                    bg="#f72585" if not self.p2_locked else "#253248",
                    fg="white",
                    bd=0,
                    width=10,
                    height=1,
                    cursor="hand2",
                    command=lambda val=k: self.on_p2_choose(val),
                ).pack(side="left", padx=4)

    # -----------------------------------------------------------------------
    # INPUT KEYBOARD (HOTKEYS P1 & P2)
    # -----------------------------------------------------------------------
    def handle_key_press(self, event):
        if self.state != "idle":
            return

        key = event.keysym.lower()

        # Player 1: A (Batu), S (Gunting), D (Kertas)
        if key == "a":
            self.on_p1_choose("batu")
        elif key == "s":
            self.on_p1_choose("gunting")
        elif key == "d":
            self.on_p1_choose("kertas")

        # Player 2 (Hanya aktif di Mode PvP)
        if self.mode == "pvp":
            if key in ("j", "left"):
                self.on_p2_choose("batu")
            elif key in ("k", "down"):
                self.on_p2_choose("gunting")
            elif key in ("l", "right"):
                self.on_p2_choose("kertas")

    # -----------------------------------------------------------------------
    # LOGIKA PEMILIHAN SUIT
    # -----------------------------------------------------------------------
    def on_p1_choose(self, choice):
        if self.state != "idle" or self.p1_locked:
            return
        self.p1_choice = choice
        self.p1_locked = True
        self.sound.play("select")

        if self.mode == "ai":
            # AI memilih lawan secara cerdas / acak
            self.p2_choice = random.choice(CHOICES)
            self.p2_locked = True
            self.start_countdown()
        else:
            self.build_controls_ui()
            if self.p1_locked and self.p2_locked:
                self.start_countdown()

    def on_p2_choose(self, choice):
        if self.state != "idle" or self.mode != "pvp" or self.p2_locked:
            return
        self.p2_choice = choice
        self.p2_locked = True
        self.sound.play("select")
        self.build_controls_ui()

        if self.p1_locked and self.p2_locked:
            self.start_countdown()

    # -----------------------------------------------------------------------
    # HITUNGAN MUNDUR (COUNTDOWN "3.. 2.. 1.. SUIT!")
    # -----------------------------------------------------------------------
    def start_countdown(self):
        self.state = "countdown"
        self.countdown_step = 3
        self.sound.play("ready")
        self.run_countdown_step()

    def run_countdown_step(self):
        if self.countdown_step > 0:
            self.sound.play("countdown")
            self.countdown_text = f"SIAP... {self.countdown_step}!"
            self.countdown_step -= 1
            self.after(380, self.run_countdown_step)
        else:
            self.sound.play("shoot")
            self.countdown_text = "💥 SUIT! 💥"
            self.after(260, self.resolve_round)

    # -----------------------------------------------------------------------
    # LOGIKA PENENTUAN PEMENANG & PEMICU TONJOKAN
    # -----------------------------------------------------------------------
    def resolve_round(self):
        p1 = self.p1_choice
        p2 = self.p2_choice

        self.anim_frame = 0
        self.state = "animating"

        if p1 == p2:
            self.anim_type = "draw"
            self.round_result_text = f"SERI! Keduanya mengeluarkan {CHOICE_INFO[p1]['name']} {CHOICE_INFO[p1]['icon']}"
            self.match_wins["draw"] += 1
        elif (p1 == "batu" and p2 == "gunting") or \
             (p1 == "gunting" and p2 == "kertas") or \
             (p1 == "kertas" and p2 == "batu"):
            self.anim_type = "p1_punch"
            self.round_result_text = f"PLAYER 1 MENANG! ({CHOICE_INFO[p1]['icon']} {CHOICE_INFO[p1]['name']} vs {CHOICE_INFO[p2]['name']} {CHOICE_INFO[p2]['icon']})"
            self.p2_lives -= 1
            self.match_wins["p1"] += 1
        else:
            self.anim_type = "p2_punch"
            p2_name = "AI" if self.mode == "ai" else "PLAYER 2"
            self.round_result_text = f"{p2_name} MENANG! ({CHOICE_INFO[p2]['icon']} {CHOICE_INFO[p2]['name']} vs {CHOICE_INFO[p1]['name']} {CHOICE_INFO[p1]['icon']})"
            self.p1_lives -= 1
            self.match_wins["p2"] += 1

    # -----------------------------------------------------------------------
    # ANIMASI NONJOK YANG KALAH (FRAME BY FRAME)
    # -----------------------------------------------------------------------
    def update_battle_animation(self):
        self.anim_frame += 1
        frame = self.anim_frame

        # Skenario 1: Player 1 Menang -> Tangan P1 Menonjok P2
        if self.anim_type == "p1_punch":
            if frame <= 8:
                # 1. Pamerkan gestur pilihan terlebih dahulu agar jelas
                pass
            elif frame <= 14:
                # 2. Anticipation: menarik kepalan tinju ke belakang
                self.p1_pos_x -= 4
            elif frame <= 24:
                # 3. Lunge: Tinju P1 meluncur kencang menyeberang arena menuju P2
                t = (frame - 14) / 10.0
                self.p1_pos_x = 236 + t * (self.p2_pos_x - 300)
            elif frame == 25:
                # 4. IMPACT! (Pukulan telak menghantam tangan lawan)
                self.sound.play("punch")
                self.shake_duration = 10
                impact_x = self.p2_pos_x - 30
                impact_y = self.p2_pos_y
                self.fx.spawn_punch_impact(impact_x, impact_y, SKINS[self.p1_skin]["glow"])
                self.fx.spawn_damage(self.p2_pos_x, self.p2_pos_y - 65, "-1 NYAWA!")
            elif frame <= 34:
                # 5. Loser recoil: Tangan P2 terpental ke belakang akibat benturan
                self.p2_pos_x += 4
            elif frame <= 50:
                # 6. Kembali ke posisi awal
                self.p1_pos_x += (260 - self.p1_pos_x) * 0.22
                self.p2_pos_x += (860 - self.p2_pos_x) * 0.22
            else:
                self.finish_round_animation()

        # Skenario 2: Player 2 / AI Menang -> Menonjok Tangan P1
        elif self.anim_type == "p2_punch":
            if frame <= 8:
                pass
            elif frame <= 14:
                # Anticipation
                self.p2_pos_x += 4
            elif frame <= 24:
                # Lunge kencang ke kiri
                t = (frame - 14) / 10.0
                self.p2_pos_x = 884 - t * (884 - (self.p1_pos_x + 60))
            elif frame == 25:
                # IMPACT!
                self.sound.play("punch")
                self.shake_duration = 10
                impact_x = self.p1_pos_x + 30
                impact_y = self.p1_pos_y
                p2_sk = self.p2_skin if self.mode == "pvp" else self.ai_skin
                self.fx.spawn_punch_impact(impact_x, impact_y, SKINS[p2_sk]["glow"])
                self.fx.spawn_damage(self.p1_pos_x, self.p1_pos_y - 65, "-1 NYAWA!")
            elif frame <= 34:
                # P1 recoil
                self.p1_pos_x -= 4
            elif frame <= 50:
                # Return
                self.p1_pos_x += (260 - self.p1_pos_x) * 0.22
                self.p2_pos_x += (860 - self.p2_pos_x) * 0.22
            else:
                self.finish_round_animation()

        # Skenario 3: Seri (Clash) -> Kedua tangan bertabrakan di tengah
        elif self.anim_type == "draw":
            if frame <= 8:
                pass
            elif frame <= 18:
                self.p1_pos_x += 16
                self.p2_pos_x -= 16
            elif frame == 19:
                self.sound.play("clash")
                self.shake_duration = 4
                self.fx.spawn_clash(560, self.p1_pos_y)
            elif frame <= 36:
                self.p1_pos_x += (260 - self.p1_pos_x) * 0.22
                self.p2_pos_x += (860 - self.p2_pos_x) * 0.22
            else:
                self.finish_round_animation()

    def finish_round_animation(self):
        self.reset_hand_positions()

        # Periksa K.O.
        if self.p1_lives <= 0 or self.p2_lives <= 0:
            self.state = "game_over"
            self.sound.play("ko")
            w, h = self.arena_canvas.winfo_width(), self.arena_canvas.winfo_height()
            self.fx.spawn_confetti(w or 1120, h or 440)
            self.show_game_over_popup()
        else:
            self.round_num += 1
            self.round_label.config(text=f"ROUND {self.round_num}")
            self.state = "idle"
            self.p1_choice = None
            self.p2_choice = None
            self.p1_locked = False
            self.p2_locked = False
            self.build_controls_ui()

    # -----------------------------------------------------------------------
    # OVERLAY HASIL K.O.
    # -----------------------------------------------------------------------
    def show_game_over_popup(self):
        if self.p1_lives <= 0 and self.p2_lives <= 0:
            winner_title = "HASIL IMBANG MUTLAK!"
            winner_sub = "Kedua petarung sama-sama kehabisan nyawa!"
            color = "#ffd166"
        elif self.p1_lives > 0:
            winner_title = "🏆 PLAYER 1 MENANG K.O.! 🏆"
            winner_sub = "Pukulan beruntunmu berhasil menumbangkan lawan!"
            color = "#4cc9f0"
            self.sound.play("victory")
        else:
            p2_name = "AI KOMPUTER" if self.mode == "ai" else "PLAYER 2"
            winner_title = f"🏆 {p2_name} MEMENANGKAN MATCH! 🏆"
            winner_sub = f"{p2_name} memberikan pukulan K.O. terakhir yang mematikan!"
            color = "#f72585"
            self.sound.play("victory")

        overlay = tk.Frame(self.arena_canvas, bg="#10141e", bd=3, relief="ridge")
        overlay.place(relx=0.5, rely=0.5, anchor="center", width=580, height=270)

        tk.Label(overlay, text="KNOCKOUT!", font=("Impact", 38), fg="#ff0054", bg="#10141e").pack(pady=(15, 2))
        tk.Label(overlay, text=winner_title, font=("Segoe UI", 16, "bold"), fg=color, bg="#10141e").pack()
        tk.Label(overlay, text=winner_sub, font=("Segoe UI", 11), fg="#e2e8f0", bg="#10141e").pack(pady=4)

        btn_row = tk.Frame(overlay, bg="#10141e")
        btn_row.pack(pady=18)

        tk.Button(
            btn_row,
            text="🔄 TANDING ULANG",
            font=("Segoe UI", 12, "bold"),
            bg="#06d6a0",
            fg="#0b0f19",
            bd=0,
            padx=18,
            pady=8,
            cursor="hand2",
            command=self.rematch,
        ).pack(side="left", padx=10)

        tk.Button(
            btn_row,
            text="🏠 MENU UTAMA",
            font=("Segoe UI", 12, "bold"),
            bg="#3a0ca3",
            fg="white",
            bd=0,
            padx=18,
            pady=8,
            cursor="hand2",
            command=self.show_main_menu,
        ).pack(side="left", padx=10)

    def rematch(self):
        self.reset_match()
        self.show_arena_screen()

    # -----------------------------------------------------------------------
    # RENDERING ARENA 2D DI CANVAS
    # -----------------------------------------------------------------------
    def render_arena(self):
        canvas = self.arena_canvas
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 100:
            w, h = 1120, 440

        ox = self.screen_shake_x
        oy = self.screen_shake_y

        # 1. Background Arena Futuristik & Ring Tinju
        canvas.create_rectangle(0, 0, w, h, fill="#0c101a", outline="")

        # Spotlight Beams
        canvas.create_polygon([w * 0.25 + ox, 0, w * 0.15 + ox, h, w * 0.35 + ox, h], fill="#131b2c", outline="")
        canvas.create_polygon([w * 0.75 + ox, 0, w * 0.65 + ox, h, w * 0.85 + ox, h], fill="#131b2c", outline="")

        # Lantai Panggung Ring
        floor_y = 330 + oy
        canvas.create_rectangle(0, floor_y, w, h, fill="#121724", outline="")

        # Tali Ring Tinju (Boxing Ropes)
        for ry, rcol in [(floor_y - 120, "#ff0054"), (floor_y - 70, "#4cc9f0"), (floor_y - 20, "#ffd166")]:
            canvas.create_line(0, ry + oy, w, ry + oy, fill=rcol, width=3)

        # Garis Grid Lantai
        for gx in range(0, w, 80):
            canvas.create_line(gx, floor_y, gx + (gx - w // 2) * 0.5, h, fill="#1f283d", width=2)

        # Teks VS di Background
        canvas.create_text(
            w // 2 + ox, 210 + oy,
            text="VS",
            font=("Impact", 56, "bold"),
            fill="#182032"
        )

        # 2. Breathing Bobbing Animation
        bob1 = math.sin(self.idle_tick * 0.08) * 6 if self.state == "idle" else 0
        bob2 = math.cos(self.idle_tick * 0.08) * 6 if self.state == "idle" else 0

        # Jika sedang countdown, tangan memompa kepalan tinju
        if self.state == "countdown":
            pump = -14 * abs(math.sin(self.idle_tick * 0.25))
            bob1 = pump
            bob2 = pump

        # 3. Tentukan Gestur & Status Tangan
        sk1 = SKINS.get(self.p1_skin, SKINS["classic"])
        sk2_key = self.p2_skin if self.mode == "pvp" else self.ai_skin
        sk2 = SKINS.get(sk2_key, SKINS["cyborg"])

        p1_state = "normal"
        p2_state = "normal"
        p1_gest = "batu"
        p2_gest = "batu"

        if self.state == "countdown":
            p1_gest = "batu"
            p2_gest = "batu"
        elif self.state in ("animating", "game_over"):
            # Fase reveal: tampilkan gestur yang dipilih
            p1_gest = self.p1_choice or "batu"
            p2_gest = self.p2_choice or "batu"

            # Setelah frame 14, tangan pemenang berubah jadi PUNCH dan menonjok
            if self.anim_type == "p1_punch":
                if self.anim_frame >= 14:
                    p1_gest = "punch"
                if self.anim_frame >= 25:
                    p2_state = "hurt"
            elif self.anim_type == "p2_punch":
                if self.anim_frame >= 14:
                    p2_gest = "punch"
                if self.anim_frame >= 25:
                    p1_state = "hurt"

        # Gambar Tangan P1
        HandRenderer.draw(
            canvas,
            self.p1_pos_x + ox,
            self.p1_pos_y + oy + bob1,
            p1_gest,
            1,
            sk1,
            state=p1_state,
            scale=1.25,
            hurt_intensity=self.anim_frame / 10.0 if p1_state == "hurt" else 0.0,
        )

        # Gambar Tangan P2 / AI
        HandRenderer.draw(
            canvas,
            self.p2_pos_x + ox,
            self.p2_pos_y + oy + bob2,
            p2_gest,
            -1,
            sk2,
            state=p2_state,
            scale=1.25,
            hurt_intensity=self.anim_frame / 10.0 if p2_state == "hurt" else 0.0,
        )

        # 4. Status Banner
        if self.state == "countdown":
            canvas.create_text(
                w // 2 + ox, 110 + oy,
                text=self.countdown_text,
                font=("Impact", 46, "bold"),
                fill="#ffe600"
            )
        elif self.state == "animating":
            canvas.create_text(
                w // 2 + ox, 90 + oy,
                text=self.round_result_text,
                font=("Segoe UI", 18, "bold"),
                fill="#ffffff"
            )
        elif self.state == "idle":
            if self.mode == "pvp":
                status_info = "Player 1 & 2: Silakan pilih tangan rahasiamu!"
            else:
                status_info = "Pilih Batu, Gunting, atau Kertas untuk menyerang AI!"
            canvas.create_text(
                w // 2 + ox, 90 + oy,
                text=status_info,
                font=("Segoe UI", 14, "bold"),
                fill="#ffd166"
            )

        # 5. Render Partikel FX & Comic Popups
        self.fx.draw(canvas)


# ---------------------------------------------------------------------------
# TITIK MASUK PROGRAM (MAIN ENTRY POINT)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    game = SuitGame()
    game.mainloop()
