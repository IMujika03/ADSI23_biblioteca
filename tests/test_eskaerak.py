from . import BaseTestClass
from bs4 import BeautifulSoup

class TestEskaerak(BaseTestClass):

    def test_adiskidetasuna_eskatu(self):
        self.db.update(
            f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'james@gmail.com'")  # hasieratu egoera berdinera
        self.db.update(f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'jhon@gmail.com'")
        self.db.delete(f"DELETE FROM LagunEgin")  # Aurretik zegoen informazioa ezabatu test-ak errepikatu ahal izateko
        self.login('james@gmail.com', '123456')
        res = self.client.get('/eskaerak')
        page = BeautifulSoup(res.data, features="html.parser")
        erabiltzailea = page.select_one('h6').getText()
        self.assertEqual('jhon@gmail.com', erabiltzailea)  # Berez, lagunakOnartzekoAukera gaituta duen bakarra
        res2 = self.client.post('/eskaerak', data={'bidali': 'bidali', 'korreoa': 'jhon@gmail.com'})
        self.assertEqual(200, res2.status_code)#Ondo bidali da
        page = BeautifulSoup(res2.data, features="html.parser") #orria aldatu da
        mezua = page.find(string=' Ez daude erabiltzailerik eskakizunak bidaltzeko')
        self.assertEqual(' Ez daude erabiltzailerik eskakizunak bidaltzeko', mezua)# Eskakizuna desagertu da
        res3 = self.db.select(f"SELECT Egoera FROM LagunEgin WHERE Erabiltzailea1 = 'james@gmail.com'")
        self.assertEqual(2, res3[0][0])  # 2 da, itxaroten dagoelako
        self.client.get('/logout')#aurreko saioa itxi
        self.login('jhon@gmail.com', '123')
        res4 = self.client.get('/eskaerak')
        page2 = BeautifulSoup(res4.data, features="html.parser")
        erabiltzailea = page2.select_one('h6').getText()
        self.assertEqual('james@gmail.com', erabiltzailea) #Jasotako eskakizuna agertzen da

    def test_onartu(self):
        self.db.update(f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'james@gmail.com'")#hasieratu egoera berdinera
        self.db.update(f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'jhon@gmail.com'")
        self.db.delete(f"DELETE FROM LagunEgin")#Aurretik zegoen informazioa ezabatu test-ak errepikatu ahal izateko
        self.login('james@gmail.com', '123456')
        res = self.client.get('/eskaerak')
        self.assertEqual(200, res.status_code)  # Orriak ondo funtzionatzen du bertara heltzen delako
        self.client.post('/eskaerak', data={'bidali': 'bidali', 'korreoa': 'jhon@gmail.com'}) #Bidali eskakizuna
        self.client.get('/logout')  # aurreko saioa itxi
        self.login('jhon@gmail.com', '123')
        self.client.get('/eskaerak')
        res2 = self.client.post('/eskaerak', data={'onartu': 'onartu', 'korreoa2': 'james@gmail.com'})
        page2 = BeautifulSoup(res2.data, features="html.parser")
        mezua = page2.find(string=' Ez dira eskakizunik jaso')
        self.assertEqual(' Ez dira eskakizunik jaso', mezua)#Eskakizuna desagertu da
        res3 = self.db.select(f"SELECT Egoera FROM LagunEgin WHERE Erabiltzailea1 = 'james@gmail.com'")
        self.assertEqual(1, res3[0][0])  # 1 da, onartu delako

    def test_ezeztatu(self):
        self.db.update(
            f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'james@gmail.com'")  # hasieratu egoera berdinera
        self.db.update(f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'jhon@gmail.com'")
        self.db.delete(f"DELETE FROM LagunEgin")  # Aurretik zegoen informazioa ezabatu test-ak errepikatu ahal izateko
        self.login('james@gmail.com', '123456')
        res = self.client.get('/eskaerak')
        self.assertEqual(200, res.status_code)  # Orriak ondo funtzionatzen du bertara heltzen delako
        self.client.post('/eskaerak', data={'bidali': 'bidali', 'korreoa': 'jhon@gmail.com'})  # Bidali eskakizuna
        self.client.get('/logout')  # aurreko saioa itxi
        self.login('jhon@gmail.com', '123')
        self.client.get('/eskaerak')
        res2 = self.client.post('/eskaerak', data={'ezeztatu': 'ezeztatu', 'korreoa2': 'james@gmail.com'})
        page2 = BeautifulSoup(res2.data, features="html.parser")
        mezua = page2.find(string=' Ez dira eskakizunik jaso')
        self.assertEqual(' Ez dira eskakizunik jaso', mezua)  # Eskakizuna desagertu da
        res3 = self.db.select(f"SELECT Egoera FROM LagunEgin WHERE Erabiltzailea1 = 'james@gmail.com'")
        self.assertEqual(0, res3[0][0])  # 0 da, ezeztatu delako

    def test_onartu_bere_burua(self): #Hau ezin da egin web orrian, ez delako aukerarik ematen
        self.db.update(
            f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'james@gmail.com'")  # hasieratu egoera berdinera
        self.db.update(f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'jhon@gmail.com'")
        self.db.delete(f"DELETE FROM LagunEgin")  # Aurretik zegoen informazioa ezabatu test-ak errepikatu ahal izateko
        self.login('james@gmail.com', '123456')
        res = self.client.get('/eskaerak')
        self.assertEqual(200, res.status_code)  # Orriak ondo funtzionatzen du bertara heltzen delako
        self.client.post('/eskaerak', data={'bidali': 'bidali', 'korreoa': 'james@gmail.com'})  # Bidali eskakizuna
        res2 = self.client.post('/eskaerak', data={'onartu': 'onartu', 'korreoa2': 'james@gmail.com'})
        page2 = BeautifulSoup(res2.data, features="html.parser")
        mezua = page2.find(string=' Ez dira eskakizunik jaso')
        self.assertEqual(' Ez dira eskakizunik jaso', mezua)  # Eskakizuna desagertu da
        res3 = self.db.select(f"SELECT Egoera FROM LagunEgin WHERE Erabiltzailea1 = 'james@gmail.com'")
        self.assertEqual(0, res3[0][0])  # 0 da, ezeztatu direlako eskakizuna berriz ez agertzeko

    def test_onartu_bi_aldiz(self): #Ez da aukerarik ematen web orrian laguna den erabiltzaile bat berriro onartzeko, baina, test-a egindo da
        self.db.update(
            f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'james@gmail.com'")  # hasieratu egoera berdinera
        self.db.update(f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'jhon@gmail.com'")
        self.db.delete(f"DELETE FROM LagunEgin")  # Aurretik zegoen informazioa ezabatu test-ak errepikatu ahal izateko
        self.login('james@gmail.com', '123456')
        res = self.client.get('/eskaerak')
        self.assertEqual(200, res.status_code)  # Orriak ondo funtzionatzen du bertara heltzen delako
        self.client.post('/eskaerak', data={'bidali': 'bidali', 'korreoa': 'jhon@gmail.com'})  # Bidali eskakizuna
        self.client.get('/logout')  # aurreko saioa itxi
        self.login('jhon@gmail.com', '123')
        self.client.get('/eskaerak')
        res2 = self.client.post('/eskaerak', data={'onartu': 'onartu', 'korreoa2': 'james@gmail.com'})
        page2 = BeautifulSoup(res2.data, features="html.parser")
        mezua = page2.find(string=' Ez dira eskakizunik jaso')
        self.assertEqual(' Ez dira eskakizunik jaso', mezua)  # Eskakizuna desagertu da
        res3 = self.db.select(f"SELECT Egoera FROM LagunEgin WHERE Erabiltzailea1 = 'james@gmail.com'")
        self.assertEqual(1, res3[0][0])  # 1 da, onartu delako
        self.client.get('/logout')  # aurreko saioa itxi
        self.login('james@gmail.com', '123456')
        res = self.client.get('/eskaerak')
        self.client.post('/eskaerak', data={'bidali': 'bidali', 'korreoa': 'jhon@gmail.com'}) #bidali berriz
        self.client.get('/logout')  # aurreko saioa itxi
        self.login('jhon@gmail.com', '123')
        self.client.get('/eskaerak')
        res2 = self.client.post('/eskaerak', data={'onartu': 'onartu', 'korreoa2': 'james@gmail.com'})
        res3 = self.db.select(f"SELECT Egoera FROM LagunEgin WHERE Erabiltzailea1 = 'james@gmail.com'")
        self.assertEqual(1, res3[0][0])  # Ez da aldatu
        self.assertEqual(1, len(res3)) #Bakarrik agertzen da behin

    def test_onartzeko_erabiltzailerik_ez(self):
        self.db.update(
            f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 0 WHERE MailKontua = 'jhon@gmail.com'")
        self.db.delete(f"DELETE FROM LagunEgin")
        self.login('james@gmail.com', '123456')
        res = self.client.get('/eskaerak')
        page = BeautifulSoup(res.data, features="html.parser")
        mezua = page.find(string=' Ez dira eskakizunik jaso')
        self.assertEqual(' Ez dira eskakizunik jaso', mezua) #Errore mezua ez badira eskakizunik jaso
        mezua = page.find(string=' Ez daude erabiltzailerik eskakizunak bidaltzeko')
        self.assertEqual(' Ez daude erabiltzailerik eskakizunak bidaltzeko', mezua)  # Errore mezua ez badaude erabiltzailerik eskakizunak bidaltzeko