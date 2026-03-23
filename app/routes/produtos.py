from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import Produto, Categoria
from app import db

produtos_bp = Blueprint('produtos', __name__, url_prefix='/produtos')

@produtos_bp.route('/')
@login_required
def listar():
    categoria_id = request.args.get('categoria')
    if categoria_id:
        produtos = Produto.query.filter_by(categoria_id=categoria_id).all()
    else:
        produtos = Produto.query.all()
    categorias = Categoria.query.all()
    return render_template('produtos/listar.html', produtos=produtos, categorias=categorias)

@produtos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    categorias = Categoria.query.all()
    if request.method == 'POST':
        nome = request.form.get('nome')
        codigo = request.form.get('codigo')
        estoque_minimo = request.form.get('estoque_minimo')
        categoria_id = request.form.get('categoria_id')
        
        novo_p = Produto(
            nome=nome, 
            codigo=codigo, 
            estoque_minimo=estoque_minimo,
            categoria_id=categoria_id
        )
        db.session.add(novo_p)
        db.session.commit()
        flash('Produto cadastrado com sucesso!')
        return redirect(url_for('produtos.listar'))
    
    return render_template('produtos/form.html', produto=None, categorias=categorias)

@produtos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    produto = Produto.query.get_or_404(id)
    categorias = Categoria.query.all()
    if request.method == 'POST':
        produto.nome = request.form.get('nome')
        produto.codigo = request.form.get('codigo')
        produto.estoque_minimo = int(request.form.get('estoque_minimo'))
        produto.categoria_id = request.form.get('categoria_id')
        
        db.session.commit()
        flash('Produto atualizado com sucesso!')
        return redirect(url_for('produtos.listar'))
    
    return render_template('produtos/form.html', produto=produto, categorias=categorias)

@produtos_bp.route('/remover/<int:id>', methods=['POST'])
@login_required
def remover(id):
    produto = Produto.query.get_or_404(id)
    # Verificar se há movimentações vinculadas
    if produto.movimentacoes.count() > 0:
        flash('Não é possível remover um produto que possui histórico de movimentações.', 'danger')
    else:
        db.session.delete(produto)
        db.session.commit()
        flash('Produto removido com sucesso!')
    return redirect(url_for('produtos.listar'))

@produtos_bp.route('/gerador-massa', methods=['POST'])
@login_required
def gerador_massa():
    import random
    categorias = Categoria.query.all()
    if not categorias:
        flash('Crie ao menos uma categoria antes de usar o gerador.', 'warning')
        return redirect(url_for('produtos.listar'))
    
    nomes = ['Parafuso', 'Porca', 'Arruela', 'Rolamento', 'Engrenagem', 'Correia', 'Válvula', 'Sensor', 'Cabo', 'Conector']
    prefixos = ['A', 'B', 'C', 'X', 'Y', 'Z']
    
    for _ in range(10):
        nome = f"{random.choice(nomes)} {random.randint(100, 999)}"
        codigo = f"{random.choice(prefixos)}-{random.randint(1000, 9999)}"
        estoque_minimo = random.randint(5, 50)
        categoria = random.choice(categorias)
        
        p = Produto(nome=nome, codigo=codigo, estoque_minimo=estoque_minimo, categoria_id=categoria.id)
        db.session.add(p)
    
    db.session.commit()
    flash('10 produtos gerados aleatoriamente com sucesso!')
    return redirect(url_for('produtos.listar'))
