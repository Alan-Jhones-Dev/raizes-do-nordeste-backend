from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from app.api.routers.auth import router_auth
from app.api.routers.usuarios import router_usuario
from app.api.routers.produto import router_produto
from app.api.routers.produto_unidade import router_produto_unidade
from app.api.routers.unidade import router_unidade
from app.api.routers.estoque import router_estoque
from app.api.routers.pedido import router_pedido
from http import HTTPStatus


system = FastAPI( title= 'RAIZES DO NORDESTE')
@system.exception_handler(HTTPException)
async def tratamento_de_erros_http(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content = {
            'status': exc.status_code,
            'erro':  HTTPStatus(exc.status_code).phrase,
            'mensagem':exc.detail
        }
    )

@system.exception_handler(RequestValidationError)
async def tratamento_de_erro_request(request: Request, exc: RequestValidationError):
    primeiro_erro = exc.errors()[0]
    campo = primeiro_erro['loc'][-1]
    return JSONResponse(
        status_code= 422,
        content = {
            'status': 422,
            'erro':HTTPStatus(422).phrase,
            'mensagem': f"{campo}: {primeiro_erro['msg']}"
        }
    )

system.include_router(router_auth)
system.include_router(router_usuario)
system.include_router(router_produto)
system.include_router(router_produto_unidade)
system.include_router(router_unidade)
system.include_router(router_estoque)
system.include_router(router_pedido)


