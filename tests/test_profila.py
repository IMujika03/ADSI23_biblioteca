from . import BaseTestClass
from bs4 import BeautifulSoup

class TestProfila(BaseTestClass):

    def test_profila_ikusi(self):
        self.login('james@gmail.com', '123456')
        res = self.client.get('/pertsonala')
        self.assertEqual(200, res.status_code) #Orriak ondo funtzionatzen du bertara heltzen delako
        page = BeautifulSoup(res.data, features="html.parser")
