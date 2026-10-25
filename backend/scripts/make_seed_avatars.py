"""Draws the cartoon profile pictures in app/seed_avatars/: one PNG per seeded username.

Only needed when you want to change or add an avatar (the PNGs are committed). From backend/:

    python scripts/make_seed_avatars.py

`flask seed` / `flask seed-test-users` attach app/seed_avatars/<username>.png to every seeded
account that has no photo yet (see `attach_missing_looks` in app/seed.py).

Everything is drawn with Pillow at 4x size and shrunk, so edges are smooth. The subject stays
inside the middle circle because the app shows avatars round. To add one: write a function that
takes a Pen, then add `username: (function, background color)` to AVATARS.
"""

from pathlib import Path

from PIL import Image, ImageDraw

OUT_DIR = Path(__file__).resolve().parent.parent / "app" / "seed_avatars"
SIZE = 256  # final PNG is SIZE x SIZE
SCALE = 4  # drawn this much bigger, then shrunk
W = SIZE * SCALE
MID = W // 2

INK = "#2d2a32"
WHITE = "#fffaf0"
PINK = "#ff9eb5"
RED = "#e8453c"
ORANGE = "#f08a24"
YELLOW = "#ffd23f"
GREEN = "#4fae6a"
LEAF = "#3f9b5e"
BROWN = "#8d6748"
SOIL = "#7a4a2b"


class Pen:
    """A square canvas with the few shapes the avatars need. Coordinates are 0..1024."""

    def __init__(self, background: str):
        self.background = background
        self.img = Image.new("RGBA", (W, W), background)
        self.d = ImageDraw.Draw(self.img)

    def oval(self, x, y, rx, ry=None, fill=INK):
        self.d.ellipse([x - rx, y - (ry or rx), x + rx, y + (ry or rx)], fill=fill)

    def poly(self, points, fill=INK):
        self.d.polygon(points, fill=fill)

    def line(self, points, fill=INK, width=24):
        self.d.line(points, fill=fill, width=width, joint="curve")
        for x, y in (points[0], points[-1]):  # round ends
            self.oval(x, y, width / 2, fill=fill)

    def arc(self, x, y, rx, ry, start, end, fill=INK, width=20):
        self.d.arc([x - rx, y - ry, x + rx, y + ry], start, end, fill=fill, width=width)

    def top_half(self, x, y, rx, ry, fill):
        """The upper half of an ellipse (a dome)."""
        self.d.pieslice([x - rx, y - ry, x + rx, y + ry], 180, 360, fill=fill)

    def rect(self, x0, y0, x1, y1, radius, fill):
        self.d.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill)

    def tilted(self, x, y, rx, ry, angle, fill, pivot=None):
        """An ellipse turned `angle` degrees (counter-clockwise) around `pivot` (default: its centre)."""
        layer = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).ellipse([x - rx, y - ry, x + rx, y + ry], fill=fill)
        layer = layer.rotate(angle, center=pivot or (x, y), resample=Image.Resampling.BICUBIC)
        self.img.alpha_composite(layer)

    def ring(self, x, y, distance, count, rx, ry, fill, offset=0):
        """`count` ellipses ("petals") around (x, y), each `distance` from the middle, pointing outward."""
        for i in range(count):
            self.tilted(x, y - distance, rx, ry, offset + i * 360 / count, fill, pivot=(x, y))

    def eyes(self, x, y, gap, r=30):
        for side in (-1, 1):
            self.oval(x + side * gap, y, r, fill=INK)
            self.oval(x + side * gap + r * 0.3, y - r * 0.35, r * 0.34, fill="white")

    def smile(self, x, y, half_width, width=18, color=INK):
        self.arc(x, y - half_width * 0.4, half_width, half_width * 0.6, 20, 160, color, width)

    def cheeks(self, x, y, gap, r=34):
        for side in (-1, 1):
            self.oval(x + side * gap, y, r, r * 0.65, fill=PINK)

    def save(self, name: str):
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        small = self.img.resize((SIZE, SIZE), Image.Resampling.LANCZOS).convert("RGB")
        small.save(OUT_DIR / f"{name}.png", optimize=True)


