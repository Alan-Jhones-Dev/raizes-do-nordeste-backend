from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.schemas import CriarProdutoSchema
from app.infrastructure.dataBase.models import Produto
from app.api.dependencias import autorizacao_acesso
from app.infrastructure.dataBase.db import get_db

router_produto = APIRouter(tags = ['Produtos'])

@router_produto.post('/produtos')
async def criar_produto(dados: CriarProdutoSchema, db: Session = Depends(get_db), usuario_logado = Depends(autorizacao_acesso(["GERENTE"]))):
    novo_produto = Produto(
        nome = dados.nome,
        descricao = dados.descricao,
        categoria = dados.categoria
    )
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return{
        "id": novo_produto.id,
        "nome": novo_produto.nome,
        "descricao": novo_produto.descricao,
        "categoria": novo_produto.categoria
    }