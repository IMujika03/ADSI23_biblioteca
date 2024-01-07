import os
import sqlite3

from . import BaseTestClass
from bs4 import BeautifulSoup

class test_liburuaSartu(BaseTestClass):

    def test_liburuaSartu(self):

        # Fitxategiaren izena hartu eta guraso direktorioaren helbidea lortu datu-basearen bidea sortzeko
        fitx_izen = os.path.dirname(__file__)
        db_path = os.path.join(fitx_izen, "..", "datos.db")  # Guraso direktoriaren helbidea behar da, bestela ez da aurkitzen

        # SQLite konexioa sortu
        con = sqlite3.connect(db_path)
        cur = con.cursor()

        # Administrazile gisa saioa hasi
        self.login('admin@gmail.com', 'master')

        # Erabiltzailearen datuak
        user_data = {
            'izenburua': 'izena',
            'egilea': 'egilea',
            'irudia': 'https://shorturl.at/jxC59',
            'deskribapena': 'desk'
        }

        # Eskatutako orrialdearen URL desiratua lortu
        desired_page_url = '/liburuaSartu'
        page_response = self.client.get(desired_page_url)

        # Orrialdearen erantzuna egiaztatu
        self.assertEqual(200, page_response.status_code)

        # Liburua sortu
        create_book_response = self.client.post(desired_page_url, data=user_data)

        # Liburua ongi sortu den egiaztatu
        self.assertEqual(302, create_book_response.status_code)
        self.assertEqual(create_book_response.headers.get('Location'), '/catalogue')

        # 'izena' izeneko liburua datu-basean bilatu
        cur.execute("SELECT * FROM Liburua WHERE Izenburua = 'izena'")
        user = cur.fetchone()

        # Liburua ez dago None-en berdina
        self.assertNotEqual(None, user)

        # Konexioa itxi
        cur.close()
