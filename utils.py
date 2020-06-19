#utils for textile bot!
import config
from telebot import types

def keyboard(user_id):
	"""
	Show keyboard for users
	"""
	kb = types.ReplyKeyboardMarkup(resize_keyboard = True)
	process = "Товары в призводстве"
	request = "Созданные товары"
	add_material = "Добавить материал"
	take_order = "Создать запрос"
	txt = "Внизу у Вас появится меню"
	#keyboard for adm
	if user_id == config.adm_id_1 or config.adm_id_2:
		kb.add(process)
		kb.add(request)
		kb.add(add_material)
		kb.add(take_order)
		return kb, txt 
	#keyboard for store
	elif user_id == config.store_id:
		kb.add(process)
		kb.add(request)
		kb.add(take_order)
		return kb, txt
	#keyboard for factory
	elif user_id == config.factory_id:
		kb.add(process)
		return kb, txt

def perm_adm(user_id):
	"""
	return 1 if adm can get a permission for this bot
	overwise return 0
	"""
	if user_id == config.adm_id_1 or user_id == config.adm_id_2:
		return 1
	else 
		return 0
def perm_store(user_id):
	"""
	return 1 if store can get a permission for this bot
	overwise return 0
	"""
	if user_id == config.store_id:
		return 1
	else 
		return 0
def perm_factory(user_id):
	"""
	return 1 if factory can get a permission for this bot
	overwise return 0
	"""
	if user_id == config.factory_id:
		return 1
	else 
		return 0




