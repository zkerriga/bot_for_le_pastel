#Bot for textile factory
import config 
import utils 
import telebot
import logging
import worker_db
import re
from SQLbase import SQLbase

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands = ['start'])
def start(message):
	"""	
	Show a keyboard for user's
	"""
	user_id = message.from_user.id
	kb, txt = utils.keyboard(user_id)
	bot.send_message(message.chat.id, text = txt, reply_markup = kb)

@bot.message_handler(commands = ['process'])
def process(message):
	"""
	Show all orders in a procces mode as a text
	"""
	#handle permissons for adm, factory, store
	user_id = message.from_user.id
	if utils.perm_adm(user_id) == 1 or utils.perm_store(user_id) == 1 or\
								utils.perm_factory(user_id) == 1:
		txt = utils.in_process()
		bot.send_message(message.chat.id, text = txt)
	else:
		bot.send_message(message.chat.id, text = "У Вас нету доступа к этой функции")

@bot.message_handler(commands = ['request'])
def request(message):
	"""
	Show all orders in a request mode as a inline_keyboard
	"""
	#handle permissons for adm, store
	user_id = message.from_user.id
	if utils.perm_adm(user_id) == 1:# or utils.perm_store(user_id) == 1:
		in_kb, txt = utils.request_orders()
		bot.send_message(message.chat.id, text = txt, reply_markup = in_kb)
	else:
		bot.send_message(message.chat.id, text = "У Вас нету доступа к этой функции")

@bot.message_handler(commands = ['add_material'])
def add_material(message):
	"""
	Let user add material as a writing text
	"""
	#handle permissons for adm
	user_id = message.from_user.id
	if utils.perm_adm(user_id) == 1:
		bot.send_message(message.chat.id, text = "Напишите имя нового материала.\
												Если Вы нажали сбда случайно напишите '0'")
		worker_db.set_state(message.chat.id, config.States.ADD_MATERIAL.value)
	else:
		bot.send_message(message.chat.id, text = "У Вас нету доступа к этой функции")

@bot.message_handler(commands = ['add_textile'])
def add_textile(message):
	"""
	Let adm add new textile 
	"""
	#handle permissons for adm
	user_id = message.from_user.id
	if utils.perm_adm(user_id) == 1:
		in_kb, txt = utils.in_kb_materials(0, "receive")
		bot.send_message(message.chat.id, text = txt, reply_markup = in_kb)
	else:
		bot.send_message(message.chat.id, text = "У Вас нету доступа к этой функции")

@bot.message_handler(commands = ['receive'])
def receive(message):
	"""
	Show to user info about all receive
	"""
	user_id = message.from_user.id
	if utils.perm_adm(user_id) == 1:
		db = SQLbase(config.db)
		txt = db.get_receive()
		db.close()
		bot.send_message(message.chat.id, text = txt)
	else:
		bot.send_message(message.chat.id, text = "У Вас нету доступа к этой функции")

@bot.message_handler(commands = ['shop_order'])
def shop_order(message):
	"""
	Give to shope in_kb with order's which in status 'process'
	"""
	#handle permissons for store
	user_id = message.from_user.id
	if utils.perm_store(user_id) == 1:
		in_kb, txt = utils.in_kb_shop()
		bot.send_message(message.chat.id, text = txt, reply_markup = in_kb)
	else:
		bot.send_message(message.chat.id, text = "У Вас нету доступа к этой функции")

@bot.message_handler(func = lambda message: worker_db.get_current_state(message.chat.id) == config.States.ADD_MATERIAL.value)
def get_name_material(message):
	"""
	getting name of the material and put in db
	"""
	if message.text != '0':
		txt = utils.add_material(message.text)
		bot.send_message(message.chat.id, text = txt)
	else:
		bot.send_message(message.chat.id, text = "Материал не был добавлен")
	worker_db.set_state(message.chat.id, config.States.START.value)

@bot.message_handler(commands = ['take_order'])
def take_order(message):
	"""
	Let user take a order as a inline_keyboard
	"""
	#handle permissons for adm, store
	user_id = message.from_user.id
	logging.info("take_order, user_id {}".format(user_id))
	if utils.perm_adm(user_id) == 1 or utils.perm_store(user_id) == 1:
		logging.info("take_order, user_id {}".format(user_id))
		in_kb, txt = utils.in_kb_product()
		bot.send_message(message.chat.id, text = txt, reply_markup = in_kb)
	else:
		bot.send_message(message.chat.id, text = "У Вас нету доступа к этой функции")



#call.data is  a id of a material from Material db	
#call.data >= 100 to handle collisions of show_material
@bot.callback_query_handler(lambda call: call.data[:4] == 'info')
def info_order(call):
	"""	
	Send a message to adm about the order
	"""
	id_info = re.findall(r"\d+", call.data)
	id_product = id_info[0]
	id_material = id_info[1]
	txt = utils.info_order(id_product, id_material)
	bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = txt)

@bot.callback_query_handler(lambda call: call.data[:3] == 'adm')
def end_request(call):
	"""
	if 'yes' change a status of order to process
	if 'no' do nothing
	"""
	if len(call.data) > 7:#adm_yes+number
		logging.info("call.data: \n{}".format(call.data))
		order_id = int(call.data[7:])
		logging.info("order_id: \n{}".format(order_id))
		txt = utils.to_process(order_id)
		bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = txt)
	elif len(call.data) == 6:#adm_no
		bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "Заявка не была допущенна на производство")

