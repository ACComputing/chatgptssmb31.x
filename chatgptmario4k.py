#!/usr/bin/env python3.14
"""
AC's Mario Forever Pygame Engine 0.1
Python 3.14
files = off
Built-in SMB3-style Mario pixel sprites. Optional user-owned PNG import is supported.

Install:
python3.14 -m pip install pygame-ce

Run:
python3.14 acs_smb4k.py
"""

import pygame
import sys
import math
import json
from pathlib import Path

pygame.init()

WIDTH, HEIGHT = 960, 540
FPS = 60
TILE = 48

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AC's Mario Forever Pygame Engine 0.1")
clock = pygame.time.Clock()

SKY = (92, 148, 252)
GROUND = (184, 96, 40)
GROUND_DARK = (120, 60, 20)
BRICK = (188, 76, 32)
BRICK_DARK = (120, 44, 20)
QUESTION = (240, 176, 32)
QUESTION_DARK = (160, 96, 16)
PIPE = (40, 176, 64)
PIPE_DARK = (24, 112, 40)
PLAYER = (220, 40, 40)
PLAYER_DARK = (120, 20, 20)
GOOMBA = (120, 70, 30)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COIN = (255, 220, 40)
FLAGPOLE = (220, 220, 220)
MENU_BLUE = (48, 96, 192)
MENU_BLUE_DARK = (24, 48, 120)
MENU_YELLOW = (255, 220, 80)

WORLD_COUNT = 8
LEVELS_PER_WORLD = 4
WORLD_THEMES = [
    {"name": "GRASS LAND", "sky": (92, 148, 252), "land": (48, 172, 80), "dark": (24, 112, 48), "path": (232, 196, 96)},
    {"name": "DESERT HILL", "sky": (252, 188, 92), "land": (220, 176, 72), "dark": (152, 104, 40), "path": (244, 220, 128)},
    {"name": "WATER COAST", "sky": (96, 188, 252), "land": (40, 152, 120), "dark": (24, 92, 104), "path": (236, 220, 132)},
    {"name": "GIANT FIELD", "sky": (132, 204, 112), "land": (72, 188, 72), "dark": (36, 120, 48), "path": (220, 204, 92)},
    {"name": "SKY BRIDGE", "sky": (132, 172, 252), "land": (168, 196, 232), "dark": (80, 112, 176), "path": (236, 236, 180)},
    {"name": "ICE VALLEY", "sky": (180, 224, 252), "land": (160, 228, 236), "dark": (68, 140, 172), "path": (240, 248, 248)},
    {"name": "PIPE MAZE", "sky": (88, 168, 124), "land": (40, 176, 64), "dark": (20, 96, 44), "path": (184, 220, 116)},
    {"name": "DARK CASTLE", "sky": (44, 48, 76), "land": (112, 80, 104), "dark": (52, 44, 64), "path": (188, 144, 96)},
]
MAP_NODE_POS = ((150, 370), (360, 330), (570, 365), (780, 295))

font = pygame.font.SysFont("Arial", 24, bold=True)
small_font = pygame.font.SysFont("Arial", 18, bold=True)
big_font = pygame.font.SysFont("Arial", 44, bold=True)
title_font = pygame.font.SysFont("Arial", 58, bold=True)
subtitle_font = pygame.font.SysFont("Arial", 34, bold=True)

BASE_DIR = Path(__file__).resolve().parent
SPRITE_DIRS = (
    BASE_DIR / "assets" / "sprites" / "smb3",
    BASE_DIR / "smb3_sprites",
    BASE_DIR / "assets" / "sprites" / "smb1",
    BASE_DIR / "smb1_sprites",
    BASE_DIR / "assets" / "sprites" / "smw",
    BASE_DIR / "smw_sprites",
)
PLAYER_DRAW_SIZE = (48, 56)
MENU_PLAYER_DRAW_SIZE = (64, 82)
GOOMBA_DRAW_SIZE = (42, 38)
COIN_DRAW_SIZE = (24, 24)

SPRITE_SPECS = {
    "player_idle": (("player_idle.png", "mario_idle.png"), PLAYER_DRAW_SIZE),
    "player_walk1": (("player_walk1.png", "mario_walk1.png"), PLAYER_DRAW_SIZE),
    "player_walk2": (("player_walk2.png", "mario_walk2.png"), PLAYER_DRAW_SIZE),
    "player_jump": (("player_jump.png", "mario_jump.png"), PLAYER_DRAW_SIZE),
    "menu_mario": (("menu_mario.png", "mario_menu.png"), MENU_PLAYER_DRAW_SIZE),
    "goomba_walk1": (("goomba_walk1.png", "goomba1.png"), GOOMBA_DRAW_SIZE),
    "goomba_walk2": (("goomba_walk2.png", "goomba2.png"), GOOMBA_DRAW_SIZE),
    "goomba_squish": (("goomba_squish.png", "goomba_flat.png"), GOOMBA_DRAW_SIZE),
    "tile_ground": (("tile_ground.png", "ground.png"), (TILE, TILE)),
    "tile_brick": (("tile_brick.png", "brick.png"), (TILE, TILE)),
    "tile_question": (("tile_question.png", "question.png"), (TILE, TILE)),
    "tile_used": (("tile_used.png", "used_block.png"), (TILE, TILE)),
    "tile_pipe": (("tile_pipe.png", "pipe.png"), (TILE, TILE)),
    "coin": (("coin.png",), COIN_DRAW_SIZE),
    "flag_ball": (("flag_ball.png",), (16, 16)),
    "flag_banner": (("flag_banner.png", "flag.png"), (92, 50)),
}


class SpriteBank:
    def __init__(self):
        self.images = {}
        self.source_label = "generated SMB3-style fallback"
        self.external_loaded = 0

    def add(self, key, image):
        self.images[key] = image

    def get(self, key):
        return self.images.get(key)


def blank_sprite(size):
    return pygame.Surface(size, pygame.SRCALPHA)


def scale_sprite(image, size):
    if size and image.get_size() != size:
        return pygame.transform.scale(image, size)
    return image


def load_sprite_image(path, size=None, frame=None):
    image = pygame.image.load(str(path)).convert_alpha()

    if frame:
        rect = pygame.Rect(*frame)
        cropped = blank_sprite(rect.size)
        cropped.blit(image, (0, 0), rect)
        image = cropped

    return scale_sprite(image, size)


