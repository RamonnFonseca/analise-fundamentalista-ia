from fastapi import APIRouter, HTTPException, Path
from typing import List
from app.services import cvm_service

router = APIRouter()

@router.post(
    "/process/{doc_type}/{year}",
    summary="Processa documentos da CVM para um tipo e ano específicos",
    response_description="Caminho do diretório onde os arquivos foram extraídos",
)
def process_cvm_documents_by_year(
    doc_type: str = Path(..., title="Tipo de Documento", description="ITR ou FRE", regex="^(ITR|FRE|itr|fre)$"),
    year: int = Path(..., title="Ano", description="Ano do documento a ser processado", ge=2010)
):
    """
    Inicia o processo de download e descompactação de um arquivo de dados da CVM.

    - **doc_type**: ITR (Informações Trimestrais) ou FRE (Formulário de Referência).
    - **year**: O ano para o qual os dados devem ser baixados.
    """
    doc_type_upper = doc_type.upper()
    
    # 1. Encontrar o nome do arquivo .zip correspondente ao ano
    available_files = cvm_service.list_available_zip_files(doc_type_upper)
    if not available_files:
        raise HTTPException(
            status_code=404,
            detail=f"Nenhum arquivo encontrado para {doc_type_upper}."
        )

    target_zip_file = None
    for file_name in available_files:
        if str(year) in file_name:
            target_zip_file = file_name
            break
    
    if not target_zip_file:
        raise HTTPException(
            status_code=404,
            detail=f"Nenhum arquivo encontrado para {doc_type_upper} no ano de {year}."
        )
    
    # 2. Chamar o serviço para baixar e descompactar o arquivo
    extracted_path = cvm_service.download_and_unzip_cvm_file(doc_type_upper, target_zip_file)

    if not extracted_path:
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao baixar ou descompactar o arquivo {target_zip_file}."
        )

    return {"message": "Processamento concluído com sucesso.", "extracted_path": extracted_path}

# @router.get("/{document_id}")
# async def get_document_status(document_id: str):
#     # Lógica para verificar status de processamento de um documento
#     return {"document_id": document_id, "status": "pending"} 