from .Connection import Connection
from .Gaia import Gaia

db = Connection()

class Foroak:
    def __init__(self, id, title, description, created_at):
        self.id = id
        self.title = title
        self.description = description
        self.created_at = created_at

    def __str__(self):
        return f"{self.title}"

    def get_gaiak(self):
        """
        Obtiene todos los temas asociados a este foro.
        """
        rows = db.select("SELECT * FROM Gaia WHERE foroak_id=?", (self.id,))
        return [Gaia(*row) for row in rows]
