from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import Funcionario
from app import db

funcionarios_bp = Blueprint('funcionarios', __name__, url_prefix='/funcionarios')

@funcionarios_bp.route('/')
@login_required
def listar():
    funcionarios = Funcionario.query.all()
    return render_template('funcionarios/listar.html', funcionarios=funcionarios)

@funcionarios_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        nome = request.form.get('nome')
        departamento = request.form.get('departamento')
        
        novo_f = Funcionario(nome=nome, departamento=departamento)
        db.session.add(novo_f)
        db.session.commit()
        flash('Funcionário cadastrado com sucesso!')
        return redirect(url_for('funcionarios.listar'))
    
    return render_template('funcionarios/form.html', funcionario=None)

@funcionarios_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    funcionario = Funcionario.query.get_or_404(id)
    if request.method == 'POST':
        funcionario.nome = request.form.get('nome')
        funcionario.departamento = request.form.get('departamento')
        db.session.commit()
        flash('Funcionário atualizado com sucesso!')
        return redirect(url_for('funcionarios.listar'))
    
    return render_template('funcionarios/form.html', funcionario=funcionario)

@funcionarios_bp.route('/remover/<int:id>', methods=['POST'])
@login_required
def remover(id):
    funcionario = Funcionario.query.get_or_404(id)
    if funcionario.movimentacoes.count() > 0:
        flash('Não é possível remover um funcionário que possui histórico de movimentações.', 'danger')
    else:
        db.session.delete(funcionario)
        db.session.commit()
        flash('Funcionário removido com sucesso!')
    return redirect(url_for('funcionarios.listar'))
