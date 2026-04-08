#!/usr/bin/env python3
"""
Генератор спрайтов для Maze: Coins and Exit
Создаёт все PNG-ассеты программно (без внешних зависимостей).

Использование:
    python3 generate_sprites.py

Результат: Assets/*.png — все спрайты игры.
"""

import struct
import zlib
import os

# === Цветовая палитра ========================================================

PALETTE = {
    # Основные
    'dark_bg':          (0x0D, 0x0D, 0x14),
    'rotten_green':     (0x2D, 0x4A, 0x2D),
    'blood_red':        (0x8B, 0x1A, 0x1A),
    'rust_orange':      (0xB8, 0x5C, 0x2E),
    'dark_gray':        (0x3A, 0x3A, 0x4A),
    'dead_gray':        (0x6B, 0x6B, 0x7B),
    'toxic_purple':     (0x4A, 0x2D, 0x4A),
    'swamp_brown':      (0x4A, 0x3A, 0x2D),
    # Предметы
    'gold':             (0xFF, 0xD7, 0x00),
    'med_white':        (0xF0, 0xF0, 0xF0),
    'red_cross':        (0xCC, 0x00, 0x00),
    'syringe_green':    (0x33, 0xCC, 0x66),
    'ammo_orange':      (0xCC, 0x77, 0x33),
    # Персонаж
    'military_green':   (0x4A, 0x6B, 0x4A),
    'skin':             (0x8B, 0x6F, 0x5E),
    'gunmetal':         (0x5A, 0x5A, 0x6A),
    # Шлем
    'helmet':           (0x3A, 0x4A, 0x3A),
    'boots':            (0x2A, 0x3A, 0x2A),
    # Зомби-глаза
    'eyes_red':         (0xFF, 0x33, 0x33),
    'eyes_yellow':      (0xFF, 0xCC, 0x00),
    'eyes_pink':        (0xFF, 0x66, 0xAA),
    'eyes_green':       (0x33, 0xFF, 0x66),
    'eyes_orange':      (0xFF, 0x88, 0x33),
    # Стены
    'wall_green_mold':  (0x1A, 0x3A, 0x1A),
    'wall_blood':       (0x6B, 0x0A, 0x0A),
    'wall_rust':        (0x8B, 0x4A, 0x1A),
    'wall_flesh':       (0x5A, 0x2A, 0x2A),
    'wall_bone':        (0x8A, 0x7A, 0x6A),
    'exit_gray':        (0x66, 0x66, 0x66),
    'exit_green':       (0x33, 0xCC, 0x33),
}

# Зомби палитры
ZOMBIE_PALETTES = {
    'green':  {'body': (0x3D, 0x5C, 0x3D), 'eyes': PALETTE['eyes_red'],    'dark': (0x2A, 0x40, 0x2A), 'light': (0x4D, 0x6C, 0x4D)},
    'grey':   {'body': (0x5A, 0x5A, 0x6A), 'eyes': PALETTE['eyes_yellow'], 'dark': (0x40, 0x40, 0x50), 'light': (0x6A, 0x6A, 0x7A)},
    'purple': {'body': (0x4A, 0x2D, 0x5A), 'eyes': PALETTE['eyes_pink'],   'dark': (0x35, 0x1D, 0x45), 'light': (0x5A, 0x3D, 0x6A)},
    'brown':  {'body': (0x5A, 0x3D, 0x2D), 'eyes': PALETTE['eyes_green'],  'dark': (0x40, 0x2A, 0x1D), 'light': (0x6A, 0x4D, 0x3D)},
    'blue':   {'body': (0x2D, 0x3D, 0x5A), 'eyes': PALETTE['eyes_orange'], 'dark': (0x1D, 0x2A, 0x40), 'light': (0x3D, 0x4D, 0x6A)},
}

# === PNG генератор (без зависимостей) =========================================

