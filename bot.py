#Bot for textile factory
import config 
import utils 
import telebot
import logging
import worker_db

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
		pass
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
		in_kb, txt = utils.in_kb_order()
		bot.send_message(message.chat.id, text = txt, reply_markup = in_kb)
	else:
		bot.send_message(message.chat.id, text = "У Вас нету доступа к этой функции")

	
@bot.message_handler(func = lambda message: True, content_types = ['text'])
def main(message):
	"""
	Answer on the query from user
	"""
	if message.text == 'Товары в призводстве':
		process(message)
	elif message.text == "Созданные товары":
		request(message)
	elif message.text == "Добавить материал":
		add_material(message)
	elif message.text == "Создать запрос":
		take_order(message)
	

if __name__ == '__main__':
	logging.basicConfig(level = logging.INFO)
	bot.infinity_polling() 
	