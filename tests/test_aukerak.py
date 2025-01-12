from . import BaseTestClass
from bs4 import BeautifulSoup

class TestAukerak(BaseTestClass):

    def test_lagun_aukera_gaitu(self):
        self.db.update(
            f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 0 WHERE MailKontua = 'james@gmail.com'")  # Aukera jarri 0-ra test-ak errepikatu ahal izateko
        self.login('james@gmail.com', '123456')#Erabiltzaile honek, berez, ez du aukera gaituta
        res = self.client.get('/aukerak')
        self.assertEqual(200, res.status_code)  # Orriak ondo funtzionatzen du bertara heltzen delako
        page = BeautifulSoup(res.data, features="html.parser")
        mezua = page.find(string='Momentu honetan ez dituzu onartzen lagunak, kontrakoa nahi baduzu, pultsatu botoia')
        self.assertEqual('Momentu honetan ez dituzu onartzen lagunak, kontrakoa nahi baduzu, pultsatu botoia', mezua)#botoia pultsatu baino lehen aukera ezgaituta zegoen
        res2 = self.client.post('/aukerak', data={'aldatu1era': 'Lagunak onartu'}) # Aukera aldatzeko botoia pulsatu
        self.assertEqual(200, res2.status_code)  # Eskakizuna ondo egin dela konprobatu
        page2 = BeautifulSoup(res2.data, features="html.parser")#orria aldatu da, beraz, aldagaia berriztu behar da
        mezua = page2.find(string='Momentu honetan lagunak onartzen dituzu, kontrakoa nahi baduzu, pultsatu botoia')# mezua aldatu dela konprobatu
        self.assertEqual('Momentu honetan lagunak onartzen dituzu, kontrakoa nahi baduzu, pultsatu botoia',
                         mezua)  # botoia pultsatu ondoren aukera gaituta dagoela ikusten da
        #Berriz exekutatzen bada test-a ez da ondo aterako, erabiltzaile honen lagunakOnartzekoAukera gaituta dagoelako orain.
        res = self.db.select(f"SELECT lagunakOnartzekoAukera FROM Erabiltzailea WHERE mailKontua='james@gmail.com'")
        self.assertEqual(1, res[0][0])#Aukera gaituta dagoela konprobatu
    def test_lagun_aukera_ezgaitu(self):
        self.db.update(
            f"UPDATE Erabiltzailea SET lagunakOnartzekoAukera = 1 WHERE MailKontua = 'jhon@gmail.com'")  # Hasierako egoerara bueltatu test-a berriro exekuta ahal izateko
        self.login('jhon@gmail.com', '123') #Erabiltzaile honek, berez, aukera gaituta du
        res = self.client.get('/aukerak')
        page = BeautifulSoup(res.data, features="html.parser")
        mezua = page.find(string='Momentu honetan lagunak onartzen dituzu, kontrakoa nahi baduzu, pultsatu botoia')
        self.assertEqual('Momentu honetan lagunak onartzen dituzu, kontrakoa nahi baduzu, pultsatu botoia',
                         mezua)#Konprobatu gaituta zegoela
        res2 = self.client.post('/aukerak', data={'aldatu0ra': 'Lagunak ez onartu'})  # Aukera aldatzeko botoia pulsatu
        page2 = BeautifulSoup(res2.data, features="html.parser")  # orria aldatu da, beraz, aldagaia berriztu behar da
        mezua = page2.find(string='Momentu honetan ez dituzu onartzen lagunak, kontrakoa nahi baduzu, pultsatu botoia')
        self.assertEqual('Momentu honetan ez dituzu onartzen lagunak, kontrakoa nahi baduzu, pultsatu botoia', mezua)#Botoia pultsatu ondoren, lagunak ez dituela onartzen agertzen da
        res = self.db.select(f"SELECT lagunakOnartzekoAukera FROM Erabiltzailea WHERE mailKontua='jhon@gmail.com'")
        self.assertEqual(0, res[0][0])  # Aukera ez dagoela gaituta konprobatu
