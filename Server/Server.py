from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import parse_qs
from http import cookies
import json
import os.path
from tasks_db import TasksDB
from session_store import SessionStore

SS = SessionStore()

class ThreadedHTTPServer(ThreadingMixIn,HTTPServer):
	pass

class myResponseHandeler(BaseHTTPRequestHandler):

	def handleNotFound(self):
		self.send_response(404)
		self.send_header("Content-Type","text/plain")
		self.End_headers()
		self.wfile.write(bytes("Not Found","utf-8"))

	def loadCookie(self):
		if "cookie" in self.headers:
			self.cookie = cookies.SimpleCookie(self.headers["Cookie"])
		else:
			self.cookie = cookies.SimpleCookie()

	def handle401(self):
		self.send_response(401)
		self.End_headers()

	def sendCookie(self):
		for morsel in self.cookie.values():
			if "Postman" not in self.headers["User-Agent"]:
				morsel["samesite"] = "None"
				morsel["secure"] = True
			self.send_header("Set-Cookie", morsel.OutputString())

	def load_session(self):
		self.loadCookie()
		if 'sessionId' not in self.cookie:
			self.cookie["sessionId"] = SS.createSession()
			self.sessionData = SS.getSessionData(self.cookie["sessionId"].value)
			return
		sessionId = self.cookie['sessionId'].value
		self.sessionData = SS.getSessionData(sessionId)
		if self.sessionData == None:
			self.cookie["sessionId"] = SS.createSession()
			self.sessionData = SS.getSessionData(self.cookie["sessionId"].value)
			return

	def handleReteriveTasks(self):
		if "userId" not in self.sessionData:
			self.handle401()
			return
		self.send_response(200)
		self.send_header("Content-Type","application/json")
		self.End_headers()
		DB = TasksDB()
		self.wfile.write(bytes(json.dumps(DB.findTasks()),"utf-8"))

	def handlePost(self):
		if "userId" not in self.sessionData:
			self.handle401()
			return
		items = parse_qs(self.rfile.read((int)(self.headers["Content-Length"])).decode("utf-8"))
		if (("name" in items) and ("startDate" in items) and ("endDate" in items) and ("progress" in items)) == False:
			self.handleNotFound()
			return
		name = items["name"][0]
		startDate = items["startDate"][0]
		endDate = items["endDate"][0]
		progress = items["progress"][0]
		DB = TasksDB()
		DB.createTask(name,startDate,endDate,progress)
		self.send_response(201)
		self.End_headers()

	def handleReplace(self, id):
		DB = TasksDB()
		if "userId" not in self.sessionData:
			self.handle401()
			return
		if DB.findTask(id):
			items = parse_qs(self.rfile.read((int)(self.headers["Content-Length"])).decode("utf-8"))
			if (("name" in items) and ("startDate" in items) and ("endDate" in items) and ("progress" in items)) == False:
				self.handleNotFound()
				return
			name = items["name"][0]
			startDate = items["startDate"][0]
			endDate = items["endDate"][0]
			progress = items["progress"][0]
			DB.updateTask(id,name,startDate,endDate,progress)
			self.send_response(200)
			self.End_headers()
		else:
			self.handleNotFound()

	def handleReteriveTask(self,id):
		DB = TasksDB()
		if "userId" not in self.sessionData:
			self.handle401()
			return
		if DB.findTask(id):
			self.send_response(200)
			self.send_header("Content-Type","application/json")
			self.End_headers()
			self.wfile.write(bytes(json.dumps(DB.findTask(id)),"utf-8"))
		else:
			self.handleNotFound()

	def handleDeleteTask(self,id):
		DB = TasksDB()
		if "userId" not in self.sessionData:
			self.handle401()
			return
		if DB.findTask(id):
			DB.deleteTask(id)
			self.send_response(200)
			self.End_headers()
		else:
			self.handleNotFound()

	def handleNewUser(self):
		DB = TasksDB()
		items = parse_qs(self.rfile.read((int)(self.headers["Content-Length"])).decode("utf-8"))
		if (("namef" in items) and ("namel" in items) and ("email" in items) and ("password" in items)) == False:
			self.handleNotFound()
			return
		namef = items["namef"][0]
		namel = items["namel"][0]
		email = items["email"][0]
		password = items["password"][0]
		created = DB.createUser(email,password,namef,namel)
		if created == False:
			self.send_response(422)
			self.End_headers()
			return
		self.sessionData["userId"] = DB.getUserId(email)
		self.send_response(201)
		self.End_headers()

	def handleLogin(self):
		DB = TasksDB()
		items = parse_qs(self.rfile.read((int)(self.headers["Content-Length"])).decode("utf-8"))
		if (("email" in items) and ("password" in items)) == False:
			self.handleNotFound()
			return
		email = items["email"][0]
		password = items["password"][0]
		if DB.validateUser(email,password) == False:
			self.send_response(401)
			self.End_headers()
			return
		self.sessionData["userId"] = DB.getUserId(email)
		self.send_response(201)
		self.End_headers()

	def End_headers(self):
		self.sendCookie()
		self.send_header("access-control-allow-origin", self.headers["Origin"])
		self.send_header("Access-Control-Allow-Credentials", "true")
		self.end_headers()

	def do_OPTIONS(self):
		self.load_session()
		self.send_response(200)
		self.send_header("access-control-allow-methods", "GET, POST, PUT, DELETE, OPTIONS")
		self.send_header("access-control-allow-headers", "Content-Type")
		self.End_headers()

	def do_DELETE(self):
		#setup
		self.load_session()
		parts = self.path.split('/')
		if len(parts) == 2:
			collection = parts[1]
			id = False
		else:
			collection = parts[1]
			id = parts[2]
		if collection == "tasks" and id:
			self.handleDeleteTask(id)
		else:
			self.handleNotFound()

	def do_PUT(self):
		#setup
		self.load_session()
		parts = self.path.split('/')
		if len(parts) == 2:
			collection = parts[1]
			id = False
		else:
			collection = parts[1]
			id = parts[2]
		if collection == "tasks" and id:
			self.handleReplace(id)
		else:
			self.handleNotFound()

	def do_GET(self):
		#setup
		self.load_session()
		parts = self.path.split('/')
		if len(parts) == 2:
			collection = parts[1]
			id = False
		else:
			collection = parts[1]
			id = parts[2]
		#choose path
		if collection == "tasks" and id == False:
			self.handleReteriveTasks()
		elif collection == "tasks" and id:
			self.handleReteriveTask(id)
		else:
			self.handleNotFound()

	# add user id to self.sessisionData['']
	def do_POST(self):
		self.load_session()
		parts = self.path.split('/')
		if len(parts) == 2:
			collection = parts[1]
			id = False
		else:
			collection = parts[1]
			id = parts[2]
		if self.path == "/tasks":
			self.handlePost()
		elif collection == "users":
			self.handleNewUser()
		elif collection == "sessions":
			self.handleLogin()
		else:
			self.handleNotFound()
def run():
	listen = ("127.0.0.1",8080)
	server = ThreadedHTTPServer(listen, myResponseHandeler)
	print("running")
	server.serve_forever()

if (__name__ == "__main__"):	
	run()

#post /sessions
#reqest with credentials
#422 if user already exists or bad login credentials

#Cookie
#SetCookie