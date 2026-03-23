from app import db
from app.models import Produto, Movimentacao
from datetime import datetime

class EstoqueService:
    @staticmethod
    def registrar_movimentacao(produto_id, tipo, quantidade, funcionario_id=None, observacao=None):
        produto = Produto.query.get(produto_id)
        if not produto:
            return False, "Produto não encontrado"

        if tipo == 'SAIDA' and produto.estoque_atual < quantidade:
            return False, "Estoque insuficiente"

        mov = Movimentacao(
            produto_id=produto_id,
            tipo=tipo,
            quantidade=quantidade,
            funcionario_id=funcionario_id,
            observacao=observacao,
            data=datetime.now()
        )

        if tipo == 'ENTRADA':
            produto.estoque_atual += quantidade
        elif tipo == 'SAIDA':
            produto.estoque_atual -= quantidade
        elif tipo == 'AJUSTE':
            produto.estoque_atual = quantidade # No ajuste, definimos o valor real

        db.session.add(mov)
        db.session.commit()
        return True, "Movimentação registrada com sucesso"

    @staticmethod
    def get_alertas_estoque_baixo():
        return Produto.query.filter(Produto.estoque_atual <= Produto.estoque_minimo).all()