# ---------- animals with a face
def fox(p: Pen):
    for side in (-1, 1):
        p.poly([(MID + side * 90, 330), (MID + side * 290, 120), (MID + side * 310, 420)], ORANGE)
        p.poly([(MID + side * 150, 340), (MID + side * 255, 215), (MID + side * 260, 400)], "#5a3320")
    p.oval(MID, 570, 315, 270, ORANGE)
    for x in (MID - 140, MID + 140):
        p.oval(x, 690, 160, 120, WHITE)
    p.oval(MID, 735, 150, 100, WHITE)
    p.eyes(MID, 545, 125)
    p.oval(MID, 668, 42, 30)
    p.smile(MID, 735, 60)


def panda(p: Pen):
    for side in (-1, 1):
        p.oval(MID + side * 250, 290, 100, fill=INK)
    p.oval(MID, 570, 330, 285, "#fdfdfd")
    for side in (-1, 1):
        p.tilted(MID + side * 130, 540, 72, 98, -side * 22, INK)
        p.oval(MID + side * 130, 535, 26, fill="white")
        p.oval(MID + side * 130, 540, 15, fill=INK)
    p.oval(MID, 665, 52, 36)
    p.smile(MID, 740, 70)


def bear(p: Pen):
    for side in (-1, 1):
        p.oval(MID + side * 255, 280, 105, fill="#7a4f33")
        p.oval(MID + side * 255, 290, 55, fill="#d9a77b")
    p.oval(MID, 570, 330, 290, "#9c6644")
    p.oval(MID, 700, 160, 120, "#e0b98c")
    p.eyes(MID, 520, 130)
    p.oval(MID, 650, 48, 34)
    p.smile(MID, 735, 60)
    p.cheeks(MID, 640, 250)


def cat(p: Pen):
    for side in (-1, 1):
        p.poly([(MID + side * 80, 330), (MID + side * 290, 110), (MID + side * 320, 430)], "#8e8e9a")
        p.poly([(MID + side * 150, 340), (MID + side * 260, 205), (MID + side * 270, 400)], PINK)
    p.oval(MID, 580, 340, 275, "#8e8e9a")
    for i in (-1, 0, 1):  # forehead stripes
        p.line([(MID + i * 60, 340), (MID + i * 60, 410)], "#6b6b78", 22)
    p.eyes(MID, 560, 135, 34)
    p.poly([(MID - 36, 650), (MID + 36, 650), (MID, 695)], PINK)
    p.arc(MID - 40, 700, 50, 40, 20, 160, INK, 14)
    p.arc(MID + 40, 700, 50, 40, 20, 160, INK, 14)
    for side in (-1, 1):  # whiskers
        for tilt in (-30, 0, 30):
            p.line([(MID + side * 190, 690 + tilt), (MID + side * 360, 680 + tilt * 2)], WHITE, 9)


def dog(p: Pen):
    for side in (-1, 1):
        p.tilted(MID + side * 330, 480, 105, 215, side * 14, "#8a5a33")
    p.oval(MID, 560, 300, 285, "#e9b872")
    p.oval(MID + 140, 520, 95, 100, "#8a5a33")  # eye patch
    p.oval(MID, 700, 185, 140, WHITE)
    p.eyes(MID, 520, 140)
    p.oval(MID, 655, 62, 44)
    p.oval(MID, 800, 55, 70, "#ff7f96")  # tongue
    p.oval(MID, 760, 105, 40, WHITE)
    p.arc(MID - 55, 745, 60, 55, 10, 170, INK, 16)
    p.arc(MID + 55, 745, 60, 55, 10, 170, INK, 16)


def rabbit(p: Pen):
    p.tilted(MID - 120, 270, 85, 230, 10, WHITE)
    p.tilted(MID + 120, 270, 85, 230, -10, WHITE)
    p.tilted(MID - 120, 280, 42, 170, 10, PINK)
    p.tilted(MID + 120, 280, 42, 170, -10, PINK)
    p.oval(MID, 640, 300, 255, WHITE)
    p.eyes(MID, 610, 125)
    p.oval(MID, 705, 36, 26, PINK)
    p.smile(MID, 770, 50)
    p.rect(MID - 36, 765, MID + 36, 840, 16, WHITE)  # buck teeth
    p.d.line([(MID, 770), (MID, 840)], fill="#e0d6d0", width=6)
    p.cheeks(MID, 700, 215)


