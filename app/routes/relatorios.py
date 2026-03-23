from flask import Blueprint, render_template, send_file, make_response, request
from flask_login import login_required
from app.models import Movimentacao, Produto
import pandas as pd
from io import BytesIO
from xhtml2pdf import pisa
import matplotlib.pyplot as plt
import base64
from datetime import datetime, timedelta

relatorios_bp = Blueprint('relatorios', __name__, url_prefix='/relatorios')

def get_chart_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_str

@relatorios_bp.route('/')
@login_required
def index():
    return render_template('relatorios/index.html')

@relatorios_bp.route('/exportar/excel')
@login_required
def exportar_excel():
    movs = Movimentacao.query.all()
    data = []
    for m in movs:
        data.append({
            'Data': m.data,
            'Produto': m.produto.nome,
            'Tipo': m.tipo,
            'Quantidade': m.quantidade,
            'Funcionário': m.funcionario.nome if m.funcionario else '-',
            'Observação': m.observacao
        })
    
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Movimentações')
    
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='relatorio_estoque.xlsx')

@relatorios_bp.route('/exportar/pdf')
@login_required
def exportar_pdf():
    # Obter opções
    grafico_fluxo = request.args.get('grafico_fluxo') == '1'
    grafico_mais_usados = request.args.get('grafico_mais_usados') == '1'
    grafico_menos_usados = request.args.get('grafico_menos_usados') == '1'
    grafico_tecnicos = request.args.get('grafico_tecnicos') == '1'
    grafico_estoque = request.args.get('grafico_estoque') == '1'
    incluir_entradas = request.args.get('incluir_entradas') == '1'
    incluir_saidas = request.args.get('incluir_saidas') == '1'
    
    # Filtrar movimentações para a tabela
    query = Movimentacao.query
    if not incluir_entradas and not incluir_saidas:
        movs = []
    elif not incluir_entradas:
        movs = query.filter(Movimentacao.tipo == 'SAIDA').order_by(Movimentacao.data.desc()).all()
    elif not incluir_saidas:
        movs = query.filter(Movimentacao.tipo == 'ENTRADA').order_by(Movimentacao.data.desc()).all()
    else:
        movs = query.order_by(Movimentacao.data.desc()).all()
    
    # Obter período selecionado para o gráfico
    try:
        dias = int(request.args.get('periodo', 30))
    except ValueError:
        dias = 30
        
    hoje = datetime.now()
    inicio = hoje - timedelta(days=dias)
    
    charts = {}
    
    if grafico_fluxo:
        # Gráfico de Fluxo
        movs_periodo = Movimentacao.query.filter(Movimentacao.data >= inicio).all()
        df_movs = pd.DataFrame([{
            'data': m.data.date(),
            'tipo': m.tipo,
            'quantidade': m.quantidade
        } for m in movs_periodo])
        
        if not df_movs.empty:
            df_grouped = df_movs.groupby(['data', 'tipo'])['quantidade'].sum().unstack(fill_value=0)
            if 'ENTRADA' not in df_grouped.columns: df_grouped['ENTRADA'] = 0
            if 'SAIDA' not in df_grouped.columns: df_grouped['SAIDA'] = 0
            
            fig, ax = plt.subplots(figsize=(10, 4))
            df_grouped.plot(kind='line', ax=ax, marker='o', color={'ENTRADA': '#34c759', 'SAIDA': '#ff3b30'})
            ax.set_title(f'Fluxo de Movimentação (Últimos {dias} dias)')
            ax.set_ylabel('Quantidade')
            ax.set_xlabel('Data')
            ax.grid(True, linestyle='--', alpha=0.6)
            charts['fluxo'] = get_chart_base64(fig)

    if grafico_mais_usados:
        # Gráfico de Peças Mais Usadas
        from app.models import Produto
        from sqlalchemy import func
        mais_usadas = Movimentacao.query.join(Produto).with_entities(
            Produto.nome,
            func.coalesce(func.sum(Movimentacao.quantidade), 0).label('total')
        ).filter(Movimentacao.tipo == 'SAIDA', Movimentacao.data >= inicio).group_by(Produto.id, Produto.nome).order_by(func.sum(Movimentacao.quantidade).desc()).limit(5).all()
        
        if mais_usadas:
            fig, ax = plt.subplots(figsize=(10, 4))
            labels = [p.nome for p in mais_usadas]
            values = [int(p.total) for p in mais_usadas]
            ax.barh(labels, values, color='#0071e3')
            ax.set_title('Top 5 Peças Mais Usadas')
            ax.invert_yaxis()
            charts['mais_usados'] = get_chart_base64(fig)

    if grafico_menos_usados:
        # Gráfico de Peças Menos Usadas
        from app.models import Produto
        from sqlalchemy import func
        menos_usadas = Movimentacao.query.join(Produto).with_entities(
            Produto.nome,
            func.coalesce(func.sum(Movimentacao.quantidade), 0).label('total')
        ).filter(Movimentacao.tipo == 'SAIDA', Movimentacao.data >= inicio).group_by(Produto.id, Produto.nome).order_by(func.sum(Movimentacao.quantidade).asc()).limit(5).all()
        
        if menos_usadas:
            fig, ax = plt.subplots(figsize=(10, 4))
            labels = [p.nome for p in menos_usadas]
            values = [int(p.total) for p in menos_usadas]
            ax.barh(labels, values, color='#ff9500')
            ax.set_title('Top 5 Peças Menos Usadas')
            ax.invert_yaxis()
            charts['menos_usados'] = get_chart_base64(fig)

    if grafico_tecnicos:
        # Gráfico de Consumo por Técnico
        from app.models import Funcionario
        from sqlalchemy import func
        top_funcionarios = Movimentacao.query.join(Funcionario).with_entities(
            Funcionario.nome,
            func.coalesce(func.sum(Movimentacao.quantidade), 0).label('total')
        ).filter(Movimentacao.tipo == 'SAIDA', Movimentacao.data >= inicio).group_by(Funcionario.id, Funcionario.nome).order_by(func.sum(Movimentacao.quantidade).desc()).limit(5).all()
        
        if top_funcionarios:
            fig, ax = plt.subplots(figsize=(10, 4))
            labels = [f.nome for f in top_funcionarios]
            values = [int(f.total) for f in top_funcionarios]
            ax.bar(labels, values, color='#af52de')
            ax.set_title('Consumo por Técnico')
            charts['tecnicos'] = get_chart_base64(fig)

    if grafico_estoque:
        # Gráfico de Distribuição de Estoque
        from app.models import Produto
        dist_estoque = Produto.query.order_by(Produto.estoque_atual.desc()).limit(5).all()
        
        if dist_estoque:
            fig, ax = plt.subplots(figsize=(10, 4))
            labels = [p.nome for p in dist_estoque]
            values = [p.estoque_atual for p in dist_estoque]
            ax.pie(values, labels=labels, autopct='%1.1f%%', colors=['#0071e3', '#34c759', '#ff9500', '#ff3b30', '#af52de'])
            ax.set_title('Distribuição de Estoque Atual')
            charts['estoque'] = get_chart_base64(fig)

    html = render_template('relatorios/pdf.html', movimentacoes=movs, charts=charts, now=datetime.now())
    
    output = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=output)
    
    if pisa_status.err:
        return "Erro ao gerar PDF", 500
    
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='relatorio_estoque.pdf')
