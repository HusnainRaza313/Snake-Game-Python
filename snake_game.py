import json
import os
import random
import sys
import tkinter as tk

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageTk

try:
    import winsound
except ImportError:                                                   
    class _WinsoundStub:
        SND_FILENAME = SND_ASYNC = SND_LOOP = SND_NODEFAULT = SND_PURGE = 0

        @staticmethod
        def PlaySound(*_a, **_k):
            pass

        @staticmethod
        def Beep(*_a, **_k):
            pass

    winsound = _WinsoundStub()

root = tk.Tk()
root.title("Snake Game")
root.geometry("600x640")
root.resizable(False, False)
root.configure(bg="#091a0c")

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MUSIC_FILE = os.path.join(BASE_DIR, "background_music.wav")
APP_DATA_FOLDER = os.path.join(
    os.getenv("APPDATA") or os.path.expanduser("~"),
    "SnakeGame",
)
HIGH_SCORE_FILE = os.path.join(APP_DATA_FOLDER, "high_score.txt")
SETTINGS_FILE = os.path.join(APP_DATA_FOLDER, "settings.json")

def load_high_score():
    try:
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, "r") as file:
                value = file.read().strip()
                if value:
                    return int(value)
    except (ValueError, OSError):
        pass
    return 0

def save_high_score():
    try:
        os.makedirs(APP_DATA_FOLDER, exist_ok=True)
        with open(HIGH_SCORE_FILE, "w") as file:
            file.write(str(high_score))
    except OSError as e:
        print("High score save error:", e)

def load_settings():
    data = {"music": True, "sfx": True}
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as file:
                stored = json.load(file)
            if isinstance(stored, dict):
                data["music"] = bool(stored.get("music", True))
                data["sfx"] = bool(stored.get("sfx", True))
    except (ValueError, OSError):
        pass
    return data

def save_settings():
    try:
        os.makedirs(APP_DATA_FOLDER, exist_ok=True)
        with open(SETTINGS_FILE, "w") as file:
            json.dump(
                {"music": music_enabled, "sfx": sfx_enabled},
                file,
            )
    except OSError as e:
        print("Settings save error:", e)

_settings = load_settings()
music_enabled = _settings["music"]
sfx_enabled = _settings["sfx"]

score = 0
high_score = load_high_score()
food_effect_id = None
food_effect_step = 0
speed = 100
game_loop_id = None
game_started = False
paused = False

WALL_LEFT = 40
WALL_RIGHT = 560
WALL_TOP = 50
WALL_BOTTOM = 550

snake = [(300, 310), (280, 310), (260, 310)]
food_x = 400
food_y = 310
direction = "right"
new_direction = "right"

def load_bold_font(size):
    for path in (
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()

def load_regular_font(size):
    for path in (
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()

def vertical_gradient(width, height, top_color, bottom_color):
    gradient = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(gradient)
    for y in range(height):
        t = y / max(height - 1, 1)
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
    return gradient

def create_menu_background(width=600, height=640):
    """Deep emerald triangle-weave background with vignette (classic-modern)."""
    img = Image.new("RGB", (width, height), (9, 26, 12))
    draw = ImageDraw.Draw(img, "RGBA")

    tri_size = 46
    shades = [
        (18, 48, 20, 90),
        (26, 66, 26, 70),
        (14, 36, 16, 100),
        (34, 78, 30, 55),
    ]
    rows = height // tri_size + 3
    cols = width // tri_size + 3
    for row in range(-1, rows):
        for col in range(-1, cols):
            x = col * tri_size
            y = row * tri_size
            shade = shades[(row * 7 + col * 13) % len(shades)]
            if (row + col) % 2 == 0:
                draw.polygon(
                    [
                        (x, y + tri_size),
                        (x + tri_size / 2, y),
                        (x + tri_size, y + tri_size),
                    ],
                    fill=shade,
                )
            else:
                draw.polygon(
                    [
                        (x, y),
                        (x + tri_size, y),
                        (x + tri_size / 2, y + tri_size),
                    ],
                    fill=shade,
                )

    for y in range(0, height, 4):
        draw.line([(0, y), (width, y)], fill=(0, 0, 0, 45))

    vignette = Image.new("L", (width, height), 0)
    ImageDraw.Draw(vignette).ellipse(
        (-width * 0.35, -height * 0.25, width * 1.35, height * 1.25),
        fill=255,
    )
    vignette = vignette.filter(ImageFilter.GaussianBlur(80))
    dark = Image.new("RGB", (width, height), (4, 12, 5))
    return Image.composite(img, dark, vignette)

create_game_over_background = create_menu_background

def create_title_text(text="GAME OVER", font_size=78):
    font = load_bold_font(font_size)
    probe_draw = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bbox = probe_draw.textbbox((0, 0), text, font=font, stroke_width=6)

    padding = 24
    width = (bbox[2] - bbox[0]) + padding * 2
    height = (bbox[3] - bbox[1]) + padding * 2

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    origin_x = padding - bbox[0]
    origin_y = padding - bbox[1]

    draw.text(
        (origin_x + 5, origin_y + 7),
        text,
        font=font,
        fill=(0, 30, 5, 170),
        stroke_width=8,
        stroke_fill=(0, 30, 5, 170),
    )
    draw.text(
        (origin_x, origin_y),
        text,
        font=font,
        fill=(20, 60, 15, 255),
        stroke_width=6,
        stroke_fill=(12, 40, 10, 255),
    )

    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).text(
        (origin_x, origin_y), text, font=font, fill=255
    )
    gradient = vertical_gradient(width, height, (214, 255, 96), (92, 168, 60))
    img.paste(gradient, (0, 0), mask)
    return img

def create_glass_card(width=380, height=250, radius=22):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        (0, 0, width - 1, height - 1), radius=radius, fill=(8, 24, 10, 165)
    )
    draw.rounded_rectangle(
        (1, 1, width - 2, height - 2),
        radius=radius,
        outline=(110, 255, 120, 220),
        width=2,
    )
    return img