def koala(p: Pen):
    for side in (-1, 1):
        p.oval(MID + side * 300, 350, 150, fill="#8d97a3")
        p.oval(MID + side * 300, 355, 95, fill="#e8ecf0")
    p.oval(MID, 580, 320, 285, "#a7b0ba")
    p.eyes(MID, 540, 125, 28)
    p.oval(MID, 650, 78, 105, "#3a3d46")
    p.oval(MID - 25, 610, 20, 14, "#8a8f9c")
    p.smile(MID, 810, 55)


def mouse(p: Pen):
    for side in (-1, 1):
        p.oval(MID + side * 270, 320, 150, fill="#bdb6b0")
        p.oval(MID + side * 270, 325, 100, fill=PINK)
    p.oval(MID, 600, 300, 265, "#d3ccc6")
    p.eyes(MID, 560, 120, 30)
    p.oval(MID, 665, 36, 28, "#ff7f96")
    p.smile(MID, 740, 55)
    for side in (-1, 1):
        for tilt in (-24, 0, 24):
            p.line([(MID + side * 80, 700 + tilt), (MID + side * 290, 690 + tilt * 2)], "#8a8580", 8)


# ---------- other animals
def crab(p: Pen):
    for side in (-1, 1):
        for i in range(3):  # legs
            p.line([(MID + side * 220, 640 + i * 60), (MID + side * (330 + i * 12), 720 + i * 75)], "#c7352e", 26)
        p.line([(MID + side * 200, 520), (MID + side * 290, 380)], "#c7352e", 40)  # arm
        p.oval(MID + side * 300, 330, 120, fill=RED)  # claw
        p.poly([(MID + side * 300, 330), (MID + side * 215, 195), (MID + side * 390, 215)], p.background)
        p.line([(MID + side * 90, 470), (MID + side * 100, 360)], "#c7352e", 22)  # eye stalk
        p.oval(MID + side * 100, 335, 52, fill="white")
        p.oval(MID + side * 100, 340, 26, fill=INK)
    p.oval(MID, 620, 290, 205, RED)
    p.smile(MID, 700, 85)
    p.cheeks(MID, 650, 190, 30)


def owl(p: Pen):
    for side in (-1, 1):
        p.poly([(MID + side * 120, 270), (MID + side * 270, 170), (MID + side * 290, 360)], "#6e4c33")
        p.tilted(MID + side * 285, 640, 80, 200, side * 15, "#6e4c33")  # wings
    p.oval(MID, 570, 290, 345, BROWN)
    p.oval(MID, 700, 190, 215, "#ecd8b5")
    for row in range(3):  # belly feathers
        for col in range(3 - row % 2):
            x = MID + (col - (2 - row % 2) / 2) * 90
            p.arc(x, 650 + row * 70, 40, 30, 0, 180, "#c9a977", 10)
    for side in (-1, 1):
        p.oval(MID + side * 125, 470, 110, fill=WHITE)
        p.oval(MID + side * 125, 470, 52, fill=INK)
        p.oval(MID + side * 125 + 16, 450, 17, fill="white")
    p.poly([(MID - 40, 545), (MID + 40, 545), (MID, 625)], ORANGE)


def chick(p: Pen):
    for side in (-1, 1):
        p.tilted(MID + side * 285, 620, 70, 120, side * 25, "#ffc233")
    p.oval(MID, 570, 305, fill="#ffd84a")
    for tilt in (-25, 0, 25):
        p.tilted(MID + tilt * 3, 245, 22, 75, tilt, "#ffd84a", pivot=(MID, 400))
    p.eyes(MID, 530, 125)
    p.poly([(MID - 60, 600), (MID + 60, 600), (MID, 680)], ORANGE)
    p.cheeks(MID, 620, 215)
    p.line([(MID - 70, 855), (MID - 70, 930)], ORANGE, 24)
    p.line([(MID + 70, 855), (MID + 70, 930)], ORANGE, 24)


