from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import Movimentacao, Produto, Funcionario
from app.services.estoque_service import EstoqueService

mov_bp = Blueprint('movimentacoes', __name__, url_prefix='/movimentacoes')

@mov_bp.route('/entradas')
@login_required
def listar_entradas():
    movs = Movimentacao.query.filter_by(tipo='ENTRADA').order_by(Movimentacao.data.desc()).all()
    return render_template('movimentacoes/listar.html', movimentacoes=movs, titulo='Entradas de Hardware', tipo_filtro='ENTRADA')

@mov_bp.route('/saidas')
@login_required
def listar_saidas():
    movs = Movimentacao.query.filter_by(tipo='SAIDA').order_by(Movimentacao.data.desc()).all()
    return render_template('movimentacoes/listar.html', movimentacoes=movs, titulo='Saídas de Hardware', tipo_filtro='SAIDA')

@mov_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    tipo_predefinido = request.args.get('tipo', 'ENTRADA')
    if request.method == 'POST':
        produto_id = request.form.get('produto_id')
        tipo = request.form.get('tipo')
        quantidade = int(request.form.get('quantidade'))
        funcionario_id = request.form.get('funcionario_id')
        obs = request.form.get('observacao')
        
        sucesso, msg = EstoqueService.registrar_movimentacao(
            produto_id, tipo, quantidade, funcionario_id, obs
        )
        
        if sucesso:
            flash(msg)
            return redirect(url_for('movimentacoes.listar_entradas' if tipo == 'ENTRADA' else 'movimentacoes.listar_saidas'))
        else:
            flash(msg, 'danger')
            
    produtos = Produto.query.all()
    funcionarios = Funcionario.query.all()
    return render_template('movimentacoes/form.html', produtos=produtos, funcionarios=funcionarios, tipo_predefinido=tipo_predefinido)
