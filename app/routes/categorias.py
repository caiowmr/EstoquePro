from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import Categoria
from app import db

categorias_bp = Blueprint('categorias', __name__, url_prefix='/categorias')

@categorias_bp.route('/')
@login_required
def listar():
    categorias = Categoria.query.all()
    return render_template('categorias/listar.html', categorias=categorias)

@categorias_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        
        if Categoria.query.filter_by(nome=nome).first():
            flash('Esta categoria já existe.', 'danger')
            return redirect(url_for('categorias.nova'))
            
        nova_c = Categoria(nome=nome, descricao=descricao)
        db.session.add(nova_c)
        db.session.commit()
        flash('Categoria criada com sucesso!')
        return redirect(url_for('categorias.listar'))
    
    return render_template('categorias/form.html', categoria=None)

@categorias_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    categoria = Categoria.query.get_or_404(id)
    if request.method == 'POST':
        categoria.nome = request.form.get('nome')
        categoria.descricao = request.form.get('descricao')
        db.session.commit()
        flash('Categoria atualizada com sucesso!')
        return redirect(url_for('categorias.listar'))
    
    return render_template('categorias/form.html', categoria=categoria)

@categorias_bp.route('/remover/<int:id>', methods=['POST'])
@login_required
def remover(id):
    categoria = Categoria.query.get_or_404(id)
    if categoria.produtos.count() > 0:
        flash('Não é possível remover uma categoria que possui produtos vinculados.', 'danger')
    else:
        db.session.delete(categoria)
        db.session.commit()
        flash('Categoria removida com sucesso!')
    return redirect(url_for('categorias.listar'))
