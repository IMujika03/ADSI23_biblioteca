from model import Connection, Book, Erabiltzailea
from model.Erreseina import Erreseina
from model.Erreserbatuta import Erreserbatuta
from model.Gaia import Gaia
from model.tools import hash_password
from datetime import datetime, timedelta
from dateutil.relativedelta import *

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
		""", (f"%{title}%", f"%{author}%", limit, limit * page))
        books = [
            Book(b[0], b[1], b[2], b[3], b[4])
            for b in res
        ]
        return books, count

    def aurkitu_liburua(self, book_id):
        try:
            lib = db.select("SELECT * FROM Liburua WHERE Kodea = ?", (book_id,))
            if lib:
                return Book(lib[0][0], lib[0][1], lib[0][2], lib[0][3], lib[0][4])
            else:
                return None
        except Exception as e:
            print(f"Errorea aurkitu_liburua: {e}")
            return None

 #   def lortu_liburu_guztiak(self):
  #      res = db.select("SELECT l.* FROM Liburua l")
   #     books = [
    #        Book(b[0], b[1], b[2], b[3], b[4])
     #       for b in res
      #  ]
       # return books

    def get_related_books_by_author(self, book_id, limit=3):

        # Obtener el autor del libro actual
        current_book = self.aurkitu_liburua(book_id)
        author = current_book.author if current_book else None
        print(f"{author}")
        if author:
            # Obtener libros del mismo autor (excluyendo el libro actual)
            res = db.select("SELECT l.* FROM Liburua l WHERE Egilea = ? AND Kodea != ? LIMIT 3", (author, book_id,))
            related_books = [
                Book(b[0], b[1], b[2], b[3], b[4])
                for b in res
            ]
            return related_books

        return []

    def erabilgarri_dago(self, book_id):
        try:
            lib_kopiak = db.select("SELECT KopiaID FROM Liburu_Kopiak WHERE LiburuID = ?", (book_id,))
            for kopia in lib_kopiak:
                kopia_id = kopia[0]
                info_erreserba = db.select(
                    "SELECT * FROM Erreserbatua WHERE LiburuKopia = ? AND (NoizEntregatuDa IS NULL )", (kopia_id,))
                if not info_erreserba:
                    return True
            return False
        except Exception as e:
            print(f"Errorea erabilgarri_dago: {e}")
            return False

    def erreserbatu_liburua(self, book_id, mailKontua):
        try:
            if not self.erabilgarri_dago(book_id):
                return False
            kopia_erabilgarria = db.select(
                "SELECT * FROM Liburu_Kopiak WHERE LiburuID = ? AND KopiaID NOT IN (SELECT LiburuKopia FROM Erreserbatua WHERE NoizEntregatuDa IS NULL) LIMIT 1",
                (book_id,))
            if not kopia_erabilgarria:
                return False  # No se encontró una copia disponible

            id_libKopia = kopia_erabilgarria[0][0]

            # Realizar la reserva en la base de datos
            # current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            date = datetime.now()
            # 2018-09-24 13:24:04.007620

            date2 = date + relativedelta(months=+2)
            print(date)
            print(f"hau da kontua: {mailKontua}")
            db.insert(
                "INSERT INTO Erreserbatua (Erabiltzailea, Data1, LiburuKopia, EntregatzeData) VALUES (?, ?, ?, ?)",
                (mailKontua, date.timestamp(), id_libKopia, date2.timestamp()), )
            print(f"erreserba ondo eginda: {kopia_erabilgarria}")
            return True  # Reserva exitosa

        except Exception as e:
            print(f"Errorea liburua erreserbatzean: {e}")
            return False  # Error durante la reserva

    # def lortuHistoriala(self,mailKontua,limit=6, page=0):
    def kantzelatu_erreserba(self, erabiltzaile, kopia_id):
        try:
            date = datetime.now()
            db.update(
                "UPDATE Erreserbatua SET noizEntregatuDa = ? WHERE LiburuKopia = ? AND Erabiltzailea = ? AND noizEntregatuDa IS NULL",
                (date.timestamp(), kopia_id, erabiltzaile), )
            print(f"Liburua entregatuta: {kopia_id}")
            return True
        except Exception as e:
            print(f"Errorea liburua kantzelatzean: {e}")
            return False  # Error durante la reserva

    def get_user(self, email, password):
        emaitza = db.select("SELECT * from Erabiltzailea WHERE MailKontua = ? AND Pasahitza = ?",
                            (email, hash_password(password)))
        if len(emaitza) > 0:
            return Erabiltzailea(emaitza[0][0], emaitza[0][1], emaitza[0][2], emaitza[0][3], emaitza[0][4],
                                 emaitza[0][5], emaitza[0][6])
        else:
            return None

    def get_user_cookies(self, token, time):
        emaitza = db.select(
            "SELECT u.* from Erabiltzailea u, Session s WHERE u.MailKontua = s.user_id AND s.last_login = ? AND s.session_hash = ?",
            (time, token))
        if len(emaitza) > 0:
            return Erabiltzailea(emaitza[0][0], emaitza[0][1], emaitza[0][2], emaitza[0][3], emaitza[0][4],
                                 emaitza[0][5], emaitza[0][6])
        else:
            return None

    def search_erreserbak(self, titulua, email, limit=6, page=0):
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
	        WHERE e.Erabiltzailea = ? AND l.Izenburua LIKE ?
	        LIMIT ? OFFSET ?
	        """, (email,f"%{titulua}%", limit, limit * page))
        erreserbak = [
            Erreserbatuta(e[0], e[1], e[2], e[3], e[4])
            for e in res
        ]
        erreseinak = [
            Erreseina(e[5], e[6])
            for e in res
        ]
        liburu_info = [self.aurkituLibKopiatik(e.libId) for e in erreserbak]
        return erreserbak, erreseinak, liburu_info, count

    def aurkituLibKopiatik(self, kopia_id):
        res = db.select("""
		            SELECT l.*
		            FROM Liburu_Kopiak k
		            INNER JOIN Liburua l
		            ON k.LiburuID = l.Kodea
		            WHERE k.KopiaID = ?
		            """, (kopia_id,))

        books = [
            Book(b[0], b[1], b[2], b[3], b[4])
            for b in res
        ]
        return books[0]

    def lagunPosibleakLortu(self, email):
        res = db.select("""
	        SELECT e.*
	        FROM Erabiltzailea e
	        WHERE e.lagunakOnartzekoAukera LIKE 1
	        AND e.MailKontua != ? -- Excluye el propio correo
	        AND e.MailKontua NOT IN (
	            SELECT l.Erabiltzailea1
	            FROM lagunEgin l
	            WHERE l.Erabiltzailea2 = ?
	            AND l.Egoera IN (0, 1, 2) -- Excluye los rechazados, aceptados y en espera
	            UNION
	            SELECT l.Erabiltzailea2
	            FROM lagunEgin l
	            WHERE l.Erabiltzailea1 = ?
	            AND l.Egoera IN (0, 1, 2) -- Excluye los rechazados,aceptados y en espera
	        )
	    """, (email, email, email))
        erabiltzaileak = [
            Erabiltzailea(e[0], e[1], e[2], e[3], e[4], e[5], e[6])
            for e in res
        ]
        return erabiltzaileak

    def eskaerak_lortu(self, email):
        res = db.select("""SELECT Erabiltzailea.*
            FROM LagunEgin 
            JOIN Erabiltzailea ON LagunEgin.Erabiltzailea1 = Erabiltzailea.MailKontua
            WHERE LagunEgin.Erabiltzailea2 = ? 
            AND LagunEgin.Egoera = 2
        """, (email,))
        erabiltzaileak = [
            Erabiltzailea(e[0], e[1], e[2], e[3], e[4], e[5], e[6])
            for e in res
        ]
        return erabiltzaileak

    def bidali(self, email1, email2):
        baldintza = db.select(
            "SELECT COUNT(*) FROM LagunEgin WHERE (Erabiltzailea1 = ? AND Erabiltzailea2 = ?) OR (Erabiltzailea1 = ? AND Erabiltzailea2 = ?)",
            (email1, email2, email2, email1))
        if baldintza[0][0] == 0:
            res = db.insert("INSERT INTO LagunEgin VALUES (?,?,2)", (email1, email2))

    def onartu(self, email1, email2):
        if email1 != email2:
            count = db.select(
                "SELECT COUNT(*) FROM LagunEgin WHERE (((Erabiltzailea1 = ? AND Erabiltzailea2 = ?) OR (Erabiltzailea1 = ? AND Erabiltzailea2 = ?)) AND Egoera = 1)",
                (email1, email2, email2, email1))  # Konprobatu erabiltzaileak ez direla lagunak jada
            if count[0][0] == 0:  # O bada, ez dira inoiz onartu lagun bezala
                res = db.update("UPDATE LagunEgin SET Egoera = 1 WHERE (Erabiltzailea1 = ? AND Erabiltzailea2 = ?) OR (Erabiltzailea1 = ? AND Erabiltzailea2 = ?) AND Egoera = 2", (email1, email2, email2, email1))
        else:
            self.ezeztatu(email1, email2)  # Ezeztatzen da ez agertzeko berriz

    def ezeztatu(self, email1, email2):
        res = db.update(
            "UPDATE LagunEgin SET Egoera = 0 WHERE (Erabiltzailea1 = ? AND Erabiltzailea2 = ?) OR (Erabiltzailea1 = ? AND Erabiltzailea2 = ?) AND Egoera = 2",
            (email1, email2, email2, email1))

    def get_all_topics(self):
        try:
            res = db.select(""" SELECT * FROM Gaia """)
            topics = [
                Gaia(t[0], t[1], t[2], t[3], t[4])
                for t in res
            ]
            return topics
        except Exception as e:
            print(f"Errorea get_all_topics: {e}")
            return []

    def get_topic_by_id(self, topic_id):
        try:
            res = db.select("SELECT * FROM Gaia WHERE ID = ?", (topic_id,))
            if res:
                return Gaia(res[0][0], res[0][1], res[0][2], res[0][3], res[0][4])
            else:
                return None
        except Exception as e:
            print(f"Errorea get_topic_by_id: {e}")
            return None

    def create_topic(self, izenburua, deskribapena, MailKontua):
        try:
            date = datetime.now()
            db.insert("""
                   INSERT INTO Gaia (Izenburua, Mezua, MailKontua, Data)
                   VALUES (?, ?, ?, ?)
               """, (izenburua, deskribapena, MailKontua, date.timestamp()))

            # Recuperar y devolver el objeto Gaia recién creado
            res = db.select("SELECT * FROM Gaia WHERE Izenburua = ?", (izenburua,))
            if res:
                return Gaia(res[0][0], res[0][1], res[0][2], res[0][3], res[0][4])
            else:
                return None
        except Exception as e:
            print(f"Errorea create_topic: {e}")
            return None

    def get_comments_for_topic(self, topic):
        try:
            res = db.select("""
                    SELECT k.*, u.MailKontua
                    FROM Komentarioa k
                    INNER JOIN Erabiltzailea u ON k.MailKontua = u.MailKontua
                    WHERE k.GaiIzenburu = ?
                """, (topic.title,))
            comments = [
                {
                    'id': comment[0],
                    'user': comment[1],  # Cambiado para mostrar la cuenta de correo
                    'text': comment[4]
                }
                for comment in res
            ]
            return comments
        except Exception as e:
            print(f"Errorea get_comments_for_topic: {e}")
            return []

    def komentarioaGehitu(self, MailKontua, GaiIzenburu, ErantzunKomentarioa, Testua):
        db.insert("INSERT INTO Komentarioa (MailKontua, GaiIzenburu, ErantzunKomentarioa, Testua) VALUES (?, ?, ?, ?)", (MailKontua, GaiIzenburu, ErantzunKomentarioa, Testua))

    def existitzenEzBadaSortu(self, MailKontua, SortzaileMailKontua, Izena, Abizena, Pasahitza, Rola,
                              lagunakOnartzekoAukera):
        s = db.select("SELECT * from Erabiltzailea WHERE MailKontua = ?", (MailKontua,))
        if len(s) <= 0:
            erab = Erabiltzailea(MailKontua, SortzaileMailKontua, Izena, Abizena, Pasahitza, Rola,
                                 lagunakOnartzekoAukera)
            self.erabiltzaileaGehitu(erab)
            return True
        else:
            return False

    def erabiltzaileaGehitu(self, erab):
        print(erab.MailKontua, erab.SortzaileMailKontua, erab.Izena, erab.Abizena, hash_password(erab.Pasahitza),
              erab.Rola, erab.lagunakOnartzekoAukera)
        db.insert("INSERT INTO Erabiltzailea VALUES (?, ?, ?, ?, ?, ?, ?)", (
            erab.MailKontua, erab.SortzaileMailKontua, erab.Izena, erab.Abizena, hash_password(erab.Pasahitza),
            erab.Rola, erab.lagunakOnartzekoAukera))

    def existitzenBadaEzabatu(self, MailKontua):
        s = db.select("SELECT * from Erabiltzailea WHERE MailKontua = ?", (MailKontua,))
        if len(s) > 0:
            erab = Erabiltzailea(MailKontua, None, None, None, None, None, None)
            self.erabiltzaileaEzabatu(erab)
            return True
        else:
            return False

    def erabiltzaileaEzabatu(self, erab):
        print(erab.MailKontua, erab.SortzaileMailKontua, erab.Izena, erab.Abizena, erab.Pasahitza,
              erab.Rola, erab.lagunakOnartzekoAukera)
        db.delete("DELETE FROM Erabiltzailea WHERE MailKontua = ?", (erab.MailKontua,))

    def existitzenEzBadaLiburuaSortu(self, izenburua, egilea, irudia, deskribapena):
        s = db.select(
            "SELECT Kodea from Liburua WHERE Izenburua = ? AND Egilea = ? AND Portada = ? AND Deskribapena = ?",
            (izenburua, egilea, irudia, deskribapena))
        if len(s) <= 0:
            lib = Book(None, izenburua, egilea, irudia, deskribapena)
            self.liburuaGehitu(lib)
            return True
        else:
            lib = Book(None, izenburua, egilea, irudia, deskribapena)
            self.liburuaKopiaGehitu(s[0][0], self.liburuaGehitu(lib))
            return False

    def liburuaGehitu(self, lib):
        db.insert("INSERT INTO Liburua (Izenburua, Egilea, Portada, Deskribapena) VALUES (?, ?, ?, ?)",
                  (lib.title, lib.author, lib.cover, lib.description))
        s = db.select("SELECT MAX(Kodea) as last_id FROM Liburua")
        return s[0][0]

    def liburuaKopiaGehitu(self, id1, id2):
        db.insert("INSERT INTO Liburu_Kopiak VALUES (?, ?)",
                  (id2, id1))

    def getErreseinak(self, book_title):
        try:
            res = db.select("""
                    SELECT e.*, u.MailKontua
                    FROM Erreseina e
                    INNER JOIN Erabiltzailea u ON e.Erabiltzailea = u.MailKontua
                    WHERE e.Liburua = ?
                """, (book_title,))
            erreseinak = [
                {
                    'id': review[0],
                    'user': review[1],  # Cambiado para mostrar la cuenta de correo
                    'puntuaketa': review[2],
                    'komentarioa': review[3]
                }
                for review in res
            ]
            return erreseinak
        except Exception as e:
            print(f"Errorea getErreseinak: {e}")
            return []

    def sortu_erreseina(self, komentarioa, puntuaketa, MailKontua, Liburua):
        try:
            date = datetime.now()
            # Suponiendo que tienes acceso a tu base de datos para realizar la inserción
            # Aquí insertarías los datos de la reseña en la base de datos
            db.insert("""
                INSERT INTO Erreseina (Komentarioa, Puntuaketa, Erabiltzailea, Liburua, Data)
                VALUES (?, ?, ?, ?, ?)
                """, (komentarioa, puntuaketa, MailKontua, Liburua, date.timestamp()))

            # Opcional: Recuperar y devolver el objeto Erreseina recién creado
            res = db.select(
                "SELECT * FROM Erreseina WHERE Komentarioa = ? AND Puntuaketa = ? AND Erabiltzailea = ? AND Liburua = ?",
                (komentarioa, puntuaketa, MailKontua, Liburua))
            if res:
                # Suponiendo que Erreseina es una clase con atributos correspondientes
                return Erreseina(res[0][0], res[0][1], res[0][2], res[0][3], res[0][4])
            else:
                return None
        except Exception as e:
            print(f"Errorea sortu_erreseina: {e}")
            return None