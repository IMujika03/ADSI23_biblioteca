from .Connection import Connection
from .Erabiltzailea import Erabiltzailea

db = Connection()

class Komentario:
    def __init__(self, id, gaia_id, user_id, content, created_at):
        self.id = id
        self.gaia_id = gaia_id
        self.user_id = user_id
        self.content = content
        self.created_at = created_at

    def __str__(self):
        return f"{self.content}"

    @property
    def user(self):
        """
        Obtiene el usuario asociado a este comentario.
        """
        row = db.select("SELECT * FROM Erabiltzailea WHERE MailKontua=?", (self.user_id,))
        if row:
            return Erabiltzailea(*row[0])

    def to_dict(self):
        """
        Devuelve una representación en forma de diccionario del comentario.
        """
        return {
            'id': self.id,
            'gaia_id': self.gaia_id,
            'user_id': self.user_id,
            'content': self.content,
            'created_at': self.created_at
        }
