import os
import sqlite3

from . import BaseTestClass
from bs4 import BeautifulSoup

class test_erabiltzaileaEzabatu(BaseTestClass):

    def test_erabiltzaileaEzabatu(self):
        # Fitxategi izenaren lerroan dagoen karpeta helbidea hartu
        fitx_izen = os.path.dirname(__file__)
        db_path = os.path.join(fitx_izen, "..",
                               "datos.db")  # Guraso direktoriaren helbidea behar da, bestela ez da aurkitzen

        # Konexioa sortu datu-basearekin
        con = sqlite3.connect(db_path)
        cur = con.cursor()

        # Erabiltzailea sortu
        cur.execute("INSERT INTO Erabiltzailea(MailKontua) VALUES ('email@email.com')")
        con.commit()

        # Erabiltzailea bilatu
        cur.execute("SELECT * FROM Erabiltzailea WHERE MailKontua = 'email@email.com'")
        user = cur.fetchone()

        # Erabiltzailea existitzen da
        self.assertNotEqual(None, user)

        # Administratzaile bezala saioa hasi
        self.login('admin@gmail.com', 'master')

        # Erabiltzailea sortzeko formularioaren datuak
        user_data = {
            'email': 'email@email.com',
        }

        # Saioa hasita, helbide horretara joan
        desired_page_url = '/erabiltzaileaEzabatu'
        page_response = self.client.get(desired_page_url)

        # Saioa hasita orri hau ondo kargatu duela egiaztatu
        self.assertEqual(200, page_response.status_code)

        # Erabiltzailea sortu orri horretan joan ondoren
        create_user_response = self.client.post(desired_page_url, data=user_data)

        # Erabiltzailea ondo sortu dela egiaztatu
        self.assertEqual(302, create_user_response.status_code)
        self.assertEqual(create_user_response.headers.get('Location'), '/catalogue')

        # Datu-basean erabiltzaile berria bilatu
        cur.execute("SELECT * FROM Erabiltzailea WHERE MailKontua = 'email@email.com'")
        user = cur.fetchone()

        # Erabiltzailea sortu da
        self.assertEqual(None, user)

        # Berriro ezabatzen saiatu
        page_response = self.client.get(desired_page_url)
        self.assertEqual(200, page_response.status_code)

        # Existitzen ez den erabiltzailea ezabatu
        create_user_response = self.client.post(desired_page_url, data=user_data)
        self.assertEqual(200, create_user_response.status_code)

        # Konexioa itxi
        cur.close()
