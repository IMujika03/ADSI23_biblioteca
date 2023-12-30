from . import BaseTestClass
from bs4 import BeautifulSoup


class TestErreserbak(BaseTestClass):
    def test_erreserbatu_liburua(self):
        self.db.delete("DELETE FROM Erreserbatua WHERE Erabiltzailea = ? AND noizEntregatuDa IS NULL", ('james@gmail.com',))
        self.login('james@gmail.com', '123456')  # add assertion here
        book_id = 250
        #lib = self.db.select("SELECT Inzeburua FROM Liburua WHERE Kodea = ?", (book_id,))
        #print(lib)
        res = self.client.get('/liburuBista')
        page = BeautifulSoup(res.data, features="html.parser")
        # Egin erreserbatzea
        res2 = self.client.post('/erreserbatu', data={'libro_id': book_id})
        self.assertEqual(200, res2.status_code)#ondo bidali dela konprobatu
        #pantailaz salto egiten du mezu.html-ra eta hori kontrobatu
        page = BeautifulSoup(res2.data, features="html.parser")
        #Baita datu basean konprobatu
        res3 = self.db.select(f"SELECT * FROM Erreserbatua WHERE Erabiltzailea = ? AND noizEntregatuDa IS NULL", ('james@gmail.com',))
        self.assertIsNotNone(res3)
        #Liburu bakoitzaren kopia bakarra dagoenez erabilgarri liburu bereko beste kopia bat eskatu nahai bada ez da datu basean sartuko
        res4 = self.client.post('/erreserbatu', data={'libro_id': book_id})
        self.assertEqual(200, res4.status_code)
        res5 = self.db.select("SELECT COUNT(*) FROM Erreserbatua WHERE Erabiltzailea = ? AND LiburuKopia = ?", ('james@gmail.com', book_id))[0][0]
        self.assertEqual(1, res5)
        #Baita beste erabiltzaile batek liburu bera nahi badu ez dio utziko:
        self.client.get('/logout')  # aurreko saioa itxi
        self.login('jhon@gmail.com', '123')
        resb1 = self.client.get('/liburuBista')
        page2 = BeautifulSoup(resb1.data, features="html.parser")
        # Erreserba egin
        resb2 = self.client.post('/erreserbatu', data={'libro_id': book_id})
        self.assertEqual(200, resb2.status_code)  # ondo bidali dela konprobatu
        resb3 = self.db.select("SELECT COUNT(*) FROM Erreserbatua WHERE Erabiltzailea = ? AND LiburuKopia = ?", ('james@gmail.com', book_id))[0][0]
        self.assertEqual(1, resb3)
        resb4 = self.db.select("SELECT COUNT(*) FROM Erreserbatua WHERE Erabiltzailea = ? AND LiburuKopia = ?", ('jhon@gmail.com', book_id))[0][0]
        self.assertEqual(0, resb4)

    def test_ikusi_erreserbak(self):
        self.login('james@gmail.com', '123456')
        res = self.client.get('/pertsonala')
        self.assertEqual(200, res.status_code)  # Orriak ondo funtzionatzen du bertara heltzen delako
        page = BeautifulSoup(res.data, features="html.parser")
        title = page.select_one('h5.card-title a').getText()
        self.assertEqual('Planilandia', title)  # Erabiltzaileak liburu hau erreserbaturik du
        mezua = page.find(string="Ez daude libururik erreserbaturik.")
        self.assertNotEqual('Ez daude libururik erreserbaturik.', mezua)  # Ez da agertzen errore mezurik

    def test_ikusi_erreserbarik_ez(self):
        self.login('ejemplo2@gmail.com', '123456')
        res2 = self.client.get('/pertsonala')
        page2 = BeautifulSoup(res2.data, features="html.parser")
        mezua = page2.find(string="Ez daude libururik erreserbaturik.")
        self.assertEqual('Ez daude libururik erreserbaturik.', mezua)#Erreserbarik ez daudelakoe errore mezua ikusten da

    #def test_kantzelatu_erreserba(self):
     #   self.db.delete("DELETE FROM Erreserbatua WHERE noizEntregatuDa IS NULL")