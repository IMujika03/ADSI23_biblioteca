import datetime
import hashlib

from .Connection import Connection
from .tools import hash_password

db = Connection()


class Session:
    def __init__(self, hash, time):
        self.hash = hash
        self.time = time

    def __str__(self):
        return f"{self.hash} ({self.time})"


class Erabiltzailea:
    def __init__(self, MailKontua, SortzaileMailKontua, Izena, Abizena, Pasahitza, Rola, lagunakOnartzekoAukera):
        self.MailKontua = MailKontua
        self.SortzaileMailKontua = SortzaileMailKontua
        self.Izena = Izena
        self.Abizena = Abizena
        self.Pasahitza = Pasahitza
        self.Rola = Rola
        self.lagunakOnartzekoAukera = lagunakOnartzekoAukera

    def __str__(self):
        return f"{self.MailKontua} ({self.Izena} {self.Abizena})"

    def new_session(self):
        now = float(datetime.datetime.now().time().strftime("%Y%m%d%H%M%S.%f"))
        session_hash = hash_password(str(self.MailKontua) + str(now))
        db.insert("INSERT INTO Session VALUES (?, ?, ?)", (session_hash, self.MailKontua, now))
        return Session(session_hash, now)

    def validate_session(self, session_hash):
        s = db.select("SELECT * from Session WHERE user_id = ? AND session_hash = ?", (self.MailKontua, session_hash))
        if len(s) > 0:
            now = float(datetime.datetime.now().strftime("%Y%m%d%H%M%S.%f"))
            session_hash_new = hash_password(str(self.MailKontua) + str(now))
            db.update("UPDATE Session SET session_hash = ?, last_login=? WHERE session_hash = ? and user_id = ?",
                      (session_hash_new, now, session_hash, self.MailKontua))
            return Session(session_hash_new, now)
        else:
            return None

    def delete_session(self, session_hash):
        db.delete("DELETE FROM Session WHERE session_hash = ? AND user_id = ?", (session_hash, self.MailKontua))

    def aldatu1era(self):
        self.lagunakOnartzekoAukera = 1
        db.update("UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = ?", (self.MailKontua,))

    def aldatu0ra(self):
        self.lagunakOnartzekoAukera = 0
        db.update("UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 0 WHERE MailKontua = ?", (self.MailKontua,))