def load_manifest_sprites(bank, root):
    manifest_path = root / "sprites.json"
    if not manifest_path.exists():
        return 0

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Sprite import skipped bad manifest: {manifest_path} ({exc})")
        return 0

    sprites = data.get("sprites", data) if isinstance(data, dict) else {}
    loaded = 0

    for key, entry in sprites.items():
        default_size = SPRITE_SPECS.get(key, ((key + ".png",), None))[1]
        filename = None
        frame = None
        size = default_size

        if isinstance(entry, str):
            filename = entry
        elif isinstance(entry, dict):
            filename = entry.get("file") or entry.get("image") or entry.get("sheet")
            frame = entry.get("rect") or entry.get("frame")
            size = tuple(entry.get("size", default_size)) if entry.get("size", default_size) else None

        if not filename:
            continue

        sprite_path = root / filename
        if not sprite_path.exists():
            print(f"Sprite import missing file: {sprite_path}")
            continue

        try:
            bank.add(key, load_sprite_image(sprite_path, size, frame))
            loaded += 1
        except pygame.error as exc:
            print(f"Sprite import skipped {sprite_path}: {exc}")

    return loaded


def load_conventional_sprites(bank, root):
    loaded = 0

    for key, (filenames, size) in SPRITE_SPECS.items():
        for filename in filenames:
            sprite_path = root / filename
            if not sprite_path.exists():
                continue

            try:
                bank.add(key, load_sprite_image(sprite_path, size))
                loaded += 1
            except pygame.error as exc:
                print(f"Sprite import skipped {sprite_path}: {exc}")
            break

    return loaded


def load_loose_sprites(bank, root):
    loaded = 0

    for sprite_path in sorted(root.glob("*.png")):
        key = sprite_path.stem.lower()
        if key in bank.images:
            continue

        try:
            bank.add(key, load_sprite_image(sprite_path))
            loaded += 1
        except pygame.error as exc:
            print(f"Sprite import skipped {sprite_path}: {exc}")

    return loaded


def make_pixel_surface(pattern, palette, scale=3, target_size=None, align_bottom=True):
    width = max(len(row) for row in pattern)
    height = len(pattern)
    low = blank_sprite((width, height))

    for y, row in enumerate(pattern):
        for x, char in enumerate(row.ljust(width)):
            color = palette.get(char)
            if color:
                low.set_at((x, y), color)

    scaled = pygame.transform.scale(low, (width * scale, height * scale))
    if not target_size:
        return scaled

    surf = blank_sprite(target_size)
    x = (target_size[0] - scaled.get_width()) // 2
    y = target_size[1] - scaled.get_height() if align_bottom else 0
    surf.blit(scaled, (x, y))
    return surf


def make_player_sprite(pose):
    low = blank_sprite((24, 28))
    red = (216, 40, 24)
    red_dark = (136, 24, 24)
    blue = (48, 92, 208)
    blue_dark = (24, 48, 132)
    skin = (252, 188, 116)
    skin_dark = (208, 128, 72)
    brown = (112, 64, 32)

    def px(color, x, y, w=1, h=1):
        pygame.draw.rect(low, color, (x, y, w, h))

    if pose == "jump":
        arm_shapes = [("left_up", 3, 8), ("right_out", 18, 13)]
        leg_shapes = [("left_tuck", 6, 21), ("right_down", 14, 21)]
    elif pose == "walk1":
        arm_shapes = [("left_out", 2, 13), ("right_back", 18, 12)]
        leg_shapes = [("left_back", 5, 21), ("right_forward", 14, 20)]
    elif pose == "walk2":
        arm_shapes = [("left_back", 3, 12), ("right_out", 18, 13)]
        leg_shapes = [("left_forward", 6, 20), ("right_back", 15, 21)]
    else:
        arm_shapes = [("left_down", 3, 12), ("right_down", 18, 12)]
        leg_shapes = [("left_down", 6, 21), ("right_down", 14, 21)]

    for shape, x, y in arm_shapes:
        if shape == "left_up":
            px(BLACK, x, y, 4, 8)
            px(red, x + 1, y + 1, 2, 5)
            px(WHITE, x - 1, y, 4, 3)
            px(BLACK, x - 1, y, 4, 1)
        elif shape == "left_out":
            px(BLACK, x, y, 6, 4)
            px(red, x + 1, y + 1, 4, 2)
            px(WHITE, x - 1, y + 2, 4, 3)
            px(BLACK, x - 1, y + 2, 4, 1)
        elif shape == "right_out":
            px(BLACK, x, y, 5, 4)
            px(red, x, y + 1, 3, 2)
            px(WHITE, x + 2, y + 2, 4, 3)
            px(BLACK, x + 2, y + 2, 4, 1)
        elif shape == "right_back":
            px(BLACK, x, y, 4, 7)
            px(red, x + 1, y + 1, 2, 4)
            px(WHITE, x + 1, y + 5, 4, 3)
            px(BLACK, x + 1, y + 5, 4, 1)
        else:
            px(BLACK, x, y, 4, 8)
            px(red, x + 1, y + 1, 2, 5)
            px(WHITE, x, y + 6, 4, 3)
            px(BLACK, x, y + 6, 4, 1)

    # SMB3-ish big Mario body, with bright overalls and white gloves.
    px(BLACK, 6, 11, 12, 12)
    px(red, 7, 11, 10, 5)
    px(red_dark, 7, 15, 10, 2)
    px(blue, 7, 16, 10, 6)
    px(blue_dark, 8, 18, 3, 4)
    px(blue_dark, 13, 18, 3, 4)
    px(blue, 9, 13, 2, 7)
    px(blue, 14, 13, 2, 7)
    px(MENU_YELLOW, 10, 16, 1, 1)
    px(MENU_YELLOW, 14, 16, 1, 1)

    for shape, x, y in leg_shapes:
        if "forward" in shape:
            px(BLACK, x, y, 5, 5)
            px(blue, x + 1, y, 3, 4)
            px(BLACK, x - 1, y + 4, 7, 3)
            px(brown, x - 1, y + 5, 6, 1)
        elif "back" in shape:
            px(BLACK, x, y, 4, 5)
            px(blue, x + 1, y, 2, 4)
            px(BLACK, x - 1, y + 4, 6, 3)
            px(brown, x, y + 5, 5, 1)
        elif "tuck" in shape:
            px(BLACK, x, y, 6, 4)
            px(blue, x + 1, y, 4, 3)
            px(BLACK, x - 1, y + 3, 5, 3)
            px(brown, x - 1, y + 4, 4, 1)
        else:
            px(BLACK, x, y, 4, 5)
            px(blue, x + 1, y, 2, 4)
            px(BLACK, x - 2, y + 4, 7, 3)
            px(brown, x - 1, y + 5, 5, 1)

    # Head, cap, hair, nose, and moustache.
    px(BLACK, 7, 0, 9, 1)
    px(BLACK, 6, 1, 12, 2)
    px(BLACK, 5, 3, 15, 2)
    px(red, 8, 1, 8, 2)
    px(red, 6, 3, 12, 2)
    px(red_dark, 17, 4, 3, 1)
    px(WHITE, 11, 2, 2, 1)
    px(BLACK, 5, 5, 14, 7)
    px(skin, 8, 5, 8, 6)
    px(skin, 7, 8, 11, 3)
    px(skin_dark, 8, 10, 8, 1)
    px(brown, 5, 5, 4, 5)
    px(brown, 10, 9, 7, 2)
    px(BLACK, 14, 6, 1, 2)
    px(skin, 16, 7, 3, 2)
    px(BLACK, 17, 9, 2, 1)

    return pygame.transform.scale(low, PLAYER_DRAW_SIZE)


