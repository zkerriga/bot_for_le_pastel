#databases for textile bot
import config
import sqlite3
import logging

class SQLbase():
	"""
	class of db Textile, Material, Product
	"""
	def __init__(self, database):
		self.connection = sqlite3.connect(database, check_same_thread = False)
		self.cur = self.connection.cursor()

	def add_material(self, name):
		"""
		insert a new position and add a name in material
		"""
		with self.connection:
			self.cur.execute("INSERT INTO Material (name, price) VALUES (?, ?)", (name, 0))
			self.connection.commit()

	def get_materials(self):
		"""
		return a list of all materials
		"""
		materials = []
		with self.connection:
			for row in self.cur.execute("SELECT * FROM Material"):
				logging.info("{}".format(row))
				encode = "{} {}".format(row[0], row[1])
				materials.append(encode)
			logging.info("{}".format(materials))
			if materials == []:
				return 0
			else:
				return materials

	def get_product(self):
		"""
		return a list with product information
		"""
		data = []
		with self.connection:
			for row in self.cur.execute("SELECT * FROM Product"):
				#row[0] is id of a product
				#row[1], row[2], row[3] is info about a product
				encode = "{} {} {} - {} п.м.".format(row[0], row[1], row[2], row[3])
				data.append(encode)
		return data

	def info_product(self, id_product):
		"""
		return a txt about a order
		"""
		with self.connection:
			row = self.cur.execute("SELECT * FROM Product WHERE id = ?", (id_product,)).fetchone()
			logging.info("{}".format(row))
			txt_0 = "Вы создали заявку на производство товара со следующими характеристиками:"
			txt_1 = "Наименование товара: {}".format(row[1])
			txt_2 = "Размер товара: {}".format(row[2])
			txt_3 = "Величина п/м: {}".format(row[3])
			txt = "{0}\n{1}\n{2}\n{3}\n".format(txt_0, txt_1, txt_2, txt_3)
			return txt

	def info_material(self, id_material):
		"""
		return a txt about material
		"""
		with self.connection:
			row = self.cur.execute("SELECT * FROM Material WHERE id = ?", (id_material,)).fetchone()
			logging.info("{}".format(row))
			txt = "Вид материала: {}".format(row[1])
			return txt

	def close(self):
		"""
		Close db
		"""
		self.connection.close()