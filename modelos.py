from pydantic import BaseModel, Field

class Prato(BaseModel):
    nome: str
    ingredientes: list[str]
    culinaria: str
    confianca: float = Field(ge=0, le=1)


from pydantic import BaseModel, Field

class Prato(BaseModel):
    e_prato: bool
    nome: str = ""
    ingredientes: list[str] = []
    culinaria: str = ""
    confianca: float = Field(ge=0, le=1)