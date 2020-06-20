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
			
			name_prod = row[1]
			size = row[2]
			p_m = row[3]
			return name_prod, size, p_m

	def info_material(self, id_material):
		"""
		return a txt about material
		"""
		with self.connection:
			row = self.cur.execute("SELECT * FROM Material WHERE id = ?", (id_material,)).fetchone()
			name_material = row[1]
			return name_material

	def add_order(self, id_product, id_material):
		"""
		Add an order in db Order
		"""
		status = "request"
		name_prod, size, p_m = self.info_product(id_product)
		name_material = self.info_material(id_material)
		with self.connection:
			self.cur.execute("INSERT INTO Orders (name_prod, name_material, size, p_m, status) VALUES (?, ?, ?, ?, ?)",\
												 (name_prod, name_material, size, p_m, status))
			self.connection.commit()

	def request_orders(self):
		"""
		Create list orders
		"""
		status = "request"
		list_orders = []
		with self.connection:
			for item in self.cur.execute("SELECT * FROM Orders WHERE status = ?", (status,)):
				#logging.info("request_orders ITEM:\n{}".format(item))
				list_orders.append(item)
		return list_orders

	def info_request(self, order_id):
		"""
		Get info about one order from db
		"""
		with self.connection:
			row = self.cur.execute("SELECT * FROM Orders WHERE id = ?", (order_id,)).fetchone()
			#name_prod = row[1]
			#name_material = row[2]
			#size = row[3]
			#p_m = row[4]
			#return name_prod, name_material, size, p_m
			return row

	def to_process(self, order_id):
		"""
		change status on process
		"""
		process = 'process'
		with self.connection:
			self.cur.execute("UPDATE Orders SET status = ? WHERE id = ?", (process, order_id))
			self.connection.commit()

	def close(self):
		"""
		Close db
		"""
		self.connection.close()