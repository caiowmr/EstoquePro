from app.models import Movimentacao, Produto, Funcionario
from sqlalchemy import func
from datetime import datetime, timedelta
import json

class DashboardService:
    @staticmethod
    def _get_periodo_dates(periodo='semana', start_date=None, end_date=None):
        hoje = datetime.now()
        fim = hoje
        
        if start_date and end_date:
            try:
                inicio = datetime.strptime(start_date, '%Y-%m-%d')
                fim = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            except ValueError:
                inicio = hoje - timedelta(days=7)
        elif periodo == 'mes':
            inicio = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif periodo == 'semana':
            inicio = (hoje - timedelta(days=hoje.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            inicio = hoje - timedelta(days=7)
        return inicio, fim

    @staticmethod
    def get_resumo_cards(inicio, fim):
        total_produtos = Produto.query.count()
        total_mov_periodo = Movimentacao.query.filter(
            Movimentacao.data >= inicio,
            Movimentacao.data <= fim
        ).count()
        itens_baixo_estoque = Produto.query.filter(
            Produto.estoque_atual <= Produto.estoque_minimo
        ).count()
        
        return {
            'total_produtos': total_produtos,
            'movimentacoes_periodo': total_mov_periodo,
            'baixo_estoque': itens_baixo_estoque
        }

    @staticmethod
    def get_dados_graficos(inicio, fim):
        # Mapeamento de meses em português
        meses = {
            1: 'jan', 2: 'fev', 3: 'mar', 4: 'abr', 5: 'mai', 6: 'jun',
            7: 'jul', 8: 'ago', 9: 'set', 10: 'out', 11: 'nov', 12: 'dez'
        }

        def format_date(date_str):
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            return f"{dt.day}/{meses[dt.month]}"

        # Saídas por dia
        uso_por_dia = Movimentacao.query.with_entities(
            func.date(Movimentacao.data).label('dia'),
            func.sum(Movimentacao.quantidade).label('total')
        ).filter(
            Movimentacao.tipo == 'SAIDA',
            Movimentacao.data >= inicio,
            Movimentacao.data <= fim
        ).group_by(func.date(Movimentacao.data)).order_by(func.date(Movimentacao.data)).all()

        # Entradas por dia
        entradas_por_dia = Movimentacao.query.with_entities(
            func.date(Movimentacao.data).label('dia'),
            func.sum(Movimentacao.quantidade).label('total')
        ).filter(
            Movimentacao.tipo == 'ENTRADA',
            Movimentacao.data >= inicio,
            Movimentacao.data <= fim
        ).group_by(func.date(Movimentacao.data)).order_by(func.date(Movimentacao.data)).all()

        # Unificar labels
        todas_datas = sorted(list(set([str(d.dia) for d in uso_por_dia] + [str(d.dia) for d in entradas_por_dia])))

        # Peças mais usadas
        mais_usadas = Movimentacao.query.join(Produto).with_entities(
            Produto.nome,
            func.coalesce(func.sum(Movimentacao.quantidade), 0).label('total')
        ).filter(Movimentacao.tipo == 'SAIDA', Movimentacao.data >= inicio, Movimentacao.data <= fim).group_by(Produto.id, Produto.nome).order_by(func.sum(Movimentacao.quantidade).desc()).limit(5).all()

        # Peças menos usadas (mas que tiveram pelo menos uma saída no período)
        menos_usadas = Movimentacao.query.join(Produto).with_entities(
            Produto.nome,
            func.coalesce(func.sum(Movimentacao.quantidade), 0).label('total')
        ).filter(Movimentacao.tipo == 'SAIDA', Movimentacao.data >= inicio, Movimentacao.data <= fim).group_by(Produto.id, Produto.nome).order_by(func.sum(Movimentacao.quantidade).asc()).limit(5).all()

        # Funcionários que mais usam
        top_funcionarios = Movimentacao.query.join(Funcionario).with_entities(
            Funcionario.nome,
            func.coalesce(func.sum(Movimentacao.quantidade), 0).label('total')
        ).filter(Movimentacao.tipo == 'SAIDA', Movimentacao.data >= inicio, Movimentacao.data <= fim).group_by(Funcionario.id, Funcionario.nome).order_by(func.sum(Movimentacao.quantidade).desc()).limit(5).all()

        # Distribuição de Estoque Atual (Top 5 volumes)
        dist_estoque = Produto.query.order_by(Produto.estoque_atual.desc()).limit(5).all()

        return {
            'comparativo_mov': {
                'labels': [format_date(d) for d in todas_datas],
                'saidas': [int(next((u.total for u in uso_por_dia if str(u.dia) == d), 0)) for d in todas_datas],
                'entradas': [int(next((e.total for e in entradas_por_dia if str(e.dia) == d), 0)) for d in todas_datas]
            },
            'mais_usadas': {
                'labels': [p.nome for p in mais_usadas],
                'data': [int(p.total) for p in mais_usadas]
            },
            'menos_usadas': {
                'labels': [p.nome for p in menos_usadas],
                'data': [int(p.total) for p in menos_usadas]
            },
            'top_funcionarios': {
                'labels': [f.nome for f in top_funcionarios],
                'data': [int(f.total) for f in top_funcionarios]
            },
            'dist_estoque': {
                'labels': [p.nome for p in dist_estoque],
                'data': [p.estoque_atual for p in dist_estoque]
            }
        }
