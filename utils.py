#utils for textile bot!
import config
import logging
from telebot import types
from SQLbase import SQLbase



def keyboard(user_id):
	"""
	Show keyboard for users
	"""
	kb = types.ReplyKeyboardMarkup(resize_keyboard = True)
	process = "Товары в призводстве"
	request = "Созданные запросы"
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
	else: 
		return 0

def perm_store(user_id):
	"""
	return 1 if store can get a permission for this bot
	overwise return 0
	"""
	if user_id == config.store_id:
		return 1
	else: 
		return 0

def perm_factory(user_id):
	"""
	return 1 if factory can get a permission for this bot
	overwise return 0
	"""
	if user_id == config.factory_id:
		return 1
	else: 
		return 0

def add_material(name):
	"""
	add material in Material db
	"""
	db = SQLbase(config.db)
	db.add_material(name)
	db.close()
	txt = "Вы добавили новый материал с названием: {}".format(name)
	logging.info("Added material with name: {}".format(name))
	return txt

def in_kb_product():
	"""
	Show inline_kb for user to make a order
	"""
	in_kb = types.InlineKeyboardMarkup(row_width = 1)
	#get list of all product from db
	db = SQLbase(config.db)
	data = db.get_product()
	db.close()
	txt = "Выберите один из товаров: "
	for item in data:
		#item[2:] - info about product
		#item[:1] - id of a product
		#first ' ' is a border between id_product and info_product
		index = item.index(' ')
		button = types.InlineKeyboardButton(text = item[(index + 1):], callback_data = str(item[:index]))
		in_kb.add(button)
	button = types.InlineKeyboardButton(text = "Произвольный размер", callback_data = str(7))
	in_kb.add(button)
	return in_kb, txt

def in_kb_materials(id_product):
	"""
	Create inline keyboard of all materials
	"""
	in_kb = types.InlineKeyboardMarkup(row_width = 1)
	#get list of all materials from db
	db = SQLbase(config.db)
	materials = db.get_materials()
	db.close()
	
	if materials != 0:
		txt = "Выберите тип материала из которого сделать ранее выбранный товар:"
		for item in materials:
			#item[2:] - name material
			#item[:1] - id of a material
			#id_product - picked product by store or abm
			encode = "info {} {}".format(id_product, item[:1]) 
			button = types.InlineKeyboardButton(text = item[2:], callback_data = encode)
			in_kb.add(button)
		return in_kb, txt
	else:
		txt = "Не созданно не одного метриала. Администратор должен добавить вид материалов."
		return in_kb, txt

def info_order(id_product, id_material):
	"""
	Create info about an order
	"""
	db = SQLbase(config.db)
	name_prod, size, p_m = db.info_product(id_product)
	name_matirial = db.info_material(id_material)
	db.add_order(int(id_product), int(id_material))
	db.close()

	
	txt_0 = "Вы создали заявку на производство товара со следующими характеристиками:"
	txt_1 = "Наименование товара: {}".format(name_prod)
	txt_2 = "Размер товара: {}".format(size)
	txt_3 = "Величина п/м: {}".format(p_m)
	txt_4 = "Вид материала: {}".format(name_matirial)
	txt = "{0}\n{1}\n{2}\n{3}\n{4}".format(txt_0, txt_1, txt_2, txt_3, txt_4)
	
	return txt

def txt_order(item):
	"""
	return a text about order
	"""
	txt_0 = "{}.{}".format(item[0], item[1])
	txt_1 = "{}".format(item[2])
	txt_2 = "{} - {}".format(item[3], item[4])
	txt = "{}; {}\n{}".format(txt_0, txt_1, txt_2)
	return txt

def request_orders():
	"""
	Create in_kb of orders with status "request"
	"""
	db = SQLbase(config.db)
	list_orders = db.request_orders()
	db.close()
	logging.info("request_orders \n{}".format(list_orders))
	in_kb = types.InlineKeyboardMarkup()
	if list_orders != []:
		text = "Выберите запрос котроый хотите отправить на производство:"
		for item in list_orders:
			logging.info("Item:\n{}".format(item))
			txt = txt_order(item)
			#item[0] - id of order
			#item[0] multiply on 100 to handle collusions with in_kb_product
			button = types.InlineKeyboardButton(text = txt, callback_data = str(item[0]*100))
			in_kb.add(button)
	else:
		text = "Нет созданных запросов"
	return in_kb, text

def decide_adm(order_id):
	"""
	In_kb with yes or no and text about order 
	"""
	db = SQLbase(config.db)
	list_order = db.info_request(order_id)
	db.close()
	txt_0 = "Вы уверенны что хотите выпустить на производство этот товар:"
	txt_1 = txt_order(list_order)
	txt = "{}\n{}".format(txt_0, txt_1)
	in_kb = types.InlineKeyboardMarkup()
	yes = types.InlineKeyboardButton(text = "Да", callback_data = "adm_yes{}".format(order_id))
	no = types.InlineKeyboardButton(text = "Нет", callback_data = "adm_no")
	in_kb.add(yes, no)
	return in_kb, txt

def to_process(order_id):
	"""
	Put order in process and return a text
	"""
	db = SQLbase(config.db)
	db.to_process(order_id)
	list_order = db.info_request(order_id)
	db.close()
	txt_0 = "Данный товар на производстве:"
	txt_1 = txt_order(list_order)
	txt = "{}\n{}".format(txt_0, txt_1)
	return txt






