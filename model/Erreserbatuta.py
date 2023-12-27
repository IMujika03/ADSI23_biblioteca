from datetime import datetime

from .Connection import Connection

db = Connection()

class Erreserbatuta:
	def __init__(self, erabiltzaile, data, liburuId, entregaData, puntuazioa, deskribapena):
		self.erabiltzaile=erabiltzaile
		self.erresData =datetime.fromtimestamp(data).strftime("%d/%m/%Y")
		self.libId = liburuId
		self.entrData = datetime.fromtimestamp(entregaData).strftime("%d/%m/%Y")
		self.punt = puntuazioa
		self.desk = deskribapena

	def __str__(self):
		return f"{self.erabiltzaile} ({self.libId})"