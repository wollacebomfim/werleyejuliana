import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'sua_chave_secreta_aqui'  # Necessário para usar sessões

db = SQLAlchemy(app)

# Modelo para o banco de dados
class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comentario = db.Column(db.String(200), nullable=False)
    posted_by = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100), nullable=False)

# Criação do banco de dados
with app.app_context():
    db.create_all()

# Página de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'admin' and password == 'buggie':  # Login básico
            session['logged_in'] = True
            return redirect(url_for('admin'))

        flash('Login inválido. Tente novamente.')
    
    return render_template('login.html')

# Página Administrativa
@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    uploads = Upload.query.order_by(Upload.id.desc()).all()
    return render_template('admin.html', uploads=uploads)

# Rota para Deletar Postagens
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    upload = Upload.query.get(id)
    if upload:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], upload.image))  # Remover a imagem do sistema
        except:
            pass
        db.session.delete(upload)
        db.session.commit()

    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Página Principal
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        comentario = request.form.get('comentario')
        posted_by = request.form.get('posted_by')
        image = request.files['image']

        if comentario and posted_by and image:
            # Salvar a imagem no diretório de uploads
            filename = secure_filename(image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(filepath)

            # Salvar os dados no banco de dados
            upload = Upload(comentario=comentario, posted_by=posted_by, image=filename)
            db.session.add(upload)
            db.session.commit()

            return redirect(url_for('index'))

    # Recuperar todos os uploads do banco de dados em ordem decrescente (mais recente primeiro)
    uploads = Upload.query.order_by(Upload.id.desc()).all()

    return render_template('index.html', uploads=uploads)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
