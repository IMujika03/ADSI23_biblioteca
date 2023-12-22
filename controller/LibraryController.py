from model import Connection, Book, User
from model.tools import hash_password

db = Connection()

class LibraryController:
	__instance = None

	def __new__(cls):
		if cls.__instance is None:
			cls.__instance = super(LibraryController, cls).__new__(cls)
			cls.__instance.__initialized = False
		return cls.__instance



	def search_books(self, title="", author="", limit=6, page=0):
		count = db.select("""
				SELECT count() 
				FROM Liburua l
				WHERE l.Izenburua LIKE ? 
					AND l.Egilea LIKE ? 
		""", (f"%{title}%", f"%{author}%"))[0][0]
		res = db.select("""
				SELECT l.* 
				FROM Liburua l 
				WHERE l.Izenburua LIKE ? 
					AND l.Egilea LIKE ? 
				LIMIT ? OFFSET ?
		""", (f"%{title}%", f"%{author}%", limit, limit*page))
		books = [
			Book(b[0],b[1],b[2],b[3],b[4])
			for b in res
		]
		return books, count

	def get_user(self, email, password):
		user = db.select("SELECT * from Erabiltzailea WHERE MailKontua = ? AND Pasahitza = ?", (email, hash_password(password)))
		if len(user) > 0:
			return User(user[0][0], user[0][2]+" "+user[0][3])
		else:
			return None

	def get_user_cookies(self, token, time):
		user = db.select("SELECT u.* from Erabiltzailea u, Session s WHERE u.MailKontua = s.user_id AND s.last_login = ? AND s.session_hash = ?", (time, token))
		if len(user) > 0:
			return User(user[0][0], user[0][2]+" "+user[0][3])
		else:
			return None