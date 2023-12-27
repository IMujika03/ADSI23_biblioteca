from model import Connection, Book
from model.Erabiltzailea import Erabiltzailea
from model.Erreserbatuta import Erreserbatuta
from model.tools import hash_password
import datetime

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

    def lortu_liburu_guztiak(self):
        res = db.select("SELECT l.* FROM Liburua l")
        books = [
            Book(b[0], b[1], b[2], b[3], b[4])
            for b in res
        ]
        return books

    def get_related_books_by_author(self, book_id, limit=3):

        # Obtener el autor del libro actual
        current_book = self.aurkitu_liburua(book_id)
        author = current_book.author if current_book else None
        print(f"{author}")
        if author:
            # Obtener libros del mismo autor (excluyendo el libro actual)
            related_books = [book for book in self.lortu_liburu_guztiak() if
                             book.author == author and str(book.id) != (book_id)]

            # Limitar la cantidad de libros relacionados
            return related_books[:limit]

        return []

    def erabilgarri_dago(self, book_id):
        try:
            lib_kopiak = db.select("SELECT KopiaID FROM Liburu_Kopiak WHERE LiburuID = ?", (book_id,))
            for kopia in lib_kopiak:
                kopia_id = kopia[0]
                info_erreserba = db.select(
                    "SELECT * FROM Erreserbatua WHERE LiburuKopia = ? AND (EntregatzeData IS NULL AND Kantzelatuta = 0)",
                    (kopia_id,))
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
                "SELECT * FROM Liburu_Kopiak WHERE LiburuID = ? AND KopiaID NOT IN (SELECT LiburuKopia FROM Erreserbatua WHERE Kantzelatuta = 0 AND EntregatzeData IS NULL) LIMIT 1",
                (book_id,))
            if not kopia_erabilgarria:
                return False  # No se encontró una copia disponible

            id_libKopia = kopia_erabilgarria[0][0]

            # Realizar la reserva en la base de datos
            # current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            print(f"hau da kontua: {mailKontua}")
            db.insert(
                "INSERT INTO Erreserbatua (Erabiltzailea, Data1, LiburuKopia, EntregatzeData, Kantzelatuta) VALUES (?, CURRENT_DATE, ?, NULL, 0)",
                (mailKontua, id_libKopia), )
            print(f"erreserba ondo eginda: {kopia_erabilgarria}")
            return True  # Reserva exitosa

        except Exception as e:
            print(f"Errorea liburua erreserbatzean: {e}")
            return False  # Error durante la reserva

    def get_user(self, email, password):
        emaitza = db.select("SELECT * from Erabiltzailea WHERE MailKontua = ? AND Pasahitza = ?",
                            (email, hash_password(password)))
        if len(emaitza) > 0:
            return Erabiltzailea(emaitza[0][0], emaitza[0][1], emaitza[0][2], emaitza[0][3], emaitza[0][4], emaitza[0][5],
                        emaitza[0][6])
        else:
            return None

    def get_user_cookies(self, token, time):
        emaitza = db.select(
            "SELECT u.* from Erabiltzailea u, Session s WHERE u.MailKontua = s.user_id AND s.last_login = ? AND s.session_hash = ?",
            (time, token))
        if len(emaitza) > 0:
            return Erabiltzailea(emaitza[0][0], emaitza[0][1], emaitza[0][2], emaitza[0][3], emaitza[0][4], emaitza[0][5],
                        emaitza[0][6])
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
            Erreserbatuta(e[0], e[1], e[2], e[3], e[5], e[6])  # 4-ak kantzelatutaren informazioa dauka
            for e in res
        ]
        liburu_info = [self.aurkituLibKopiatik(e.libId) for e in erreserbak]
        return erreserbak, liburu_info, count

    def aurkituLibKopiatik(self, kopia_id):
        res = db.select("""
                    SELECT l.Izenburua,l.Kodea,l.Portada
                    FROM Liburu_Kopiak k
                    INNER JOIN Liburua l
                    ON k.LiburuID = l.Kodea
                    WHERE k.KopiaID = ?
                    """, (kopia_id,))
        return res[0]

    def lagunakAukera(self, email):
        res = db.select("""
                SELECT e.lagunakOnartzekoAukera
                FROM Erabiltzailea e
                WHERE MailKontua = ? 
                """, (email,))
        return res[0][0]

    def aldatu1era(self, email):

        db.update("UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = ?", (email,))

    def aldatu0ra(self, email):

        db.update("UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 0 WHERE MailKontua = ?", (email,))

    def lagunPosibleakLortu(self, email):
        res = db.select("""
            SELECT e.MailKontua
            FROM Erabiltzailea e
            WHERE e.lagunakOnartzekoAukera LIKE 1
            AND e.MailKontua != ? -- Excluye el propio correo
            AND e.MailKontua NOT IN (
                SELECT l.Erabiltzailea1
                FROM lagunEgin l
                WHERE l.Erabiltzailea2 = ?
                AND l.Egoera IN (0, 1) -- Excluye los rechazados y los aceptados
                UNION
                SELECT l.Erabiltzailea2
                FROM lagunEgin l
                WHERE l.Erabiltzailea1 = ?
                AND l.Egoera IN (0, 1) -- Excluye los rechazados y los aceptados
            )
        """, (email, email, email))
        return res

    def onartu(self, email1, email2):
        res = db.insert("INSERT INTO LagunEgin VALUES (?,?,1)", (email1, email2))

    def ezeztatu(self, email1, email2):
        res = db.insert("INSERT INTO LagunEgin VALUES (?,?,0)", (email1, email2))

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
