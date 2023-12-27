import hashlib
import os.path
import sqlite3
import json

salt = "library"
fitx_izen = os.path.dirname(__file__)
db_path = os.path.join(fitx_izen,"..","datos.db")#Guraso direktoriaren helbidea behar da, bestela ez da aurkitzen

con = sqlite3.connect(db_path)
cur = con.cursor()


tables_to_drop = [
    'Book', 'Erabiltzailea', 'Erreseina', 'Erreserbatua',
    'Gaia', 'Komentarioa', 'LagunEgin', 'Liburu_Kopiak',
    'Liburua', 'Session', 'User'
]

for table in tables_to_drop:
    cur.execute(f"DROP TABLE IF EXISTS {table};")

### Create tables
cur.execute("""
	CREATE TABLE IF NOT EXISTS Liburu_Kopiak(
		KopiaID integer primary key AUTOINCREMENT,
		LiburuID integer,
		FOREIGN KEY (LiburuID) REFERENCES Liburua(Kodea)
	)
""")

cur.execute("""
	CREATE TABLE IF NOT EXISTS Liburua(
		Kodea integer primary key AUTOINCREMENT,
		Izenburua varchar(50),
		Egilea varchar(50),
		Portada varchar(50),
		Deskribapena TEXT
	)
""")

cur.execute("""
	CREATE TABLE IF NOT EXISTS Erabiltzailea(
		MailKontua varchar(50) primary key,
		SortzaileMailKontua varchar(50),
		Izena varchar(30),
		Abizena varchar(32),
		Pasahitza varchar(30),
		Rola varchar(30),
		lagunakOnartzekoAukera integer,
		FOREIGN KEY (SortzaileMailKontua) REFERENCES Erabiltzailea(MailKontua)
	)
""")

cur.execute("""
	CREATE TABLE IF NOT EXISTS Session(
		session_hash varchar(32) primary key,
		user_id varchar(50),
		last_login float,
		FOREIGN KEY(user_id) REFERENCES Erabiltzailea(MailKontua)
	)
""")

cur.execute("""
	CREATE TABLE IF NOT EXISTS Erreseina(
		Liburua integer,
		Erabiltzailea varchar,
		Puntuaketa integer,
		Komentarioa TEXT,
		PRIMARY KEY (Liburua,Erabiltzailea),
		FOREIGN KEY (Liburua) REFERENCES Liburua(Kodea),
		FOREIGN KEY (Erabiltzailea) REFERENCES Erabiltzailea(MailKontua)
	)
""")

cur.execute("""
	CREATE TABLE IF NOT EXISTS LagunEgin(
		Erabiltzailea1 varchar,
		Erabiltzailea2 varchar,
		Egoera integer,
		PRIMARY KEY(Erabiltzailea1, Erabiltzailea2),
		FOREIGN KEY (Erabiltzailea1) REFERENCES Erabiltzailea(MailKontua),
		FOREIGN KEY (Erabiltzailea2) REFERENCES Erabiltzailea(MailKontua)
	)
""")

cur.execute("""
	CREATE TABLE IF NOT EXISTS Gaia(
		id integer PRIMARY KEY autoincrement,
		Izenburua varchar,
		Mezua varchar,
		MailKontua varchar,
		Data DATE,
		FOREIGN KEY (MailKontua) REFERENCES Erabiltzailea(MailKontua)
	)
""")

cur.execute("""
	CREATE TABLE IF NOT EXISTS Komentarioa(
		ID integer,
		MailKontua varchar,
		GaiIzenburu varchar,
		ErantzunKomentarioa integer,
		Testua TEXT,
		PRIMARY KEY (ID,MailKontua),
		FOREIGN KEY (MailKontua) REFERENCES Erabiltzailea(MailKontua),
		FOREIGN KEY (GaiIzenburu) REFERENCES Gaia(Izenburua),
		FOREIGN KEY (ErantzunKomentarioa) REFERENCES Komentarioa(ID)
	)
""")

