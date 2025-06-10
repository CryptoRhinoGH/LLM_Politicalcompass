# llm_response.py

from dataclasses import dataclass, asdict


@dataclass
class LLMResponse:
    id: int
    question: str
    answer: str

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "LLMResponse":
        return LLMResponse(
            id=data["id"],
            question=data["question"],
            answer=data["answer"]
        )
