from model import User
from .LibraryController import LibraryController
from flask import Flask, render_template, request, make_response, redirect, url_for

app = Flask(__name__, static_url_path='', static_folder='../view/static', template_folder='../view/')
app.jinja_env.globals.update(zip=zip) # Añadir esta línea


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
	email = library.aurkituSaioaDuenErab()
	erreserbak, lib_info, nb_erreserbak = library.search_erreserbak(email=email, page=page-1)
	total_pages = (nb_erreserbak//6)+1
	return render_template('pertsonala.html', erreserbak=erreserbak, lib_info=lib_info, current_page=page,
						   total_pages=total_pages, max=max, min=min)

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
	title = request.values.get("title", "")
	author = request.values.get("author", "")
	page = int(request.values.get("page", 1))
	liburua = library.search_books(title=title, author=author, page=page - 1)
	return render_template('liburuBista.html', book=liburua)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if 'user' in dir(request) and request.user and request.user.token:
		return redirect('/')
	email = request.values.get("email", "") #html-tik aterata, izen hori duten input-ak
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

		user = User(MailKontua, SortzaileMailKontua, Izena, Abizena, Pasahitza, Rola, lagunakOnartzekoAukera)

		if user.new_user():
			# Si el usuario se crea correctamente, redirigir a la página catalogue.html
			return redirect(url_for('catalogue'))

	# Si no es un método POST o si hay algún error, mostrar el formulario erabiltzaileaSortu.html
	return redirectNoAdmin("erabiltzaileaSortu.html", "login")

@app.route('/erabiltzaileaEzabatu', methods=['GET', 'POST'])
def erabiltzaileaEzabatu():
	if request.method == 'POST':
		MailKontua = request.form.get("email")

		user = User(MailKontua, None, None, None, None, None, None)

		if user.delete_user():
			# Si el usuario se elimina correctamente, redirigir a la página catalogue.html
			return redirect(url_for('catalogue'))

	# Si no es un método POST o si hay algún error, mostrar el formulario erabiltzaileaSortu.html
	return redirectNoAdmin("erabiltzaileaEzabatu.html", "login")