from fastapi import APIRouter, Depends, HTTPException
from app.api.schemas import CriarUnidadeSchema
from app.infrastructure.dataBase.models import Unidade
from sqlalchemy.orm import Session
from app.infrastructure.dataBase.db import get_db
from app.api.dependencias import autorizacao_acesso

router_unidade = APIRouter(tags = ['Unidades'])

@router_unidade.post("/unidades")
async def criar_unidade(dados: CriarUnidadeSchema, db: Session = Depends(get_db), usuario_logado = Depends(autorizacao_acesso(["COORDENADOR"]))):
    nova_unidade = Unidade(
        nome=dados.nome,
        endereco=dados.endereco,
        telefone=dados.telefone,
        regiao=dados.regiao,
    )
    db.add(nova_unidade)
    db.commit()
    db.refresh(nova_unidade)
    return {
        "id": nova_unidade.id,
        "nome": nova_unidade.nome,
        "endereco": nova_unidade.endereco,
        "telefone": nova_unidade.telefone,
        "regiao": nova_unidade.regiao
    }