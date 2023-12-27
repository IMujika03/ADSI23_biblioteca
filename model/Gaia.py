from . import Erabiltzailea
from .Connection import Connection
from .Komentarioa import Komentarioa

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
