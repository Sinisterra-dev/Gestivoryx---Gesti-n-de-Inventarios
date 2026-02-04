from fastapi import APIRouter

router = APIRouter(
    prefix="/api/clientes",
    tags=["Clientes"]
)

@router.get("/")
def listar_clientes():
    return {"message": "Endpoint de clientes funcionando"}

