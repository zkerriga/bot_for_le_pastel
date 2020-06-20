#Bot for textile factory
import config 
import utils 
import telebot
import logging
import worker_db
import re

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
		pass
	else:
		bot.send_message(message.chat.id, text = "У Вас нету доступа к этой функции")

@bot.message_handler(commands = ['request'])
def request(message):
	"""
	Show all orders in a request mode as a inline_keyboard
	"""
	#handle permissons for adm, store
	user_id = message.from_user.id
	if utils.perm_adm(user_id) == 1 or utils.perm_store(user_id) == 1:
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

#call.data is  a id of a poduct from Product db
@bot.callback_query_handler(lambda call: int(call.data) >= 1 and int(call.data) <= 7)
def show_material(call):
	"""
	Let user pick up a type of a material
	"""
	in_kb, txt = utils.in_kb_materials(int(call.data))
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
	

if __name__ == '__main__':
	logging.basicConfig(level = logging.INFO)
	bot.infinity_polling() 
	