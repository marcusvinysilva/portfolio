import re
from flask import Flask, render_template, redirect, request, flash, session
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'bluedtech'

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'marcusvinyport@gmail.com',
    "MAIL_PASSWORD": 'mvps1997'
}

app.config.update(mail_settings)
mail = Mail(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://runueoqg:8VqQnfsVmJ0-YM3e8nAR7uB8jcDN-fLY@kesavan.db.elephantsql.com/runueoqg'
db = SQLAlchemy(app)

class Contato:
    def __init__(self, nome, email, mensagem):
        self.nome = nome
        self.email = email
        self.mensagem = mensagem

class Projeto(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    imagem = db.Column(db.String(500), nullable=False)
    descricao = db.Column(db.String(500), nullable=False)
    link = db.Column(db.String(300), nullable=False)

    def __init__(self, nome, imagem, descricao, link):
        self.nome = nome
        self.imagem = imagem
        self.descricao = descricao
        self.link = link

@app.route('/')
def index():
    session['user_logado'] = None
    projetos = Projeto.query.all()
    return render_template('index.html', projetos=projetos)

@app.route('/adm')
def adm():
    if 'user_logado' not in session or session['user_logado'] == None:
        flash('Faça o login antes de acessar essa rota!')
        return redirect('/login')

    projetos = Projeto.query.all()
    return render_template('adm.html', projetos=projetos, projeto='')

@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        projeto = Projeto(
            request.form['nome'],
            request.form['imagem'],
            request.form['descricao'],
            request.form['link']
        )
        db.session.add(projeto)
        db.session.commit()
        flash('Projeto criado com sucesso!')
        return redirect('/adm')
    flash('Você não tem autorização para acessar essa rota!')
    return redirect('/login')

@app.route('/delete/<id>')
def delete(id):
    if 'user_logado' not in session or session['user_logado'] == None:
        flash('Faça o login antes de acessar essa rota!')
        return redirect('/login')

    projeto = Projeto.query.get(id)
    db.session.delete(projeto) #para apagar a tabela no browse do elephant digitar: drop table 'projeto'
    db.session.commit()
    flash('Projeto apagado com sucesso!')
    return redirect('/adm')

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    if 'user_logado' not in session or session['user_logado'] == None:
        flash('Faça o login antes de acessar essa rota!')
        return redirect('/login')

    projeto = Projeto.query.get(id)
    projetos = Projeto.query.all()
    if request.method == 'POST':
        projeto.nome = request.form['nome']
        projeto.descricao = request.form['descricao']
        projeto.imagem = request.form['imagem']
        projeto.link = request.form['link']
        db.session.commit()
        return redirect('/adm')
    return render_template('adm.html', projeto=projeto, projetos=projetos)

@app.route('/<id>')
def projeto_por_id(id):
    projetoDel = Projeto.query.get(id)
    return render_template('adm.html', projetoDel=projetoDel, projeto='')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.form['senha'] == 'adm123':
        session['user_logado'] = 'logado'
        flash('Login feito com sucesso!')
        return redirect('/adm')
    else:
        flash('Erro no login, tente novamente!')
        return redirect('/login')

@app.route('/send', methods=['GET', 'POST'])
def send():
    session['user_logado'] = None
    if request.method == 'POST':
        formContato = Contato(
            request.form['nome'],
            request.form['email'],
            request.form['mensagem']
        )

        msg = Message(
            subject= 'Contato do seu Portfólio',
            sender=app.config.get("MAIL_USERNAME"),
            recipients=[app.config.get("MAIL_USERNAME")],
            body=f'''O {formContato.nome} com email {formContato.email}, te mandou a seguinte mensagem:

                {formContato.mensagem}'''
        )
        mail.send(msg)
    return render_template('send.html',formContato=formContato)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)