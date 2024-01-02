from . import BaseTestClass
from bs4 import BeautifulSoup

class TestForoak(BaseTestClass):
    def test_gaiak_kontsultatu(self):
        res = self.client.get('/foroak')
        self.assertEqual(200, res.status_code)  # Orriak ondo funtzionatzen du bertara heltzen delako
        page = BeautifulSoup(res.data, features="html.parser")
        titles = [a.get_text(strip=True) for a in page.select('.container ul li a')]
        self.assertIn('Pasahitza ahastuta?', titles)
        self.assertIn('Nola logeatu', titles)

    def test_komentarioak_kontsultatu(self):
        gaia_id = 2
        res = self.client.get(f'/gaia?id={gaia_id}')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        komentarioak = [li.get_text(strip=True) for li in page.select('.container ul li')]
        self.assertIn('admin@gmail.com komentatu du: Sartu login atalean, ez du zailtasunik', komentarioak)
        self.assertIn('jhon@gmail.com komentatu du: Eskerrik asko!!!', komentarioak)

    def test_komentatu(self):
        self.login('james@gmail.com', '123456')
        gaia_id = 2
        komentarioa_string = "Testaren proba"
        res = self.client.post(f'/gaia?id={gaia_id}', data={'komentarioa': komentarioa_string})
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        komentario_berria = f'james@gmail.com komentatu du: {komentarioa_string}'
        self.assertIn('james@gmail.com komentatu du: Testaren proba', komentario_berria)