def make_menu_player_sprite():
    return pygame.transform.scale(make_player_sprite("idle"), MENU_PLAYER_DRAW_SIZE)


def make_goomba_sprite(squish=False, step=0):
    palette = {
        "K": BLACK,
        "B": (132, 76, 32),
        "D": (80, 44, 20),
        "W": WHITE,
    }
    if squish:
        return make_pixel_surface(
            [
                "..............",
                "..............",
                "..............",
                "...KKKKKKKK...",
                "..KBBBBBBBBK..",
                ".KBBBBBBBBBBK.",
                ".KBDDBBDDBBDK.",
                "..KKK....KKK..",
                "..............",
                "..............",
                "..............",
                "..............",
            ],
            palette,
            scale=3,
            target_size=GOOMBA_DRAW_SIZE,
        )

    feet = ("..KK......KK..", ".KKK......KKK.") if step else (".KKK......KKK.", "..KK......KK..")
    pattern = [
        "....KKKKKK....",
        "...KBBBBBBK...",
        "..KBBBBBBBBK..",
        ".KBBBBBBBBBBK.",
        ".KBBKBBBBKBBK.",
        ".KBBWKBBWBBBK.",
        ".KBBKBBBBKBBK.",
        "..KBBBDDBBBK..",
        "...KBBBBBBK...",
        feet[0],
        feet[1],
        "..............",
    ]
    return make_pixel_surface(pattern, palette, scale=3, target_size=GOOMBA_DRAW_SIZE)


def make_tile_sprite(kind):
    palette = {
        "K": BLACK,
        "G": GROUND,
        "D": GROUND_DARK,
        "B": BRICK,
        "b": BRICK_DARK,
        "Q": QUESTION,
        "q": QUESTION_DARK,
        "Y": MENU_YELLOW,
        "P": PIPE,
        "p": PIPE_DARK,
        "H": (92, 224, 104),
        "W": WHITE,
    }
    if kind == "ground":
        pattern = [
            "DDDDDDDDDDDDDDDD",
            "DGGGGDGGGGDGGGGD",
            "DGGGGDGGGGDGGGGD",
            "DGGGGDGGGGDGGGGD",
            "DDDDDDDDDDDDDDDD",
            "GGDGGGGDGGGGDGGG",
            "GGDGGGGDGGGGDGGG",
            "GGDGGGGDGGGGDGGG",
            "DDDDDDDDDDDDDDDD",
            "DGGGGDGGGGDGGGGD",
            "DGGGGDGGGGDGGGGD",
            "DGGGGDGGGGDGGGGD",
            "DDDDDDDDDDDDDDDD",
            "GGDGGGGDGGGGDGGG",
            "GGDGGGGDGGGGDGGG",
            "GGDGGGGDGGGGDGGG",
        ]
    elif kind == "brick":
        pattern = [
            "bbbbbbbbbbbbbbbb",
            "bBBBBBBbBBBBBBBb",
            "bBBBBBBbBBBBBBBb",
            "bBBBBBBbBBBBBBBb",
            "bbbbbbbbbbbbbbbb",
            "BBBBbBBBBBBBbBBB",
            "BBBBbBBBBBBBbBBB",
            "BBBBbBBBBBBBbBBB",
            "bbbbbbbbbbbbbbbb",
            "bBBBBBBbBBBBBBBb",
            "bBBBBBBbBBBBBBBb",
            "bBBBBBBbBBBBBBBb",
            "bbbbbbbbbbbbbbbb",
            "BBBBbBBBBBBBbBBB",
            "BBBBbBBBBBBBbBBB",
            "BBBBbBBBBBBBbBBB",
        ]
    elif kind == "question":
        pattern = [
            "qqqqqqqqqqqqqqqq",
            "qQQQQQQQQQQQQQQq",
            "qQQYYYYYYYYQQQQq",
            "qQYYQQQQQQYYQQQq",
            "qQYQQqqqqQQYQQQq",
            "qQQQqQQQQqYQQQQq",
            "qQQQQQQQQYQQQQQq",
            "qQQQQQQqYQQQQQQq",
            "qQQQQQqYQQQQQQQq",
            "qQQQQQYQQQQQQQQq",
            "qQQQQQYQQQQQQQQq",
            "qQQQQQQQQQQQQQQq",
            "qQQQQQYYQQQQQQQq",
            "qQQQQQYYQQQQQQQq",
            "qQQQQQQQQQQQQQQq",
            "qqqqqqqqqqqqqqqq",
        ]
    elif kind == "used":
        pattern = [
            "bbbbbbbbbbbbbbbb",
            "bBBBBBBBBBBBBBBb",
            "bBBBBBBBBBBBBBBb",
            "bBBbBBBBBBBbBBBb",
            "bBBBBBBBBBBBBBBb",
            "bBBBBBBBBBBBBBBb",
            "bBBBBBBBBBBBBBBb",
            "bBBBBbBBBbBBBBBb",
            "bBBBBbBBBbBBBBBb",
            "bBBBBBBBBBBBBBBb",
            "bBBBBBBBBBBBBBBb",
            "bBBBBBBBBBBBBBBb",
            "bBBbBBBBBBBbBBBb",
            "bBBBBBBBBBBBBBBb",
            "bBBBBBBBBBBBBBBb",
            "bbbbbbbbbbbbbbbb",
        ]
    elif kind == "pipe":
        pattern = [
            "pppppppppppppppp",
            "pHHHHHHPPPPPPPPp",
            "pHHHHHHPPPPPPPPp",
            "pHHHHHHPPPPPPPPp",
            "pHHHHHHPPPPPPPPp",
            "pPPPPPPPPPPPPPPp",
            "pppppppppppppppp",
            "..pHHHHPPPPPPp..",
            "..pHHHHPPPPPPp..",
            "..pHHHHPPPPPPp..",
            "..pHHHHPPPPPPp..",
            "..pHHHHPPPPPPp..",
            "..pHHHHPPPPPPp..",
            "..pHHHHPPPPPPp..",
            "..pHHHHPPPPPPp..",
            "..ppppppppppp...",
        ]
    else:
        pattern = ["." * 16 for _ in range(16)]

    return make_pixel_surface(pattern, palette, scale=3, target_size=(TILE, TILE))


