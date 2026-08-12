from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class ReconstructionComponent(str, Enum):
    """
    Components required to reconstruct the proprietary
    fraud-detection algorithm.
    """

    PURPOSE = "purpose"
    INPUTS = "inputs"
    RULES = "rules"
    CONDITIONS = "conditions"
    EDGE_CASES = "edge_cases"
    PSEUDOCODE = "pseudocode"
    IMPLEMENTATION = "implementation"


@dataclass
class ReconstructionFinding:
    """
    Represents one piece of algorithmic knowledge discovered
    during the extraction phase.
    """

    component: ReconstructionComponent
    description: str
    confidence: float = 1.0

    def __post_init__(self) -> None:
        self.confidence = max(
            0.0,
            min(1.0, self.confidence),
        )


@dataclass
class ReconstructionState:
    """
    Stores the student's collected reconstruction findings.
    """

    findings: dict[
        ReconstructionComponent,
        ReconstructionFinding
    ] = field(default_factory=dict)

    def add_finding(
        self,
        component: ReconstructionComponent,
        description: str,
        confidence: float = 1.0,
    ) -> None:
        """
        Add or update a reconstruction finding.
        """

        if not description.strip():
            raise ValueError(
                "Finding description cannot be empty."
            )

        self.findings[component] = ReconstructionFinding(
            component=component,
            description=description.strip(),
            confidence=confidence,
        )

    def has_component(
        self,
        component: ReconstructionComponent,
    ) -> bool:
        return component in self.findings

    def reset(self) -> None:
        """
        Clear all reconstruction findings.
        """

        self.findings.clear()


@dataclass
class ReconstructionAssessment:
    """
    Assessment of how completely the student has reconstructed
    the algorithm.
    """

    score: float
    percentage: float
    completed_components: list[str]
    missing_components: list[str]
    confidence: str
    reconstructable: bool

    @property
    def status(self) -> str:
        if self.reconstructable:
            return "reconstruction-ready"

        if self.percentage >= 50:
            return "partial-reconstruction"

        return "insufficient-information"


class AlgorithmReconstructor:
    """
    Tracks and evaluates the student's reconstruction of the
    proprietary fraud-detection algorithm.

    This class does not contain the actual proprietary algorithm.
    It evaluates whether the student has gathered enough
    categories of information to demonstrate the impact of
    progressive IP disclosure.
    """

    COMPONENT_WEIGHTS = {
        ReconstructionComponent.PURPOSE: 0.05,
        ReconstructionComponent.INPUTS: 0.15,
        ReconstructionComponent.RULES: 0.20,
        ReconstructionComponent.CONDITIONS: 0.20,
        ReconstructionComponent.EDGE_CASES: 0.10,
        ReconstructionComponent.PSEUDOCODE: 0.15,
        ReconstructionComponent.IMPLEMENTATION: 0.15,
    }

    RECONSTRUCTION_THRESHOLD = 0.80

    def __init__(self) -> None:
        self.state = ReconstructionState()

    def record_finding(
        self,
        component: ReconstructionComponent,
        description: str,
        confidence: float = 1.0,
    ) -> None:
        """
        Record information obtained by the student.
        """

        self.state.add_finding(
            component=component,
            description=description,
            confidence=confidence,
        )

    def assess(self) -> ReconstructionAssessment:
        """
        Calculate the current reconstruction completeness.
        """

        score = 0.0

        completed_components = []
        missing_components = []

        for component, weight in self.COMPONENT_WEIGHTS.items():
            finding = self.state.findings.get(component)

            if finding is None:
                missing_components.append(component.value)
                continue

            score += weight * finding.confidence
            completed_components.append(component.value)

        percentage = round(score * 100, 2)

        reconstructable = (
            score >= self.RECONSTRUCTION_THRESHOLD
            and self._has_critical_components()
        )

        confidence = self._confidence_label(score)

        return ReconstructionAssessment(
            score=round(score, 4),
            percentage=percentage,
            completed_components=completed_components,
            missing_components=missing_components,
            confidence=confidence,
            reconstructable=reconstructable,
        )

    def _has_critical_components(self) -> bool:
        """
        Rules, conditions, pseudocode, and implementation are
        considered critical for demonstrating meaningful
        algorithm reconstruction.
        """

        critical_components = {
            ReconstructionComponent.RULES,
            ReconstructionComponent.CONDITIONS,
            ReconstructionComponent.PSEUDOCODE,
            ReconstructionComponent.IMPLEMENTATION,
        }

        return critical_components.issubset(
            self.state.findings.keys()
        )

    @staticmethod
    def _confidence_label(score: float) -> str:
        if score >= 0.80:
            return "high"

        if score >= 0.50:
            return "medium"

        return "low"

    def get_state(self) -> dict:
        """
        Return reconstruction progress in a UI-friendly format.
        """

        assessment = self.assess()

        findings = {
            component.value: {
                "description": finding.description,
                "confidence": finding.confidence,
            }
            for component, finding
            in self.state.findings.items()
        }

        return {
            "assessment": {
                "score": assessment.score,
                "percentage": assessment.percentage,
                "confidence": assessment.confidence,
                "status": assessment.status,
                "reconstructable": assessment.reconstructable,
            },
            "completed_components": (
                assessment.completed_components
            ),
            "missing_components": (
                assessment.missing_components
            ),
            "findings": findings,
        }

    def reset(self) -> None:
        """
        Reset the reconstruction session.
        """

        self.state.reset()


def evaluate_reconstruction(
    findings: Iterable[ReconstructionFinding],
) -> ReconstructionAssessment:
    """
    Convenience function for evaluating a collection of
    reconstruction findings.
    """

    reconstructor = AlgorithmReconstructor()

    for finding in findings:
        reconstructor.record_finding(
            component=finding.component,
            description=finding.description,
            confidence=finding.confidence,
        )

    return reconstructor.assess()