def duck(p: Pen):
    p.poly([(190, 600), (80, 480), (270, 540)], YELLOW)  # tail
    p.oval(480, 690, 310, 210, YELLOW)
    p.oval(610, 420, 175, fill=YELLOW)
    p.oval(790, 465, 100, 48, ORANGE)  # beak
    p.oval(650, 385, 24)
    p.oval(640, 450, 36, 22, PINK)
    p.tilted(430, 690, 150, 95, 15, "#ffb800")  # wing
    for x in (260, 512, 764):  # water
        p.arc(x, 905, 130, 55, 200, 340, "#8ec9ea", 18)


def snail(p: Pen):
    p.oval(500, 790, 330, 80, "#e5c07b")
    p.oval(800, 650, 78, 165, "#e5c07b")
    for x in (770, 850):  # eye stalks
        p.line([(x, 560), (x + 15, 430)], "#e5c07b", 22)
        p.oval(x + 15, 420, 36, fill="white")
        p.oval(x + 20, 422, 17)
    p.smile(815, 700, 36, 12)
    for r, color in ((250, "#b8754a"), (190, "#d9955f"), (130, "#b8754a"), (68, "#d9955f")):
        p.oval(440, 570, r, fill=color)


def bluebird(p: Pen):
    p.poly([(250, 560), (60, 440), (80, 640)], "#2f7ed1")  # tail
    p.oval(480, 600, 310, 230, "#4aa3f0")
    p.oval(500, 700, 230, 120, "#cfe8ff")
    p.oval(660, 430, 160, fill="#4aa3f0")
    for tilt in (-20, 0, 20):  # crest
        p.tilted(660 + tilt * 3, 245, 20, 70, tilt, "#2f7ed1", pivot=(660, 430))
    p.poly([(790, 400), (930, 450), (790, 495)], ORANGE)
    p.oval(700, 400, 26)
    p.oval(708, 392, 9, fill="white")
    p.tilted(420, 590, 175, 100, 20, "#2f7ed1")
    p.line([(450, 830), (450, 920)], ORANGE, 20)
    p.line([(570, 830), (570, 920)], ORANGE, 20)


def ghost(p: Pen):
    p.oval(MID, 440, 235, fill="#f5f3ff")
    p.rect(MID - 235, 440, MID + 235, 750, 0, "#f5f3ff")
    for x in (MID - 157, MID, MID + 157):
        p.oval(x, 750, 78, fill="#f5f3ff")
    p.eyes(MID, 470, 100, 36)
    p.oval(MID, 600, 34, 44)
    p.cheeks(MID, 560, 175, 34)


def ladybug(p: Pen):
    p.line([(MID - 120, 300), (MID - 200, 190)], INK, 16)
    p.line([(MID + 120, 300), (MID + 200, 190)], INK, 16)
    p.oval(MID, 600, 310, 310, RED)
    p.top_half(MID, 330, 175, 150, INK)
    p.oval(MID - 80, 300, 34, fill="white")
    p.oval(MID + 80, 300, 34, fill="white")
    p.oval(MID - 74, 305, 16)
    p.oval(MID + 86, 305, 16)
    p.line([(MID, 340), (MID, 905)], INK, 16)
    for x, y, r in ((MID - 150, 520, 50), (MID + 150, 520, 50), (MID - 175, 700, 44), (MID + 175, 700, 44), (MID - 70, 810, 34), (MID + 70, 810, 34)):
        p.oval(x, y, r)


def butterfly(p: Pen):
    for side in (-1, 1):
        p.tilted(MID + side * 190, 400, 215, 135, side * 30, "#9b6cf0")
        p.tilted(MID + side * 190, 395, 95, 55, side * 30, "#cdb4ff")
        p.tilted(MID + side * 150, 660, 140, 100, -side * 30, "#ff8fc0")
        p.oval(MID + side * 150, 670, 40, fill="#ffd0e5")
        p.line([(MID + side * 25, 330), (MID + side * 130, 160)], INK, 12)
        p.oval(MID + side * 130, 160, 24)
    p.oval(MID, 560, 40, 215, INK)
    p.oval(MID, 330, 56)


