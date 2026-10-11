from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.schemas.common import EngineResult, Finding
from app.services.ingestion.extractor import ExtractedDocument
from app.models.journal import GuidelineVersion


class BaseEvaluationEngine(ABC):
    @abstractmethod
    def evaluate(
        self,
        document: ExtractedDocument,
        guideline_version: Optional[GuidelineVersion] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> EngineResult:
        """
        Executes engine checks against the extracted manuscript and returns a standardized EngineResult.
        """
        pass
