import base64, os

class SessionStore:

	def __init__(self):
		self.sessions = {}

	def createSession(self):
		id =  self.generateSessionId()
		self.sessions[id] = {}
		return id

	def generateSessionId(self):
		rnum = os.urandom(32)
		rstr = base64.b64encode(rnum).decode("utf-8")
		return rstr

	def getSessionData(self, sessionId):
		if sessionId in self.sessions:
			return self.sessions[sessionId]
		return None