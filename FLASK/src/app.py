from flask import Flask, render_template, request, redirect, url_for, flash, send_file, send_from_directory
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import config
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import base64
from io import BytesIO
from PIL import Image
import hashlib
import os
import tempfile
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader, PdfWriter

import random
from flask import session
from flask_mail import Mail, Message 


# Models 
from models.ModelUser import ModelUser
from models.ModelForo import ModelForo
from models.ModelArticulo import ModelArticulo
from models.ModelNoticia import ModelNoticia
from models.ModelDocumento import ModelDocumento


# Entities
from models.entities.User import User
from models.entities.Post import Post
from models.entities.Respuesta import Respuesta
from models.entities.Notificacion import Notificacion
from models.entities.Articulo import Articulo
from models.entities.Noticia import Noticia





 

app = Flask(__name__)
db = MySQL(app)
login_manager_app = LoginManager(app)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'contratacionelectronicatfg@gmail.com'
app.config['MAIL_PASSWORD'] = 'uwwbhkmaxcohgutz'

mail = Mail(app)


def generar_otp():
    return random.randint(100000, 999999)

def calcular_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)

# Configurar UPLOAD_FOLDER para que esté dentro del directorio del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return redirect(url_for('login'))

#REGISTRO Y LOGIN
#------------------------------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        fullname = request.form['fullname']
        password = request.form['password']
        password2 = request.form['password2']
        if password == password2:
            #hashear las pass
            passwordHash = User.hash_pass(password)
            user = User(0, username, passwordHash, fullname, email, False)
            try:
                ModelUser.register(db, user)
                return redirect(url_for('login'))
            except Exception as ex:
                flash(str(ex))
                return render_template('register.html')
        else:
            flash("las contraseñas no coinciden..")
            return render_template('register.html')
    else:
        print("error al registrar")
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        user = User(0, request.form['username'], request.form['password'], ' ' , ' ')
        logged_user = ModelUser.login(db, user)
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('home'))
            else:
                flash("Contraseña incorrecta...")
                return render_template('login.html') 
        else:
            flash("Usuario no registrado...")
            return render_template('login.html')        
    else:
        return render_template('login.html')
 
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
#------------------------------------------------------------------------------
#HOME        
@app.route('/home')
@login_required
def home():
    return render_template('home.html')
#------------------------------------------------------------------------------
#PERFIL


@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    return render_template('perfil.html')

