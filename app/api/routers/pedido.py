from fastapi import APIRouter, Depends, HTTPException
from app.api.schemas import CriarPedidoSchema
from sqlalchemy.orm import Session
from app.api.dependencias import autorizacao_acesso, autenticar_acesso
from app.infrastructure.dataBase.db import get_db
from app.infrastructure.dataBase.models import Estoque
from app.infrastructure.dataBase.models import Pedido
from app.infrastructure.dataBase.models import StatusPedido
from app.infrastructure.dataBase.models import StatusPg
from app.infrastructure.dataBase.models import Produto_Unidade
from app.infrastructure.dataBase.models import ItemPedido
from app.infrastructure.dataBase.models import Pagamento
import random
from datetime import datetime

router_pedido = APIRouter()


@router_pedido.post("/pedido", tags=["pedido"])
async def criar_novo_pedido(dados: CriarPedidoSchema, db: Session = Depends(get_db), usuario_logado=Depends(autorizacao_acesso(["ATENDENTE", "CLIENTE"]))):
    for item in dados.lista_itens:
        estoque_item = db.query(Estoque).filter(Estoque.produto_id == item.produto_id, Estoque.unidade_id == dados.unidade_id).first()
        if not estoque_item or item.quantidade > estoque_item.quantidade:
            raise HTTPException(status_code=409, detail='Estoque insuficiente')

    # LAÇO PARA CALCULAR O VALOR TOTAL DO PEDIDO
    valor_total_pedido = 0
    for item in dados.lista_itens:
        preco_produto = db.query(Produto_Unidade).filter(Produto_Unidade.produto_id == item.produto_id, Produto_Unidade.unidade_id == dados.unidade_id).first()
        valor_total_pedido += (preco_produto.preco * item.quantidade)

    # INSTANCIANDO UM NOVO PEDIDO E ADICIONANDO NO BANCO
    novo_pedido = Pedido(
        canal=dados.canal,
        unidade_id=dados.unidade_id,
        status=StatusPedido.PAGAMENTO_PENDENTE,
        data=datetime.now(),
        usuario_id=usuario_logado['id'],
        valor_total=valor_total_pedido)
    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)

    for informacao_item in dados.lista_itens:
        preco_por_item = db.query(Produto_Unidade).filter(Produto_Unidade.produto_id == informacao_item.produto_id, Produto_Unidade.unidade_id == dados.unidade_id).first()
        novo_item = ItemPedido(
            pedido_id=novo_pedido.id,
            produto_id=informacao_item.produto_id,
            preco_unitario=preco_por_item.preco,
            quantidade=informacao_item.quantidade,
        )
        db.add(novo_item)
    db.commit()
    return {
        'id': novo_pedido.id,
        'data': novo_pedido.data,
        'unidade': novo_pedido.unidade_id,
        'valor_total': novo_pedido.valor_total,
        'status_pedido': novo_pedido.status
    }


