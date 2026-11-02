from pydantic import BaseModel, Field


class Prato(BaseModel):
    nome: str
    ingredientes: list[str]
    culinaria: str
    confianca: float = Field(ge=0, le=1)