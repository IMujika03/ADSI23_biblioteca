import os
import sqlite3

from . import BaseTestClass
from bs4 import BeautifulSoup

class test_erabiltzaileaSortu(BaseTestClass):

    def test_erabiltzaileaSortu(self):
        # Fitxategi izenaren lerroan dagoen karpeta helbidea hartu
        fitx_izen = os.path.dirname(__file__)
        db_path = os.path.join(fitx_izen, "..",
                               "datos.db")  # Guraso direktoriaren helbidea behar da, bestela ez da aurkitzen

        # Konexioa sortu datu-basearekin
        con = sqlite3.connect(db_path)
        cur = con.cursor()

        # Erabiltzailea bilatu
        cur.execute("SELECT * FROM Erabiltzailea WHERE MailKontua = 'email@email.com'")
        user = cur.fetchone()

        # Erabiltzailea ez da existitzen
        self.assertEqual(None, user)

        # Administratzaile bezala saioa hasi
        self.login('admin@gmail.com', 'master')

        # Erabiltzailea sortzeko formularioaren datuak
        user_data = {
            'izena': 'izena',
            'abizena': 'abizena',
            'email': 'email@email.com',
            'password': 'pasahitza'
        }

        # Saioa hasita, helbide horretara joan
        desired_page_url = '/erabiltzaileaSortu'
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
        self.assertNotEqual(None, user)

        # Berriro sortzen saiatu
        page_response = self.client.get(desired_page_url)
        self.assertEqual(200, page_response.status_code)

        # Erabiltzailea berriro ez sortu dela egiaztatu
        create_user_response = self.client.post(desired_page_url, data=user_data)
        self.assertEqual(302, create_user_response.status_code)
        self.assertEqual(create_user_response.headers.get('Location'), '/erabiltzaileaSortu')

        # Erabiltzailea ezabatu
        cur.execute("DELETE FROM Erabiltzailea WHERE MailKontua = 'email@email.com'")
        con.commit()

        # Erabiltzailea ondo ezabatu dela egiaztatu
        cur.execute("SELECT * FROM Erabiltzailea WHERE MailKontua = 'email@email.com'")
        user = cur.fetchone()
        self.assertEqual(None, user)

        # Konexioa itxi
        cur.close()
