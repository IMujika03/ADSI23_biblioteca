from .Connection import Connection
from .Comentario import Komentarioa

db = Connection()

class Gaia:
    def __init__(self, id, title, content, created_at):
        self.id = id
        self.title = title
        self.content = content
        self.created_at = created_at

    def __str__(self):
        return f"{self.title}"

    def get_komentarioak(self):
        """
        Obtiene todos los comentarios asociados a este tema.
        """
        rows = db.select("SELECT * FROM Komentarioa WHERE gaia_id=?", (self.id,))
        return [Komentarioa(*row) for row in rows]
