from . import BaseTestClass
from bs4 import BeautifulSoup

class TestEskaerak(BaseTestClass):
    def test_onartu(self):
        self.db.update(f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'james@gmail.com'")#hasieratu egoera berdinera
        self.db.delete(f"DELETE FROM LagunEgin")#Aurretik zegoen informazioa ezabatu test-ak errepikatu ahal izateko
        self.login('james@gmail.com', '123456')
        res = self.client.get('/eskaerak')
        self.assertEqual(200, res.status_code)  # Orriak ondo funtzionatzen du bertara heltzen delako
        page = BeautifulSoup(res.data, features="html.parser")
        erabiltzailea = page.select_one('h6').getText()
        self.assertEqual('jhon@gmail.com',erabiltzailea)# Berez, lagunakOnartzekoAukera gaituta duen bakarra
        res2 = self.client.post('/eskaerak', data={'onartu': 'onartu', 'korreoa': 'jhon@gmail.com'})
        self.assertEqual(200, res2.status_code)#Ondo egin da eskakizuna
        page2 = BeautifulSoup(res2.data, features="html.parser")  # orria aldatu da
        mezua = page2.find(string=' Ez daude erabiltzailerik lagunak izateko')
        self.assertEqual(' Ez daude erabiltzailerik lagunak izateko', mezua) #Eskaera kendu da
        res3 = self.db.select(f"SELECT Erabiltzailea2 FROM LagunEgin WHERE Erabiltzailea1 = 'james@gmail.com'")
        self.assertEqual('jhon@gmail.com',res3[0][0])