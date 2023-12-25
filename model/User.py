import datetime
import hashlib

from .Connection import Connection
from .tools import hash_password

db = Connection()

class Session:
	def __init__(self, hash, time):
		self.hash = hash
		self.time = time

	def __str__(self):
		return f"{self.hash} ({self.time})"

class User:
	def __init__(self, MailKontua, SortzaileMailKontua, Izena, Abizena, Pasahitza, Rola, lagunakOnartzekoAukera):
		self.MailKontua = MailKontua
		self.SortzaileMailKontua = SortzaileMailKontua
		self.Izena = Izena
		self.Abizena = Abizena
		self.Pasahitza = Pasahitza
		self.Rola = Rola
		self.lagunakOnartzekoAukera = lagunakOnartzekoAukera
	def __str__(self):
		return f"{self.MailKontua} ({self.Izena} {self.Abizena})"

	def new_session(self):
		now = float(datetime.datetime.now().time().strftime("%Y%m%d%H%M%S.%f"))
		session_hash = hash_password(str(self.MailKontua)+str(now))
		db.insert("INSERT INTO Session VALUES (?, ?, ?)", (session_hash, self.MailKontua, now))
		return Session(session_hash, now)

	def validate_session(self, session_hash):
		s = db.select("SELECT * from Session WHERE user_id = ? AND session_hash = ?", (self.MailKontua, session_hash))
		if len(s) > 0:
			now = float(datetime.datetime.now().strftime("%Y%m%d%H%M%S.%f"))
			session_hash_new = hash_password(str(self.MailKontua) + str(now))
			db.update("UPDATE Session SET session_hash = ?, last_login=? WHERE session_hash = ? and user_id = ?", (session_hash_new, now, session_hash, self.MailKontua))
			return Session(session_hash_new, now)
		else:
			return None

	def delete_session(self, session_hash):
		db.delete("DELETE FROM Session WHERE session_hash = ? AND user_id = ?", (session_hash, self.MailKontua))

	def new_user(self):
		#print(self.MailKontua + self.SortzaileMailKontua + self.Izena + self.Abizena + self.Pasahitza + self.Rola + self.lagunakOnartzekoAukera)
		s = db.select("SELECT * from Erabiltzailea WHERE MailKontua = ?", (self.MailKontua,))
		if len(s) <= 0:
			dataBase_password = self.Pasahitza + "library"
			hashed = hashlib.md5(dataBase_password.encode())
			dataBase_password = hashed.hexdigest()
			db.insert("INSERT INTO Erabiltzailea VALUES (?, ?, ?, ?, ?, ?, ?)", (self.MailKontua, self.SortzaileMailKontua, self.Izena, self.Abizena, dataBase_password, self.Rola, self.lagunakOnartzekoAukera))
			return True
		else:
			return False

	def delete_user(self):
		s = db.select("SELECT * from Erabiltzailea WHERE MailKontua = ?", (self.MailKontua,))
		if len(s) > 0:
			db.delete("DELETE FROM Erabiltzailea WHERE MailKontua = ?", (self.MailKontua,))
			return True
		else:
			return False