def acorn(p: Pen):
    p.oval(MID, 640, 245, 275, "#d9904a")
    p.oval(MID - 90, 600, 40, 110, "#ecb277")  # shine
    p.top_half(MID, 470, 285, 215, SOIL)
    for i in range(5):  # cap pattern
        p.line([(MID - 230 + i * 115, 440), (MID - 190 + i * 115, 360)], "#a06a43", 12)
    p.rect(MID - 28, 170, MID + 28, 280, 24, SOIL)
    p.eyes(MID, 610, 100, 28)
    p.smile(MID, 720, 60)
    p.cheeks(MID, 680, 160, 30)


def frog(p: Pen):
    p.oval(MID, 620, 365, 265, "#5ec26a")
    p.oval(MID, 720, 290, 150, "#a8e6a1")
    for side in (-1, 1):
        p.oval(MID + side * 190, 380, 125, fill="#5ec26a")
        p.oval(MID + side * 190, 385, 85, fill="white")
        p.oval(MID + side * 175, 395, 45)
        p.oval(MID + side * 160, 380, 15, fill="white")
    p.arc(MID, 560, 255, 200, 25, 155, INK, 20)
    for side in (-1, 1):
        p.oval(MID + side * 40, 560, 10)
    p.cheeks(MID, 690, 280, 38)


def moon(p: Pen):
    p.oval(MID, MID, 330, fill="#ffe9a8")
    p.oval(MID + 130, MID - 90, 290, fill=p.background)  # bite out of the disc: a crescent
    for x, y, r in ((730, 270, 26), (810, 470, 18), (700, 700, 22), (840, 640, 14)):
        p.poly([(x, y - r * 2), (x + r * .6, y - r * .6), (x + r * 2, y), (x + r * .6, y + r * .6), (x, y + r * 2), (x - r * .6, y + r * .6), (x - r * 2, y), (x - r * .6, y - r * .6)], "white")
    p.arc(300, 560, 42, 24, 20, 160, INK, 14)  # a closed, sleepy eye on the thick part of the crescent
    p.oval(255, 640, 30, 20, PINK)


def slime(p: Pen):
    p.top_half(MID, 640, 305, 340, "#5ee08a")
    p.oval(MID, 700, 345, 150, "#5ee08a")
    p.tilted(MID - 150, 410, 40, 80, 35, "#a8f5c1")  # shine
    p.eyes(MID, 600, 115, 42)
    p.smile(MID, 700, 70, 16)
    p.cheeks(MID, 690, 210, 32)


def sun(p: Pen):
    p.ring(MID, MID, 330, 12, 38, 85, "#ffb627")
    p.oval(MID, MID, 235, fill=YELLOW)
    p.eyes(MID, 480, 90, 30)
    p.smile(MID, 600, 80)
    p.cheeks(MID, 560, 165, 36)


# ---------- flowers and plants
def sunflower(p: Pen):
    p.ring(MID, 500, 235, 16, 62, 135, "#f5b800", offset=11)
    p.ring(MID, 500, 215, 16, 62, 135, YELLOW)
    p.oval(MID, 500, 175, fill="#6b3f1d")
    p.eyes(MID, 480, 70, 22)
    p.smile(MID, 560, 55, 14, "#f6d6a6")
    p.line([(MID, 700), (MID, 1000)], LEAF, 34)
    p.tilted(MID - 120, 850, 110, 50, 35, GREEN)
    p.tilted(MID + 120, 880, 110, 50, -35, GREEN)


def sakura(p: Pen):
    p.ring(MID, MID, 175, 5, 135, 135, "#ffb7cc")
    for i in range(5):  # a notch at each petal tip
        p.tilted(MID, MID - 318, 24, 52, i * 72, p.background, pivot=(MID, MID))
    p.oval(MID, MID, 70, fill="#ff6f9c")
    for i in range(8):
        p.tilted(MID, MID - 105, 7, 38, i * 45, "#c2305f", pivot=(MID, MID))


