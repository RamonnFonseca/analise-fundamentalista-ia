from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services import cvm_service, ai_service

router = APIRouter()

class ReportRequest(BaseModel):
    cnpj: str = Field(..., description="CNPJ da empresa no formato XX.XXX.XXX/XXXX-XX", pattern=r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$")
    year: int = Field(..., description="Ano do relatório", ge=2010)
    doc_type: str = Field(..., description="Tipo de documento (ITR ou FRE)", pattern="^(ITR|FRE|itr|fre)$")

@router.post(
    "/generate",
    summary="Gera um relatório de análise fundamentalista e dados financeiros estruturados",
    response_description="Um JSON com a análise textual e um resumo financeiro"
)
def generate_report(request: ReportRequest):
    """
    Gera uma análise fundamentalista completa para uma empresa, utilizando os dados
    da CVM e um modelo de linguagem avançado.
    """
    # 1. Obter os dados financeiros usando o cvm_service
    financial_data = cvm_service.get_financial_statements(
        doc_type=request.doc_type.upper(),
        year=request.year,
        cnpj=request.cnpj
    )

    if not financial_data:
        raise HTTPException(
            status_code=404,
            detail=f"Não foi possível encontrar dados financeiros para o CNPJ {request.cnpj} para {request.doc_type.upper()} de {request.year}."
        )

    # 2. Gerar a análise e os dados estruturados usando o ai_service
    analysis_data = ai_service.generate_financial_analysis(financial_data)

    if not analysis_data or "report" not in analysis_data or "financial_summary" not in analysis_data:
        raise HTTPException(
            status_code=500,
            detail="Ocorreu um erro no serviço de IA ao tentar gerar a análise."
        )

    return {
        "company_cnpj": request.cnpj,
        "year": request.year,
        "report": analysis_data["report"],
        "financial_summary": analysis_data["financial_summary"]
    }

# @router.get("/{report_id}")
# async def get_generated_report(report_id: str):
#     # Lógica para obter um relatório gerado
#     return {"report_id": report_id, "content": "..."} 