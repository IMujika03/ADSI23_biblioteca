from .LibraryController import LibraryController
from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify, flash

app = Flask(__name__, static_url_path='', static_folder='../view/static', template_folder='../view/')
app.jinja_env.globals.update(zip=zip)  # Añadir esta línea
app.secret_key = 'aunicau8sdf23u4oiusdf98we'

library = LibraryController()


@app.before_request
def get_logged_user():
    if '/css' not in request.path and '/js' not in request.path:
        token = request.cookies.get('token')
        time = request.cookies.get('time')
        if token and time:
            request.user = library.get_user_cookies(token, float(time))
            if request.user:
                request.user.token = token


@app.after_request
def add_cookies(response):
    if 'user' in dir(request) and request.user and request.user.token:
        session = request.user.validate_session(request.user.token)
        response.set_cookie('token', session.hash)
        response.set_cookie('time', str(session.time))
    return response


@app.route('/')
def index():
    return render_template('index.html')


def redirectNoAdmin(url1, url2):
    if 'user' in request.__dict__ and request.user and request.user.token:
        if request.user.Rola == "admin":
            return render_template(url1)
    return redirect(url_for(url2))


@app.route('/besteak')
def besteak():
    return redirectNoAdmin("besteak.html", "login")


@app.route('/pertsonala')
def pertsonala():
    page = int(request.values.get("page", 1))
    if 'user' in request.__dict__ and request.user and request.user.token:
        email = request.user.MailKontua
        erreserbak, erreseinak, lib_info, nb_erreserbak = library.search_erreserbak(email=email, page=page - 1)
        total_pages = (nb_erreserbak // 6) + 1
        return render_template('pertsonala.html', erreserbak=erreserbak, erreseinak=erreseinak, lib_info=lib_info,
                               current_page=page,
                               total_pages=total_pages, max=max, min=min)
    else:
        return redirect('/login')  # Saioa itxi da edo zati honetara heldu da saio barik--> saioa hasi berriz


@app.route('/aukerak', methods=['GET', 'POST'])
def aukerak():
    if 'user' in request.__dict__ and request.user and request.user.token:
        if "aldatu1era" in request.values:
            request.user.aldatu1era()
        elif "aldatu0ra" in request.values:
            request.user.aldatu0ra()
        lagunAukera = request.user.lagunakOnartzekoAukera
        return render_template('aukerak.html', lagunAukera=lagunAukera)
    else:
        return redirect('/login')  # Saioa itxi da edo zati honetara heldu da saio barik--> saioa hasi berriz


@app.route('/eskaerak', methods=['GET', 'POST'])
def eskaerak():
    if 'user' in request.__dict__ and request.user and request.user.token:
        email = request.user.MailKontua
        if "onartu" in request.values:
            library.onartu(email, request.values.get("korreoa"))
        elif "ezeztatu" in request.values:
            library.ezeztatu(email, request.values.get("korreoa"))
        erabiltzaileLista = library.lagunPosibleakLortu(request.user.MailKontua)
        return render_template('eskaerak.html', erabiltzaileLista=erabiltzaileLista)
    else:
        return redirect('/login')  # Saioa itxi da edo zati honetara heldu da saio barik--> saioa hasi berriz


@app.route('/catalogue')
def catalogue():
    title = request.values.get("title", "")
    author = request.values.get("author", "")
    page = int(request.values.get("page", 1))
    books, nb_books = library.search_books(title=title, author=author, page=page - 1)
    total_pages = (nb_books // 6) + 1
    return render_template('catalogue.html', books=books, title=title, author=author, current_page=page,
                           total_pages=total_pages, max=max, min=min)


@app.route('/liburua')
def liburua():
    book_id = request.values.get("id", "")
    liburua = library.aurkitu_liburua(book_id)
    if liburua:
        print(f"Liburuaren datuak: {liburua}")
        related_books = library.get_related_books_by_author(book_id)
        return render_template('liburuBista.html', book=liburua, related_books=related_books)
    else:
        print(f" ID hau duen liburua ez da aurkitu: {book_id}")
        return render_template('mezua.html', tituloa="Errorea", mezua="Ezin izan da liburua aurkitu",
                               location='/catalogue')


@app.route('/liburua')
def liburua2():
    book_id = request.values.get("id", "")
    mail = request.user.MailKontua
    erreserba = library.aurkitu_erreserba(book_id, mail)


@app.route('/erreserbatu', methods=['POST'])
def erreserbatu_liburua():
    try:
        if 'user' not in dir(request) or not request.user or not request.user.token:
            # Erabiltzailea ez dago identifikatuta
            return redirect('/login')
        else:
            book_id = request.form.get('libro_id')  # ese libro id no se que hay que poner
            disponible = library.erabilgarri_dago(book_id)
            if disponible:
                mailKontua = request.user.MailKontua
                print(f"mail : {type(mailKontua)}")
                print(f" hau da mail kontua: {mailKontua}")
                library.erreserbatu_liburua(book_id, mailKontua)
                return render_template('mezua.html', tituloa="Erreserbatuta",
                                       mezua="Aukeratutako liburua erreserbatu da", location='/catalogue')
            # print(f"Liburua erreserbatuta!: {disponible}")
            else:
                print(f"Ezin izan da liburua erreserbatu")  # que salte un mensaje en la pantalla
                return render_template('mezua.html', tituloa="Errorea", mezua="Ezin izan da liburua erreserbatu",
                                       location='/catalogue')
    except Exception as e:
        print(f"Errorea liburua erreserbatzeko prozesuan: {e}")
        return redirect('/catalogue')


# @app.route('/historiala', methods=['POST'])
# def historiala_pantailaratu():
#	try:
#		if 'user' not in dir(request) or not request.user or not request.user.token:
#			#Erabiltzailea ez dago identifikatuta
#			return redirect('/login')
#		else:
#			mailKontua = request.user.MailKontua
#			erreserba_Lista = library.lortuHistoriala(mailKontua)
#			return render_template('historiala', historial=erreserba_Lista)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in dir(request) and request.user and request.user.token:
        return redirect('/')
    email = request.values.get("email", "")  # html-tik aterata, izen hori duten input-ak
    password = request.values.get("password", "")
    user = library.get_user(email, password)
    if user:
        session = user.new_session()
        resp = redirect("/")
        resp.set_cookie('token', session.hash)
        resp.set_cookie('time', str(session.time))
    else:
        if request.method == 'POST':
            return redirect('/login')
        else:
            resp = render_template('login.html')
    return resp


@app.route('/logout')
def logout():
    path = request.values.get("path", "/")
    resp = redirect(path)
    resp.delete_cookie('token')
    resp.delete_cookie('time')
    if 'user' in dir(request) and request.user and request.user.token:
        request.user.delete_session(request.user.token)
        request.user = None
    return resp


@app.route('/erabiltzaileaSortu', methods=['GET', 'POST'])
def erabiltzaileaSortu():
    if request.method == 'POST':
        MailKontua = request.form.get("email")
        SortzaileMailKontua = request.user.MailKontua
        Izena = request.form.get("izena")
        Abizena = request.form.get("abizena")
        Pasahitza = request.form.get("password")
        Rola = "erab"
        lagunakOnartzekoAukera = "0"

        if library.existitzenEzBadaSortu(MailKontua, SortzaileMailKontua, Izena, Abizena, Pasahitza, Rola,
                                         lagunakOnartzekoAukera):
            return redirect(url_for('catalogue'))
        else:
            flash('Errore bat egon da. Ziur zaude erabiltzaile hori existitzen ez dela?', 'error')
            return redirect(url_for('erabiltzaileaSortu'))

    # Si no es un método POST o si hay algún error, mostrar el formulario erabiltzaileaSortu.html
    return redirectNoAdmin("erabiltzaileaSortu.html", "login")


@app.route('/erabiltzaileaEzabatu', methods=['GET', 'POST'])
def erabiltzaileaEzabatu():
    if request.method == 'POST':
        MailKontua = request.form.get("email")

        if library.existitzenBadaEzabatu(MailKontua):
            return redirect(url_for('catalogue'))
        else:
            flash('Errore bat egon da. Ziur zaude erabiltzaile hori existitzen dela?', 'error')
            return redirectNoAdmin("erabiltzaileaEzabatu.html", "login")

    # Si no es un método POST o si hay algún error, mostrar el formulario erabiltzaileaSortu.html
    return redirectNoAdmin("erabiltzaileaEzabatu.html", "login")


@app.route('/liburuaSartu', methods=['GET', 'POST'])
def liburuaSartu():
    if request.method == 'POST':
        izenburua = request.form.get("izenburua")
        egilea = request.form.get("egilea")
        irudia = request.form.get("irudia")
        deskribapena = request.form.get("deskribapena")

        if library.existitzenEzBadaLiburuaSortu(izenburua, egilea, irudia, deskribapena):
            return redirect(url_for('catalogue'))
        else:
            flash('Errore bat egon da. Ziur zaude liburu hori existitzen ez dela?', 'error')
            return redirectNoAdmin("liburuaSartu.html", "login")

    # Si no es un método POST , mostrar el formulario erabiltzaileaSortu.html
    return redirectNoAdmin("liburuaSartu.html", "login")


@app.route('/foroak', methods=['GET', 'POST'])
def foroak():
    if 'user' in request.__dict__ and request.user and request.user.token:
        topics = library.get_all_topics()
        return render_template('foroak.html', Gaiak=topics)
    else:
        return redirect('/login')


@app.route('/gaia', methods=['GET', 'POST'])
def gaia():
    gaia_id = request.values.get("id", -1)
    gaia = library.get_topic_by_id(gaia_id)

    if request.method == 'POST':
        komentarioa = request.form.get("komentarioa")
        print(gaia)
        library.komentarioaGehitu(request.user.MailKontua, gaia.title, 0, komentarioa)
    else:
        if gaia is None:
            # Maneja el caso en el que el tema no se encuentra, por ejemplo, redirige o muestra un mensaje
            return render_template('mezua.html', tituloa="Ez da aurkitu gai hori",
                                   mezua="Aukeratutako gaia ez da existitzen", location='/foroak')

    komentarioak = library.get_comments_for_topic(gaia)
    print(komentarioak)
    return render_template('gaia.html', gaia=gaia, Komentarioak=komentarioak)


@app.route('/gaiaSortu', methods=['POST'])
def gaiaSortu():
    izenburua = request.values.get("nuevoTitulo", "")
    deskribapena = request.values.get("nuevaDeskribapena", "")
    topic = library.create_topic(izenburua, deskribapena, request.user.MailKontua)
    return redirect('/gaia?id={}'.format(topic.id))


@app.route('/komentatu', methods=['POST'])
def Komentatu():
    topic_id = request.values.get("id", -1)
    topic = library.get_topic_by_id(topic_id)
    komentarioa_string = request.values.get("komentarioa", "")
    komentarioa = topic.sortu_komentarioa(komentarioa_string)
    return redirect('/gaia?id={}'.format(topic.id))


@app.route('/editatu', methods=['POST'])
def ErreseinaEditatu():
    if 'user' in request.__dict__ and request.user and request.user.token:
        if "liburua" in request.values and "erabiltzailea" in request.values:
            liburua = request.values.get("liburua")
            erabiltzailea = request.values.get("erabiltzailea")

            # Erreseinen datu berriak jaso
            puntuaketa = request.values.get("puntuaketa")
            komentarioa = request.values.get("komentarioa")

            # Datu basea aktualizatu
            library.editarErresina(liburua, erabiltzailea, puntuaketa, komentarioa)

            # Erreseina editatu ta gero pertsonalara eraman
            return redirect('/pertsonala')
        else:
            # Manejar el caso en el que los datos no estén completos
            flash('Faltan datos para editar la reseña', 'error')
            return redirect('/pertsonala')  # O redirige a donde desees
    else:
        return redirect('/login')

@app.route('/erreseinak_pantailaratu')
def erreseinak_pantailaratu():
    if 'user' in request.__dict__ and request.user and request.user.token:
        # Datu basetik erreseinak guztiak izan
        erreseinak = library.getErreseinak()  # Library Controller-ko metodoari deitu

        return render_template('erreseinak_pantailaratu.html', erreseinak=erreseinak)
    else:
        return redirect('/login')  # Redirigir al usuario a la página de inicio de sesión si no está autenticado