@bot.callback_query_handler(lambda call: call.data[:7] == 'receive')
def receive_material(call):
	"""
	show a in_kb of materials
	"""
	id_info = re.findall(r"\d+", call.data)
	id_material = id_info[0]
	db = SQLbase(config.db)
	db.add_material_term_receive(id_material)
	db.close()
	worker_db.set_state(call.from_user.id, config.States.RECEIVE_P_M.value)
	txt_1 = "Теперь напишите погонный метр(п.м.)"
	txt_2 = "Пример: 50.30"
	txt_3 = "Используйте '.'! Не верно: 50,30"
	txt = "{}\n{}\n{}".format(txt_1, txt_2, txt_3)
	bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = txt)

@bot.message_handler(func = lambda message: worker_db.get_current_state(message.chat.id) == config.States.RECEIVE_P_M.value)
def receive_p_m(message):
	try:
		p_m = float(message.text)
	except:
		p_m = None

	if p_m == None:

		txt = "Вы ввели не правильное число для п.м.! Используйте целое число(Например: 50) или число с точкой (Например: 50.30)"
		bot.send_message(message.chat.id, text = txt)
		return
	else:
		#add_p_m to table Unique_term
		db = SQLbase(config.db)
		db.add_p_m_term_receive(p_m)
		id_material, p_m = db.term_receive_info() 
		db.add_receive(p_m, id_material)
		material = db.info_material(id_material)
		db.close()
		txt = "Вы добавили ткань материала: {}. И размером {} п.м.".format(material, p_m)
		worker_db.set_state(message.chat.id, config.States.START.value)
		bot.send_message(message.chat.id, text = txt)

@bot.message_handler(func = lambda message: worker_db.get_current_state(message.chat.id) == config.States.SIZE.value)
def write_size(message):
	"""
	Adm or shop writing a size of a unique product
	"""
	logging.info(message.text)
	if message.text == "0":
		bot.send_message(message.chat.id, text = "Вы прекратили заполнять заявку на произвольный размер.")
		worker_db.set_state(message.chat.id, config.States.START.value)
		return
	
	try:
		index = message.text.index('*')
	except:
		index = None
	logging.info(index)
	check, txt = utils.check_size(message.text, index)
	if check == 0:
		bot.send_message(message.chat.id, text = txt)
		return
	else:
		bot.send_message(message.chat.id, text = txt)
		worker_db.set_state(message.chat.id, config.States.P_M.value)


@bot.message_handler(func = lambda message: worker_db.get_current_state(message.chat.id) == config.States.P_M.value)
def write_p_m(message):
	"""
	Adm or shop writing a p_m of a unique product
	"""
	try:
		p_m = float(message.text)
	except:
		p_m = None

	if p_m == None:
		txt = "Вы ввели не правильное число для п.м.! Используйте целое число(Например: 4) или число с точкой (Например: 4.30)"
		bot.send_message(message.chat.id, text = txt)
		return
	else:
		#add_p_m to table Unique_term
		db = SQLbase(config.db)
		db.add_item_unique('p_m', p_m)
		db.close()
		worker_db.set_state(message.chat.id, config.States.UNIQUE_MATERIAL.value)
		pick_material(message)

@bot.message_handler(func = lambda message: worker_db.get_current_state(message.chat.id) == config.States.UNIQUE_MATERIAL.value)
def pick_material(message):
	"""
	user picks a material for a unique order
	"""
	#7 - is id of a unique product
	logging.info("In the UNIQUE_MATERIAL")
	in_kb, txt = utils.in_kb_materials(7, "order")
	bot.send_message(message.chat.id, text = txt, reply_markup = in_kb)
	worker_db.set_state(message.chat.id, config.States.START.value)

@bot.callback_query_handler(lambda call: call.data[:4] == 'shop')
def done_order_shop(call):
	"""
	Show message about done product which shop picked before
	"""
	id_info = re.findall(r"\d+", call.data)
	id_order = id_info[0]
	txt = utils.done_order(id_order)
	bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = txt)

@bot.callback_query_handler(lambda call: call.data[:6] == 'unique')
def info_unique_order(call):
	"""
	show the user a unique order
	"""
	id_info = re.findall(r"\d+", call.data)
	id_material = id_info[0]
	txt = utils.add_unique_order(id_material)
	bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = txt)

#if adm or shope pick a create a unique product
@bot.callback_query_handler(lambda call: int(call.data) == 7)
def unique_product(call):
	"""
	send a message with instruction of unique product
	"""
	txt = utils.txt_size()
	bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = txt)
	worker_db.set_state(call.from_user.id, config.States.SIZE.value)

#call.data is  a id of a poduct from Product db
@bot.callback_query_handler(lambda call: int(call.data) >= 1 and int(call.data) < 7)
def show_material(call):
	"""
	Let user pick up a type of a material
	"""
	in_kb, txt = utils.in_kb_materials(int(call.data), "order")
	bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = txt, reply_markup = in_kb)

@bot.callback_query_handler(lambda call: int(call.data) >= 100)
def decide_adm(call):
	"""
	Give a finel qestion before put a product on factory
	"""
	order_id = int(int(call.data)/100)
	in_kb, txt = utils.decide_adm(order_id)
	bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = txt, reply_markup = in_kb)



@bot.message_handler(func = lambda message: True, content_types = ['text'])
def main(message):
	"""
	Answer on the query from user
	"""
	if message.text == 'Товары в призводстве':
		process(message)
	elif message.text == "Созданные запросы":
		request(message)
	elif message.text == "Добавить материал":
		add_material(message)
	elif message.text == "Создать запрос":
		take_order(message)
	elif message.text == "Завершить заказ":
		shop_order(message)
	elif message.text == "Добавить ткань":
		add_textile(message)
	elif message.text == "Отчёт":
		receive(message)

if __name__ == '__main__':
	logging.basicConfig(level = logging.INFO)
	bot.infinity_polling() 
	