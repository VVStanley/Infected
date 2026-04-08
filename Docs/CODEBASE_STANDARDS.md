# Требования к кодовой базе

> **Проект:** Maze: Coins and Exit  
> **Движок:** Godot 4.6 (минимум 4.2+)  
> **Дата:** 7 апреля 2026

---

## 1. Движок и среда

- Игра **запускается на Godot 4.6** (совместима с 4.2+)
- Язык скриптов: **GDScript 2.0** (встроенный в Godot 4)
- Спрайты генерируются через `generate_sprites.py` (Python 3, без зависимостей, zlib)
- Главный файл проекта: `project.godot`
- Главная сцена: `res://Scenes/Main.tscn` (запуск по F5)

---

## 2. Архитектура

### 2.1 Паттерн: Scene-Tree + Autoload Singletons

Три уровня архитектуры:

```
┌─────────────────────────────────────────────────┐
│ LAYER 1: Autoload (глобальные, между сценами)   │
│ ├── Settings.gd     — только данные, без логики │
│ ├── LevelManager.gd — состояние между уровнями  │
│ └── SoundManager.gd — звуковая система          │
├─────────────────────────────────────────────────┤
│ LAYER 2: Main сцена (контроллер уровня)         │
│ └── Main.gd — генерация, спавн, HUD, логика    │
├─────────────────────────────────────────────────┤
│ LAYER 3: Entity сцены (префабы)                 │
│ └── Player, Enemy, Bullet, Coin, Exit, Pickups  │
└─────────────────────────────────────────────────┘
```

### 2.2 Принципы проектирования

- **Композиция вместо наследования** — не создавать глубокие иерархии, не использовать `class_name` без необходимости
- **Один скрипт = одна ответственность** — каждый `.gd` файл решает одну задачу
- **Настройки в Settings.gd** — все настраиваемые значения (скорости, размеры, цвета, количества) живут в `Settings.gd`, не в скриптах сущностей
- **Централизованный спавн** — `Main.gd` создаёт все сущности, сущности не знают когда/где они созданы
- **Разделённая коммуникация** — сущности общаются с `Main.gd` через сигналы, `Main.gd` запрашивает сущности через публичные геттеры
- **Прямые ссылки между сущностями запрещены** — Player не ссылается на Enemy напрямую

### 2.3 Autoload синглтоны

Зарегистрированы в `project.godot` → Autoload:

```ini
[autoload]
Settings="*res://Settings/Settings.gd"
SoundManager="*res://Settings/SoundManager.gd"
LevelManager="*res://Settings/LevelManager.gd"
```

Правила:
- `Settings.gd` — **только данные**, никаких методов кроме констант
- `LevelManager.gd` — хранит `current_level`, `total_score`, `carried_ammo`, `has_medicine`
- `SoundManager.gd` — процедурная генерация звуков через `AudioStreamGenerator`
- Новые autoload добавлять **только если** данные должны сохраняться между перезапусками сцены И использоваться из нескольких несвязанных сцен

---

## 3. Стиль кода

### 3.1 Именование

| Элемент | Правило | Пример |
|---------|---------|--------|
| Приватные переменные | `_snake_case` | `_ammo`, `_hp`, `_maze` |
| Публичные переменные | `snake_case` | `total_score`, `current_level` |
| Константы | `UPPER_SNAKE_CASE` | `MAZE_COLS`, `PLAYER_SPAWN` |
| Приватные функции | `_snake_case()` | `_shoot()`, `_spawn_coins()` |
| Публичные функции | `snake_case()` | `get_ammo()`, `heal()`, `advance_level()` |
| Сигналы | `snake_case` | `coin_collected`, `enemy_died` |
| Файлы скриптов | `PascalCase.gd` | `Player.gd`, `LevelManager.gd` |
| Файлы сцен | `PascalCase.tscn` | `Player.tscn`, `Main.tscn` |
| Ноды в сценах | `PascalCase` | `Sprite`, `CollisionShape2D`, `Flashlight` |
| Ассеты (PNG) | `snake_case.png` | `player_up.png`, `ammo_pickup.png` |

### 3.2 Типизация

**Обязательна для всех переменных и функций:**

```gdscript
var _hp: int = 100
var _is_infected: bool = false
var _coins: Array[Node2D] = []
var _walkable_positions: Array[Vector2] = []

func _shoot() -> void:
    pass

func get_ammo() -> int:
    return _ammo

func heal(amount: int) -> int:
    _hp = mini(_hp + amount, Settings.player_max_hp)
    return _hp
```

### 3.3 Структура файла

Каждый `.gd` файл следует обязательному порядку секций:

