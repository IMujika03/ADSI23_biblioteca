from . import BaseTestClass
from bs4 import BeautifulSoup


class test_erreseina(BaseTestClass):
    def test_erreseina_sortu(self):
        # Eliminar cualquier reseña previa del usuario 'james@gmail.com' si existe
        self.db.delete("DELETE FROM Erreseinak WHERE Erabiltzailea = ?", ('james@gmail.com',))

        # Iniciar sesión como 'james@gmail.com'
        self.login('james@gmail.com', '123456')

        # Datos para la reseña
        book_id = 1
        puntuaketa = 5
        komentarioa = "Liburu hau benetan gustatu zait!"

        # Obtener la página de detalles del libro o la página donde se crea la reseña
        res = self.client.get(f'/liburu/{book_id}/sortuErresena')
        self.assertEqual(200, res.status_code)

        # Enviar datos para crear la reseña
        res2 = self.client.post('/sortuErresena',data={'libro_id': book_id, 'puntuaketa': puntuaketa, 'komentarioa': komentarioa})
        self.assertEqual(200, res2.status_code)

        # Verificar si la reseña se ha guardado en la base de datos para 'james@gmail.com'
        res3 = self.db.select("SELECT * FROM Erreseinak WHERE Erabiltzailea = ?", ('james@gmail.com',))
        self.assertIsNotNone(res3)

        # Verificar que la reseña contiene la información correcta
        resena = res3[0] if res3 else None
        self.assertIsNotNone(resena)
        self.assertEqual(book_id, resena['Liburua'])
        self.assertEqual('james@gmail.com', resena['Erabiltzailea'])
        self.assertEqual(puntuaketa, resena['Puntuaketa'])
        self.assertEqual(komentarioa, resena['Komentarioa'])

    def test_erreseina_editatu(self):
        # Crear una reseña inicial para 'james@gmail.com' si no existe
        if not self.db.select("SELECT * FROM Erreseinak WHERE Erabiltzailea = ?", ('james@gmail.com',)):
            self.db.insert(
                "INSERT INTO Erreseinak (Liburua, Erabiltzailea, Puntuaketa, Komentarioa) VALUES (?, ?, ?, ?)",
                (1, 'james@gmail.com', 4, "Liburu hau oso ondo dago."))

        # Iniciar sesión como 'james@gmail.com'
        self.login('james@gmail.com', '123456')

        # Obtener la reseña existente de la base de datos
        aurreko_erreseina = self.db.select("SELECT * FROM Erreseinak WHERE Erabiltzailea = ?", ('james@gmail.com',))[
            0]

        # Datos actualizados para la reseña
        book_id = aurreko_erreseina['Liburua']
        puntuaketa_berria = 5
        komentarioa_berria = "Liburu hau oso ondo dago! Ikaragarria!"

        # Obtener la página para editar la reseña
        res = self.client.get(f'/editatuErresena/{book_id}')
        self.assertEqual(200, res.status_code)

        # Enviar datos actualizados para editar la reseña
        res2 = self.client.post(f'/editatuErresena/{book_id}',data={'puntuaketa': puntuaketa_berria, 'komentarioa': komentarioa_berria})
        self.assertEqual(200, res2.status_code)

        # Verificar si la reseña se ha actualizado correctamente en la base de datos

        erreseina_aktualizatuta =  self.db.select("SELECT * FROM Erreseinak WHERE Erabiltzailea = ?", ('james@gmail.com',))[0]

        # Verificar que la reseña se ha actualizado con los nuevos datos
        self.assertEqual(puntuaketa_berria, erreseina_aktualizatuta['Puntuaketa'])
        self.assertEqual(komentarioa_berria, erreseina_aktualizatuta['Komentarioa'])

    def test_erreseinak_pantailaratu(self):
        # Simular el inicio de sesión
        with self.client:
            with self.client.session_transaction() as session:
                # Simular la existencia de un usuario autenticado
                session['user'] = {'token': 'your_token_here'}

            # Realizar una solicitud GET a la página que muestra todas las reseñas
            res = self.client.get('/erreseinak_pantailaratu')

            # Verificar que la solicitud se realizó exitosamente
            self.assertEqual(200, res.status_code)

            # Verificar que la respuesta incluye las reseñas esperadas
            self.assertIn(b'<h1>Erreseinak</h1>', res.data)  # Verificar que hay un título 'Erreseinak' en la respuesta