# from pydantic import BaseModel
# from typing import List, Optional

# # Exemplo de schema para um Documento
# class DocumentBase(BaseModel):
#     filename: str
#     source_url: Optional[str] = None

# class DocumentCreate(DocumentBase):
#     pass

# class Document(DocumentBase):
#     id: int
#     status: str

#     class Config:
#         orm_mode = True # or from_attributes = True for Pydantic v2

# # Exemplo de schema para um Relatório
# class ReportBase(BaseModel):
#     title: str

# class ReportCreate(ReportBase):
#     document_ids: List[int]

# class Report(ReportBase):
#     id: int
#     content_summary: str # ou uma estrutura mais complexa
#     charts_data: Optional[dict] = None # Dados para gráficos

#     class Config:
#         orm_mode = True # or from_attributes = True for Pydantic v2 