cur.execute("""
	CREATE TABLE IF NOT EXISTS Erreserbatua(
		Erabiltzailea varchar,
		Data1 DATE,
		LiburuKopia integer,
		EntregatzeData DATE,
		NoizEntregatuDa DATE,
		PRIMARY KEY(Erabiltzailea,Data1,LiburuKopia),
		FOREIGN KEY (Erabiltzailea) REFERENCES Erabiltzailea(MailKontua),
		FOREIGN KEY (LiburuKopia) REFERENCES Liburu_Kopiak(KopiaID)
	)
""")

### Insert users
json_path = os.path.join(fitx_izen,"..","usuarios.json")
with open(json_path, 'r') as f:
	usuarios = json.load(f)['usuarios']

for user in usuarios:
	dataBase_password = user['Pasahitza'] + salt
	hashed = hashlib.md5(dataBase_password.encode())
	dataBase_password = hashed.hexdigest()
	cur.execute(f"""INSERT OR REPLACE INTO Erabiltzailea VALUES ('{user['MailKontua']}','{user['SortzaileMailKontua']}', '{user['Izena']}','{user['Abizena']}', '{dataBase_password}','{user['Rola']}',{user['lagunakOnartzekoAukera']})""")
	con.commit()

#### Insert books
libros_path = os.path.join(fitx_izen,"..","libros.tsv")
with open(libros_path, 'r',encoding='utf-8') as f:
    libros = [x.split("\t") for x in f]

cont = 0
for author, title, cover, description in libros:
	cur.execute("INSERT INTO Liburua VALUES (NULL, ?, ?, ?, ?)",(title, author, cover, description.strip()))

	copia_num = (cont%4)+1
	cur.execute(f"""INSERT OR REPLACE INTO Liburu_Kopiak VALUES (Null, {cont})""")
	cont+=1



con.commit()

###Insert kopiak
#kopiak_path = os.path.join(fitx_izen, "..", "kopiak.json")
#with open(kopiak_path, 'r') as k:
#	kopiak = json.load(k)['kopiak']
#for kopia in kopiak:
#	cur.execute(f"""INSERT OR REPLACE INTO Liburu_Kopiak VALUES ('{kopia['KopiaID']}','{kopia['LiburuID']}')""")
#con.commit()

###Insert erreserbak
erreserbak_path = os.path.join(fitx_izen, "..", "erreserbak.json")
with open(erreserbak_path, 'r') as e:
	erreserbak = json.load(e)['erreserbak']
for erreserba in erreserbak:
	cur.execute(f"""INSERT OR REPLACE INTO Erreserbatua VALUES('{erreserba['Erabiltzailea']}','{erreserba['Data1']/1000}','{erreserba['LiburuKopia']}','{erreserba['EntregatzeData']/1000}','{erreserba['EntregatzeData2']/1000}')""")
con.commit()

###Insert erreseinak
erreseinak_path = os.path.join(fitx_izen, "..", "erreseinak.json")
with open(erreseinak_path, 'r') as er:
	erreseinak = json.load(er)['erreseinak']
for erreseina in erreseinak:
	cur.execute(f"""INSERT OR REPLACE INTO Erreseina VALUES('{erreseina['Liburua']}','{erreseina['Erabiltzailea']}','{erreseina['Puntuaketa']}','{erreseina['Komentarioa']}')""")
con.commit()

###Insert gaiak
gaiak_path = os.path.join(fitx_izen, "..", "gaiak.json")
with open(gaiak_path, 'r', encoding="utf-8") as er:
	gaiak = json.load(er)['gaiak']
for gaia in gaiak:
	cur.execute(f"""INSERT OR REPLACE INTO Gaia VALUES(NULL,'{gaia['Izenburua']}','{gaia['Mezua']}','{gaia['MailKontua']}','{gaia['Data']}')""")
con.commit()


con.close()



