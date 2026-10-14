from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.dataBase.db import get_db
from app.api.schemas import CriarEstoqueSchema
from app.api.dependencias import autorizacao_acesso
from app.infrastructure.dataBase.models import Estoque
from app.infrastructure.dataBase.models import Produto_Unidade


router_estoque = APIRouter(tags = ['Estoques'])
@router_estoque.post("/estoques", summary = 'Cadastra no estoque')
async def criar_estoque(dados: CriarEstoqueSchema, db: Session = Depends(get_db), usuario_logado = Depends(autorizacao_acesso(['GERENTE']))):
    estoque_precificado = db.query(Produto_Unidade).filter(Produto_Unidade.produto_id == dados.produto_id, Produto_Unidade.unidade_id == dados.unidade_id).first()
    if not estoque_precificado:
        raise HTTPException(status_code=404, detail='Cadastre o preço antes de cadastrar o estoque')
    estoque_duplicado = db.query(Estoque).filter(Estoque.unidade_id == dados.unidade_id, Estoque.produto_id == dados.produto_id).first()
    if estoque_duplicado:
        raise HTTPException(status_code = 409 , detail = 'Produto ja cadastrado no estoque')
    novo_estoque = Estoque(
        unidade_id = dados.unidade_id,
        produto_id = dados.produto_id,
        quantidade = dados.quantidade
    )
    db.add(novo_estoque)
    db.commit()
    db.refresh(novo_estoque)
    return {
        'id': novo_estoque.id,
        'unidade_id': novo_estoque.unidade_id,
        'produto_id': novo_estoque.produto_id,
        'quantidade': novo_estoque.quantidade
    }