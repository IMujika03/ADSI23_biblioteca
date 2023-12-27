from . import BaseTestClass
from bs4 import BeautifulSoup

class TestProfila(BaseTestClass):

    def test_ikusi_erreserbak(self):
        self.login('james@gmail.com', '123456')
        res = self.client.get('/pertsonala')
        self.assertEqual(200, res.status_code) #Orriak ondo funtzionatzen du bertara heltzen delako
        page = BeautifulSoup(res.data, features="html.parser")
        title = page.select_one('h5.card-title a').getText()
        self.assertEqual('Planilandia', title)#Erabiltzaileak liburu hau erreserbaturik du
        mezua = page.find(string="Ez daude libururik erreserbaturik.")
        self.assertNotEqual('Ez daude libururik erreserbaturik.', mezua)# Ez da agertzen errore mezurik

    def test_ikusi_ez_duela_erreseinarik(self):
        self.login('james@gmail.com', '123456')
        res = self.client.get('/pertsonala')
        page = BeautifulSoup(res.data, features="html.parser")
        valoracion = page.select_one('div.valoracion').getText()
        self.assertIn('Ez da egin erreseinarik', valoracion)#Liburuak erreseinarik ez duelako errore mezua agertzen da
    def test_ikusi_erreseina(self):
        self.login('james@gmail.com', '123456')
        res = self.client.get('/pertsonala')
        page = BeautifulSoup(res.data, features="html.parser")
        valoraciones = page.select('div.valoracion')
        erreseina = valoraciones[2].getText().strip().replace('\n', '')#hutsune zuriak ezabatu, konprobazioa ondo egiteko
        self.assertEqual('Liburu ona, baina, pertsonaiak txarrak', erreseina)#Erreseinak ondo agertzen direla ikusten da
    def test_ikusi_erreserbarik_ez(self):
        self.login('ejemplo2@gmail.com', '123456')
        res2 = self.client.get('/pertsonala')
        page2 = BeautifulSoup(res2.data, features="html.parser")
        mezua = page2.find(string="Ez daude libururik erreserbaturik.")
        self.assertEqual('Ez daude libururik erreserbaturik.', mezua)#Erreserbarik ez daudelakoe errore mezua ikusten da