def create_png(width: int, height: int, pixels: list[list[tuple]]) -> bytes:
    """
    Создаёт PNG-файл из списка пикселей.
    pixels: список строк, каждая — список (R, G, B) или (R, G, B, A).
    """
    def make_png_filter(raw: bytes, filter_type: int = 0) -> bytes:
        return bytes([filter_type]) + raw

    raw_data = b''
    for row in pixels:
        row_bytes = b''
        for px in row:
            if len(px) == 3:
                row_bytes += bytes(px) + b'\xff'
            else:
                row_bytes += bytes(px)
        raw_data += make_png_filter(row_bytes)

    def chunk(chunk_type: bytes, data: bytes) -> bytes:
        c = chunk_type + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    signature = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    ihdr = chunk(b'IHDR', ihdr_data)

    compressed = zlib.compress(raw_data)
    idat = chunk(b'IDAT', compressed)
    iend = chunk(b'IEND', b'')

    return signature + ihdr + idat + iend


def save_png(filepath: str, width: int, height: int, pixels: list[list[tuple]]) -> None:
    png_data = create_png(width, height, pixels)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(png_data)
    print(f"  ✓ {filepath}")


# === Утилиты рисования =======================================================

def blank(w: int, h: int, color: tuple = None) -> list:
    """Создаёт пустой холст (полностью прозрачный или залитый цветом)."""
    if color is None:
        return [[(0, 0, 0, 0)] * w for _ in range(h)]
    return [[color] * w for _ in range(h)]


def set_pixel(canvas: list, x: int, y: int, color: tuple) -> None:
    if 0 <= x < len(canvas[0]) and 0 <= y < len(canvas):
        canvas[y][x] = color


def fill_rect(canvas: list, x1: int, y1: int, x2: int, y2: int, color: tuple) -> None:
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            set_pixel(canvas, x, y, color)


def draw_line(canvas: list, x1: int, y1: int, x2: int, y2: int, color: tuple) -> None:
    """Линия Bresenham."""
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    while True:
        set_pixel(canvas, x1, y1, color)
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy


def draw_ellipse(canvas: list, cx: int, cy: int, rx: int, ry: int, color: tuple) -> None:
    """Заполненный эллипс."""
    for y in range(-ry, ry + 1):
        for x in range(-rx, rx + 1):
            if (x * x) / (rx * rx + 0.01) + (y * y) / (ry * ry + 0.01) <= 1.0:
                set_pixel(canvas, cx + x, cy + y, color)


def add_noise(canvas: list, w: int, h: int, colors: list[tuple], density: float = 0.15) -> None:
    """Добавляет случайные пиксели (для текстур стен, зомби)."""
    import random
    random.seed(42)  # для воспроизводимости
    for y in range(h):
        for x in range(w):
            if canvas[y][x][3] == 0 or random.random() < density:
                if random.random() < density * 2:
                    c = random.choice(colors)
                    set_pixel(canvas, x, y, c)


# === Спрайт: Игрок ===========================================================

