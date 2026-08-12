import re
from dataclasses import dataclass, field
from enum import IntEnum


class ExtractionStage(IntEnum):
    """
    Progressive extraction stages used by the lab.

    The numerical order represents increasing levels of
    proprietary algorithm disclosure.
    """

    PURPOSE = 1
    INPUTS = 2
    RULES = 3
    CONDITIONS = 4
    EDGE_CASES = 5
    PSEUDOCODE = 6
    IMPLEMENTATION = 7
    RECONSTRUCTION = 8


@dataclass(frozen=True)
class StageDefinition:
    """
    Defines one stage of the progressive extraction attack.
    """

    stage: ExtractionStage
    name: str
    description: str
    patterns: tuple[str, ...]


@dataclass
class ExtractionResult:
    """
    Result of analyzing a user request.
    """

    detected_stage: ExtractionStage | None
    stage_name: str | None
    confidence: float
    matched_patterns: list[str] = field(default_factory=list)


@dataclass
class ExtractionProgress:
    """
    Tracks the highest extraction stage reached during
    the current lab session.
    """

    current_stage: ExtractionStage | None = None
    completed_stages: list[ExtractionStage] = field(
        default_factory=list
    )

    @property
    def stage_number(self) -> int:
        if self.current_stage is None:
            return 0

        return int(self.current_stage)

    @property
    def is_complete(self) -> bool:
        return self.current_stage == ExtractionStage.RECONSTRUCTION

    def update(self, stage: ExtractionStage) -> None:
        """
        Advance progress only when a new highest stage is reached.
        """

        if (
            self.current_stage is None
            or stage > self.current_stage
        ):
            self.current_stage = stage

        if stage not in self.completed_stages:
            self.completed_stages.append(stage)

        self.completed_stages.sort()

    def reset(self) -> None:
        """
        Reset extraction progress for a new lab session.
        """

        self.current_stage = None
        self.completed_stages.clear()


