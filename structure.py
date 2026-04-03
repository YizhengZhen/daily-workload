from pydantic import BaseModel, Field
from typing import Optional


class PaperAnalysis(BaseModel):
    """Structured output for AI analysis of research papers."""
    # Core fields from original structure
    tldr: str = Field(description="One-sentence summary (English)")
    motivation: str = Field(description="Research motivation/goal")
    method: str = Field(description="Methodology/approach")
    result: str = Field(description="Key results/findings")
    conclusion: str = Field(description="Main conclusion")
    
    # New fields for scoring
    score: float = Field(
        description="Relevance score 0-10 based on research directions. "
                   "0=completely unrelated, 10=perfectly aligned",
        ge=0.0,
        le=10.0
    )
    recommendation: bool = Field(
        description="Whether to recommend reading this paper (True/False) "
                   "based on score threshold and research relevance"
    )
    reasoning: str = Field(
        description="Brief explanation for the score and recommendation "
                   "(2-3 sentences)"
    )
    
    # Optional fields
    key_contributions: Optional[str] = Field(
        default="",
        description="Key contributions (if any standout)"
    )
    limitations: Optional[str] = Field(
        default="",
        description="Limitations or weaknesses noted"
    )
    follow_up_questions: Optional[str] = Field(
        default="",
        description="Interesting follow-up questions"
    )