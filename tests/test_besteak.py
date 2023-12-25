from . import BaseTestClass
from bs4 import BeautifulSoup

class test_besteak(BaseTestClass):

    def test_admin_access(self):
        # Admin erabiltzaile bat simulatu
        self.login('admin@gmail.com', 'master')
        res = self.client.get('/besteak')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        admin_options = page.find_all('div', class_='besteak-container')  # Nagusiko edukiontzi nagusia bilatu

        # Administratzaileentzako aukera espezifikoak agertzea egiaztatu
        self.assertTrue(any("Administratzailea erabiltzaileak sortzeko aukera" in str(option) for option in admin_options))
        self.assertTrue(any("Administratzaileak erabiltzaileak ezabatzeko aukera" in str(option) for option in admin_options))
        self.assertTrue(any("Administratzaileak liburuak sartzeko aukera" in str(option) for option in admin_options))

    def test_non_admin_access(self):
        # Admin erabiltzailea ez den erabiltzaile bat simulatu
        self.login('james@gmail.com', '123456')
        res = self.client.get('/besteak')
        self.assertEqual(302, res.status_code)  # Saioa hasi behar den orrialdera bideratzen du edo beste orri batera
        # Zuzenean bideratzea zuzentasunezkoa den egiaztatu zure autorizazio logikaren arabera