@app.route('/editar_perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    if request.method == 'POST':
        username = request.form['username']
        fullname = request.form['fullname']
        email = request.form['email']
        user = User(current_user.id, username, None, fullname, email)
        try:
            ModelUser.actualizar_user(db, user)
            flash('Perfil actualizado exitosamente')
            return redirect(url_for('perfil'))
        except Exception as ex:
            flash(str(ex))
    return render_template('editar_perfil.html')

@app.route('/cambiar_contraseña', methods=['POST'])
@login_required
def cambiar_contraseña():
    old_password = request.form['old_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    print(old_password)
    print(current_user.password)
    if new_password == confirm_password:
        if User.check_password(current_user.password, old_password):
            try:
                ModelUser.cambiar_password(db, current_user.id, new_password)
                flash('Contraseña actualizada exitosamente')
            except Exception as ex:
                flash(str(ex))
        else:
            flash('La contraseña actual no es correcta')
    else:
        flash('Las nuevas contraseñas no coinciden')
    
    return redirect(url_for('perfil'))
# #------------------------------------------------------------------------------



#FORO
#------------------------------------------------------------------------------
@app.route('/foro', methods=['GET', 'POST'])
@login_required
def foro():
    if request.method == 'POST':
        # Comprobamos si se ha enviado el formulario de nueva publicación
        if 'title' in request.form and 'content' in request.form:
            titulo = request.form['title']
            contenido = request.form['content']
            autor = current_user.username
            fecha = datetime.now().strftime('%Y-%m-%d %H:%M')
            post = Post(0, titulo, contenido, autor, fecha)
            result = ModelForo.publicar(db, post)
            if result:
                flash("Publicación creada exitosamente!")
            else:
                flash("Error al publicar!")
            return redirect(url_for('foro'))
        # Si no es el formulario de nueva publicación, asumimos que es el de búsqueda
        query = request.form.get('query')
        if query:
            publicaciones = ModelForo.buscar_publicaciones(db, query)
            return render_template('foro.html', publicaciones=publicaciones)
        
    publicaciones = ModelForo.obtener_todas(db)
    return render_template('foro.html', publicaciones=publicaciones)

@app.route('/misposts', methods=['GET'])
@login_required
def misposts():
    publicaciones = ModelForo.obtener_misPosts(db, current_user.username)
    return render_template('misposts.html', publicaciones=publicaciones)

@app.route('/publicacion/<int:post_id>', methods=['GET', 'POST'])
@login_required
def ver_publicacion(post_id):
    if request.method == 'POST':
        contenido = request.form['respuesta']
        autor = current_user.username
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M')
        resp = Respuesta(0, post_id, contenido, autor, fecha)       
        ModelForo.add_respuesta(db, resp)     

        publicacion = ModelForo.obtener_por_id(db, post_id)
        noti = Notificacion(0, resp.idResp, publicacion[3], 0)
        ModelForo.add_notificacion(db, noti)

        return redirect(url_for('ver_publicacion', post_id=post_id))
    
    # Obtener la publicación por ID
    publicacion = ModelForo.obtener_por_id(db, post_id)
    respuestas =  ModelForo.obtener_respuestas(db, post_id)
    return render_template('publicacion.html', publicacion=publicacion, respuestas=respuestas)


#------------------------------------------------------------------------------


#NOTIFICACIONES
#------------------------------------------------------------------------------

@app.route('/notificaciones', methods=['GET'])
@login_required
def notificaciones():
    notificaciones = ModelForo.obtener_notificaciones(db, current_user.username)  
    print(notificaciones)
    return render_template('notificaciones.html', notificaciones=notificaciones)

@app.route('/notificacion/<int:notificacion_id>/leer')
@login_required
def leer_notificacion(notificacion_id):
    notificacion = ModelForo.obtener_notificacion(db, notificacion_id)
    if notificacion and notificacion[2] == current_user.username:
        ModelForo.actualizar_notificacion(db, notificacion[0])
        post_id = ModelForo.obtener_post_by_idResp(db, notificacion[1])
        return redirect(url_for('ver_publicacion', post_id=post_id[0]))
    return redirect(url_for('notificaciones'))
@app.context_processor

def inject_notifications():
    if current_user.is_authenticated:
        username = current_user.username
        num_notificaciones = ModelForo.obtener_notificaciones_no_leidas(db, username)
        return dict(num_notificaciones=num_notificaciones)
    return dict(num_notificaciones=0)

@app.route('/limpiar_notificaciones', methods=['POST'])
@login_required
def limpiar_notificaciones():
    ModelForo.eliminar_notificaciones_por_usuario(db, current_user.username)
    flash("Tus notificaciones han sido eliminadas.")
    return redirect(url_for('notificaciones'))
#------------------------------------------------------------------------------



# Noticias
#------------------------------------------------------------------------------

@app.route('/noticias')
@login_required
def noticias():
    
    noticias = ModelNoticia.obtener_todas(db)
    print(noticias)
    return render_template('noticias.html', noticias=noticias)

@app.route('/admin/noticias', methods=['GET', 'POST'])
@login_required
def admin_noticias():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    noticias = ModelNoticia.obtener_todas(db)
    print(noticias)
    return render_template('admin_noticias.html', noticias=noticias)

@app.route('/admin/noticias/nueva', methods=['GET', 'POST'])
@login_required
def nueva_noticia():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    if request.method == 'POST':
        titulo = request.form['titulo']
        contenido = request.form['contenido']
        link = request.form['link']
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        noticia = Noticia(0, titulo, contenido, fecha, link)
        print(noticia)
        ModelNoticia.crear(db, noticia)
        return redirect(url_for('admin_noticias'))
    return render_template('nueva_noticia.html')

@app.route('/admin/noticias/editar/<int:noticia_id>', methods=['GET', 'POST'])
@login_required
def editar_noticia(noticia_id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    noticia = ModelNoticia.obtener_por_id(db, noticia_id)
    if request.method == 'POST':
        noticia.titulo = request.form['titulo']
        noticia.contenido = request.form['contenido']
        noticia.link = request.form['link']
        noticia.fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ModelNoticia.actualizar(db, noticia)
        return redirect(url_for('admin_noticias'))
    return render_template('editar_noticia.html', noticia=noticia)

@app.route('/admin/noticias/eliminar/<int:noticia_id>', methods=['POST'])
@login_required
def eliminar_noticia(noticia_id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    ModelNoticia.eliminar(db, noticia_id)
    return redirect(url_for('admin_noticias'))
#------------------------------------------------------------------------------

#Tutorial
#------------------------------------------------------------------------------

@app.route('/simularcontrato', methods=['GET', 'POST'])
def simularcontrato():
    return render_template('simularcontrato.html')

@app.route('/subir_contrato', methods=['POST', 'GET'])
@login_required
def subir_contrato():
    if 'contrato_pdf' not in request.files:
        flash('No se ha seleccionado ningún archivo')
        return redirect(request.url)
    file = request.files['contrato_pdf']
    if file.filename == '':
        flash('No se ha seleccionado ningún archivo')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        if os.path.exists(filepath):
            return render_template('firmar_contrato.html', filename=filename)
        else:
            flash('Hubo un error al guardar el archivo.')
            return redirect(request.url)
    else:
        flash('Formato de archivo no permitido. Solo se permiten archivos PDF.')
        return redirect(request.url)
    
@app.route('/guardar_contrato', methods=['POST'])
@login_required
def guardar_contrato():
    signature = request.form.get('signature')
    filename = request.form.get('filename')
    posX = float(request.form.get('posX'))
    posY = float(request.form.get('posY'))
    width = float(request.form.get('width'))
    height = float(request.form.get('height'))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Convertir la firma de base64 a una imagen
    signature_data = signature.split(",")[1]
    signature_image = Image.open(BytesIO(base64.b64decode(signature_data)))

    # Guardar la imagen de la firma en un archivo temporal en formato PNG
    temp_signature_path = os.path.join(tempfile.gettempdir(), "signature.png")
    signature_image.save(temp_signature_path, format="PNG")

    # Añadir la firma al PDF
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    #Ajustar las coordenadas Y para el sistema de coordenadas del PDF
    pdf_height = letter[1]  # Altura de la página en puntos
    posY = pdf_height - posY - height  # Ajustar para que el origen sea la esquina inferior izquierda

    can.drawImage(temp_signature_path,  posX, posY, width=width, height=height, mask='auto')
    can.save()

    packet.seek(0)
    new_pdf = PdfReader(packet)
    pdf_reader  = PdfReader(open(filepath, "rb"))
    output = PdfWriter()
    num_pages = len (pdf_reader.pages)

    # Copiar el contenido del PDF existente al nuevo PDF
    for i in range(num_pages):
        page = pdf_reader.pages[i]
        if i == num_pages - 1: 
            page.merge_page(new_pdf.pages[0])
        output.add_page(page)

    output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"firmado_{filename}")
    with open(output_filepath, "wb") as outputStream:
        output.write(outputStream)

    # Eliminar el archivo temporal
    os.remove(temp_signature_path)

     # Guardar la información del documento en la base de datos
    documento_hash = calcular_hash(output_filepath)
    ModelDocumento.guardar_documento(db, current_user.id, f"firmado_{filename}", output_filepath, documento_hash)

    # Eliminar la verificación OTP de la sesión después de firmar
    session.pop('otp_verified', None)

    flash('Contrato firmado y guardado exitosamente.')
    return send_file(output_filepath, as_attachment=True)

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        print(f"Sirviendo archivo: {filepath}")  # Línea de depuración
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    else:
        print(f"Archivo no encontrado: {filepath}")  # Línea de depuración
        return "Archivo no encontrado", 404


@app.route('/enviar_otp')
@login_required
def enviar_otp():
    otp = generar_otp()
    session['otp'] = otp
    msg = Message('Tu OTP para firmar el documento', sender='contratacionelectronicatfg@gmail.com', recipients=[current_user.email])
    msg.body = f'Tu OTP es: {otp}'
    mail.send(msg)
    flash('OTP enviado. Revisa tu correo electrónico.')
    return redirect(url_for('firmar_contrato', filename=request.args.get('filename')))

@app.route('/verificar_otp', methods=['POST'])
@login_required
def verificar_otp():
    otp_ingresado = request.form['otp']
    if 'otp' in session and session['otp'] == int(otp_ingresado):
        session['otp_verified'] = True  # Actualiza otp_verified en la sesión
        flash('OTP verificado con éxito. Ahora puedes firmar el documento.')
    else:
        session['otp_verified'] = False 
        flash('OTP incorrecto. Inténtalo de nuevo.')

    return redirect(url_for('firmar_contrato', filename=request.form['filename']))


@app.route('/firmar_contrato', methods=['GET'])
@login_required
def firmar_contrato():
    filename = request.args.get('filename')
    if not filename:
        return redirect(url_for('subir_contrato'))

    otp_verified = session.get('otp_verified', False)

    return render_template('firmar_contrato.html', filename=filename, otp_verified=otp_verified)



@app.route('/misdocumentos')
@login_required
def misdocumentos():
    documentos = ModelDocumento.obtener_documentos(db, current_user.id)
    return render_template('misdocumentos.html', documentos=documentos)
#------------------------------------------------------------------------------


#Articulos de la ley
#------------------------------------------------------------------------------
@app.route('/ley', methods=['GET', 'POST'])
@login_required
def ley():
    query = request.form.get('query', '')
    resultados = []
    if query:
        resultados = ModelArticulo.buscar_articulos(db, query)
    return render_template('ley.html', query=query, resultados=resultados)

@app.route('/articulo/<int:articulo_id>')
@login_required
def ver_articulo(articulo_id):
    articulo = ModelArticulo.obtener_por_id(db, articulo_id)
    if articulo:
        return render_template('articulo.html', articulo=articulo)
    else:
        flash('Artículo no encontrado.')
        return redirect(url_for('ley'))
#------------------------------------------------------------------------------

#ADMINISTRADOR
#------------------------------------------------------------------------------
@app.route('/admin/usuarios', methods=['GET', 'POST'])
@login_required
def admin_usuarios():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    
    query = request.form.get('query')
    if query:
        usuarios = ModelUser.buscar_usuarios(db, query)
    else:
        usuarios = ModelUser.obtener_todos(db)
    
    return render_template('admin_usuarios.html', usuarios=usuarios)

@app.route('/admin/usuarios/eliminar/<int:user_id>', methods=['POST'])
@login_required
def eliminar_usuario(user_id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    
    ModelUser.eliminar(db, user_id)
    return redirect(url_for('admin_usuarios'))

@app.route('/foro/eliminar/<int:post_id>', methods=['POST'])
@login_required
def eliminar_post(post_id):
    if not current_user.is_admin:
        return redirect(url_for('foro'))
    ModelForo.eliminarPost(db, post_id)
    flash("Publicación eliminada exitosamente!")
    return redirect(url_for('foro'))

@app.route('/eliminar_respuesta/<int:idResp>/<int:post_id>', methods=['POST'])
@login_required
def eliminar_respuesta(idResp, post_id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    ModelForo.eliminarResp(db, idResp)
    return redirect(url_for('ver_publicacion', post_id=post_id))


# Rutas para gestión de artículos

@app.route('/admin/articulos', methods=['GET'])
@login_required
def admin_articulos():
    if not current_user.is_admin:
        return redirect(url_for('home'))

    query = request.args.get('query')
    if query:
        articulos = ModelArticulo.buscar_articulos(db, query)
    else:
        cursor = db.connection.cursor()
        cursor.execute("SELECT idArticulo, titulo, contenido, resumen FROM articulos")
        articulos = cursor.fetchall()
        
    return render_template('admin_articulos.html', articulos=articulos)

@app.route('/admin/articulos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_articulo():
    if not current_user.is_admin:
        return redirect(url_for('home'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        contenido = request.form['contenido']
        resumen = request.form['resumen']
        ModelArticulo.crear_articulo(db, titulo, contenido, resumen)
        return redirect(url_for('admin_articulos'))

    return render_template('nuevo_articulo.html')

@app.route('/admin/articulos/editar/<int:articulo_id>', methods=['GET', 'POST'])
@login_required
def editar_articulo(articulo_id):
    if not current_user.is_admin:
        return redirect(url_for('home'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        contenido = request.form['contenido']
        resumen = request.form['resumen']
        ModelArticulo.actualizar_articulo(db, articulo_id, titulo, contenido, resumen)
        return redirect(url_for('admin_articulos'))

    articulo = ModelArticulo.obtener_por_id(db, articulo_id)
    return render_template('editar_articulo.html', articulo=articulo)

@app.route('/admin/articulos/eliminar/<int:articulo_id>', methods=['POST'])
@login_required
def eliminar_articulo(articulo_id):
    if not current_user.is_admin:
        return redirect(url_for('home'))

    ModelArticulo.eliminar_articulo(db, articulo_id)
    return redirect(url_for('admin_articulos'))
#------------------------------------------------------------------------------




if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run()