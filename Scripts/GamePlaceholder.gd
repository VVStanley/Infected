## Заглушка для игровой сцены (будет заменена на Main.tscn)
extends Control

# === NODE REFERENCES =========================================================
@onready var _back_button: Button = $BackButton

# === LIFECYCLE ===============================================================
func _ready() -> void:
	_back_button.pressed.connect(_on_back_pressed)

# === PRIVATE FUNCTIONS =======================================================
func _on_back_pressed() -> void:
	get_tree().change_scene_to_file("res://Scenes/MainMenu.tscn")
