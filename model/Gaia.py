from . import Erabiltzailea
from .Connection import Connection
from .Komentarioa import Komentarioa
from datetime import datetime

db = Connection()

class Gaia:
    def __init__(self, id, title, content, autor, created_at):
        self.id = id
        self.title = title
        self.content = content
        self.author = autor
        self.created_at = created_at

    def __str__(self):
        return f"{self.title}"

    @property
    def author(self):
        if type(self._author) == str:
            em = db.select("SELECT * from Erabiltzailea WHERE id=?", (self._author,))[0]
            self._author = Erabiltzailea(em[0], em[1], em[2], em[3], em[4], em[5], em[6])
        return self._author

    @author.setter
    def author(self, value):
        self._author = value

    def get_komentarioak(self):
        """
        Obtiene todos los comentarios asociados a este tema.
        """
        rows = db.select("SELECT * FROM Komentarioa WHERE gaia_id=?", (self.id,))
        return [Komentarioa(*row) for row in rows]

    def sortu_komentarioa(self, komentarioa_string):
        try:
            # Crear un nuevo comentario
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            komentarioa = Komentarioa(
                #id=None,  # Esto debería establecerse automáticamente si es un ID autoincremental
                gaia_id=self.id,
                Izenburua=self.title,  # O ajusta según cómo estés manejando los comentarios para los temas
                Mezua=komentarioa_string,
                MailKontua=self.author,
                created_at=now
            )

            # Insertar el comentario en la base de datos
            db.insert("""
                INSERT INTO Komentarioa (gaia_id, Izenburua, Mezua, MailKontua, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (komentarioa.gaia_id, komentarioa.Izenburua, komentarioa.Mezua,
                  komentarioa.MailKontua, komentarioa.created_at))

            return komentarioa
        except Exception as e:
            print(f"Errorea sortu_komentarioa: {e}")
            return None