@router_pedido.post("/pedido/{id}/pagamento", tags=["pedido-pagamento"])
async def validar_pagamento(id: int, db: Session = Depends(get_db)):
    pagamento_pedido_id = db.query(Pedido).filter(Pedido.id == id).first()
    if not pagamento_pedido_id:
        raise HTTPException(status_code=404, detail= 'Pedido não encontrado' )
    if pagamento_pedido_id.status != StatusPedido.PAGAMENTO_PENDENTE:
        raise HTTPException(status_code=409, detail='Esse pagamento ja foi processado')
    if pagamento_pedido_id:
        aprovacao = random.choice([True, False])
        if aprovacao:
            status_do_pagamento = StatusPg.APROVADO
            status_do_pedido = StatusPedido.EM_PREPARACAO

            payload_status ={
                'status': 'aprovado',
                'mensagem': 'Pagamento processado com sucesso',

            }
            #ATUALIZA O NOVO STATUS DO PEDIDO
            pagamento_pedido_id.status = status_do_pedido
            novo_Pagamento = Pagamento(
                status_pagamento=status_do_pagamento,
                data_pagamento=datetime.now(),
                pedido_id = pagamento_pedido_id.id,
                payload = payload_status,
                valor = pagamento_pedido_id.valor_total
            )
            db.add(novo_Pagamento)

            itens_do_pedido = db.query(ItemPedido).filter(ItemPedido.pedido_id == pagamento_pedido_id.id ).all()
            for item in itens_do_pedido:
                itens_do_estoque = db.query(Estoque).filter(Estoque.produto_id == item.produto_id, Estoque.unidade_id == pagamento_pedido_id.unidade_id).first()
                itens_do_estoque.quantidade = itens_do_estoque.quantidade - item.quantidade
            db.commit()
            db.refresh(novo_Pagamento)
            return novo_Pagamento
        else:
            status_do_pedido_reprovado = StatusPedido.NAO_AUTORIZADO
            status_do_pagamento_reprovado =StatusPg.REPROVADO
            payload_status_reprovado = {
                'status': 'reprovado',
                'mensagem': 'Pagamento invalido',
            }
            pagamento_pedido_id.status = status_do_pedido_reprovado
            novo_pagamento_reprovado = Pagamento(
                status_pagamento=status_do_pagamento_reprovado,
                data_pagamento=datetime.now(),
                pedido_id=pagamento_pedido_id.id,
                payload=payload_status_reprovado,
                valor=pagamento_pedido_id.valor_total
            )
            db.add(novo_pagamento_reprovado)
            db.commit()
            db.refresh(novo_pagamento_reprovado)
            return novo_pagamento_reprovado

@router_pedido.post("/pedido/{id}/pronto", tags=["pedido-pronto"])
async def marcar_como_pronto(id: int, db: Session = Depends(get_db), usuario_logado=Depends(autorizacao_acesso(["COZINHA"]))):
    status_pedido_id = db.query(Pedido).filter(Pedido.id == id).first()
    if not status_pedido_id:
        raise HTTPException(status_code= 404 , detail = "Esse pedido nao existe" )
    elif status_pedido_id.status != StatusPedido.EM_PREPARACAO:
        raise HTTPException(status_code = 409, detail= 'Esse pedido não esta na lista "EM PREPARACAO"' )
    else:
        status_pedido_id.status = StatusPedido.PRONTO
        db.commit()
        db.refresh(status_pedido_id)
        return status_pedido_id

@router_pedido.post("/pedido/{id}/entregue", tags=["pedido-entregue"])
async def marcar_como_entregue(id: int, db: Session = Depends(get_db), usuario_logado = Depends(autorizacao_acesso(["ATENDENTE"]))):
    status_pedido_id = db.query(Pedido).filter(Pedido.id == id).first()
    if not status_pedido_id:
        raise HTTPException(status_code= 404 , detail = "Esse pedido nao existe" )
    elif status_pedido_id.status != StatusPedido.PRONTO:
        raise HTTPException(status_code = 409, detail= 'Esse pedido não esta pronto para ser entregue' )
    else:
        status_pedido_id.status = StatusPedido.ENTREGUE
        db.commit()
        db.refresh(status_pedido_id)
        return status_pedido_id

@router_pedido.post("/pedido/{id}/cancelado", tags=["pedido-cancelado"])
async def marcar_como_cancelado (id: int, db: Session = Depends(get_db), usuario_logado = Depends(autorizacao_acesso(["ATENDENTE", "CLIENTE"])) ):
    status_pedido_id = db.query(Pedido).filter(Pedido.id == id).first()
    if not status_pedido_id:
        raise HTTPException(status_code=404, detail="Esse pedido nao existe")
    if status_pedido_id.status != StatusPedido.PAGAMENTO_PENDENTE:
        raise HTTPException(status_code=409, detail= 'Esse pedido nao pode mais ser cancelado')
    else:
        status_pedido_id.status = StatusPedido.CANCELADO
        db.commit()
        db.refresh(status_pedido_id)
        return status_pedido_id


