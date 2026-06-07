from fastapi import APIRouter

from app.schemas.review import GenerateMockExamRequest, GenerateMockExamResponse
from app.services.mock_exam_generator import generate_mock_exam

router = APIRouter()


@router.post("/generate-mock-exam", response_model=GenerateMockExamResponse)
def generate_mock_exam_endpoint(
    request: GenerateMockExamRequest,
) -> GenerateMockExamResponse:
    questions, message = generate_mock_exam(request.review_report, request.count)
    return GenerateMockExamResponse(questions=questions, message=message)
