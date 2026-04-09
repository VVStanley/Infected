## Менеджер сохранений: никнейм игрока и таблица лидеров
extends Node

# === CONSTANTS =================================================================
const SAVE_PATH: String = "user://save_data.json"

# === PRIVATE VARIABLES =======================================================
var _player_nickname: String = ""
var _leaderboard: Array[Dictionary] = []

# === LIFECYCLE ===============================================================
func _ready() -> void:
	_load_data()

# === PUBLIC FUNCTIONS ========================================================
## Сохранить никнейм игрока
func save_nickname(nickname: String) -> void:
	_player_nickname = nickname
	_save_data()

## Получить никнейм игрока
func get_nickname() -> String:
	return _player_nickname

## Сохранить результат игрока
func save_score(score: int) -> void:
	if _player_nickname.is_empty():
		push_warning("SaveManager: Cannot save score without nickname")
		return
	
	_leaderboard.append({
		"nickname": _player_nickname,
		"score": score,
		"date": Time.get_datetime_string_from_system()
	})
	
	# Сортировка по убыванию очков
	_leaderboard.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		return a["score"] > b["score"]
	)
	
	# Храним только топ-10
	if _leaderboard.size() > 10:
		_leaderboard.resize(10)
	
	_save_data()

## Получить таблицу лидеров
func get_leaderboard() -> Array[Dictionary]:
	return _leaderboard

## Очистить таблицу лидеров
func clear_leaderboard() -> void:
	_leaderboard.clear()
	_save_data()

# === PRIVATE FUNCTIONS =======================================================
## Загрузить данные из файла
func _load_data() -> void:
	if not FileAccess.file_exists(SAVE_PATH):
		return
	
	var file = FileAccess.open(SAVE_PATH, FileAccess.READ)
	if file == null:
		push_error("SaveManager: Failed to open save file")
		return
	
	var json_text = file.get_as_text()
	file.close()
	
	var json = JSON.new()
	var parse_result = json.parse(json_text)
	
	if parse_result != OK:
		push_error("SaveManager: Failed to parse save data")
		return
	
	var data = json.get_data()
	if not data is Dictionary:
		push_error("SaveManager: Invalid save data format")
		return
	
	_player_nickname = data.get("nickname", "")
	
	var lb_data = data.get("leaderboard", [])
	if lb_data is Array:
		for entry in lb_data:
			if entry is Dictionary and entry.has("nickname") and entry.has("score"):
				_leaderboard.append(entry)

## Сохранить данные в файл
func _save_data() -> void:
	var file = FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file == null:
		push_error("SaveManager: Failed to open save file for writing")
		return
	
	var data = {
		"nickname": _player_nickname,
		"leaderboard": _leaderboard
	}
	
	var json_text = JSON.stringify(data, "  ")
	file.store_string(json_text)
	file.close()
