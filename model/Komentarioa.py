from .Connection import Connection
from .Erabiltzailea import Erabiltzailea

db = Connection()

class Komentarioa:
    def __init__(self, id, autor, title, ErantzunKomentarioa, content):
        self.id = id
        self.author = autor
        self.title = title
        self.ErantzunKomentarioa = ErantzunKomentarioa
        self.content = content

    def __str__(self):
        return f"{self.content}"

    @property
    def user(self):
        """
        Obtiene el usuario asociado a este comentario.
        """
        row = db.select("SELECT * FROM Erabiltzailea WHERE MailKontua=?", (self.author,))
        if row:
            return Erabiltzailea(*row[0])

