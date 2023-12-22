from model import Connection, Book, User
from model.Erreserbatuta import Erreserbatuta
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
		emaitza = db.select("SELECT * from Erabiltzailea WHERE MailKontua = ? AND Pasahitza = ?", (email, hash_password(password)))
		if len(emaitza) > 0:
			return User(emaitza[0][0], emaitza[0][1], emaitza[0][2], emaitza[0][3], emaitza[0][4], emaitza[0][5], emaitza[0][6])
		else:
			return None

	def get_user_cookies(self, token, time):
		emaitza = db.select("SELECT u.* from Erabiltzailea u, Session s WHERE u.MailKontua = s.user_id AND s.last_login = ? AND s.session_hash = ?", (time, token))
		if len(emaitza) > 0:
			return User(emaitza[0][0], emaitza[0][1], emaitza[0][2], emaitza[0][3], emaitza[0][4], emaitza[0][5], emaitza[0][6])
		else:
			return None

	def search_erreserbak(self, email, limit=6, page=0):
		count = db.select("""
	        SELECT COUNT (*)
	        FROM Liburu_Kopiak k
	        INNER JOIN Liburua l
	        ON k.LiburuID = l.Kodea
	        INNER JOIN Erreserbatua e
	        ON k.KopiaID = e.LiburuKopia
	        WHERE e.Erabiltzailea = ?
	        """, (email,))[0][0]
		res = db.select("""
	        SELECT e.*, v.Puntuaketa, v.Komentarioa
	        FROM Liburu_Kopiak k
	        INNER JOIN Liburua l
	        ON k.LiburuID = l.Kodea
	        INNER JOIN Erreserbatua e
	        ON k.KopiaID = e.LiburuKopia
	        LEFT JOIN Erreseina v
	        ON l.Kodea = v.Liburua AND e.Erabiltzailea = v.Erabiltzailea
	        WHERE e.Erabiltzailea = ? 
	        LIMIT ? OFFSET ?
	        """, (email, limit, limit * page))
		erreserbak = [
			Erreserbatuta(e[0], e[1], e[2], e[3], e[5], e[6])#4-ak kantzelatutaren informazioa dauka
			for e in res
		]
		liburu_info = [self.aurkituLibKopiatik(e.libId) for e in erreserbak]
		return erreserbak, liburu_info, count

	def aurkituLibKopiatik(self,kopia_id):
		res = db.select("""
		            SELECT l.Izenburua,l.Kodea,l.Portada
		            FROM Liburu_Kopiak k
		            INNER JOIN Liburua l
		            ON k.LiburuID = l.Kodea
		            WHERE k.KopiaID = ?
		            """, (kopia_id,))
		return res[0]
	def aurkituSaioaDuenErab(self):
		res = db.select("""
				SELECT s.user_id
				FROM Session s
			""")
		return res[0][0]