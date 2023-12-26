import os
import sqlite3

from . import BaseTestClass
from bs4 import BeautifulSoup


class test_erabiltzaileaSortu(BaseTestClass):

    def test_admin_user_creation(self):
        # Simulando el inicio de sesión como administrador
        self.login('admin@gmail.com', 'master')

        # Datos para el formulario de creación de usuario
        user_data = {
            'izena': 'izena',
            'abizena': 'abizena',
            'email': 'email@email.com',
            'password': 'pasahitza'
        }

        # URL de la página a la que quieres ir después del inicio de sesión
        desired_page_url = '/erabiltzaileaSortu'

        # Ir a la página deseada después de iniciar sesión
        page_response = self.client.get(desired_page_url)

        # Verificar si la página se cargó correctamente después de iniciar sesión
        self.assertEqual(200, page_response.status_code)

        # Crear un usuario después de ir a la página deseada
        create_user_response = self.client.post(desired_page_url, data=user_data)

        # Verificar si la creación de usuario fue exitosa
        self.assertEqual(200, create_user_response.status_code)

        fitx_izen = os.path.dirname(__file__)
        db_path = os.path.join(fitx_izen, "..", "datos.db")  # Guraso direktoriaren helbidea behar da, bestela ez da aurkitzen

        con = sqlite3.connect(db_path)
        cur = con.cursor()

        # Ejecutar una consulta para verificar la existencia de la nueva persona
        cur.execute("SELECT * FROM Erabiltzailea WHERE MailKontua = 'email@email.com'")
        user = cur.fetchone()

        # Cerrar la conexión
        cur.close()

        # Verificar si se encontró la nueva persona en la base de datos
        if user is not None:
            print("La nueva persona ha sido añadida a la base de datos")
        else:
            print("La nueva persona no se encontró en la base de datos")
