from sqlalchemy import Integer, Column, String, DateTime, ForeignKey, Float, JSON
from app.infrastructure.dataBase.db import Base
from enum import Enum
from sqlalchemy import Enum as SQLEnum

class Unidade(Base):
    __tablename__ = "unidades"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    endereco = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    regiao = Column(String, nullable=False)

class CategoriaProduto(str, Enum):
    LANCHE = "LANCHE"
    BEBIDA = "BEBIDA"
    SOBREMESA = "SOBREMESA"

class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=False)
    categoria = Column(SQLEnum(CategoriaProduto), nullable=False)


class Produto_Unidade(Base):
    __tablename__ = "produto_unidades"
    id = Column(Integer, primary_key=True)
    preco = Column(Float, nullable=False)
    unidade_id = Column(Integer, ForeignKey('unidades.id'), nullable=False)
    produto_id = Column(Integer, ForeignKey('produtos.id'), nullable=False)

class Estoque(Base):
    __tablename__ = "estoques"
    id = Column(Integer, primary_key=True)
    unidade_id = Column(Integer,ForeignKey('unidades.id'), nullable=False)
    quantidade = Column(Integer, nullable=False)
    produto_id = Column(Integer , ForeignKey('produtos.id'),nullable=False)

class PerfilLogado(str,Enum):
    CLIENTE = "CLIENTE"
    ATENDENTE = "ATENDENTE"
    COZINHA = "COZINHA"
    GERENTE = "GERENTE"
    COORDENADOR = "COORDENADOR"

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    senha_hash = Column(String, nullable=False)
    perfil = Column(SQLEnum(PerfilLogado), nullable=False)
    unidade_id = Column(Integer, ForeignKey('unidades.id'), nullable=True)

class StatusPedido(str,Enum):
    PAGAMENTO_PENDENTE = "PAGAMENTO_PENDENTE"
    EM_PREPARACAO = "EM_PREPARACAO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    NAO_AUTORIZADO = "NAO_AUTORIZADO"
    CANCELADO = "CANCELADO"

class CanalPedido(str, Enum):
    APP = "APP"
    WEB = 'WEB'
    BALCAO = "BALCAO"
    PICKUP = "PICKUP"
    TOTEM = "TOTEM"

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True)
    data = Column(DateTime, nullable=False)
    valor_total = Column(Float, nullable=False)
    canal = Column(SQLEnum(CanalPedido), nullable=False)
    status = Column(SQLEnum(StatusPedido),nullable=False)
    unidade_id = Column(Integer, ForeignKey('unidades.id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)

class ItemPedido(Base):
    __tablename__ = "item_pedidos"
    id = Column(Integer, primary_key=True)
    preco_unitario = Column(Float, nullable=False)
    quantidade = Column(Integer, nullable=False)
    pedido_id = Column(Integer, ForeignKey('pedidos.id'), nullable=False)
    produto_id = Column(Integer, ForeignKey('produtos.id'), nullable=False)


class StatusPg(str,Enum):
    APROVADO = "APROVADO"
    REPROVADO = "REPROVADO"

class Pagamento(Base):
    __tablename__ = "pagamentos"
    id = Column(Integer, primary_key=True)
    payload = Column(JSON, nullable=False)
    status_pagamento = Column(SQLEnum(StatusPg), nullable=False)
    valor = Column(Float, nullable=False)
    data_pagamento = Column(DateTime, nullable=False)
    pedido_id = Column(Integer, ForeignKey('pedidos.id'), nullable=False, unique=True)

    #   ERRO 500 AO TENTAR REALZAR O PEDIDO,
    #   ERRO 500 AO TENTAR REALZAR O PEDIDO,