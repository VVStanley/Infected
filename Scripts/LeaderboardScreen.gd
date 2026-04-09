## Экран таблицы лидеров
extends Control

# === NODE REFERENCES =========================================================
@onready var _leaderboard_container: VBoxContainer = $ScrollContainer/LeaderboardContainer
@onready var _back_button: Button = $BackButton

# === LIFECYCLE ===============================================================
func _ready() -> void:
	_back_button.pressed.connect(_on_back_pressed)
	_populate_leaderboard()

# === PRIVATE FUNCTIONS =======================================================
func _populate_leaderboard() -> void:
	var leaderboard = SaveManager.get_leaderboard()
	
	if leaderboard.is_empty():
		var empty_label = Label.new()
		empty_label.text = "Пока нет результатов"
		empty_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		empty_label.add_theme_color_override("font_color", Color(0.5, 0.5, 0.5, 1))
		_leaderboard_container.add_child(empty_label)
		return
	
	for i in range(leaderboard.size()):
		var entry = leaderboard[i]
		var rank = i + 1
		
		var entry_label = Label.new()
		var score = entry.get("score", 0)
		var nickname = entry.get("nickname", "Unknown")
		var date = entry.get("date", "")
		
		entry_label.text = "%d. %s — %d очков" % [rank, nickname, score]
		entry_label.add_theme_font_size_override("font_size", 22)
		
		# Топ-3 выделяем цветом
		if rank == 1:
			entry_label.add_theme_color_override("font_color", Color(1, 0.84, 0, 1))  # Золотой
		elif rank == 2:
			entry_label.add_theme_color_override("font_color", Color(0.75, 0.75, 0.75, 1))  # Серебряный
		elif rank == 3:
			entry_label.add_theme_color_override("font_color", Color(0.8, 0.4, 0.2, 1))  # Бронзовый
		else:
			entry_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.8, 1))
		
		_leaderboard_container.add_child(entry_label)

func _on_back_pressed() -> void:
	get_tree().change_scene_to_file("res://Scenes/MainMenu.tscn")