def draw_player_sprite(direction: str, frame: int, is_idle: bool = False) -> list:
    """Спрайт игрока 48×48. direction: up/down/left/right, frame: 0-4."""
    size = 48
    c = blank(size, size)

    mc = PALETTE['military_green']  # форма
    sk = PALETTE['skin']             # кожа
    gm = PALETTE['gunmetal']         # оружие
    hm = PALETTE['helmet']           # шлем
    bt = PALETTE['boots']            # ботинки

    # Смещение ног/рук в зависимости от кадра
    leg_offset = 0
    if not is_idle:
        leg_offset = [0, 2, 0, -2, 0][frame]
    arm_sway = 0
    if not is_idle:
        arm_sway = [0, 1, 0, -1, 0][frame]

    if direction == 'down':
        # Тело (зелёная форма)
        fill_rect(c, 16, 14, 31, 30, mc)
        # Ноги
        fill_rect(c, 17, 30, 22, 40 + leg_offset, bt)
        fill_rect(c, 25, 30, 30, 40 - leg_offset, bt)
        # Голова
        draw_ellipse(c, 23, 12, 7, 7, sk)
        # Шлем
        draw_ellipse(c, 23, 10, 8, 5, hm)
        # Оружие (в руках, направлено вниз)
        fill_rect(c, 22, 32 + arm_sway, 25, 38 + arm_sway, gm)
        # Лицо
        set_pixel(c, 20, 12, (0x2A, 0x2A, 0x2A))  # глаз левый
        set_pixel(c, 26, 12, (0x2A, 0x2A, 0x2A))  # глаз правый

    elif direction == 'up':
        # Тело
        fill_rect(c, 16, 14, 31, 30, mc)
        # Ноги
        fill_rect(c, 17, 30, 22, 40 + leg_offset, bt)
        fill_rect(c, 25, 30, 30, 40 - leg_offset, bt)
        # Голова (затылок)
        draw_ellipse(c, 23, 12, 7, 7, hm)
        # Оружие (на плече, видно сверху)
        fill_rect(c, 18, 16 + arm_sway, 21, 24, gm)

    elif direction == 'left':
        # Тело
        fill_rect(c, 12, 14, 28, 30, mc)
        # Ноги
        fill_rect(c, 14, 30 + leg_offset, 19, 40, bt)
        fill_rect(c, 21, 30 - leg_offset, 26, 40, bt)
        # Голова
        draw_ellipse(c, 10, 12, 6, 7, sk)
        # Шлем
        draw_ellipse(c, 9, 10, 7, 5, hm)
        # Оружие (направлено влево)
        fill_rect(c, 2, 20 + arm_sway, 10, 24, gm)
        # Глаз
        set_pixel(c, 7, 12, (0x2A, 0x2A, 0x2A))

    elif direction == 'right':
        # Тело
        fill_rect(c, 19, 14, 35, 30, mc)
        # Ноги
        fill_rect(c, 21, 30 + leg_offset, 26, 40, bt)
        fill_rect(c, 28, 30 - leg_offset, 33, 40, bt)
        # Голова
        draw_ellipse(c, 37, 12, 6, 7, sk)
        # Шлем
        draw_ellipse(c, 38, 10, 7, 5, hm)
        # Оружие (направлено вправо)
        fill_rect(c, 37, 20 + arm_sway, 45, 24, gm)
        # Глаз
        set_pixel(c, 40, 12, (0x2A, 0x2A, 0x2A))

    return c


