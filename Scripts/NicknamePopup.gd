## Попап для ввода никнейма игрока
extends PopupPanel

# === SIGNALS =================================================================
signal nickname_submitted(nickname: String)

# === NODE REFERENCES =========================================================
@onready var _line_edit: LineEdit = $PopupVBox/NicknameLineEdit
@onready var _submit_button: Button = $PopupVBox/SubmitButton

# === LIFECYCLE ===============================================================
func _ready() -> void:
	_line_edit.text_submitted.connect(_on_nickname_entered)
	_submit_button.pressed.connect(_on_submit_pressed)
	about_to_popup.connect(_on_about_to_popup)

# === PRIVATE FUNCTIONS =======================================================
func _on_about_to_popup() -> void:
	_line_edit.text = ""
	_line_edit.grab_focus()

func _on_nickname_entered(text: String) -> void:
	_submit_nickname(text)

func _on_submit_pressed() -> void:
	var nickname = _line_edit.text.strip_edges()
	_submit_nickname(nickname)

func _submit_nickname(nickname: String) -> void:
	if nickname.is_empty():
		return
	
	if nickname.length() > 15:
		nickname = nickname.substr(0, 15)
	
	nickname_submitted.emit(nickname)
	hide()
