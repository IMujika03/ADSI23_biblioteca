import hashlib
import sqlite3
import json

salt = "library"


con = sqlite3.connect("datos.db")
cur = con.cursor()


### Create tables
cur.execute("""
	CREATE TABLE Liburu_Kopiak(
		KopiaID integer primary key AUTOINCREMENT,
		LiburuID integer,
		FOREIGN KEY (LiburuID) REFERENCES Liburua(Kodea)
	)
""")

cur.execute("""
	CREATE TABLE Liburua(
		Kodea integer primary key AUTOINCREMENT,
		GehitzaileMailKontua varchar(50),
		Izenburua varchar(50),
		Egilea integer,
		Mota varchar(50),
		FOREIGN KEY(GehitzaileMailKontua) REFERENCES Erabiltzailea(MailKontua)
	)
""")

cur.execute("""
	CREATE TABLE Erabiltzailea(
		MailKontua integer primary key AUTOINCREMENT,
		SortzaileMailKontua varchar(20),
		Izena varchar(30),
		Abizena varchar(32),
		Pasahitza varchar(30),
		Rola varchar(30),
		lagunakOnartzekoAukera integer,
		FOREIGN KEY (SortzaileMailKontua) REFERENCES Erabiltzailea(MailKontua)
	)
""")

cur.execute("""
	CREATE TABLE Session(
		session_hash varchar(32) primary key,
		user_id integer,
		last_login float,
		FOREIGN KEY(user_id) REFERENCES Erabiltzailea(MailKontua)
	)
""")

cur.execute("""
	CREATE TABLE Erreseina(
		Liburua integer primary key,
		Erabiltzailea varchar primary key ,
		Puntuaketa integer,
		Komentarioa TEXT,
		FOREIGN KEY (Liburua) REFERENCES Liburua(Kodea),
		FOREIGN KEY (Erabiltzailea) REFERENCES Erabiltzailea(MailKontua)
	)
""")

cur.execute("""
	CREATE TABLE LagunEgin(
		Erabiltzailea1 varchar primary key,
		Erabiltzailea2 varchar primary key ,
		FOREIGN KEY (Erabiltzailea1) REFERENCES Erabiltzailea(MailKontua),
		FOREIGN KEY (Erabiltzailea2) REFERENCES Erabiltzailea(MailKontua)
	)
""")

cur.execute("""
	CREATE TABLE Gaia(
		Izenburua varchar primary key,
		MailKontua varchar,
		FOREIGN KEY (MailKontua) REFERENCES Erabiltzailea(MailKontua)
	)
""")

cur.execute("""
	CREATE TABLE Komentarioa(
		ID integer primary key AUTOINCREMENT,
		MailKontua varchar primary key ,
		GaiIzenburu varchar,
		ErantzunKomentarioa integer,
		Testua TEXT,
		FOREIGN KEY (MailKontua) REFERENCES Erabiltzailea(MailKontua),
		FOREIGN KEY (GaiIzenburu) REFERENCES Gaia(Izenburua),
		FOREIGN KEY (ErantzunKomentarioa) REFERENCES Komentarioa(ID)
	)
""")

cur.execute("""
	CREATE TABLE Erreserbatua(
		Erabiltzailea varchar primary key,
		Data DATE primary key ,
		LiburuKopia integer primary key ,
		EntregatzeData DATE,
		Kantzelatuta integer,
		FOREIGN KEY (Erabiltzailea) REFERENCES Erabiltzailea(MailKontua),
		FOREIGN KEY (LiburuKopia) REFERENCES Liburu_Kopiak(KopiaID)
	)
""")


### Insert users

with open('usuarios.json', 'r') as f:
	usuarios = json.load(f)['usuarios']

for user in usuarios:
	dataBase_password = user['password'] + salt
	hashed = hashlib.md5(dataBase_password.encode())
	dataBase_password = hashed.hexdigest()
	cur.execute(f"""INSERT INTO User VALUES (NULL, '{user['nombres']}', '{user['email']}', '{dataBase_password}')""")
	con.commit()


#### Insert books
with open('libros.tsv', 'r') as f:
	libros = [x.split("\t") for x in f.readlines()]

for author, title, cover, description in libros:
	res = cur.execute(f"SELECT id FROM Author WHERE name=\"{author}\"")
	if res.rowcount == -1:
		cur.execute(f"""INSERT INTO Author VALUES (NULL, \"{author}\")""")
		con.commit()
		res = cur.execute(f"SELECT id FROM Author WHERE name=\"{author}\"")
	author_id = res.fetchone()[0]

	cur.execute("INSERT INTO Book VALUES (NULL, ?, ?, ?, ?)",
		            (title, author_id, cover, description.strip()))

	con.commit()