```gdscript
## Краткое описание назначения скрипта
extends Node2D

# === SIGNALS =================================================================
signal coin_collected(coin_node: Node2D)

# === CONSTANTS =================================================================
const MOVE_SPEED: float = 200.0

# === PRIVATE VARIABLES =======================================================
var _ammo: int = 10
var _hp: int = 100

# === NODE REFERENCES =========================================================
var _sprite: Sprite2D

# === LIFECYCLE ===============================================================
func _ready() -> void:
    _setup_nodes()
    _apply_settings()

func _physics_process(delta: float) -> void:
    _handle_input()
    _move()

# === PUBLIC FUNCTIONS ========================================================
func get_ammo() -> int:
    return _ammo

# === PRIVATE FUNCTIONS =======================================================
func _setup_nodes() -> void:
    _sprite = $Sprite

func _apply_settings() -> void:
    pass
```

### 3.4 Разделители секций

```gdscript
# === LIFECYCLE ===============================================================
# === PUBLIC FUNCTIONS ========================================================
# === PRIVATE FUNCTIONS =======================================================
# === SIGNALS =================================================================
# === CONSTANTS ===============================================================
```

### 3.5 Форматирование

- **Отступы:** табы (стандарт Godot)
- **Длина строки:** мягкий лимит ~120 символов
- **Пустые строки:** 1 между функциями, 2 между секциями
- **Конечные пробелы:** удалять
- **Конец файла:** одна пустая строка

---

## 4. Комментарии

- **Заголовок файла:** первые 2 строки — описание назначения (`## Описание`)
- **Сложная логика:** комментировать **ПОЧЕМУ** сделано так, а не **ЧТО** сделано
- **TODO/FIXME:** формат `# TODO: описание` или `# FIXME: описание`
- **Не комментировать очевидное:**

```gdscript
# ПЛОХО: _hp -= 1  # Уменьшаем HP на 1
# ХОРОШО:  # Ограничиваем урон чтобы HP не стал отрицательным
           _hp = maxi(_hp - damage, 0)
```

---

## 5. Сигналы

### 5.1 Объявление

Все сигналы объявляются вверху скрипта:

```gdscript
signal coin_collected(coin_node: Node2D)
signal health_changed(current_hp: int, max_hp: int, is_infected: bool)
signal player_died
```

### 5.2 Подключение

Все подключения делаются в `Main.gd` в `_ready()`:

```gdscript
func _ready() -> void:
    _player.coin_collected.connect(_on_coin_collected)
    _player.bullet_fired.connect(_on_bullet_fired)
    _player.health_changed.connect(_on_health_changed)
    _player.player_died.connect(_on_player_died)
```

### 5.3 Именование обработчиков

Формат: `_on_<источник>_<событие>`:

```gdscript
func _on_coin_collected(coin_node: Node2D) -> void:
    pass

func _on_enemy_died() -> void:
    pass
```

### 5.4 Карта сигналов проекта

| Источник | Сигнал | Обработчик в Main.gd | Назначение |
|----------|--------|---------------------|------------|
| Player | `coin_collected(coin_node)` | `_on_coin_collected` | Игрок собрал монету |
| Player | `bullet_fired(bullet_node)` | `_on_bullet_fired` | Пуля выпущена |
| Player | `health_changed(hp, max_hp, infected)` | `_on_health_changed` | HP изменился |
| Player | `player_died` | `_on_player_died` | Смерть игрока |
| Bullet | `hit_enemy(enemy_node)` | `_on_bullet_hit` | Пуля попала во врага |
| Enemy | `enemy_collected_coin(coin_node)` | `_on_enemy_collected_coin` | Враг съел монету |
| Enemy | `enemy_died()` | `_on_enemy_died` | Враг убит |
| Exit | `exited()` | `_on_exit` | Игрок вышел |

---

## 6. Управление состоянием

### 6.1 Владение состоянием

| Состояние | Владелец | Сохраняется между уровнями? |
|-----------|----------|----------------------------|
| `current_level` | LevelManager | ✅ Да |
| `total_score` | LevelManager | ✅ Да |
| `carried_ammo` | LevelManager | ✅ Да |
| `has_medicine` | LevelManager | ✅ Да |
| HP игрока | Player.gd | ❌ Нет |
| Патроны игрока | Player.gd | ⚠️ Сохраняется в LevelManager при выходе |
| Сетка лабиринта | Main.gd | ❌ Нет |
| Массивы сущностей | Main.gd | ❌ Нет |

### 6.2 Правила

- Автосостояние (`LevelManager`) — авторитетный источник для меж-уровневых данных
- Сцена **НЕ** сбрасывает autoload при перезапуске
- При переходе уровня `Main.gd` сохраняет временное состояние в `LevelManager`:

```gdscript
func _on_exit() -> void:
    LevelManager.carried_ammo = maxi(_player.get_ammo(), 10)
    LevelManager.add_score(_player.get_score())
```

