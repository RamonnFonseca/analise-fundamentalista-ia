# Funções para interagir com o banco de dados (CRUD operations).
# Exemplo com SQLAlchemy:
# from sqlalchemy.orm import Session
# from .. import models, schemas

# def get_document(db: Session, document_id: int):
#     return db.query(models.DocumentDB).filter(models.DocumentDB.id == document_id).first()

# def create_document(db: Session, document: schemas.DocumentCreate):
#     db_document = models.DocumentDB(**document.dict()) # ou model_dump() para Pydantic v2
#     db.add(db_document)
#     db.commit()
#     db.refresh(db_document)
#     return db_document 