def daisy(p: Pen):
    p.ring(MID, MID, 215, 14, 58, 150, WHITE, offset=6)
    p.ring(MID, MID, 205, 14, 58, 150, "#f4efe4")
    p.oval(MID, MID, 125, fill="#ffc928")
    p.oval(MID - 35, MID - 40, 30, fill="#ffe27a")


def tulip(p: Pen):
    p.line([(MID, 480), (MID, 1000)], LEAF, 38)
    p.tilted(MID - 150, 800, 170, 55, 45, GREEN)
    p.tilted(MID + 160, 740, 170, 55, -45, GREEN)
    p.tilted(MID - 105, 360, 105, 190, 18, "#ff7aa2")
    p.tilted(MID + 105, 360, 105, 190, -18, "#ff7aa2")
    p.tilted(MID, 330, 115, 210, 0, "#ff4f86")


def sprout(p: Pen):
    p.line([(MID, 760), (MID, 430)], LEAF, 38)
    p.tilted(MID - 125, 420, 150, 75, 25, "#5cc26a", pivot=(MID, 440))
    p.tilted(MID + 135, 330, 150, 80, -30, GREEN, pivot=(MID, 440))
    p.top_half(MID, 760, 330, 160, SOIL)


def mushroom(p: Pen):
    p.rect(MID - 120, 460, MID + 120, 800, 70, "#f6e7cf")
    p.top_half(MID, 480, 335, 280, RED)
    for x, y, r in ((MID - 150, 360, 55), (MID + 130, 330, 65), (MID, 245, 42), (MID + 235, 440, 36), (MID - 255, 450, 34)):
        p.oval(x, y, r, fill="white")
    p.eyes(MID, 600, 70, 24)
    p.smile(MID, 670, 50, 14)


def cactus(p: Pen):
    p.rect(MID - 115, 190, MID + 115, 800, 115, "#3f9b5e")
    p.line([(MID - 115, 520), (MID - 235, 520), (MID - 235, 380)], "#3f9b5e", 90)
    p.line([(MID + 115, 600), (MID + 235, 600), (MID + 235, 450)], "#3f9b5e", 90)
    for x in (MID - 60, MID, MID + 60):
        p.line([(x, 260), (x, 740)], "#34865a", 8)
    p.oval(MID, 195, 40, fill=PINK)
    p.oval(MID, 195, 14, fill=YELLOW)
    p.eyes(MID, 440, 52, 20)
    p.smile(MID, 510, 36, 12)
    p.poly([(MID - 255, 760), (MID + 255, 760), (MID + 200, 960), (MID - 200, 960)], "#d2693f")
    p.rect(MID - 290, 725, MID + 290, 800, 30, "#e07a4c")
    for x, y in ((MID - 120, 300), (MID + 130, 360), (MID - 200, 330), (MID + 210, 520)):
        p.line([(x, y), (x + 22, y - 22)], "white", 8)


def turtle(p: Pen):
    for x in (MID - 270, MID + 270):
        for y in (380, 700):
            p.oval(x, y, 85, 62, "#8ccf9d")
    p.oval(MID, 190, 100, 110, "#8ccf9d")
    p.eyes(MID, 175, 45, 18)
    p.poly([(MID - 40, 860), (MID + 40, 860), (MID, 960)], "#8ccf9d")
    p.oval(MID, 540, 285, 320, "#3f8f5b")
    hexagon = [(MID + 135 * x, 540 + 135 * y) for x, y in ((0, -1), (.87, -.5), (.87, .5), (0, 1), (-.87, .5), (-.87, -.5))]
    for (x, y) in hexagon:  # lines from the hexagon to the rim
        p.line([(x, y), (MID + (x - MID) * 1.9, 540 + (y - 540) * 1.9)], "#2f7048", 14)
    p.poly(hexagon, "#5db57c")