def draw_player_death(frame: int) -> list:
    """6 кадров анимации смерти."""
    size = 48
    c = blank(size, size)
    mc = PALETTE['military_green']
    sk = PALETTE['skin']
    bt = PALETTE['boots']
    blood = PALETTE['blood_red']

    # Прогрессия: стоит → спотыкается → падает → лежит
    tilt = frame * 3  # наклон
    y_off = frame * 2  # смещение вниз

    if frame < 4:
        # Тело с наклоном
        body_y = 14 + y_off
        fill_rect(c, 16, body_y + tilt, 31, body_y + 16 + tilt, mc)
        fill_rect(c, 17, body_y + 16, 22, 40, bt)
        fill_rect(c, 25, body_y + 16, 30, 40, bt)
        # Голова
        draw_ellipse(c, 23, 12 + y_off + tilt, 7 - frame // 2, 7 - frame // 2, sk)
        # Кровь
        if frame >= 2:
            fill_rect(c, 20, 38 + frame, 28, 42 + frame, blood)
    else:
        # Лежит — горизонтальная форма
        fill_rect(c, 8, 35, 40, 42, mc)
        # Голова сбоку
        draw_ellipse(c, 6, 38, 5, 4, sk)
        # Кровь
        fill_rect(c, 20, 40, 36, 44, blood)
        if frame >= 5:
            # Затемнение
            for y in range(48):
                for x in range(48):
                    px = c[y][x]
                    has_alpha = len(px) == 4 and px[3] > 0
                    is_opaque = len(px) == 3
                    if has_alpha or is_opaque:
                        r, g, b = px[:3]
                        a = 200 if has_alpha else 255
                        c[y][x] = (r // 2, g // 2, b // 2, a)

    return c


# === Спрайт: Зомби ===========================================================

def draw_zombie_sprite(color_name: str, direction: str, frame: int, is_idle: bool = False) -> list:
    """Спрайт зомби 48×48."""
    size = 48
    pal = ZOMBIE_PALETTES[color_name]
    c = blank(size, size)

    body = pal['body']
    dark = pal['dark']
    light = pal['light']
    eyes = pal['eyes']

    leg_offset = 0
    if not is_idle:
        leg_offset = [0, 3, 0, -2, 0][frame]
    head_wobble = 0
    if not is_idle:
        head_wobble = [0, 1, -1, 0, 1][frame]

    if direction == 'down':
        # Тело — неровное, гниющее
        fill_rect(c, 15, 14, 32, 30, body)
        # Пятна гнили
        fill_rect(c, 18, 16, 20, 18, dark)
        fill_rect(c, 26, 22, 29, 25, light)
        # Ноги (хромые)
        fill_rect(c, 16, 30, 21, 40 + leg_offset, dark)
        fill_rect(c, 26, 30, 31, 40 - leg_offset, dark)
        # Голова
        draw_ellipse(c, 23 + head_wobble, 12, 7, 7, body)
        # Глаза (зловещие)
        set_pixel(c, 19, 12, eyes)
        set_pixel(c, 27, 12, eyes)
        # Куски мяса
        set_pixel(c, 15, 20, dark)
        set_pixel(c, 32, 24, dark)

    elif direction == 'up':
        fill_rect(c, 15, 14, 32, 30, body)
        fill_rect(c, 18, 16, 20, 18, dark)
        fill_rect(c, 16, 30, 21, 40 + leg_offset, dark)
        fill_rect(c, 26, 30, 31, 40 - leg_offset, dark)
        draw_ellipse(c, 23 + head_wobble, 12, 7, 7, body)
        # Шрам на затылке
        fill_rect(c, 20, 10, 26, 12, dark)

    elif direction == 'left':
        fill_rect(c, 11, 14, 28, 30, body)
        fill_rect(c, 13, 18, 16, 22, dark)
        fill_rect(c, 12, 30 + leg_offset, 18, 40, dark)
        fill_rect(c, 20, 30 - leg_offset, 26, 40, dark)
        draw_ellipse(c, 9 + head_wobble, 12, 7, 7, body)
        set_pixel(c, 6, 12, eyes)
        set_pixel(c, 28, 22, dark)

    elif direction == 'right':
        fill_rect(c, 19, 14, 36, 30, body)
        fill_rect(c, 21, 20, 24, 24, dark)
        fill_rect(c, 20, 30 + leg_offset, 26, 40, dark)
        fill_rect(c, 28, 30 - leg_offset, 34, 40, dark)
        draw_ellipse(c, 38 + head_wobble, 12, 7, 7, body)
        set_pixel(c, 41, 12, eyes)
        set_pixel(c, 19, 22, dark)

    return c


def draw_zombie_death(frame: int) -> list:
    """8 кадров смерти зомби."""
    size = 48
    c = blank(size, size)
    body = (0x3D, 0x5C, 0x3D)
    blood = PALETTE['blood_red']

    if frame < 3:
        # Падает
        tilt = frame * 8
        fill_rect(c, 15 + tilt, 14 + frame * 3, 32 + tilt, 30 + frame * 3, body)
        draw_ellipse(c, 23 + tilt, 12 + frame * 3, 7, 7, body)
        if frame >= 1:
            fill_rect(c, 20, 38, 28, 44, blood)
    elif frame < 6:
        # Корчится
        shrink = (frame - 3) * 3
        fill_rect(c, 15 + shrink, 20 + frame * 2, 32 - shrink, 35, body)
        fill_rect(c, 18, 35, 30, 44, blood)
    else:
        # Растворяется
        alpha = 255 - (frame - 6) * 80
        for y in range(48):
            for x in range(48):
                r, g, b = body
                if (x + y + frame * 7) % 5 != 0:
                    c[y][x] = (r, g, b, max(0, alpha - 60))
        fill_rect(c, 15, 38, 33, 46, (0x4A, 0x1A, 0x1A))  # останки

    return c


# === Спрайты: Стены ==========================================================

def draw_wall(wall_type: str, variant: str) -> list:
    """48×48 тайл стены. Бесшовный."""
    size = 48
    c = blank(size, size)

    if wall_type == 'brick_rotten':
        colors = [PALETTE['dark_gray'], PALETTE['rotten_green'], PALETTE['wall_green_mold']]
        fill_rect(c, 0, 0, 47, 47, PALETTE['dark_gray'])
        # Кирпичики
        for row in range(6):
            for col in range(4):
                offset = 12 if row % 2 else 0
                x = col * 14 + offset
                y = row * 8
                fill_rect(c, x + 1, y + 1, x + 12, y + 6, colors[row % 3])
        # Трещины и плесень
        for i in range(8):
            set_pixel(c, 10 + i * 4, 5 + i * 5, PALETTE['wall_green_mold'])
        # Края для бесшовности
        for y in range(48):
            c[y][0] = c[y][1]
            c[y][47] = c[y][46]
        for x in range(48):
            c[0][x] = c[1][x]
            c[47][x] = c[46][x]

    elif wall_type == 'stone_bloody':
        colors = [PALETTE['swamp_brown'], PALETTE['wall_blood'], PALETTE['dead_gray']]
        fill_rect(c, 0, 0, 47, 47, PALETTE['swamp_brown'])
        # Камни
        for i in range(6):
            for j in range(6):
                cx, cy = 4 + i * 8, 4 + j * 8
                draw_ellipse(c, cx, cy, 3, 3, colors[(i + j) % 3])
        # Кровавые потёки
        for x in [8, 20, 35]:
            for y in range(5, 30):
                if y % 3 == 0:
                    set_pixel(c, x, y, PALETTE['wall_blood'])
        # Бесшовность
        for y in range(48):
            c[y][0] = c[y][1]
            c[y][47] = c[y][46]
        for x in range(48):
            c[0][x] = c[1][x]
            c[47][x] = c[46][x]

    elif wall_type == 'metal_rusty':
        fill_rect(c, 0, 0, 47, 47, PALETTE['dark_gray'])
        # Панели
        fill_rect(c, 1, 1, 22, 22, PALETTE['dead_gray'])
        fill_rect(c, 25, 1, 46, 22, PALETTE['dead_gray'])
        fill_rect(c, 1, 25, 22, 46, PALETTE['dead_gray'])
        fill_rect(c, 25, 25, 46, 46, PALETTE['dead_gray'])
        # Заклёпки
        for x, y in [(2, 2), (21, 2), (2, 21), (21, 21),
                      (26, 2), (45, 2), (26, 21), (45, 21),
                      (2, 26), (21, 26), (2, 45), (21, 45),
                      (26, 26), (45, 26), (26, 45), (45, 45)]:
            draw_ellipse(c, x, y, 1, 1, PALETTE['dead_gray'])
        # Ржавчина
        for _ in range(30):
            rx = (_ * 17 + 5) % 48
            ry = (_ * 23 + 7) % 48
            set_pixel(c, rx, ry, PALETTE['rust_orange'])
        # Бесшовность
        for y in range(48):
            c[y][0] = c[y][1]
            c[y][47] = c[y][46]
        for x in range(48):
            c[0][x] = c[1][x]
            c[47][x] = c[46][x]

    elif wall_type == 'wood_rotten':
        fill_rect(c, 0, 0, 47, 47, PALETTE['swamp_brown'])
        # Доски (вертикальные)
        for i in range(4):
            x = i * 12 + 1
            fill_rect(c, x, 1, x + 10, 46, PALETTE['swamp_brown'])
            # Текстура дерева
            for y in range(2, 46, 3):
                set_pixel(c, x + 2, y, PALETTE['wall_green_mold'])
                set_pixel(c, x + 7, y + 1, PALETTE['dark_gray'])
        # Грибок
        for i in range(5):
            draw_ellipse(c, 6 + i * 10, 10 + i * 6, 2, 2, PALETTE['wall_green_mold'])
        # Бесшовность
        for y in range(48):
            c[y][0] = c[y][1]
            c[y][47] = c[y][46]
        for x in range(48):
            c[0][x] = c[1][x]
            c[47][x] = c[46][x]

    elif wall_type == 'bone_flesh':
        fill_rect(c, 0, 0, 47, 47, PALETTE['wall_flesh'])
        # Кости
        for i in range(8):
            bx = (i * 13 + 3) % 44 + 2
            by = (i * 17 + 5) % 40 + 4
            draw_ellipse(c, bx, by, 4, 2, PALETTE['wall_bone'])
        # Мясо
        for i in range(6):
            mx = (i * 11 + 7) % 42 + 3
            my = (i * 19 + 3) % 38 + 5
            draw_ellipse(c, mx, my, 3, 3, PALETTE['wall_flesh'])
        # Глаз
        draw_ellipse(c, 24, 24, 3, 3, PALETTE['dead_gray'])
        set_pixel(c, 24, 24, PALETTE['eyes_red'])
        # Бесшовность
        for y in range(48):
            c[y][0] = c[y][1]
            c[y][47] = c[y][46]
        for x in range(48):
            c[0][x] = c[1][x]
            c[47][x] = c[46][x]

    elif wall_type == 'bars_prison':
        fill_rect(c, 0, 0, 47, 47, (0x0A, 0x0A, 0x10))  # темнота за решёткой
        # Прутья (вертикальные)
        for x in range(4, 48, 8):
            fill_rect(c, x, 0, x + 2, 47, PALETTE['dead_gray'])
            # Ржавчина на прутьях
            for y in range(0, 48, 4):
                set_pixel(c, x + 1, y, PALETTE['rust_orange'])
        # Горизонтальные перекладины
        fill_rect(c, 0, 12, 47, 14, PALETTE['dark_gray'])
        fill_rect(c, 0, 36, 47, 38, PALETTE['dark_gray'])
        # Бесшовность
        for y in range(48):
            c[y][0] = c[y][1]
            c[y][47] = c[y][46]
        for x in range(48):
            c[0][x] = c[1][x]
            c[47][x] = c[46][x]

    # Варианты
    if variant == 'b':
        # Больше повреждений
        for i in range(15):
            rx = (i * 13 + 3) % 48
            ry = (i * 17 + 5) % 48
            set_pixel(c, rx, ry, (0x1A, 0x1A, 0x1A))
    elif variant == 'c':
        # Дыра / особое повреждение
        if wall_type != 'bars_prison':
            fill_rect(c, 18, 18, 30, 30, (0x05, 0x05, 0x0A))
        else:
            # Погнутые прутья
            for y in range(10, 30):
                set_pixel(c, 14, y, PALETTE['dead_gray'])

    return c


# === Спрайты: Предметы =======================================================

def draw_coin_frame(frame: int) -> list:
    """24×24 монета, 4 кадра вращения."""
    size = 24
    c = blank(size, size)
    gold = PALETTE['gold']
    dark_gold = (0xCC, 0xAA, 0x00)

    # Имитация вращения через scaleX
    widths = [10, 6, 2, 6]
    w = widths[frame % 4]

    draw_ellipse(c, 12, 12, w // 2, 8, gold)
    if w > 4:
        # Знак доллара
        fill_rect(c, 11, 7, 12, 17, dark_gold)

    # Свечение
    glow = (0xFF, 0xEE, 0x88, 100)
    draw_ellipse(c, 12, 12, w // 2 + 1, 9, glow)

    return c


def draw_exit(locked: bool) -> list:
    """48×48 дверь."""
    size = 48
    c = blank(size, size)

    if locked:
        fill_rect(c, 8, 2, 39, 45, PALETTE['exit_gray'])
        fill_rect(c, 10, 4, 37, 43, PALETTE['dark_gray'])
        # Замок/цепь
        fill_rect(c, 34, 22, 38, 30, PALETTE['rust_orange'])
        draw_ellipse(c, 36, 26, 3, 3, PALETTE['rust_orange'])
    else:
        fill_rect(c, 8, 2, 39, 45, PALETTE['exit_green'])
        fill_rect(c, 10, 4, 37, 43, (0x1A, 0x6B, 0x1A))
        # Открытый замок
        fill_rect(c, 34, 22, 38, 28, PALETTE['dead_gray'])
        # Свечение
        for i in range(3):
            alpha = 80 - i * 20
            draw_ellipse(c, 23, 23, 18 + i * 2, 18 + i * 2, (0x33, 0xCC, 0x33, alpha))

    return c


def draw_bullet() -> list:
    """12×12 пуля."""
    size = 12
    c = blank(size, size)
    bullet_color = (0xFF, 0x66, 0x00)

    draw_ellipse(c, 6, 6, 4, 4, bullet_color)
    # Свечение
    set_pixel(c, 6, 2, (0xFF, 0x88, 0x00, 150))
    set_pixel(c, 6, 10, (0xFF, 0x88, 0x00, 150))
    set_pixel(c, 2, 6, (0xFF, 0x88, 0x00, 150))
    set_pixel(c, 10, 6, (0xFF, 0x88, 0x00, 150))

    return c


def draw_medkit(frame: int) -> list:
    """24×24 аптечка, 2 кадра пульсации."""
    size = 24
    c = blank(size, size)
    white = PALETTE['med_white']
    red = PALETTE['red_cross']

    scale = 1 if frame == 0 else 0  # для имитации пульсации можно менять размер
    offset = scale

    fill_rect(c, 4 + offset, 6, 19 - offset, 17, white)
    fill_rect(c, 5 + offset, 7, 18 - offset, 16, white)
    # Красный крест
    fill_rect(c, 10, 8, 13, 15, red)
    fill_rect(c, 8, 10, 15, 13, red)

    # Свечение
    glow = (0xFF, 0x88, 0x88, 60)
    fill_rect(c, 3, 5, 20, 6, glow)
    fill_rect(c, 3, 17, 20, 18, glow)

    return c


def draw_medicine(frame: int) -> list:
    """24×24 шприц, 2 кадра покачивания."""
    size = 24
    c = blank(size, size)
    green = PALETTE['syringe_green']
    gray = PALETTE['dead_gray']

    # Покачивание через сдвиг
    offset = 1 if frame == 1 else 0

    # Корпус шприца
    fill_rect(c, 9 + offset, 4, 14 + offset, 18, gray)
    fill_rect(c, 10 + offset, 5, 13 + offset, 17, (0xDD, 0xDD, 0xDD))
    # Жидкость
    fill_rect(c, 10 + offset, 10, 13 + offset, 17, green)
    # Игла
    fill_rect(c, 11 + offset, 1, 12 + offset, 4, PALETTE['dark_gray'])
    # Поршень
    fill_rect(c, 9 + offset, 18, 14 + offset, 21, gray)

    # Свечение
    glow = (0x33, 0xFF, 0x66, 60)
    fill_rect(c, 8 + offset, 3, 16 + offset, 4, glow)

    return c


def draw_ammo_pickup(frame: int) -> list:
    """24×24 коробка патронов, 2 кадра пульсации."""
    size = 24
    c = blank(size, size)
    orange = PALETTE['ammo_orange']
    dark_orange = (0x99, 0x55, 0x22)

    offset = 1 if frame == 0 else 0

    # Коробка
    fill_rect(c, 4 + offset, 6, 19 - offset, 18, orange)
    fill_rect(c, 5 + offset, 7, 18 - offset, 10, dark_orange)
    # Пули (видны сверху)
    for i in range(3):
        draw_ellipse(c, 8 + i * 4, 14, 1, 1, PALETTE['gunmetal'])

    return c


# === Генерация всех спрайтов =================================================

def generate_all():
    """Генерирует все PNG-файлы."""
    assets_dir = 'Assets'
    count = 0

    print("\n=== Генерация спрайтов ===\n")

    # --- Игрок: ходьба ---
    print("[Игрок] Ходьба...")
    for direction in ['up', 'down', 'left', 'right']:
        for frame in range(5):
            is_idle = (frame == 0)
            name = f'player_{direction}_idle.png' if is_idle else f'player_{direction}_walk_{frame}.png'
            pixels = draw_player_sprite(direction, frame, is_idle)
            save_png(f'{assets_dir}/{name}', 48, 48, pixels)
            count += 1

    # --- Игрок: смерть ---
    print("[Игрок] Смерть...")
    for frame in range(6):
        name = f'player_death_{frame + 1}.png'
        pixels = draw_player_death(frame)
        save_png(f'{assets_dir}/{name}', 48, 48, pixels)
        count += 1

    # --- Игрок: стрельба ---
    print("[Игрок] Стрельба...")
    for direction in ['up', 'down', 'left', 'right']:
        name = f'player_{direction}_shoot.png'
        pixels = draw_player_sprite(direction, 0, is_idle=False)
        save_png(f'{assets_dir}/{name}', 48, 48, pixels)
        count += 1

    # --- Зомби: ходьба ---
    print("[Зомби] Ходьба...")
    for color_name in ['green', 'grey', 'purple', 'brown', 'blue']:
        for direction in ['up', 'down', 'left', 'right']:
            for frame in range(5):
                is_idle = (frame == 0)
                name = (f'zombie_{color_name}_{direction}_idle.png' if is_idle
                        else f'zombie_{color_name}_{direction}_walk_{frame}.png')
                pixels = draw_zombie_sprite(color_name, direction, frame, is_idle)
                save_png(f'{assets_dir}/{name}', 48, 48, pixels)
                count += 1

    # --- Зомби: смерть ---
    print("[Зомби] Смерть...")
    for frame in range(8):
        name = f'zombie_death_{frame + 1}.png'
        pixels = draw_zombie_death(frame)
        save_png(f'{assets_dir}/{name}', 48, 48, pixels)
        count += 1

    # --- Стены ---
    print("[Стены] Генерация...")
    wall_types = [
        ('brick_rotten', ['a', 'b', 'c']),
        ('stone_bloody', ['a', 'b', 'c']),
        ('metal_rusty', ['a', 'b', 'c']),
        ('wood_rotten', ['a', 'b', 'c']),
        ('bone_flesh', ['a', 'b', 'c']),
        ('bars_prison', ['a', 'b', 'c']),
    ]
    for wall_type, variants in wall_types:
        for variant in variants:
            name = f'wall_{wall_type}_{variant}.png'
            pixels = draw_wall(wall_type, variant)
            save_png(f'{assets_dir}/{name}', 48, 48, pixels)
            count += 1

    # --- Монета ---
    print("[Монета] Вращение...")
    for frame in range(4):
        name = f'coin_frame_{frame + 1}.png'
        pixels = draw_coin_frame(frame)
        save_png(f'{assets_dir}/{name}', 24, 24, pixels)
        count += 1

    # --- Дверь ---
    print("[Дверь] Locked/Unlocked...")
    for locked in [True, False]:
        name = 'exit_locked.png' if locked else 'exit_unlocked.png'
        pixels = draw_exit(locked)
        save_png(f'{assets_dir}/{name}', 48, 48, pixels)
        count += 1

    # --- Пуля ---
    print("[Пуля]...")
    save_png(f'{assets_dir}/bullet.png', 12, 12, draw_bullet())
    count += 1

    # --- Аптечка ---
    print("[Аптечка] Пульсация...")
    for frame in range(2):
        name = f'medkit_frame_{frame + 1}.png'
        pixels = draw_medkit(frame)
        save_png(f'{assets_dir}/{name}', 24, 24, pixels)
        count += 1

    # --- Шприц ---
    print("[Шприц] Покачивание...")
    for frame in range(2):
        name = f'medicine_frame_{frame + 1}.png'
        pixels = draw_medicine(frame)
        save_png(f'{assets_dir}/{name}', 24, 24, pixels)
        count += 1

    # --- Коробка патронов ---
    print("[Патроны] Пульсация...")
    for frame in range(2):
        name = f'ammo_pickup_frame_{frame + 1}.png'
        pixels = draw_ammo_pickup(frame)
        save_png(f'{assets_dir}/{name}', 24, 24, pixels)
        count += 1

    print(f"\n=== Готово! Сгенерировано {count} файлов в {assets_dir}/ ===\n")


if __name__ == '__main__':
    generate_all()
