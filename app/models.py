from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), unique=True, nullable=False)
    descricao = db.Column(db.String(255))
    produtos = db.relationship('Produto', backref='categoria', lazy='dynamic')

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(128), nullable=False)
    codigo = db.Column(db.String(64), unique=True, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'))
    estoque_minimo = db.Column(db.Integer, default=0)
    estoque_atual = db.Column(db.Integer, default=0)
    descricao = db.Column(db.Text)
    movimentacoes = db.relationship('Movimentacao', backref='produto', lazy='dynamic')

class Funcionario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(128), nullable=False)
    departamento = db.Column(db.String(64))
    movimentacoes = db.relationship('Movimentacao', backref='funcionario', lazy='dynamic')

class Movimentacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False) # ENTRADA, SAIDA, AJUSTE
    quantidade = db.Column(db.Integer, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    observacao = db.Column(db.String(256))
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionario.id'))
