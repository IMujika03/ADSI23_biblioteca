from . import BaseTestClass
from bs4 import BeautifulSoup

class TestEskaerak(BaseTestClass):
    def test_onartu(self):
        self.db.update(f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'james@gmail.com'")#hasieratu egoera berdinera


