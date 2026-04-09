## Главное меню игры
extends Control

# === SIGNALS =================================================================
signal play_pressed
signal settings_pressed
signal leaderboard_pressed
signal exit_pressed

# === NODE REFERENCES =========================================================
@onready var _play_button: Button = $MenuContainer/PlayButton
@onready var _settings_button: Button = $MenuContainer/SettingsButton
@onready var _leaderboard_button: Button = $MenuContainer/LeaderboardButton
@onready var _exit_button: Button = $MenuContainer/ExitButton
@onready var _nickname_popup: PopupPanel = $NicknamePopup

# === LIFECYCLE ===============================================================
func _ready() -> void:
	_connect_signals()

# === PRIVATE FUNCTIONS =======================================================
func _connect_signals() -> void:
	_play_button.pressed.connect(_on_play_pressed)
	_settings_button.pressed.connect(_on_settings_pressed)
	_leaderboard_button.pressed.connect(_on_leaderboard_pressed)
	_exit_button.pressed.connect(_on_exit_pressed)
	_nickname_popup.nickname_submitted.connect(_on_nickname_submitted)

func _start_game() -> void:
	get_tree().change_scene_to_file("res://Scenes/GamePlaceholder.tscn")

# === SIGNAL HANDLERS =========================================================
func _on_play_pressed() -> void:
	var existing_nickname = SaveManager.get_nickname()
	if existing_nickname.is_empty():
		_nickname_popup.popup_centered()
	else:
		_start_game()

func _on_settings_pressed() -> void:
	get_tree().change_scene_to_file("res://Scenes/SettingsScreen.tscn")

func _on_leaderboard_pressed() -> void:
	get_tree().change_scene_to_file("res://Scenes/LeaderboardScreen.tscn")

func _on_exit_pressed() -> void:
	get_tree().quit()

func _on_nickname_submitted(nickname: String) -> void:
	SaveManager.save_nickname(nickname)
	_start_game()
