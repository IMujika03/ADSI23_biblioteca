
from .Connection import Connection

db = Connection()

class Erreseina:
    def __init__(self,puntuazioa, deskribapena):
        self.punt = puntuazioa
        self.desk = deskribapena

    def __str__(self):
        return f"{self.punt} ({self.desk})"