def make_coin_sprite():
    return make_pixel_surface(
        [
            "..KKKK..",
            ".KYYYYK.",
            "KYYWWYYK",
            "KYYYYYYK",
            "KYYYYYYK",
            "KYYqqYYK",
            ".KYYYYK.",
            "..KKKK..",
        ],
        {
            "K": BLACK,
            "Y": COIN,
            "W": WHITE,
            "q": QUESTION_DARK,
        },
        scale=3,
        target_size=COIN_DRAW_SIZE,
    )


def make_flag_ball_sprite():
    return make_pixel_surface(
        [
            "...KK...",
            "..KYYK..",
            ".KYYYYK.",
            "KYYWWYYK",
            "KYYYYYYK",
            ".KYYYYK.",
            "..KYYK..",
            "...KK...",
        ],
        {"K": BLACK, "Y": COIN, "W": WHITE},
        scale=2,
        target_size=(16, 16),
    )


def make_flag_banner_sprite():
    pattern = [
        "KKKKKKKKKKKKKKKKKKKKKKK",
        "KWWWWWWWWWWWWWWWWWWKKK.",
        "KWWWWWWWWWWWWWWWWKKK...",
        "KWWWWWWWWWWWWWWKKK.....",
        "KWWWWWWWWWWWWKKK.......",
        "KWWWWWWWWWWKKK.........",
        "KWWWWWWWWKKK...........",
        "KWWWWWWKKK.............",
        "KWWWWKKK...............",
        "KWWKKK.................",
        "KKK....................",
    ]
    return make_pixel_surface(pattern, {"K": BLACK, "W": WHITE}, scale=4, target_size=(92, 50), align_bottom=False)


def add_generated_sprites(bank):
    bank.add("player_idle", make_player_sprite("idle"))
    bank.add("player_walk1", make_player_sprite("walk1"))
    bank.add("player_walk2", make_player_sprite("walk2"))
    bank.add("player_jump", make_player_sprite("jump"))
    bank.add("menu_mario", make_menu_player_sprite())
    bank.add("goomba_walk1", make_goomba_sprite(step=0))
    bank.add("goomba_walk2", make_goomba_sprite(step=1))
    bank.add("goomba_squish", make_goomba_sprite(squish=True))
    bank.add("tile_ground", make_tile_sprite("ground"))
    bank.add("tile_brick", make_tile_sprite("brick"))
    bank.add("tile_question", make_tile_sprite("question"))
    bank.add("tile_used", make_tile_sprite("used"))
    bank.add("tile_pipe", make_tile_sprite("pipe"))
    bank.add("coin", make_coin_sprite())
    bank.add("flag_ball", make_flag_ball_sprite())
    bank.add("flag_banner", make_flag_banner_sprite())


def build_sprite_bank():
    bank = SpriteBank()
    add_generated_sprites(bank)

    for root in SPRITE_DIRS:
        if not root.exists():
            continue

        loaded = load_loose_sprites(bank, root)
        loaded += load_conventional_sprites(bank, root)
        loaded += load_manifest_sprites(bank, root)

        if loaded:
            bank.external_loaded = loaded
            bank.source_label = f"user sprites from {root}"
            break

    return bank


SPRITES = build_sprite_bank()


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def world_theme(world):
    return WORLD_THEMES[(world - 1) % len(WORLD_THEMES)]


def draw_center_text(text, y, color=WHITE, fnt=font, shadow=True):
    img = fnt.render(text, True, color)
    x = WIDTH // 2 - img.get_width() // 2

    if shadow:
        shadow_img = fnt.render(text, True, BLACK)
        screen.blit(shadow_img, (x + 4, y + 4))

    screen.blit(img, (x, y))


def draw_text(text, x, y, color=WHITE, fnt=font):
    img = fnt.render(text, True, color)
    screen.blit(img, (x, y))


def draw_cloud(x, y, cam):
    px = x - cam * 0.35
    pygame.draw.ellipse(screen, WHITE, (px, y, 80, 34))
    pygame.draw.ellipse(screen, WHITE, (px + 25, y - 18, 60, 45))
    pygame.draw.ellipse(screen, WHITE, (px + 65, y, 80, 34))


def draw_hill(x, y, cam, light=(40, 180, 80), dark=(28, 130, 60)):
    px = x - cam * 0.5
    pygame.draw.polygon(
        screen,
        light,
        [(px, y + 90), (px + 140, y - 40), (px + 280, y + 90)],
    )
    pygame.draw.polygon(
        screen,
        dark,
        [(px + 35, y + 90), (px + 140, y - 10), (px + 245, y + 90)],
    )


def add_pipe(grid, x, top_y=9):
    """
    2-tile-tall pipe.
    Ground starts at row 11, so rows 9 and 10 are pipe.
    """
    for y in range(top_y, 11):
        grid[y][x] = "P"
        grid[y][x + 1] = "P"


def place_tile(grid, x, y, value):
    if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
        grid[y][x] = value