- При 3+ состояниях использовать явный `enum` вместо булевых флагов

---

## 7. Обработка ошибок

- **Null-безопасность:** всегда проверять ссылки перед использованием
- **`is_instance_valid()`:** проверять динамически полученные ноды
- **`has_method()`:** проверять наличие метода перед вызовом
- **`push_error()` / `push_warning()`:** логировать все неожиданные ситуации
- **Fallback ассеты:** при загрузке внешних файлов предусматривать fallback
- **Игра НЕ должна падать** при отсутствии ассета — логировать и продолжить

```gdscript
var tex = load("res://Assets/ammo_pickup.png")
if tex:
    sprite.texture = tex
else:
    push_warning("AmmoPickup: Failed to load sprite, using fallback")
```

---

## 8. Слои коллизий

Определены в `project.godot` → Physics → 2D Physics Layers:

| Слой | Имя | Используется |
|------|-----|-------------|
| 1 | `walls` | Стены (StaticBody2D) |
| 2 | `player` | Игрок |
| 3 | `enemy` | Враги |
| 5 | `bullet` | Пули (Area2D) |

### Матрица коллизий

| Сущность | Layer | Mask | Поведение |
|----------|-------|------|-----------|
| Player | 2 (player) | 1 (walls) | Столкновение со стенами |
| Enemy | 3 (enemy) | 1 (walls) | Столкновение со стенами |
| Bullet | 5 (bullet) | 1\|3 (walls+enemy) | Попадание в стены и врагов |
| Exit | 0 | 2 (player) | Detect player only |
| Pickups | 0 | 2 (player) | Detect player only |
| Walls | 1 (walls) | 0 | Твёрдые, не мониторят |

Правила:
- Все 32 слоя должны быть именованы (даже неиспользуемые)
- Подбираемые предметы — `Area2D` с `layer=0`, не блокируют движение
- Монеты — `Node2D`, подбор через проверку дистанции

---

## 9. Структура проекта

```
Project/
├── project.godot
├── .gitignore
├── generate_sprites.py
├── Docs/
│   ├── README.md
│   ├── README_DEV.md
│   ├── CODEBASE_STANDARDS.md
│   ├── GAME_REQUIREMENTS.md
│   └── TASKS.md
├── Settings/
│   ├── Settings.gd           # Autoload: параметры
│   ├── SoundManager.gd       # Autoload: звук
│   └── LevelManager.gd       # Autoload: состояние
├── Scenes/
│   ├── Main.tscn
│   ├── Player.tscn
│   ├── Enemy.tscn
│   ├── Bullet.tscn
│   ├── Coin.tscn
│   ├── Exit.tscn
│   ├── AmmoPickup.tscn
│   ├── Medkit.tscn
│   └── Medicine.tscn
├── Scripts/
│   ├── Main.gd
│   ├── Player.gd
│   ├── Enemy.gd
│   ├── Bullet.gd
│   ├── Coin.gd
│   ├── Exit.gd
│   ├── AmmoPickup.gd
│   ├── Medkit.gd
│   └── Medicine.gd
└── Assets/
    └── *.png
```

Правило: **одна сцена = один скрипт**. Каждая `.tscn` имеет соответствующий `.gd`.

---

## 10. Производительность

| Метрика | Цель |
|---------|------|
| FPS | 60+ ПК, 30+ мобильные |
| Загрузка уровня | < 3 секунд |
| Память | Без утечек за 30+ минут |

Правила:
- **Не создавать** массивы/объекты в `_process()` / `_physics_process()`
- Предварительно выделять и переиспользовать в `_ready()`
- Миникарта: кастомный `Control` с `_draw()`, **НЕ** SubViewport
- Освещение: на мобильных/низких настройках отключать тени
- Для будущих частиц и пуль — object pooling

---

## 11. Тестирование

Перед каждым коммитом — ручная проверка:

- [ ] Игрок двигается (WASD/стрелки)
- [ ] Стрельба работает (Space)
- [ ] Монеты собираются
- [ ] Враги двигаются и собирают монеты
- [ ] Пули наносят ущерб врагам
- [ ] Выход открывается при сборе всех монет
- [ ] Переход между уровнями
- [ ] Очки сохраняются между уровнями
- [ ] Заражение/иммунитет работают
- [ ] Аптечки лечат, лекарство снижает урон
- [ ] Смерть при 0 HP → экран смерти → ирга закончилась 1 попытка пройти
- [ ] Патроны не регенерируются, подбираются, переносятся между уровнями
- [ ] Фонарик вращается, стены блокируют свет
- [ ] Миникарта: туман войны, раскрытие, точка игрока
- [ ] Все спрайты загружаются
- [ ] FPS стабилен 60+

