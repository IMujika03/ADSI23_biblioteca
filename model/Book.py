from .Connection import Connection
from .Author import Author

db = Connection()

class Book:
	def __init__(self, kode, izenburu, egile, portada, deskribapen):
		self.id = kode
		self.title = izenburu
		self.author = egile
		self.cover = portada
		self.description = deskribapen

	def __str__(self):
		return f"{self.title} ({self.author})"