def create_solid_button(
    width, height, fill_color, bottom_color, border_color, radius=16
):
    """Draws a solid colored button without any glass effect or gradient."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        (1, 1, width - 2, height - 2),
        radius=radius,
        fill=fill_color,
        outline=border_color,
        width=2,
    )
    return img

def draw_refresh_icon(draw, x, y, size, color):
    draw.arc((x, y, x + size, y + size), start=25, end=300, fill=color, width=3)
    draw.polygon(
        [
            (x + size - 1, y - 1),
            (x + size + 6, y + 5),
            (x + size - 6, y + 9),
        ],
        fill=color,
    )

def draw_exit_icon(draw, x, y, size, color):
    draw.rounded_rectangle(
        (x, y + 1, x + size * 0.4, y + size - 1), radius=2, outline=color, width=2
    )
    mid_y = y + size / 2
    draw.line((x + size * 0.3, mid_y, x + size, mid_y), fill=color, width=3)
    draw.polygon(
        [
            (x + size - 6, mid_y - 6),
            (x + size + 2, mid_y),
            (x + size - 6, mid_y + 6),
        ],
        fill=color,
    )

def draw_play_icon(draw, x, y, size, color):
    draw.polygon(
        [
            (x + 2, y),
            (x + size, y + size / 2),
            (x + 2, y + size),
        ],
        fill=color,
    )

def draw_book_icon(draw, x, y, size, color):
    draw.rounded_rectangle(
        (x, y + 1, x + size, y + size - 1), radius=3, outline=color, width=2
    )
    draw.line((x + size / 2, y + 2, x + size / 2, y + size - 2), fill=color, width=2)
    draw.line((x + 4, y + 7, x + size / 2 - 4, y + 7), fill=color, width=1)
    draw.line((x + 4, y + 12, x + size / 2 - 4, y + 12), fill=color, width=1)

def draw_gear_icon(draw, x, y, size, color):
    cx = x + size / 2
    cy = y + size / 2
    outer = size / 2
    draw.ellipse((cx - outer, cy - outer, cx + outer, cy + outer), outline=color, width=2)
    draw.ellipse(
        (cx - outer / 2.4, cy - outer / 2.4, cx + outer / 2.4, cy + outer / 2.4),
        outline=color,
        width=2,
    )
    for angle in range(0, 360, 45):
        import math

        rad = math.radians(angle)
        draw.line(
            (
                cx + math.cos(rad) * outer * 0.85,
                cy + math.sin(rad) * outer * 0.85,
                cx + math.cos(rad) * (outer + 3),
                cy + math.sin(rad) * (outer + 3),
            ),
            fill=color,
            width=2,
        )

def draw_back_icon(draw, x, y, size, color):
    mid_y = y + size / 2
    draw.line((x + 2, mid_y, x + size, mid_y), fill=color, width=3)
    draw.polygon(
        [
            (x + 9, mid_y - 7),
            (x, mid_y),
            (x + 9, mid_y + 7),
        ],
        fill=color,
    )

def draw_note_icon(draw, x, y, size, color):
    draw.line((x + size * 0.7, y + 1, x + size * 0.7, y + size - 6), fill=color, width=2)
    draw.line((x + size * 0.7, y + 1, x + size, y + 5), fill=color, width=2)
    draw.ellipse(
        (x + size * 0.32, y + size - 10, x + size * 0.72, y + size),
        outline=color,
        width=2,
    )

def draw_speaker_icon(draw, x, y, size, color):
    draw.polygon(
        [
            (x + 1, y + size * 0.35),
            (x + size * 0.32, y + size * 0.35),
            (x + size * 0.6, y + 1),
            (x + size * 0.6, y + size - 1),
            (x + size * 0.32, y + size * 0.65),
            (x + 1, y + size * 0.65),
        ],
        fill=color,
    )
    draw.arc(
        (x + size * 0.55, y + 2, x + size + 4, y + size - 2),
        start=300,
        end=60,
        fill=color,
        width=2,
    )

ICON_DRAWERS = {
    "refresh": draw_refresh_icon,
    "exit": draw_exit_icon,
    "play": draw_play_icon,
    "book": draw_book_icon,
    "gear": draw_gear_icon,
    "back": draw_back_icon,
    "note": draw_note_icon,
    "speaker": draw_speaker_icon,
}

def create_button_with_text(
    width,
    height,
    top_color,
    bottom_color,
    border_color,
    text,
    icon,
    font_size=19,
):
                                                               
    img = create_solid_button(
        width, height, top_color, bottom_color, border_color
    )
    draw = ImageDraw.Draw(img)
    font = load_bold_font(font_size)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    icon_size = 22
    spacing = 12
    has_icon = icon in ICON_DRAWERS
    total_w = (icon_size + spacing if has_icon else 0) + text_w

    start_x = (width - total_w) // 2
    icon_y = (height - icon_size) // 2
    text_x = start_x + (icon_size + spacing if has_icon else 0)
    text_y = (height - text_h) // 2 - bbox[1]

    if has_icon:
        ICON_DRAWERS[icon](draw, start_x, icon_y, icon_size, "white")

    draw.text((text_x, text_y), text, font=font, fill="white")
    return img

GREEN_NORMAL = ((72, 201, 96), (40, 140, 62), (150, 255, 160))
GREEN_HOVER = ((92, 221, 116), (56, 160, 82), (180, 255, 190))
GOLD_NORMAL = ((226, 186, 82), (168, 126, 34), (255, 226, 140))
GOLD_HOVER = ((244, 206, 106), (188, 146, 52), (255, 240, 180))
SLATE_NORMAL = ((72, 104, 92), (36, 62, 52), (140, 200, 176))
SLATE_HOVER = ((92, 128, 114), (50, 82, 68), (176, 230, 206))
RED_NORMAL = ((224, 72, 88), (176, 40, 56), (255, 150, 160))
RED_HOVER = ((240, 92, 108), (196, 56, 72), (255, 180, 190))

def make_button_pair(width, height, palette_normal, palette_hover, text, icon,
                     font_size=19):
    normal = ImageTk.PhotoImage(
        create_button_with_text(width, height, *palette_normal, text, icon, font_size)
    )
    hover = ImageTk.PhotoImage(
        create_button_with_text(width, height, *palette_hover, text, icon, font_size)
    )
    return normal, hover

def safe_open_image(filename, size=None):
    """Load an image from the application folder."""
    candidates = [
        os.path.join(BASE_DIR, filename),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filename),
        filename,
    ]

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        candidates.insert(0, os.path.join(sys._MEIPASS, filename))

    for candidate in candidates:
        try:
            if os.path.exists(candidate):
                img = Image.open(candidate).convert("RGBA")
                if size:
                    img = img.resize(size)
                return img
        except Exception as e:
            print("Image loading error:", candidate, e)

    print("Image not found:", filename)
    return None

def fallback_badge(label, color):
    img = Image.new("RGBA", (170, 34), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, 169, 33), radius=14, fill=(10, 30, 14, 220),
                           outline=color, width=2)
    draw.text((14, 8), label, font=load_bold_font(14), fill=color)
    return img

def fallback_play_field(width=600, height=600):
    """Classic checkerboard arena with a stone border."""
    img = Image.new("RGB", (width, height), (10, 22, 12))
    draw = ImageDraw.Draw(img)
    light = (26, 62, 30)
    dark = (20, 50, 25)
    for y in range(WALL_TOP, WALL_BOTTOM, 20):
        for x in range(WALL_LEFT, WALL_RIGHT, 20):
            fill = light if ((x // 20) + (y // 20)) % 2 == 0 else dark
            draw.rectangle((x, y, x + 19, y + 19), fill=fill)
    draw.rectangle(
        (WALL_LEFT - 6, WALL_TOP - 6, WALL_RIGHT + 5, WALL_BOTTOM + 5),
        outline=(122, 196, 106),
        width=4,
    )
    return img

def fallback_segment(color_top, color_bottom, radius=6):
    img = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    grad = vertical_gradient(20, 20, color_top, color_bottom)
    mask = Image.new("L", (20, 20), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 19, 19), radius=radius, fill=255)
    img.paste(grad, (0, 0), mask)
    return img

def fallback_head():
    img = fallback_segment((150, 240, 120), (70, 165, 70), radius=8)
    draw = ImageDraw.Draw(img)
    draw.ellipse((11, 4, 16, 9), fill=(12, 24, 12))
    draw.ellipse((11, 11, 16, 16), fill=(12, 24, 12))
    return img

def fallback_food():
    img = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((2, 3, 18, 19), fill=(226, 62, 62), outline=(255, 168, 168))
    draw.line((10, 3, 12, 0), fill=(120, 200, 90), width=2)
    draw.ellipse((6, 7, 9, 10), fill=(255, 220, 220))
    return img

MENU_BG_FILES = (
    "start_background.png",
    "menu_background.png",
    "start_screen.png",
    "background.png",
)

def load_menu_background():
    for name in MENU_BG_FILES:
        img = safe_open_image(name, (600, 640))
        if img is not None:
            return img.convert("RGB")
    return create_menu_background()

menu_background_image = load_menu_background()
menu_background_photo = ImageTk.PhotoImage(menu_background_image)

game_over_photo = ImageTk.PhotoImage(create_game_over_background())

snake_title_photo = ImageTk.PhotoImage(create_title_text("SNAKE", 84))
howto_title_photo = ImageTk.PhotoImage(create_title_text("HOW TO PLAY", 48))
settings_title_photo = ImageTk.PhotoImage(create_title_text("SETTINGS", 54))
title_text_photo = ImageTk.PhotoImage(create_title_text("GAME OVER", 72))

glass_card_photo = ImageTk.PhotoImage(create_glass_card())
howto_card_photo = ImageTk.PhotoImage(create_glass_card(460, 300, 24))
settings_card_photo = ImageTk.PhotoImage(create_glass_card(460, 250, 24))

menu_canvas = tk.Canvas(
    root, width=600, height=640, bg="#091a0c", highlightthickness=0
)

MENU_BTN_W = 240
MENU_BTN_H = 42                                               
MENU_BTN_X = 30
MENU_FIRST_Y = 380                              
MENU_GAP = 48                              

play_btn_normal, play_btn_hover = make_button_pair(
    MENU_BTN_W, MENU_BTN_H, GREEN_NORMAL, GREEN_HOVER, "PLAY", "play", 16
)
howto_btn_normal, howto_btn_hover = make_button_pair(
    MENU_BTN_W, MENU_BTN_H, GOLD_NORMAL, GOLD_HOVER, "HOW TO PLAY", "book", 16
)
settings_btn_normal, settings_btn_hover = make_button_pair(
    MENU_BTN_W, MENU_BTN_H, SLATE_NORMAL, SLATE_HOVER, "SETTINGS", "gear", 16
)
menu_quit_normal, menu_quit_hover = make_button_pair(
    MENU_BTN_W, MENU_BTN_H, RED_NORMAL, RED_HOVER, "QUIT", "exit", 16
)
back_btn_normal, back_btn_hover = make_button_pair(
    220, 48, SLATE_NORMAL, SLATE_HOVER, "BACK", "back", 17
)

toggle_on_normal, toggle_on_hover = make_button_pair(
    120, 40, GREEN_NORMAL, GREEN_HOVER, "ON", None, 16
)
toggle_off_normal, toggle_off_hover = make_button_pair(
    120, 40, RED_NORMAL, RED_HOVER, "OFF", None, 16
)

def bind_canvas_button(canvas, tag, normal, hover, command):
    canvas.tag_bind(tag, "<Button-1>", lambda e: command())
    canvas.tag_bind(
        tag, "<Enter>", lambda e: canvas.itemconfigure(tag, image=hover)
    )
    canvas.tag_bind(
        tag, "<Leave>", lambda e: canvas.itemconfigure(tag, image=normal)
    )

def hide_all_screens():
    menu_canvas.place_forget()
    howto_canvas.place_forget()
    settings_canvas.place_forget()
    game_over_canvas.place_forget()
    hud_canvas.place_forget()
    canvas.place_forget()

def show_menu():
    global game_started, paused, game_loop_id, game_menu_open
    game_started = False
    paused = False
    game_menu_open = False
    canvas.delete("game_menu")
    if game_loop_id is not None:
        try:
            root.after_cancel(game_loop_id)
        except Exception:
            pass
        game_loop_id = None
    stop_background_music()

    hide_all_screens()
    menu_canvas.delete("all")
    menu_canvas.create_image(0, 0, image=menu_background_photo, anchor="nw")

    items = (
        ("menu_play", play_btn_normal, play_btn_hover, start_game),
        ("menu_howto", howto_btn_normal, howto_btn_hover, show_how_to_play),
        ("menu_settings", settings_btn_normal, settings_btn_hover, show_settings),
        ("menu_quit", menu_quit_normal, menu_quit_hover, quit_game),
    )
    for index, (tag, normal, hover, command) in enumerate(items):
        menu_canvas.create_image(
            MENU_BTN_X,
            MENU_FIRST_Y + index * MENU_GAP,
            image=normal,
            anchor="nw",
            tags=tag,
        )
        bind_canvas_button(menu_canvas, tag, normal, hover, command)

    menu_canvas.place(x=0, y=0)

howto_canvas = tk.Canvas(
    root, width=600, height=640, bg="#091a0c", highlightthickness=0
)

HOW_TO_LINES = [
    ("\u2191 \u2193 \u2190 \u2192", "Arrow keys move the snake"),
    ("P", "Pause / resume the game"),
    ("ESC", "Quit the game instantly"),
    ("APPLE", "Eat food to grow and score +1"),
    ("SPEED", "Every 5 points the snake gets faster"),
    ("CARE", "Hitting a wall or yourself ends the run"),
]

def show_how_to_play():
    hide_all_screens()
    howto_canvas.delete("all")
    howto_canvas.create_image(0, 0, image=menu_background_photo, anchor="nw")
    howto_canvas.create_image(300, 110, image=howto_title_photo, anchor="center")
    howto_canvas.create_image(70, 190, image=howto_card_photo, anchor="nw")

    y = 232
    for key, text in HOW_TO_LINES:
        howto_canvas.create_text(
            110, y, text=key, fill="#ffd778", font=("Poppins", 13, "bold"), anchor="w"
        )
        howto_canvas.create_text(
            250, y, text=text, fill="#dffbe3", font=("Poppins", 12), anchor="w"
        )
        y += 44

    howto_canvas.create_text(
        300,
        532,
        text="Tip: plan your turns early — the tail is unforgiving.",
        fill="#8fe39a",
        font=("Poppins", 11, "italic"),
    )
    howto_canvas.create_image(
        190, 560, image=back_btn_normal, anchor="nw", tags="howto_back"
    )
    bind_canvas_button(
        howto_canvas, "howto_back", back_btn_normal, back_btn_hover, show_menu
    )
    howto_canvas.place(x=0, y=0)

settings_canvas = tk.Canvas(
    root, width=600, height=640, bg="#091a0c", highlightthickness=0
)

def toggle_music():
    global music_enabled
    music_enabled = not music_enabled
    save_settings()
    if music_enabled:
        if game_started and not paused:
            play_background_music()
    else:
        stop_background_music()
    play_sound("pause")
    render_settings_toggles()

def toggle_sfx():
    global sfx_enabled
    sfx_enabled = not sfx_enabled
    save_settings()
    play_sound("pause")
    render_settings_toggles()

def render_settings_toggles():
    """(Re)draw only the two toggle buttons so state changes stay snappy."""
    settings_canvas.delete("music_toggle")
    settings_canvas.delete("sfx_toggle")

    music_normal = toggle_on_normal if music_enabled else toggle_off_normal
    music_hover = toggle_on_hover if music_enabled else toggle_off_hover
    sfx_normal = toggle_on_normal if sfx_enabled else toggle_off_normal
    sfx_hover = toggle_on_hover if sfx_enabled else toggle_off_hover

    settings_canvas.create_image(
        400, 262, image=music_normal, anchor="nw", tags="music_toggle"
    )
    bind_canvas_button(
        settings_canvas, "music_toggle", music_normal, music_hover, toggle_music
    )

    settings_canvas.create_image(
        400, 342, image=sfx_normal, anchor="nw", tags="sfx_toggle"
    )
    bind_canvas_button(
        settings_canvas, "sfx_toggle", sfx_normal, sfx_hover, toggle_sfx
    )

def show_settings():
    hide_all_screens()
    settings_canvas.delete("all")
    settings_canvas.create_image(0, 0, image=menu_background_photo, anchor="nw")
    settings_canvas.create_image(300, 130, image=settings_title_photo, anchor="center")
    settings_canvas.create_image(70, 220, image=settings_card_photo, anchor="nw")

    settings_canvas.create_text(
        110, 282, text="Music", fill="#dffbe3",
        font=("Poppins", 15, "bold"), anchor="w",
    )
    settings_canvas.create_text(
        110, 306, text="Looping background track", fill="#7fc48c",
        font=("Poppins", 10), anchor="w",
    )
    settings_canvas.create_text(
        110, 362, text="Sound effects", fill="#dffbe3",
        font=("Poppins", 15, "bold"), anchor="w",
    )
    settings_canvas.create_text(
        110, 386, text="Eating, pausing and game over", fill="#7fc48c",
        font=("Poppins", 10), anchor="w",
    )
    settings_canvas.create_text(
        300, 500, text="Your choices are saved automatically.",
        fill="#8fe39a", font=("Poppins", 11, "italic"),
    )

    render_settings_toggles()

    settings_canvas.create_image(
        190, 545, image=back_btn_normal, anchor="nw", tags="settings_back"
    )
    bind_canvas_button(
        settings_canvas, "settings_back", back_btn_normal, back_btn_hover, show_menu
    )
    settings_canvas.place(x=0, y=0)

score_badge_image = safe_open_image("score_badge.png") or fallback_badge(
    "SCORE", (150, 255, 160)
)
best_badge_image = safe_open_image("best_badge.png") or fallback_badge(
    "BEST", (255, 215, 120)
)
score_badge_photo = ImageTk.PhotoImage(score_badge_image)
best_badge_photo = ImageTk.PhotoImage(best_badge_image)

pause_btn_normal_photo = ImageTk.PhotoImage(
    safe_open_image("pause_btn_normal.png", (40, 34))
    or create_button_with_text(40, 34, *SLATE_NORMAL, "II", None, 14)
)
pause_btn_hover_photo = ImageTk.PhotoImage(
    safe_open_image("pause_btn_hover.png", (40, 34))
    or create_button_with_text(40, 34, *SLATE_HOVER, "II", None, 14)
)
resume_btn_normal_photo = ImageTk.PhotoImage(
    safe_open_image("resume_btn_normal.png", (40, 34))
    or create_button_with_text(40, 34, *GREEN_NORMAL, "\u25b6", None, 14)
)
resume_btn_hover_photo = ImageTk.PhotoImage(
    safe_open_image("resume_btn_hover.png", (40, 34))
    or create_button_with_text(40, 34, *GREEN_HOVER, "\u25b6", None, 14)
)

hud_button_mode = "pause"

hud_canvas = tk.Canvas(
    root, width=600, height=40, bg="#0a100c", highlightthickness=0
)
hud_canvas.create_rectangle(0, 38, 600, 40, fill="#3c7838", width=0)
hud_canvas.create_image(8, 3, image=score_badge_photo, anchor="nw")
hud_canvas.create_image(188, 3, image=best_badge_photo, anchor="nw")

score_value_item = hud_canvas.create_text(
    156, 20, text="0", font=("Poppins", 13, "bold"), fill="#96ffa0", anchor="e"
)
best_value_item = hud_canvas.create_text(
    336, 20, text=str(high_score), font=("Poppins", 13, "bold"),
    fill="#ffd778", anchor="e",
)
hud_menu_normal_photo, hud_menu_hover_photo = make_button_pair(
    104, 30, SLATE_NORMAL, SLATE_HOVER, "MENU", "book", 13
)
hud_menu_item = hud_canvas.create_image(
    424, 5, image=hud_menu_normal_photo, anchor="nw"
)
hud_button_item = hud_canvas.create_image(
    552, 3, image=pause_btn_normal_photo, anchor="nw"
)

def update_hud_score():
    hud_canvas.itemconfigure(score_value_item, text=str(score))
    hud_canvas.itemconfigure(best_value_item, text=str(high_score))

def set_hud_button_mode(mode):
    global hud_button_mode
    hud_button_mode = mode
    hud_canvas.itemconfigure(
        hud_button_item,
        image=(
            pause_btn_normal_photo if mode == "pause" else resume_btn_normal_photo
        ),
    )

def hud_button_enter(event):
    hud_canvas.itemconfigure(
        hud_button_item,
        image=(
            pause_btn_hover_photo
            if hud_button_mode == "pause"
            else resume_btn_hover_photo
        ),
    )

def hud_button_leave(event):
    hud_canvas.itemconfigure(
        hud_button_item,
        image=(
            pause_btn_normal_photo
            if hud_button_mode == "pause"
            else resume_btn_normal_photo
        ),
    )

hud_canvas.tag_bind(hud_button_item, "<Button-1>", lambda e: toggle_pause())        
hud_canvas.tag_bind(hud_button_item, "<Enter>", hud_button_enter)
hud_canvas.tag_bind(hud_button_item, "<Leave>", hud_button_leave)

hud_canvas.tag_bind(hud_menu_item, "<Button-1>", lambda e: open_game_menu())
hud_canvas.tag_bind(
    hud_menu_item,
    "<Enter>",
    lambda e: hud_canvas.itemconfigure(hud_menu_item, image=hud_menu_hover_photo),
)
hud_canvas.tag_bind(
    hud_menu_item,
    "<Leave>",
    lambda e: hud_canvas.itemconfigure(hud_menu_item, image=hud_menu_normal_photo),
)
hud_canvas.place_forget()

canvas = tk.Canvas(root, width=600, height=600, bg="black", highlightthickness=0)

background_image = safe_open_image("snake_background.png", (600, 600)) \
    or fallback_play_field()
background_photo = ImageTk.PhotoImage(background_image)

snake_head_image = safe_open_image("snake_head.png", (20, 20)) or fallback_head()
snake_head_up_image = snake_head_image.rotate(90, expand=True)
snake_head_down_image = snake_head_image.rotate(-90, expand=True)
snake_head_left_image = snake_head_image.transpose(
    Image.Transpose.FLIP_LEFT_RIGHT
)
snake_head_photo = ImageTk.PhotoImage(snake_head_image)
snake_head_up_photo = ImageTk.PhotoImage(snake_head_up_image)
snake_head_down_photo = ImageTk.PhotoImage(snake_head_down_image)
snake_head_left_photo = ImageTk.PhotoImage(snake_head_left_image)

snake_body_image = safe_open_image("snake_body.png", (20, 20)) or fallback_segment(
    (120, 214, 104), (56, 138, 62)
)
snake_body_photo = ImageTk.PhotoImage(snake_body_image)
snake_body_up_image = snake_body_image.rotate(90, expand=True)
snake_body_down_image = snake_body_image.rotate(-90, expand=True)
snake_body_left_image = snake_body_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
snake_body_up_photo = ImageTk.PhotoImage(snake_body_up_image)
snake_body_down_photo = ImageTk.PhotoImage(snake_body_down_image)
snake_body_left_photo = ImageTk.PhotoImage(snake_body_left_image)

snake_tail_up_image = snake_body_image.rotate(90, expand=True)
snake_tail_down_image = snake_body_image.rotate(-90, expand=True)
snake_tail_left_image = snake_body_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
snake_tail_photo = ImageTk.PhotoImage(snake_body_image)
snake_tail_up_photo = ImageTk.PhotoImage(snake_tail_up_image)
snake_tail_down_photo = ImageTk.PhotoImage(snake_tail_down_image)
snake_tail_left_photo = ImageTk.PhotoImage(snake_tail_left_image)

snake_corner_up_right_photo = ImageTk.PhotoImage(
    snake_body_image.rotate(0, expand=True)
)
snake_corner_right_down_photo = ImageTk.PhotoImage(
    snake_body_image.rotate(-90, expand=True)
)
snake_corner_down_left_photo = ImageTk.PhotoImage(
    snake_body_image.rotate(180, expand=True)
)
snake_corner_left_up_photo = ImageTk.PhotoImage(
    snake_body_image.rotate(90, expand=True)
)

snake_food_image = safe_open_image("snake_food.png", (20, 20)) or fallback_food()
snake_food_photo = ImageTk.PhotoImage(snake_food_image)

game_over_canvas = tk.Canvas(
    root, width=600, height=640, bg="black", highlightthickness=0
)

def draw_background():
    canvas.create_image(0, 0, image=background_photo, anchor="nw")

def draw_snake():
    for index, (x, y) in enumerate(snake):
        if index == 0:
            if direction == "right":
                head_image = snake_head_photo
            elif direction == "left":
                head_image = snake_head_left_photo
            elif direction == "up":
                head_image = snake_head_up_photo
            else:
                head_image = snake_head_down_photo
            canvas.create_image(x + 10, y + 10, image=head_image)

        elif index == len(snake) - 1:
            tail_x, tail_y = snake[index]
            body_x, body_y = snake[index - 1]
            if tail_x < body_x:
                tail_image = snake_tail_left_photo
            elif tail_x > body_x:
                tail_image = snake_tail_photo
            elif tail_y < body_y:
                tail_image = snake_tail_up_photo
            else:
                tail_image = snake_tail_down_photo
            canvas.create_image(x + 10, y + 10, image=tail_image)

        else:
            previous_x, previous_y = snake[index - 1]
            next_x, next_y = snake[index + 1]
            if previous_x == next_x:
                body_image = snake_body_photo
            elif previous_y == next_y:
                body_image = snake_body_left_photo
            elif (previous_y < y and next_x > x) or (next_y < y and previous_x > x):
                body_image = snake_corner_up_right_photo
            elif (previous_x > x and next_y > y) or (next_x > x and previous_y > y):
                body_image = snake_corner_right_down_photo
            elif (previous_y > y and next_x < x) or (next_y > y and previous_x < x):
                body_image = snake_corner_down_left_photo
            else:
                body_image = snake_corner_left_up_photo
            canvas.create_image(x + 10, y + 10, image=body_image)

def draw_food():
    canvas.create_image(food_x + 10, food_y + 10, image=snake_food_photo)

def change_direction(event):
    global new_direction
    if not game_started or paused:
        return
    if event.keysym == "Up":
        new_direction = "up"
    elif event.keysym == "Down":
        new_direction = "down"
    elif event.keysym == "Left":
        new_direction = "left"
    elif event.keysym == "Right":
        new_direction = "right"

def create_food():
    global food_x, food_y
    while True:
        food_x = random.randrange(WALL_LEFT, WALL_RIGHT, 20)
        food_y = random.randrange(WALL_TOP, WALL_BOTTOM, 20)
        if (food_x, food_y) not in snake:
            break

def play_background_music():
    if not music_enabled:
        return
    try:
        winsound.PlaySound(
            MUSIC_FILE,
            winsound.SND_FILENAME
            | winsound.SND_ASYNC
            | winsound.SND_LOOP
            | winsound.SND_NODEFAULT,
        )
    except Exception as e:
        print("Background music error:", e)

def stop_background_music():
    try:
        winsound.PlaySound(None, winsound.SND_PURGE)
    except Exception:
        pass

def play_sound(sound_type):
    if not sfx_enabled:
        return
    try:
        if sound_type == "eat":
            winsound.Beep(800, 80)
        elif sound_type == "game_over":
            winsound.Beep(300, 200)
            winsound.Beep(200, 300)
        elif sound_type == "pause":
            winsound.Beep(500, 100)
    except Exception:
        pass

def begin_round():
    """Shared entry point used by PLAY and PLAY AGAIN."""
    global snake, score, speed, direction, new_direction
    global game_loop_id, game_started, paused

    global game_menu_open
    game_menu_open = False
    game_started = True
    paused = False
    score = 0
    speed = 100
    direction = "right"
    new_direction = "right"
    snake = [(300, 310), (280, 310), (260, 310)]

    hide_all_screens()
    hud_canvas.place(x=0, y=0)
    hud_canvas.itemconfigure(hud_button_item, state="normal")
    set_hud_button_mode("pause")
    update_hud_score()

    canvas.place(x=0, y=40)
    create_food()
    canvas.delete("all")
    draw_background()
    draw_snake()
    draw_food()
    play_background_music()

    game_loop_id = root.after(speed, move_snake)

def start_game(event=None):
    begin_round()

def restart_game():
    begin_round()

GO_BTN_W = 300
GO_BTN_H = 52
GO_BTN_GAP = 60
CARD_WIDTH = 360
CARD_HEIGHT = 130 + GO_BTN_GAP * 3 + 12                                      
CARD_X = (600 - CARD_WIDTH) // 2
CARD_Y = 640 - CARD_HEIGHT - 40
TITLE_Y = 130
BUTTON_X = (600 - GO_BTN_W) // 2
PLAY_AGAIN_Y = CARD_Y + 122
MENU_BACK_Y = PLAY_AGAIN_Y + GO_BTN_GAP
QUIT_Y = MENU_BACK_Y + GO_BTN_GAP

game_over_card_photo = ImageTk.PhotoImage(
    create_glass_card(CARD_WIDTH, CARD_HEIGHT, 24)
)

play_again_btn_normal_photo, play_again_btn_hover_photo = make_button_pair(
    GO_BTN_W, GO_BTN_H, GREEN_NORMAL, GREEN_HOVER, "PLAY AGAIN", "refresh", 18
)
quit_btn_normal_photo, quit_btn_hover_photo = make_button_pair(
    GO_BTN_W, GO_BTN_H, RED_NORMAL, RED_HOVER, "QUIT", "exit", 18
)
menu_btn_normal_photo, menu_btn_hover_photo = make_button_pair(
    GO_BTN_W, GO_BTN_H, SLATE_NORMAL, SLATE_HOVER, "MAIN MENU", "back", 18
)

GAME_MENU_CARD_W = 320
GAME_MENU_CARD_H = 300
GAME_MENU_CARD_X = (600 - GAME_MENU_CARD_W) // 2
GAME_MENU_CARD_Y = 140
GAME_MENU_BTN_W = 250
GAME_MENU_BTN_H = 46
GAME_MENU_BTN_X = (600 - GAME_MENU_BTN_W) // 2
GAME_MENU_FIRST_Y = GAME_MENU_CARD_Y + 74
GAME_MENU_GAP = 56

game_menu_card_photo = ImageTk.PhotoImage(
    create_glass_card(GAME_MENU_CARD_W, GAME_MENU_CARD_H, 24)
)
gm_resume_normal, gm_resume_hover = make_button_pair(
    GAME_MENU_BTN_W, GAME_MENU_BTN_H, GREEN_NORMAL, GREEN_HOVER, "RESUME", "play", 17
)
gm_restart_normal, gm_restart_hover = make_button_pair(
    GAME_MENU_BTN_W, GAME_MENU_BTN_H, GOLD_NORMAL, GOLD_HOVER, "RESTART", "refresh", 17
)
gm_mainmenu_normal, gm_mainmenu_hover = make_button_pair(
    GAME_MENU_BTN_W, GAME_MENU_BTN_H, SLATE_NORMAL, SLATE_HOVER, "MAIN MENU", "back", 17
)

game_menu_open = False

def open_game_menu():
    """MENU button during play: pause and show an overlay - never quits."""
    global game_menu_open, paused, game_loop_id
    if not game_started or game_menu_open:
        return

    game_menu_open = True
    paused = True
    if game_loop_id is not None:
        try:
            root.after_cancel(game_loop_id)
        except Exception:
            pass
        game_loop_id = None
    stop_background_music()
    set_hud_button_mode("resume")
    play_sound("pause")
    draw_game_menu()

def draw_game_menu():
    canvas.delete("game_menu")
    canvas.create_rectangle(
        0, 0, 600, 600, fill="#041206", stipple="gray50", width=0, tags="game_menu"
    )
    canvas.create_image(
        GAME_MENU_CARD_X, GAME_MENU_CARD_Y,
        image=game_menu_card_photo, anchor="nw", tags="game_menu",
    )
    canvas.create_text(
        300, GAME_MENU_CARD_Y + 40, text="PAUSED", fill="#ffd778",
        font=("Poppins", 26, "bold"), tags="game_menu",
    )

    items = (
        ("gm_resume", gm_resume_normal, gm_resume_hover, close_game_menu),
        ("gm_restart", gm_restart_normal, gm_restart_hover, restart_game),
        ("gm_main", gm_mainmenu_normal, gm_mainmenu_hover, show_menu),
    )
    for index, (tag, normal, hover, command) in enumerate(items):
        canvas.create_image(
            GAME_MENU_BTN_X,
            GAME_MENU_FIRST_Y + index * GAME_MENU_GAP,
            image=normal,
            anchor="nw",
            tags=("game_menu", tag),
        )
        bind_canvas_button(canvas, tag, normal, hover, command)

    canvas.create_text(
        300, GAME_MENU_CARD_Y + GAME_MENU_CARD_H - 22,
        text="P resumes  \u00b7  ESC returns to the start screen",
        fill="#8fe39a", font=("Poppins", 10), tags="game_menu",
    )

def close_game_menu(event=None):
    """Resume play from the overlay."""
    global game_menu_open, paused, game_loop_id
    if not game_menu_open:
        return
    game_menu_open = False
    paused = False
    canvas.delete("game_menu")
    set_hud_button_mode("pause")
    play_background_music()
    canvas.delete("all")
    draw_background()
    draw_snake()
    draw_food()
    game_loop_id = root.after(speed, move_snake)

def quit_game(event=None):
    global game_loop_id
    if game_loop_id is not None:
        try:
            root.after_cancel(game_loop_id)
        except Exception:
            pass
        game_loop_id = None
    save_high_score()
    save_settings()
    stop_background_music()
    root.destroy()

def game_over():
    global game_loop_id, game_started, paused

    game_started = False
    paused = False
    stop_background_music()
    play_sound("game_over")

    if game_loop_id is not None:
        root.after_cancel(game_loop_id)
        game_loop_id = None

    hide_all_screens()
    game_over_canvas.place(x=0, y=0)
    game_over_canvas.delete("all")
    game_over_canvas.create_image(0, 0, image=game_over_photo, anchor="nw")
    game_over_canvas.create_image(300, TITLE_Y, image=title_text_photo, anchor="center")
    game_over_canvas.create_image(
        CARD_X, CARD_Y, image=game_over_card_photo, anchor="nw"
    )

    game_over_canvas.create_text(
        300, CARD_Y + 34, text="YOUR SCORE", fill="#b4ffbe",
        font=("Poppins", 13, "bold"),
    )
    game_over_canvas.create_text(
        300, CARD_Y + 74, text=str(score), fill="white",
        font=("Poppins", 34, "bold"),
    )
    game_over_canvas.create_text(
        300, CARD_Y + 104, text="Best  " + str(high_score), fill="#ffd778",
        font=("Poppins", 12, "bold"),
    )

    game_over_canvas.create_image(
        BUTTON_X, PLAY_AGAIN_Y, image=play_again_btn_normal_photo,
        anchor="nw", tags="play_again_btn",
    )
    bind_canvas_button(
        game_over_canvas, "play_again_btn",
        play_again_btn_normal_photo, play_again_btn_hover_photo, restart_game,
    )

    game_over_canvas.create_image(
        BUTTON_X, MENU_BACK_Y, image=menu_btn_normal_photo,
        anchor="nw", tags="menu_btn",
    )
    bind_canvas_button(
        game_over_canvas, "menu_btn",
        menu_btn_normal_photo, menu_btn_hover_photo, show_menu,
    )

    game_over_canvas.create_image(
        BUTTON_X, QUIT_Y, image=quit_btn_normal_photo,
        anchor="nw", tags="quit_btn",
    )
    bind_canvas_button(
        game_over_canvas, "quit_btn",
        quit_btn_normal_photo, quit_btn_hover_photo, quit_game,
    )

def toggle_pause(event=None):
    global paused, game_loop_id
    if not game_started:
        return

    if paused or game_menu_open:
        close_game_menu()
    else:
        open_game_menu()

def food_eat_effect():
    global food_effect_id, food_effect_step

    food_effect_step += 1
    if food_effect_step >= 5:
        if food_effect_id is not None:
            canvas.after_cancel(food_effect_id)
        food_effect_id = None
        food_effect_step = 0
        return

    canvas.delete("food_effect")
    size = food_effect_step * 3
    canvas.create_oval(
        food_x + 10 - size,
        food_y + 10 - size,
        food_x + 10 + size,
        food_y + 10 + size,
        outline="yellow",
        width=2,
        tags="food_effect",
    )
    food_effect_id = canvas.after(40, food_eat_effect)

def move_snake():
    global snake, score, high_score, speed, direction
    global game_loop_id, food_effect_step

    if new_direction == "up" and direction != "down":
        direction = "up"
    elif new_direction == "down" and direction != "up":
        direction = "down"
    elif new_direction == "left" and direction != "right":
        direction = "left"
    elif new_direction == "right" and direction != "left":
        direction = "right"

    head_x, head_y = snake[0]
    if direction == "up":
        new_head = (head_x, head_y - 20)
    elif direction == "down":
        new_head = (head_x, head_y + 20)
    elif direction == "left":
        new_head = (head_x - 20, head_y)
    else:
        new_head = (head_x + 20, head_y)

    if (
        new_head[0] < WALL_LEFT
        or new_head[0] >= WALL_RIGHT
        or new_head[1] < WALL_TOP
        or new_head[1] >= WALL_BOTTOM
    ):
        game_over()
        return

    if new_head in snake:
        game_over()
        return

    snake.insert(0, new_head)

    if new_head[0] == food_x and new_head[1] == food_y:
        food_effect_step = 0
        food_eat_effect()
        play_sound("eat")
        score += 1
        if score > high_score:
            high_score = score
            save_high_score()
        update_hud_score()
        create_food()
        if score % 5 == 0 and speed > 40:
            speed -= 10
    else:
        snake.pop()

    canvas.delete("all")
    draw_background()
    draw_snake()
    draw_food()
    game_loop_id = root.after(speed, move_snake)

def handle_escape(event=None):
    """ESC: leave a screen back to the menu, or quit from the menu."""
    if game_started:
        show_menu()
    else:
        quit_game()

root.bind("<Key>", change_direction)
root.bind("<p>", toggle_pause)
root.bind("<P>", toggle_pause)
root.bind("<Escape>", handle_escape)
root.protocol("WM_DELETE_WINDOW", quit_game)

show_menu()
root.mainloop()
