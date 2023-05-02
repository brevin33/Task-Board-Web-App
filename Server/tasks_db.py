import sqlite3
from passlib.hash import bcrypt

def dict_factory(cursor, row):
	col_names = [col[0] for col in cursor.description]
	return {key: value for key, value in zip(col_names, row)}

class TasksDB:

	def __init__(self):
		self.connection = sqlite3.connect("tasks.db")
		self.connection.row_factory = dict_factory
		self.cursor = self.connection.cursor()

	def createTask(self, name,startDate,endDate,progress):
		data = [name,startDate,endDate,progress]
		self.cursor.execute("INSERT INTO tasks (name, startDate, endDate, progress) VALUES (?,?,?,?)", data)
		self.connection.commit()

	def findTasks(self):	
		self.cursor.execute("SELECT * FROM tasks")
		return self.cursor.fetchall()

	def findTask(self,id):
		data = [id]
		self.cursor.execute("SELECT * FROM tasks WHERE id = ?", data)
		return self.cursor.fetchone()

	def deleteTask(self,id):
		data = [id]
		self.cursor.execute("DELETE FROM tasks WHERE id = ?", data)
		self.connection.commit()

	def updateTask(self,id,name,startDate,endDate,progress):
		data = [name,startDate,endDate,progress,id]
		self.cursor.execute("UPDATE tasks SET name = ?, startDate = ?, endDate = ?, progress = ? WHERE id = ?", data)
		self.connection.commit()

	def createUser(self,email,password,namef,namel):
		data = [email]
		self.cursor.execute("SELECT * FROM users WHERE email = ?", data)
		if self.cursor.fetchone() == None:
			encript = bcrypt.hash(password)
			data = [email,encript,namef,namel]
			self.cursor.execute("INSERT INTO users (email,password,namef,namel) VALUES (?,?,?,?)", data)
			self.connection.commit()
			return True
		return False

	def validateUser(self,email,password):	
		data = [email]
		self.cursor.execute("SELECT password FROM users WHERE email = ?", data)
		passhash = self.cursor.fetchone()
		if passhash == None:
			return False
		if bcrypt.verify(password, passhash['password']):
			return True
		return False

	def getUserId(self,email):
		data = [email]
		self.cursor.execute("SELECT id FROM users WHERE email = ?", data)
		return self.cursor.fetchone()



# DELETE FROM tasks WHERE id = ?
# UPDATE tasks SET name = ?, otherelement = ? WHERE id = ?