def make_level(world=1, stage=1):
    width = 96 + world * 8 + stage * 6
    height = 13
    grid = [["." for _ in range(width)] for _ in range(height)]

    # Continuous ground. No accidental gaps.
    for x in range(width):
        grid[11][x] = "X"
        grid[12][x] = "X"

    # SMB1-style block runs, varied per world/stage.
    first_block = 14 + (world % 3) * 2
    clusters = 4 + stage + world // 2
    spacing = 11 + (world + stage) % 4

    for i in range(clusters):
        x = first_block + i * spacing
        if x > width - 18:
            break

        y = 7 if i % 2 == 0 else 6
        run = 3 + (i + stage) % 3
        for dx in range(run):
            tile = "?" if (dx + i + world) % 4 == 0 else "B"
            place_tile(grid, x + dx, y, tile)

        if i % 2 == 1:
            for dx in range(3):
                place_tile(grid, x + dx + 1, 3, "?" if dx == 1 else "B")

    # Mario-height pipes: all remain 2 tiles tall.
    pipe_count = 2 + stage + (1 if world >= 6 else 0)
    pipe_start = 30 + (world % 4) * 2
    pipe_spacing = 12 + (world % 3)
    for i in range(pipe_count):
        x = pipe_start + i * pipe_spacing
        if x < width - 18:
            add_pipe(grid, x, 9)

    # Goombas and walkers.
    enemy_count = 3 + stage + world // 2
    enemy_spacing = 10 + ((world + stage) % 5)
    for i in range(enemy_count):
        x = 24 + i * enemy_spacing
        if x >= width - 12:
            break
        if grid[10][x] == ".":
            grid[10][x] = "G"

    # World 7 gets a small pipe-field rhythm without changing pipe height.
    if world == 7:
        for x in range(42, min(width - 16, 86), 10):
            add_pipe(grid, x, 9)

    # Staircase up.
    start = width - 32
    for step in range(1, 6):
        x = start + step
        for y in range(11 - step, 11):
            place_tile(grid, x, y, "B")

    # Staircase down.
    start = width - 22
    for step in range(5, 0, -1):
        x = start + (5 - step)
        for y in range(11 - step, 11):
            place_tile(grid, x, y, "B")

    # Castle-style finish for every fourth stage.
    if stage == 4:
        tower_x = width - 15
        for y in range(7, 11):
            place_tile(grid, tower_x, y, "B")
            place_tile(grid, tower_x + 1, y, "B")
        for x in range(width - 28, width - 18):
            place_tile(grid, x, 8, "B")
            if x % 2 == 0:
                place_tile(grid, x, 7, "B")
    else:
        place_tile(grid, width - 14, 7, "B")
        place_tile(grid, width - 13, 7, "B")

    target_enemies = min(3 + stage + world // 2, 10)
    enemy_total = sum(row.count("G") for row in grid)
    for x in range(18, width - 12, 7):
        if enemy_total >= target_enemies:
            break
        if grid[10][x] == ".":
            grid[10][x] = "G"
            enemy_total += 1

    # Flagpole.
    flag_x = width - 6
    for y in range(4, 11):
        place_tile(grid, flag_x, y, "F")

    return ["".join(row) for row in grid]


LEVEL = []
LEVEL_W = 0


def rect_from_tile(tx, ty):
    return pygame.Rect(tx * TILE, ty * TILE, TILE, TILE)


def find_pipe_groups(level):
    groups = []
    visited = set()

    for y, row in enumerate(level):
        for x, c in enumerate(row):
            if c != "P" or (x, y) in visited:
                continue

            width = 0
            while x + width < len(row) and row[x + width] == "P":
                width += 1

            height = 1
            while y + height < len(level):
                next_row = level[y + height]
                if all(next_row[x + dx] == "P" for dx in range(width)):
                    height += 1
                else:
                    break

            for gy in range(y, y + height):
                for gx in range(x, x + width):
                    visited.add((gx, gy))

            groups.append(pygame.Rect(x * TILE, y * TILE, width * TILE, height * TILE))

    return groups


solid_tiles = []
question_tiles = []
coins = []
goombas = []
pipe_groups = []
flag_rect = None
current_world = 1
current_level = 1
map_cursor = 0
completed_levels = set()


def load_level(world, stage):
    global LEVEL, LEVEL_W, solid_tiles, question_tiles, coins, goombas, pipe_groups
    global flag_rect, current_world, current_level

    current_world = world
    current_level = stage
    LEVEL = make_level(world, stage)
    LEVEL_W = len(LEVEL[0]) * TILE
    solid_tiles = []
    question_tiles = []
    coins = []
    goombas = []
    pipe_groups = find_pipe_groups(LEVEL)
    flag_rect = None

    for y, row in enumerate(LEVEL):
        for x, c in enumerate(row):
            r = rect_from_tile(x, y)

            if c in ("X", "B", "?", "P"):
                solid_tiles.append((r, c))

            if c == "?":
                question_tiles.append(r)

            if c == "G":
                goombas.append({
                    "rect": pygame.Rect(x * TILE + 6, y * TILE + 12, 36, 36),
                    "vx": -1.2,
                    "alive": True,
                    "squish": 0,
                })

            if c == "F":
                flag_rect = pygame.Rect(x * TILE + TILE // 2, 120, 8, 390)


player = pygame.Rect(120, 300, 34, 44)
vel_x = 0
vel_y = 0
on_ground = False
facing = 1
score = 0
coins_count = 0
lives = 3
won = False
camera_x = 0
game_state = "menu"

GRAVITY = 0.75
MOVE_ACC = 0.75
MAX_SPEED = 5.2
FRICTION = 0.82
JUMP = -15.5

load_level(current_world, current_level)


def reset_player():
    global vel_x, vel_y, camera_x, won
    player.x = 120
    player.y = 300
    vel_x = 0
    vel_y = 0
    camera_x = 0
    won = False


def start_overworld():
    global game_state
    game_state = "map"


def start_level(world, stage):
    global game_state
    load_level(world, stage)
    reset_player()
    game_state = "game"


def complete_current_level():
    global game_state, map_cursor
    completed_levels.add((current_world, current_level))
    map_cursor = current_level - 1
    game_state = "map"


def get_nearby_solids(rect):
    nearby = []
    buffer = rect.inflate(TILE * 4, TILE * 4)

    for tile, kind in solid_tiles:
        if buffer.colliderect(tile):
            nearby.append((tile, kind))

    return nearby


def hit_question_block(tile):
    global score, coins_count

    for i, q in enumerate(question_tiles):
        if q == tile:
            question_tiles.pop(i)
            score += 100
            coins_count += 1

            coins.append({
                "x": tile.centerx,
                "y": tile.top,
                "vy": -5,
                "life": 35,
            })

            for j, (r, kind) in enumerate(solid_tiles):
                if r == tile:
                    solid_tiles[j] = (r, "B")
                    break

            return


def draw_tile(rect, kind, cam):
    x = rect.x - cam
    y = rect.y
    sprite_key = None

    if kind == "X":
        sprite_key = "tile_ground"
    elif kind == "B":
        sprite_key = "tile_brick"
    elif kind == "?":
        sprite_key = "tile_question" if rect in question_tiles else "tile_used"
    elif kind == "P":
        sprite_key = "tile_pipe"

    sprite = SPRITES.get(sprite_key)
    if sprite:
        screen.blit(sprite, (x, y))
        return

    if kind == "X":
        pygame.draw.rect(screen, GROUND, (x, y, TILE, TILE))
        pygame.draw.rect(screen, GROUND_DARK, (x, y, TILE, TILE), 3)

        for i in range(0, TILE, 12):
            pygame.draw.line(screen, GROUND_DARK, (x + i, y), (x + i, y + TILE), 1)
            pygame.draw.line(screen, GROUND_DARK, (x, y + i), (x + TILE, y + i), 1)

    elif kind == "B":
        pygame.draw.rect(screen, BRICK, (x, y, TILE, TILE))
        pygame.draw.rect(screen, BRICK_DARK, (x, y, TILE, TILE), 3)
        pygame.draw.line(screen, BRICK_DARK, (x, y + TILE // 2), (x + TILE, y + TILE // 2), 2)
        pygame.draw.line(screen, BRICK_DARK, (x + TILE // 2, y), (x + TILE // 2, y + TILE // 2), 2)

    elif kind == "?":
        used = rect not in question_tiles
        color = BRICK if used else QUESTION
        dark = BRICK_DARK if used else QUESTION_DARK

        pygame.draw.rect(screen, color, (x, y, TILE, TILE))
        pygame.draw.rect(screen, dark, (x, y, TILE, TILE), 3)

        if not used:
            q = font.render("?", True, WHITE)
            screen.blit(
                q,
                (
                    x + TILE // 2 - q.get_width() // 2,
                    y + TILE // 2 - q.get_height() // 2,
                ),
            )

    elif kind == "P":
        pygame.draw.rect(screen, PIPE, (x, y, TILE, TILE))
        pygame.draw.rect(screen, PIPE_DARK, (x, y, TILE, TILE), 3)
        pygame.draw.rect(screen, (80, 220, 100), (x + 8, y, 10, TILE))


def draw_pipe(pipe_rect, cam):
    x = pipe_rect.x - cam
    y = pipe_rect.y
    width = pipe_rect.width
    height = pipe_rect.height
    lip_h = min(24, height // 3)
    stem_margin = max(8, width // 8)
    stem_x = x + stem_margin
    stem_w = width - stem_margin * 2

    pygame.draw.rect(screen, PIPE_DARK, (x, y, width, lip_h + 6))
    pygame.draw.rect(screen, PIPE, (x + 4, y + 4, width - 8, lip_h - 2))
    pygame.draw.rect(screen, (92, 224, 104), (x + 10, y + 4, 14, lip_h - 2))
    pygame.draw.rect(screen, PIPE_DARK, (x, y, width, lip_h + 6), 4)

    pygame.draw.rect(screen, PIPE_DARK, (stem_x, y + lip_h + 6, stem_w, height - lip_h - 6))
    pygame.draw.rect(screen, PIPE, (stem_x + 4, y + lip_h + 6, stem_w - 8, height - lip_h - 10))
    pygame.draw.rect(screen, (92, 224, 104), (stem_x + 10, y + lip_h + 6, 14, height - lip_h - 10))
    pygame.draw.rect(screen, PIPE_DARK, (stem_x, y + lip_h + 6, stem_w, height - lip_h - 6), 4)


def draw_player():
    if not on_ground:
        sprite_key = "player_jump"
    elif abs(vel_x) > 0.8:
        sprite_key = "player_walk1" if (pygame.time.get_ticks() // 120) % 2 == 0 else "player_walk2"
    else:
        sprite_key = "player_idle"

    sprite = SPRITES.get(sprite_key)
    if sprite:
        if facing < 0:
            sprite = pygame.transform.flip(sprite, True, False)

        x = player.centerx - camera_x - sprite.get_width() // 2
        y = player.bottom + 8 - sprite.get_height()
        screen.blit(sprite, (x, y))
        return

    x = player.x - camera_x
    y = player.y
    pygame.draw.rect(screen, PLAYER, (x, y + 8, player.width, player.height - 8))
    pygame.draw.rect(screen, PLAYER_DARK, (x, y + 8, player.width, player.height - 8), 3)
    pygame.draw.rect(screen, (180, 20, 20), (x - 4, y, player.width + 8, 14))
    pygame.draw.rect(screen, (255, 210, 160), (x + 6, y + 14, 22, 16))
    eye_x = x + 22 if facing == 1 else x + 10
    pygame.draw.rect(screen, BLACK, (eye_x, y + 19, 4, 4))
    pygame.draw.rect(screen, (40, 60, 180), (x + 3, y + 34, 11, 18))
    pygame.draw.rect(screen, (40, 60, 180), (x + 20, y + 34, 11, 18))


def draw_menu_mario(x, y):
    sprite = SPRITES.get("menu_mario")
    if sprite:
        screen.blit(sprite, (x - 11, y))
        return

    pygame.draw.rect(screen, PLAYER, (x, y + 20, 42, 50))
    pygame.draw.rect(screen, PLAYER_DARK, (x, y + 20, 42, 50), 3)
    pygame.draw.rect(screen, (180, 20, 20), (x - 6, y + 6, 54, 18))
    pygame.draw.rect(screen, (255, 210, 160), (x + 7, y + 24, 28, 22))
    pygame.draw.rect(screen, BLACK, (x + 27, y + 32, 5, 5))
    pygame.draw.rect(screen, (40, 60, 180), (x + 3, y + 54, 14, 22))
    pygame.draw.rect(screen, (40, 60, 180), (x + 25, y + 54, 14, 22))


def draw_goomba(g):
    if not g["alive"] and g["squish"] <= 0:
        return

    r = g["rect"]
    x = r.x - camera_x
    y = r.y

    if g["squish"] > 0:
        sprite = SPRITES.get("goomba_squish")
        if sprite:
            screen.blit(sprite, (r.centerx - camera_x - sprite.get_width() // 2, r.bottom - sprite.get_height()))
        else:
            pygame.draw.ellipse(screen, GOOMBA, (x, y + 24, r.width, 14))
        return

    sprite_key = "goomba_walk1" if (pygame.time.get_ticks() // 180) % 2 == 0 else "goomba_walk2"
    sprite = SPRITES.get(sprite_key)
    if sprite:
        screen.blit(sprite, (r.centerx - camera_x - sprite.get_width() // 2, r.bottom - sprite.get_height() + 2))
        return

    pygame.draw.ellipse(screen, GOOMBA, (x, y, r.width, r.height))
    pygame.draw.rect(screen, (70, 40, 20), (x + 3, y + 28, 12, 10))
    pygame.draw.rect(screen, (70, 40, 20), (x + 22, y + 28, 12, 10))
    pygame.draw.rect(screen, BLACK, (x + 9, y + 13, 5, 5))
    pygame.draw.rect(screen, BLACK, (x + 23, y + 13, 5, 5))


def draw_flag():
    if flag_rect:
        x = flag_rect.x - camera_x
        pygame.draw.rect(screen, FLAGPOLE, (x, 110, 8, 390))
        banner = SPRITES.get("flag_banner")
        ball = SPRITES.get("flag_ball")

        if banner:
            screen.blit(banner, (x + 8, 120))
        else:
            pygame.draw.polygon(screen, WHITE, [(x + 8, 120), (x + 92, 145), (x + 8, 170)])

        if ball:
            screen.blit(ball, (x - 4, 100))
        else:
            pygame.draw.circle(screen, COIN, (x + 4, 108), 8)


def draw_world_background(cam, world=None):
    theme = world_theme(world or current_world)
    screen.fill(theme["sky"])

    draw_cloud(220, 90, cam)
    draw_cloud(620, 55, cam)
    draw_cloud(1100, 115, cam)
    draw_cloud(1800, 70, cam)
    draw_hill(300, 380, cam, theme["land"], theme["dark"])
    draw_hill(1200, 390, cam, theme["land"], theme["dark"])
    draw_hill(2300, 380, cam, theme["land"], theme["dark"])


def draw_menu(timer):
    draw_world_background(timer * 0.7)

    # SMW-ish blue title panel
    pygame.draw.rect(screen, MENU_BLUE_DARK, (145, 82, 670, 220), border_radius=18)
    pygame.draw.rect(screen, MENU_BLUE, (130, 68, 670, 220), border_radius=18)
    pygame.draw.rect(screen, WHITE, (130, 68, 670, 220), 5, border_radius=18)

    draw_center_text("AC'S MARIO FOREVER", 105, MENU_YELLOW, title_font)
    draw_center_text("PYGAME ENGINE 0.1", 170, WHITE, subtitle_font)

    # Little decorative blocks
    for i in range(6):
        bx = 220 + i * 90
        pygame.draw.rect(screen, QUESTION if i % 2 == 0 else BRICK, (bx, 245, 42, 42))
        pygame.draw.rect(screen, BLACK, (bx, 245, 42, 42), 3)
        if i % 2 == 0:
            q = font.render("?", True, WHITE)
            screen.blit(q, (bx + 14, 252))

    # Ground strip
    for x in range(0, WIDTH, TILE):
        pygame.draw.rect(screen, GROUND, (x, HEIGHT - 72, TILE, TILE))
        pygame.draw.rect(screen, GROUND_DARK, (x, HEIGHT - 72, TILE, TILE), 3)
        pygame.draw.rect(screen, GROUND, (x, HEIGHT - 24, TILE, TILE))
        pygame.draw.rect(screen, GROUND_DARK, (x, HEIGHT - 24, TILE, TILE), 3)

    # Walking menu character
    bob = int(math.sin(timer * 0.12) * 5)
    draw_menu_mario(450, 365 + bob)

    blink = (timer // 30) % 2 == 0
    if blink:
        draw_center_text("PRESS ENTER / SPACE / Z", 330, WHITE, font)

    draw_center_text("1 PLAYER GAME", 390, WHITE, font)
    draw_center_text("[c] AC HOLDINGS 1999-2026", 430, WHITE, small_font)


def draw_overworld_node(x, y, stage, selected, completed):
    node_color = MENU_YELLOW if completed else WHITE
    border = BLACK if not selected else COIN

    if stage == LEVELS_PER_WORLD:
        pygame.draw.rect(screen, border, (x - 30, y - 34, 60, 58))
        pygame.draw.rect(screen, (132, 76, 64), (x - 24, y - 24, 48, 48))
        pygame.draw.rect(screen, node_color, (x - 18, y - 14, 36, 38))
        pygame.draw.rect(screen, BLACK, (x - 10, y + 1, 20, 23))
        pygame.draw.rect(screen, border, (x - 24, y - 24, 48, 48), 4)
        draw_text("4", x - 7, y - 53, WHITE, small_font)
    else:
        pygame.draw.circle(screen, border, (x, y), 30)
        pygame.draw.circle(screen, node_color, (x, y), 24)
        pygame.draw.circle(screen, (232, 196, 96), (x - 7, y - 7), 5)
        label = small_font.render(str(stage), True, BLACK)
        screen.blit(label, (x - label.get_width() // 2, y - label.get_height() // 2))

    if selected:
        pygame.draw.circle(screen, COIN, (x, y), 36, 4)


def draw_map_mario(x, y, timer):
    sprite = SPRITES.get("player_idle")
    if not sprite:
        draw_menu_mario(x - 24, y - 78)
        return

    small = pygame.transform.scale(sprite, (34, 42))
    bob = int(math.sin(timer * 0.18) * 4)
    screen.blit(small, (x - small.get_width() // 2, y - 70 + bob))


def draw_overworld(timer):
    theme = world_theme(current_world)
    screen.fill(theme["sky"])

    # Terrain bands and SMB3-ish map islands.
    pygame.draw.rect(screen, (64, 128, 224), (0, 410, WIDTH, 130))
    pygame.draw.polygon(
        screen,
        theme["dark"],
        [(0, 440), (120, 370), (280, 400), (420, 340), (610, 390), (760, 320), (960, 365), (960, 540), (0, 540)],
    )
    pygame.draw.polygon(
        screen,
        theme["land"],
        [(0, 420), (130, 350), (285, 380), (425, 320), (615, 370), (765, 300), (960, 345), (960, 520), (0, 520)],
    )

    for i in range(8):
        tab_x = 34 + i * 112
        tab_color = MENU_YELLOW if i + 1 == current_world else WHITE
        pygame.draw.rect(screen, BLACK, (tab_x - 4, 18, 78, 42))
        pygame.draw.rect(screen, tab_color, (tab_x, 22, 70, 34))
        text = small_font.render(f"W{i + 1}", True, BLACK)
        screen.blit(text, (tab_x + 35 - text.get_width() // 2, 31))

    draw_center_text(f"WORLD {current_world}  {theme['name']}", 82, WHITE, big_font)

    for a, b in zip(MAP_NODE_POS, MAP_NODE_POS[1:]):
        pygame.draw.line(screen, BLACK, a, b, 18)
        pygame.draw.line(screen, theme["path"], a, b, 10)

    for idx, (x, y) in enumerate(MAP_NODE_POS):
        stage = idx + 1
        draw_overworld_node(x, y, stage, idx == map_cursor, (current_world, stage) in completed_levels)

    cursor_x, cursor_y = MAP_NODE_POS[map_cursor]
    draw_map_mario(cursor_x, cursor_y, timer)

    pygame.draw.rect(screen, BLACK, (0, 468, WIDTH, 72))
    draw_text("ARROWS/WASD SELECT WORLD + LEVEL", 28, 482, WHITE, small_font)
    draw_text("ENTER / SPACE / Z PLAY", 390, 482, WHITE, small_font)
    draw_text(f"SELECTED {current_world}-{map_cursor + 1}", 680, 482, MENU_YELLOW, small_font)
    draw_text("ESC BACK", 28, 510, WHITE, small_font)


def move_map_cursor(dx=0, dy=0):
    global current_world, map_cursor
    map_cursor = int(clamp(map_cursor + dx, 0, LEVELS_PER_WORLD - 1))
    current_world = int(clamp(current_world + dy, 1, WORLD_COUNT))


def update_gameplay():
    global vel_x, vel_y, on_ground, facing, camera_x, lives, score, coins_count, won

    keys = pygame.key.get_pressed()

    if not won:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vel_x -= MOVE_ACC
            facing = -1

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vel_x += MOVE_ACC
            facing = 1

        if not (
            keys[pygame.K_LEFT]
            or keys[pygame.K_RIGHT]
            or keys[pygame.K_a]
            or keys[pygame.K_d]
        ):
            vel_x *= FRICTION

        vel_x = clamp(vel_x, -MAX_SPEED, MAX_SPEED)

        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and on_ground:
            vel_y = JUMP
            on_ground = False

        vel_y += GRAVITY
        vel_y = min(vel_y, 18)

        player.x += int(vel_x)

        for tile, kind in get_nearby_solids(player):
            if player.colliderect(tile):
                if vel_x > 0:
                    player.right = tile.left
                elif vel_x < 0:
                    player.left = tile.right
                vel_x = 0

        player.y += int(vel_y)
        on_ground = False

        for tile, kind in get_nearby_solids(player):
            if player.colliderect(tile):
                if vel_y > 0:
                    player.bottom = tile.top
                    vel_y = 0
                    on_ground = True

                elif vel_y < 0:
                    player.top = tile.bottom
                    vel_y = 0

                    if kind == "?":
                        hit_question_block(tile)

        camera_x = clamp(player.centerx - WIDTH // 2, 0, max(0, LEVEL_W - WIDTH))

        for g in goombas:
            if not g["alive"]:
                if g["squish"] > 0:
                    g["squish"] -= 1
                continue

            g["rect"].x += int(g["vx"])

            for tile, kind in get_nearby_solids(g["rect"]):
                if g["rect"].colliderect(tile):
                    if g["vx"] > 0:
                        g["rect"].right = tile.left
                    else:
                        g["rect"].left = tile.right
                    g["vx"] *= -1

            g["rect"].y += 6

            for tile, kind in get_nearby_solids(g["rect"]):
                if g["rect"].colliderect(tile):
                    g["rect"].bottom = tile.top

            if player.colliderect(g["rect"]):
                if vel_y > 0 and player.bottom - g["rect"].top < 24:
                    g["alive"] = False
                    g["squish"] = 18
                    vel_y = -8
                    score += 200
                else:
                    lives -= 1
                    if lives <= 0:
                        lives = 3
                        score = 0
                        coins_count = 0
                    reset_player()

        for c in coins[:]:
            c["y"] += c["vy"]
            c["vy"] += 0.35
            c["life"] -= 1
            if c["life"] <= 0:
                coins.remove(c)

        if player.y > HEIGHT + 200:
            lives -= 1
            reset_player()

        if flag_rect and player.colliderect(flag_rect):
            won = True
            score += 1000


def draw_gameplay():
    draw_world_background(camera_x)

    start_tx = max(0, int(camera_x // TILE) - 2)
    end_tx = min(len(LEVEL[0]), int((camera_x + WIDTH) // TILE) + 3)

    for y, row in enumerate(LEVEL):
        for x in range(start_tx, end_tx):
            c = row[x]
            if c in ("X", "B", "?"):
                draw_tile(rect_from_tile(x, y), c, camera_x)

    for pipe in pipe_groups:
        if pipe.right >= camera_x - TILE and pipe.left <= camera_x + WIDTH + TILE:
            draw_pipe(pipe, camera_x)

    draw_flag()

    for g in goombas:
        draw_goomba(g)

    for c in coins:
        coin_sprite = SPRITES.get("coin")
        if coin_sprite:
            screen.blit(
                coin_sprite,
                (
                    int(c["x"] - camera_x - coin_sprite.get_width() // 2),
                    int(c["y"] - coin_sprite.get_height() // 2),
                ),
            )
        else:
            pygame.draw.circle(screen, COIN, (int(c["x"] - camera_x), int(c["y"])), 12)
            pygame.draw.circle(screen, WHITE, (int(c["x"] - camera_x) - 4, int(c["y"]) - 4), 3)

    draw_player()

    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 44))
    draw_text(f"SCORE {score:06}", 24, 10)
    draw_text(f"COINS {coins_count:02}", 220, 10)
    draw_text(f"LIVES {lives}", 370, 10)
    draw_text(f"AC {current_world}-{current_level}", 500, 10)
    draw_text("ARROWS/WASD MOVE  SPACE JUMP", 650, 10)

    if won:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        draw_text("LEVEL CLEAR!", WIDTH // 2 - 150, HEIGHT // 2 - 50, WHITE, big_font)
        draw_text("Press ENTER for map", WIDTH // 2 - 128, HEIGHT // 2 + 8, WHITE, font)


running = True
menu_timer = 0

while running:
    clock.tick(FPS)
    menu_timer += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_state == "menu":
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                    start_overworld()

            elif game_state == "map":
                if event.key == pygame.K_ESCAPE:
                    game_state = "menu"
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    move_map_cursor(dx=-1)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    move_map_cursor(dx=1)
                elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_q):
                    move_map_cursor(dy=-1)
                elif event.key in (pygame.K_DOWN, pygame.K_s, pygame.K_e):
                    move_map_cursor(dy=1)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                    start_level(current_world, map_cursor + 1)

            elif game_state == "game":
                if event.key == pygame.K_ESCAPE:
                    game_state = "map"
                elif won and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                    complete_current_level()

    if game_state == "menu":
        draw_menu(menu_timer)

    elif game_state == "map":
        draw_overworld(menu_timer)

    elif game_state == "game":
        update_gameplay()
        draw_gameplay()

    pygame.display.flip()

pygame.quit()
sys.exit()
