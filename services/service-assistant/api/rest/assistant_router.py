from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from application.use_cases.ask_assistant_use_case import AskAssistantUseCase
from application.use_cases.generate_report_use_case import GenerateReportUseCase
from domain.exceptions.domain_exceptions import UnsafeQuestionException


class AskRequest(BaseModel):
    question: str


class ReportRequest(BaseModel):
    hours: int = 24


def get_router(
    ask_use_case: AskAssistantUseCase,
    report_use_case: GenerateReportUseCase,
) -> APIRouter:

    router = APIRouter()

    @router.post("/assistant/ask")
    async def ask(req: AskRequest):
        try:
            answer = await ask_use_case.execute(req.question)
            return {"answer": answer}
        except UnsafeQuestionException as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/assistant/report")
    async def report(req: ReportRequest = ReportRequest()):
        report_text = await report_use_case.execute(hours=req.hours)
        return {"report": report_text}

    return router