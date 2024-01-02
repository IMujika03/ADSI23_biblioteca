from . import BaseTestClass
from bs4 import BeautifulSoup

class TestForoak(BaseTestClass):
    def test_gaiak_kontsultatu(self):
        res = self.client.get('/foroak')
        self.assertEqual(200, res.status_code)  # Orriak ondo funtzionatzen du bertara heltzen delako
        page = BeautifulSoup(res.data, features="html.parser")

    def test_komentarioak_kontsultatu(self):
        gaia_id = 1
        res = self.client.get(f'/gaia?id={gaia_id}')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")

    def test_komentatu(self):
        self.login('james@gmail.com', '123456')
        gaia_id = 1
        komentarioa_string = "Testaren proba"
        res = self.client.post(f'/gaia?id={gaia_id}', data={'komentarioa': komentarioa_string})
