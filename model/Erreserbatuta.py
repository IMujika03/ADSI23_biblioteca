from .Connection import Connection

db = Connection()

class Erreserbatuta:
	def __init__(self, erabiltzaile, data, liburuId, entregaData):
		self.erabiltzaile=erabiltzaile
		self.erresData =data
		self.libId = liburuId
		self.entrData = entregaData

	def __str__(self):
		return f"{self.erabiltzaile} ({self.libId})"