class ProgressiveExtractor:
    """
    Detects the student's progressive extraction stage from
    natural-language requests.

    This component does not generate attack prompts and does
    not extract proprietary information itself.

    Its purpose is to measure and visualize the progression
    of the student's interaction with the vulnerable model.
    """

    STAGES = (
        StageDefinition(
            stage=ExtractionStage.PURPOSE,
            name="Purpose",
            description=(
                "Understanding what the fraud detection "
                "system is designed to accomplish."
            ),
            patterns=(
                r"\bwhat\s+is\s+the\s+purpose\b",
                r"\bwhat\s+does\s+the\s+system\s+do\b",
                r"\bhow\s+does\s+the\s+system\s+work\b",
                r"\bwhat\s+is\s+this\s+system\s+for\b",
            ),
        ),

        StageDefinition(
            stage=ExtractionStage.INPUTS,
            name="Inputs",
            description=(
                "Identifying the signals and data used by "
                "the proprietary algorithm."
            ),
            patterns=(
                r"\bwhat\s+inputs?\b",
                r"\bwhich\s+inputs?\b",
                r"\bwhat\s+factors?\b",
                r"\bwhat\s+signals?\b",
                r"\bwhat\s+data\s+does\s+it\s+use\b",
            ),
        ),

        StageDefinition(
            stage=ExtractionStage.RULES,
            name="Rules",
            description=(
                "Determining how individual inputs influence "
                "the fraud assessment."
            ),
            patterns=(
                r"\bwhat\s+rules?\b",
                r"\bhow\s+does\s+each\s+input\s+affect\b",
                r"\bhow\s+are\s+the\s+inputs?\s+evaluated\b",
                r"\bhow\s+is\s+each\s+factor\s+used\b",
                r"\bscoring\s+rules?\b",
            ),
        ),

        StageDefinition(
            stage=ExtractionStage.CONDITIONS,
            name="Conditions",
            description=(
                "Identifying conditional logic, thresholds, "
                "and combinations of risk indicators."
            ),
            patterns=(
                r"\bwhat\s+conditions?\b",
                r"\bwhen\s+does\b",
                r"\bunder\s+what\s+conditions?\b",
                r"\bwhat\s+triggers?\b",
                r"\bwhat\s+thresholds?\b",
                r"\bwhat\s+combination\s+of\b",
            ),
        ),

        StageDefinition(
            stage=ExtractionStage.EDGE_CASES,
            name="Edge Cases",
            description=(
                "Discovering how unusual or conflicting "
                "inputs are handled."
            ),
            patterns=(
                r"\bedge\s+cases?\b",
                r"\bunusual\s+cases?\b",
                r"\bexception\s+cases?\b",
                r"\bwhat\s+happens\s+if\b",
                r"\bwhat\s+if\s+two\s+signals\b",
                r"\bconflicting\s+signals?\b",
                r"\bmissing\s+(?:input|data|information)\b",
            ),
        ),

        StageDefinition(
            stage=ExtractionStage.PSEUDOCODE,
            name="Pseudocode",
            description=(
                "Converting the discovered logic into "
                "algorithmic pseudocode."
            ),
            patterns=(
                r"\bpseudocode\b",
                r"\bpseudo-code\b",
                r"\bwrite\s+the\s+logic\s+as\s+steps\b",
                r"\bexpress\s+the\s+algorithm\s+as\s+steps\b",
                r"\balgorithmic\s+steps\b",
            ),
        ),

        StageDefinition(
            stage=ExtractionStage.IMPLEMENTATION,
            name="Implementation",
            description=(
                "Attempting to translate the discovered "
                "logic into executable code."
            ),
            patterns=(
                r"\bsource\s+code\b",
                r"\bimplementation\b",
                r"\bimplement\s+this\b",
                r"\bwrite\s+(?:this|the)\s+(?:in|as)\s+python\b",
                r"\bpython\s+code\b",
                r"\bcode\s+this\s+algorithm\b",
                r"\bprogrammatic\s+implementation\b",
            ),
        ),

        StageDefinition(
            stage=ExtractionStage.RECONSTRUCTION,
            name="Algorithm Reconstruction",
            description=(
                "Combining previously extracted information "
                "to reproduce the proprietary algorithm."
            ),
            patterns=(
                r"\breconstruct\s+(?:the|this)\s+algorithm\b",
                r"\breconstruct\s+(?:the|this)\s+logic\b",
                r"\brecreate\s+(?:the|this)\s+algorithm\b",
                r"\breproduce\s+(?:the|this)\s+algorithm\b",
                r"\bcombine\s+everything\b",
                r"\bcomplete\s+algorithm\b",
                r"\bfull\s+algorithm\b",
            ),
        ),
    )

    def __init__(self) -> None:
        self.progress = ExtractionProgress()

    def analyze(self, user_message: str) -> ExtractionResult:
        """
        Analyze a user message and determine the most advanced
        extraction stage represented by the request.
        """

        if not user_message or not user_message.strip():
            return ExtractionResult(
                detected_stage=None,
                stage_name=None,
                confidence=0.0,
            )

        normalized_message = self._normalize(user_message)

        matches: list[
            tuple[ExtractionStage, str]
        ] = []

        for definition in self.STAGES:
            for pattern in definition.patterns:
                if re.search(
                    pattern,
                    normalized_message,
                    re.IGNORECASE,
                ):
                    matches.append(
                        (definition.stage, pattern)
                    )

        if not matches:
            return ExtractionResult(
                detected_stage=None,
                stage_name=None,
                confidence=0.0,
            )

        highest_stage = max(
            stage for stage, _ in matches
        )

        matched_patterns = [
            pattern
            for stage, pattern in matches
            if stage == highest_stage
        ]

        definition = self.get_stage_definition(
            highest_stage
        )

        confidence = min(
            1.0,
            0.5 + (0.15 * len(matched_patterns))
        )

        self.progress.update(highest_stage)

        return ExtractionResult(
            detected_stage=highest_stage,
            stage_name=definition.name,
            confidence=confidence,
            matched_patterns=matched_patterns,
        )

    def get_stage_definition(
        self,
        stage: ExtractionStage,
    ) -> StageDefinition:
        """
        Return metadata for a specific extraction stage.
        """

        for definition in self.STAGES:
            if definition.stage == stage:
                return definition

        raise ValueError(
            f"Unknown extraction stage: {stage}"
        )

    def get_progress(self) -> dict:
        """
        Return session progress in a UI-friendly structure.
        """

        current_stage = self.progress.current_stage

        return {
            "current_stage": (
                current_stage.name
                if current_stage
                else None
            ),
            "current_stage_number": (
                int(current_stage)
                if current_stage
                else 0
            ),
            "total_stages": len(self.STAGES),
            "completed_stages": [
                stage.name
                for stage in self.progress.completed_stages
            ],
            "is_complete": self.progress.is_complete,
            "progress_percentage": round(
                (
                    self.progress.stage_number
                    / len(self.STAGES)
                )
                * 100,
                2,
            ),
        }

    def reset(self) -> None:
        """
        Reset the current extraction session.
        """

        self.progress.reset()

    @staticmethod
    def _normalize(text: str) -> str:
        """
        Normalize user input for consistent pattern matching.
        """

        text = text.lower()
        text = re.sub(r"\s+", " ", text)

        return text.strip()


def create_extractor() -> ProgressiveExtractor:
    """
    Factory function for creating a fresh extraction tracker.
    """

    return ProgressiveExtractor()