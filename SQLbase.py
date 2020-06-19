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

	def show_material(self):
		"""
		return a list of all materials
		"""
		with self.connection:
			materials = self.cur.execute("SELECT name FROM Material")
			logging.info("{}".format(materials))
			return materials

	def get_product(self):
		"""
		return a list with product information
		"""
		data = []
		with self.connection:
			for row in self.cur.execute("SELECT * FROM Product"):
				txt = "{} {} {} - {} п.м.".format(row[0], row[1], row[2], row[3])
				data.append(txt)
		return data

	def close(self):
		"""
		Close db
		"""
		self.connection.close()