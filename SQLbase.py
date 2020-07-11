#databases for textile bot
import config
import sqlite3
import logging
from datetime import datetime

class SQLbase():
	"""
	class of db Textile, Material, Product
	"""
	def __init__(self, database):
		self.connection = sqlite3.connect(database, check_same_thread = False)
		self.cur = self.connection.cursor()

	#Podeuct table
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

	#Material table
	def add_material(self, name):
		"""
		insert a new position and add a name in material
		"""
		with self.connection:
			self.cur.execute("INSERT INTO Material (name, rest, price) VALUES (?, ?, ?)", (name, 0, 0))
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

	def info_material(self, id_material):
		"""
		return a txt about material
		"""
		with self.connection:
			logging.info("id_material is: {}".format(id_material))
			row = self.cur.execute("SELECT * FROM Material WHERE id = ?", (id_material,)).fetchone()
			name_material = row[1]
		return name_material

	#Orders table
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

	def list_orders(self, status):
		"""
		Create list orders with a status
		"""
		list_orders = []
		with self.connection:
			for item in self.cur.execute("SELECT * FROM Orders WHERE status = ?", (status,)):
				logging.info("request_orders ITEM:\n{}".format(item))
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

	def done_process(self, order_id):
		"""
		Change status on done
		"""
		done = 'done'
		with self.connection:
			self.cur.execute("UPDATE Orders SET status = ? WHERE id = ?", (done, order_id))
			self.connection.commit()

	#Unique table
	def add_item_unique(self, column, value):
		"""
		add a size in the Unique db only for unique product 
		column - is a size or p_m or material
		value - is a value of a cloumn
		"""
		with self.connection:
			logging.info("is k: {}".format(self.cur.execute("SELECT id FROM Unique_term").fetchone()))
			if self.cur.execute("SELECT id FROM Unique_term").fetchone() == None:
				self.cur.execute("INSERT INTO Unique_term (id, size, p_m, name_material) VALUES (?, ?, ?, ?)",\
													 (1, value, 0, ""))
			elif self.cur.execute("SELECT id FROM Unique_term").fetchone()[0] == 1:
				self.cur.execute("UPDATE Unique_term SET {} = ? WHERE id = ?".format(column), (value, 1))
			self.connection.commit()

	def info_unique(self):
		"""
		get all info about unique order
		"""
		with self.connection:
			size = self.cur.execute("SELECT size FROM Unique_term WHERE id = ?", (1,)).fetchone()[0]
			p_m = self.cur.execute("SELECT p_m FROM Unique_term WHERE id = ?", (1,)).fetchone()[0]
			name_material = self.cur.execute("SELECT name_material FROM Unique_term WHERE id = ?", (1,)).fetchone()[0]
		return size, p_m, name_material

	def add_unique(self):
		"""
		Add unique order in db Order
		"""
		status = "request"
		name_prod = "Произвольный размер"
		size, p_m, name_material = self.info_unique()
		logging.info("name_prod - {}\nname_material - {}\nsize - {}\np_m - {}\nstatus - {}".format(name_prod, name_material, size, p_m, status))
		with self.connection:
			self.cur.execute("INSERT INTO Orders (name_prod, name_material, size, p_m, status) VALUES (?, ?, ?, ?, ?)",\
												 (name_prod, name_material, size, p_m, status))
			self.connection.commit()
		return name_prod, size, p_m

	#Receive

	def current_date(self):
		"""
		return a current date
		"""
		current_date = str(datetime.now())
		logging.info("CURRENT_DATE {}".format(current_date))
		#get year
		year = int(current_date[0] + current_date[1] + current_date[2] + current_date[3])
		#get dat
		if current_date[5] == "0":
			month = int(current_date[6])
		else:
			month = int(current_date[5] + current_date[6])
		#get date
		if current_date[8] == "0":
			date = int(current_date[9])
		else:
			date = int(current_date[8] + current_date[9])
		txt = "{}.{}.{}".format(date, month, year)

		return txt

	def add_receive(self, p_m, id_material):
		"""
		Add to table Receive a material
		Add to table Material to column rest a valur of p_m of id_material
		"""
		with self.connection:
			#add info to Receive table
			date = self.current_date()
			logging.info("DATE: {}".format(date))
			self.cur.execute("INSERT INTO Receive (p_m, data, id_material) VALUES (?, ?, ?)", (p_m, date, id_material))
			#Update info to Material table
			p_m_material = self.cur.execute("SELECT rest FROM Material WHERE id = ?", (id_material,)).fetchone()[0]
			rest = p_m + p_m_material
			self.cur.execute("UPDATE Material SET rest = ? WHERE id = ?", (rest, id_material))
			self.connection.commit()

	def get_receive(self):
		"""	
		Take from db info about material
		"""
		receive_txt = "Поступило:\n"
		rest_txt = "Осталось:\n"
		with self.connection:
			#receive staff
			for receive in self.cur.execute("SELECT * FROM Receive").fetchall():
			
				p_m = receive[1]
				data = receive[2]
				id_material = receive[3]
				material = self.info_material(id_material)
				receive_txt += "{} {} - {} п.м.\n".format(data, material, p_m) 
			#rest staf
			for rest in self.cur.execute("SELECT * FROM Material").fetchall():
				logging.info("REST: {}".format(rest))
				rest_material = rest[1]
				rest_pm = rest[2]
				rest_txt += "{} - {} п.м.\n".format(rest_material, rest_pm)
			txt = "{}\n{}".format(receive_txt, rest_txt)
		return txt				

	#Receive_term

	def add_material_term_receive(self, id_material):
		"""
		add or update a name of material
		"""
		with self.connection:
			logging.info("ID_MATERIAL: {}".format(id_material))
			if self.cur.execute("SELECT id FROM Receive_term").fetchone() == None:
				self.cur.execute("INSERT INTO Receive_term (id, id_material, p_m) VALUES (?, ?, ?)",\
													 (1, id_material, 0))
			elif self.cur.execute("SELECT id FROM Receive_term").fetchone()[0] == 1:
				self.cur.execute("UPDATE Receive_term SET id_material = ? WHERE id = ?", (id_material, 1))
			self.connection.commit()

	def add_p_m_term_receive(self, p_m):
		"""
		add or update a p_m of material
		"""
		with self.connection:
			self.cur.execute("UPDATE Receive_term SET p_m = ? WHERE id = ?", (p_m, 1))
			self.connection.commit()

	def term_receive_info(self):
		"""
		Get a info textile which has been added to db
		"""
		with self.connection:
			id_material = self.cur.execute("SELECT id_material FROM Receive_term WHERE id = ?", (1,)).fetchone()[0]
			p_m = self.cur.execute("SELECT p_m FROM Receive_term WHERE id = ?", (1,)).fetchone()[0]
		return id_material, p_m
	
	#remains of textile
	def remains(self, order_id):
		"""
		Minus p_m which is on factory now
		"""
		with self.connection:
			remains = self.cur.execute("SELECT p_m FROM Orders WHERE id = ?", (order_id,)).fetchone()[0]
			name_material = self.cur.execute("SELECT name_material FROM Orders WHERE id = ?", (order_id,)).fetchone()[0]
			rest_textile = self.cur.execute("SELECT rest FROM Material WHERE name = ?", (name_material, )).fetchone()[0]
			self.cur.execute("UPDATE Material SET rest = ? WHERE name = ?", ((rest_textile - remains), name_material))
			self.connection.commit()

	def close(self):
		"""
		Close db
		"""
		self.connection.close()