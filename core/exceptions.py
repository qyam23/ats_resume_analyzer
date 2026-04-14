from __future__ import annotations

from core.schemas import PipelineEvent


class AnalysisPipelineError(Exception):
    def __init__(self, stage: str, message: str, timeline: list[PipelineEvent]) -> None:
        super().__init__(message)
        self.stage = stage
        self.timeline = timeline
