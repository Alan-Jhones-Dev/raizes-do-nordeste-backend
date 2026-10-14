from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from app.api.schemas import CadastrarUsuarioSchema
from app.domain.hashes import gerar_hash
from app.infrastructure.dataBase.models import Usuario
from app.infrastructure.dataBase.db import get_db

router_usuario = APIRouter(tags = ['Usuarios'])

@router_usuario.post("/usuarios")
async def usuarios(dados:CadastrarUsuarioSchema, db: Session = Depends(get_db)):
    validar_email = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if validar_email:
        raise HTTPException(status_code=409, detail='Email inexistente ou ja cadastrado')
    else:
        novo_hash_senha = gerar_hash(dados.senha)
        novo_usuario = Usuario(nome= dados.nome, email=dados.email, senha_hash= novo_hash_senha, perfil=dados.perfil)
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        return {'id': novo_usuario.id,
                'nome': novo_usuario.nome,
                'email': novo_usuario.email,
                'perfil': novo_usuario.perfil,}
