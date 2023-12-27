from . import BaseTestClass
from bs4 import BeautifulSoup

class TestEskaerak(BaseTestClass):
    def test_onartu(self):
        self.db.update(f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'james@gmail.com'")#hasieratu egoera berdinera
        self.db.update(f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'jhon@gmail.com'")
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
        res3 = self.db.select(f"SELECT Egoera FROM LagunEgin WHERE Erabiltzailea1 = 'james@gmail.com'")
        self.assertEqual(1, res3[0][0])  # 1 da, onartu delako

    def test_ezeztatu(self):
        self.db.update(
            f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'james@gmail.com'")  # hasieratu egoera berdinera
        self.db.update(f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'jhon@gmail.com'")
        self.db.delete(f"DELETE FROM LagunEgin")  # Aurretik zegoen informazioa ezabatu test-ak errepikatu ahal izateko
        self.login('james@gmail.com', '123456')
        res = self.client.get('/eskaerak')
        page = BeautifulSoup(res.data, features="html.parser")
        res2 = self.client.post('/eskaerak', data={'ezeztatu': 'ezeztatu', 'korreoa': 'jhon@gmail.com'})
        self.assertEqual(200, res2.status_code)  # Ondo egin da eskakizuna
        page2 = BeautifulSoup(res2.data, features="html.parser")  # orria aldatu da
        mezua = page2.find(string=' Ez daude erabiltzailerik lagunak izateko')
        self.assertEqual(' Ez daude erabiltzailerik lagunak izateko', mezua)  # Eskaera kendu da
        res3 = self.db.select(f"SELECT Egoera FROM LagunEgin WHERE Erabiltzailea1 = 'james@gmail.com'")
        self.assertEqual(0, res3[0][0])  # 0 da, ez delako onartu

    def test_onartu_bere_burua(self): #Hau ezin da egin web orrian, ez delako aukerarik ematen
        self.db.update(
            f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 0 WHERE MailKontua = 'james@gmail.com'")
        self.db.update(f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'jhon@gmail.com'")
        self.db.delete(f"DELETE FROM LagunEgin")
        self.login('james@gmail.com', '123456')
        res = self.client.get('/eskaerak')
        page = BeautifulSoup(res.data, features="html.parser")
        res2 = self.client.post('/eskaerak', data={'onartu': 'onartu', 'korreoa': 'james@gmail.com'})
        self.assertEqual(200, res2.status_code)  # Ondo egin da eskakizuna
        res3 = self.db.select(f"SELECT Egoera FROM LagunEgin WHERE Erabiltzailea1 = 'james@gmail.com'")
        self.assertEqual(0, res3[0][0])  # 0 da, ez delako onartu

    def test_onartu_erab_bera(self): #Ez da aukerarik ematen web orrian laguna den erabiltzaile bat berriro onartzeko, baina, test-a egindo da
        self.db.update(
            f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'james@gmail.com'")
        self.db.update(f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'jhon@gmail.com'")
        self.db.delete(f"DELETE FROM LagunEgin")
        self.login('james@gmail.com', '123456')
        self.client.post('/eskaerak', data={'onartu': 'onartu', 'korreoa': 'jhon@gmail.com'})
        res3 = self.db.select(f"SELECT Egoera FROM LagunEgin WHERE Erabiltzailea1 = 'james@gmail.com'")
        self.assertEqual(1, res3[0][0])  # 1 da, onartu delako
        self.assertEqual(1, len(res3)) #Bakarrik agertzen da behin
        self.client.post('/eskaerak', data={'onartu': 'onartu', 'korreoa': 'jhon@gmail.com'}) # Saiatu berriro onartzen
        res3 = self.db.select(f"SELECT Egoera FROM LagunEgin WHERE Erabiltzailea1 = 'james@gmail.com'")
        self.assertEqual(1, res3[0][0])  # Ez da aldatu
        self.assertEqual(1, len(res3))  # Bakarrik agertzen da behin, ez da berriro gehitu

    def test_onartzeko_erabiltzailerik_ez(self):
        self.db.update(
            f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 0 WHERE MailKontua = 'jhon@gmail.com'")
        self.db.delete(f"DELETE FROM LagunEgin")
        self.login('james@gmail.com', '123456')
        res = self.client.get('/eskaerak')
        page = BeautifulSoup(res.data, features="html.parser")
        mezua = page.find(string=' Ez daude erabiltzailerik lagunak izateko')
        self.assertEqual(' Ez daude erabiltzailerik lagunak izateko', mezua) #Errore mezua agertzen da

