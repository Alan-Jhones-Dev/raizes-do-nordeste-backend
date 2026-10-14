from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.dataBase.db import get_db
from app.api.schemas import CriarProdutoUnidadeSchema
from app.infrastructure.dataBase.models import Produto_Unidade

from app.api.dependencias import autorizacao_acesso

router_produto_unidade = APIRouter(tags = ['Produto-Unidades'])
@router_produto_unidade.post('/produto-unidades')
async def criar_produto_unidade(dados: CriarProdutoUnidadeSchema, db: Session = Depends(get_db), usuario_logado = Depends(autorizacao_acesso(['COORDENADOR']))):
    novo_produto_unidade = Produto_Unidade(
        produto_id=dados.produto_id,
        unidade_id=dados.unidade_id,
        preco = dados.preco
    )
    db.add(novo_produto_unidade)
    db.commit()
    db.refresh(novo_produto_unidade)
    return {
        'id': novo_produto_unidade.id,
        'produto_id': novo_produto_unidade.produto_id,
        'unidade_id': novo_produto_unidade.unidade_id,
        'preco': novo_produto_unidade.preco

    }