def whale(p: Pen):
    p.tilted(150, 430, 55, 140, -35, "#3f7fd9")  # tail
    p.tilted(235, 400, 50, 120, 40, "#3f7fd9")
    p.oval(500, 610, 340, 235, "#3f7fd9")
    p.d.pieslice([160, 375, 840, 845], 0, 180, fill="#cfe2fb")
    p.oval(690, 540, 28)
    p.oval(698, 531, 10, fill="white")
    p.smile(700, 690, 85, 14)
    for dx in (-1, 1):  # water spout
        p.arc(560 + dx * 60, 360, 60, 90, 180 if dx < 0 else 270, 270 if dx < 0 else 360, "#7cc4f5", 18)
    for x, y in ((470, 330), (650, 330), (560, 265)):
        p.oval(x, y, 22, 30, "#7cc4f5")


def coffee(p: Pen):
    p.d.ellipse([502, 520, 862, 670], outline=WHITE, width=44)  # handle
    p.rect(262, 400, 722, 790, 150, WHITE)
    p.oval(492, 405, 230, 52, WHITE)
    p.oval(492, 410, 200, 38, "#6b3f1d")
    p.oval(492, 835, 340, 48, "#e6dccf")
    p.oval(492, 815, 300, 36, "#f6efe6")
    for x in (400, 492, 584):
        p.arc(x, 270, 30, 60, 90, 270, "white", 16)
        p.arc(x, 150, 30, 60, 270, 450, "white", 16)
    p.eyes(492, 600, 90, 28)
    p.smile(492, 690, 60)
    p.cheeks(492, 650, 165, 30)


def egg(p: Pen):
    p.oval(MID, 600, 245, 295, "#fff3dc")
    p.oval(MID, 410, 190, 245, "#fff3dc")
    p.line([(300, 480), (390, 400), (470, 500), (560, 400), (650, 500), (730, 410)], "#c9a977", 18)
    for x, y in ((380, 700), (650, 760), (600, 620)):
        p.oval(x, y, 14, fill="#e6cf9f")
    p.eyes(MID, 600, 90, 24)
    p.smile(MID, 690, 50, 14)
    p.cheeks(MID, 650, 160, 28)


# username -> (drawing function, background color)
AVATARS = {
    # flask seed
    "jordan-dev": (fox, "#ffe3c4"),
    "mayacodes": (sakura, "#e8dcff"),
    "diego-rs": (crab, "#cdeef0"),
    "priya-ml": (owl, "#e6dcf7"),
    "samfullstack": (sunflower, "#cfe9ff"),
    "lena-gamedev": (mushroom, "#d9f0d4"),
    "m-sec": (cactus, "#fdeccd"),
    "aisha-data": (turtle, "#d6f1f7"),
    "kenji-mobile": (rabbit, "#e8dcff"),
    "liv-devops": (whale, "#e1f3ff"),
    "noah-learns": (chick, "#cfe8f7"),
    # flask seed-test-users
    "user1": (panda, "#bfe8cf"),
    "user2": (koala, "#d6ecf5"),
    "javajade": (coffee, "#f6e3d0"),
    "juniorjo": (duck, "#cde9f7"),
    "studentstu": (bear, "#fde9c9"),
    "learnerlee": (sprout, "#fbeed4"),
    "copypasta": (cat, "#d8e4ff"),
    "newbie": (egg, "#d9e7fb"),
    "lurker": (snail, "#e5f4e3"),
    "printhello": (bluebird, "#fff1cc"),
    "ghostdev": (ghost, "#2e2a4f"),
    "firststep": (ladybug, "#e2f4d8"),
    "djangodeb": (tulip, "#fde3ec"),
    "hackhannah": (butterfly, "#e9f1fb"),
    "datadan": (acorn, "#d7ecf2"),
    "ittomas": (dog, "#ffe9f0"),
    "gamergus": (frog, "#fff3c9"),
    "justjoined": (daisy, "#cfe9ff"),
    "codecurious": (mouse, "#fff0d1"),
    "nullnick": (moon, "#1f2740"),
    "helloharper": (sun, "#bfe3ff"),
    "zeroxp": (slime, "#3a2a66"),
}


if __name__ == "__main__":
    for username, (draw, background) in AVATARS.items():
        pen = Pen(background)
        draw(pen)
        pen.save(username)
    print(f"Wrote {len(AVATARS)} avatars to {OUT_DIR}")
