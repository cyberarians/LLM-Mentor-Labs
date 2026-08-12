import re
from dataclasses import dataclass


@dataclass(frozen=True)
class GuardResult:
    """
    Result returned by the intellectual-property guard.
    """

    allowed: bool
    content: str
    detected_categories: tuple[str, ...]
    risk_score: int


class IPGuard:
    """
    Defense-in-depth output guard for the
    Proprietary Algorithm & Intellectual Property
    Exposure lab.

    The guard protects against disclosure of:

    - Proprietary scoring methodology
    - Factor-level scoring contributions
    - Internal decision rules
    - Thresholds and boundaries
    - Weighting logic
    - Interaction logic
    - Override logic
    - Edge-case logic
    - Pseudocode
    - Source code
    - Internal implementation details

    The primary mitigation remains preventing proprietary
    implementation details from entering the LLM context.
    """

    SAFE_RESPONSE = (
        "I can provide a high-level explanation of fraud-risk "
        "assessment, but I cannot disclose proprietary scoring "
        "logic, factor-level contributions, formulas, weights, "
        "thresholds, decision rules, override mechanisms, "
        "pseudocode, or implementation details."
    )

    # =========================================================
    # 1. Explicit proprietary information
    # =========================================================

    EXPLICIT_PATTERNS = {
        "source_code": (
            r"\bsource\s+code\b",
            r"\bsource-code\b",
            r"\bimplementation\s+code\b",
            r"\bpython\s+implementation\b",
            r"\bexecutable\s+implementation\b",
        ),

        "pseudocode": (
            r"\bpseudocode\b",
            r"\bpseudo-code\b",
            r"\balgorithmic\s+steps\b",
        ),

        "algorithm": (
            r"\bproprietary\s+algorithm\b",
            r"\binternal\s+algorithm\b",
            r"\bconfidential\s+algorithm\b",
            r"\bcomplete\s+algorithm\b",
            r"\bfull\s+algorithm\b",
        ),

        "formula": (
            r"\bproprietary\s+formula\b",
            r"\bexact\s+formula\b",
            r"\bscoring\s+formula\b",
            r"\bscoring\s+equation\b",
        ),

        "threshold": (
            r"\bexact\s+threshold\b",
            r"\bexact\s+thresholds\b",
            r"\bthreshold\s+value\b",
            r"\bthreshold\s+values\b",
            r"\bdecision\s+threshold\b",
            r"\brisk\s+threshold\b",
            r"\bcut[-\s]?off\s+value\b",
        ),

        "weights": (
            r"\bexact\s+weight\b",
            r"\bexact\s+weights\b",
            r"\bscoring\s+weight\b",
            r"\bscoring\s+weights\b",
            r"\bweighting\s+strategy\b",
            r"\bweighting\s+mechanism\b",
        ),

        "decision_boundary": (
            r"\bdecision\s+boundary\b",
            r"\bdecision\s+boundaries\b",
            r"\brisk\s+boundary\b",
            r"\brisk\s+boundaries\b",
            r"\bclassification\s+boundary\b",
        ),

        "reconstruction": (
            r"\balgorithm\s+reconstruction\b",
            r"\breconstruct\s+(?:the|this)\s+algorithm\b",
            r"\brecreate\s+(?:the|this)\s+algorithm\b",
            r"\breproduce\s+(?:the|this)\s+algorithm\b",
        ),
    }

    # =========================================================
    # 2. Internal scoring / decision logic
    # =========================================================

    INTERNAL_LOGIC_PATTERNS = {
        "internal_scoring": (
            r"\binternal\s+scoring\b",
            r"\bproprietary\s+scoring\b",
            r"\bscoring\s+methodology\b",
            r"\bscoring\s+mechanism\b",
            r"\bhow\s+the\s+score\s+is\s+calculated\b",
            r"\bhow\s+the\s+score\s+is\s+computed\b",
        ),

        "factor_contribution": (
            r"\bcontribution\s+to\s+the\s+(?:overall\s+)?(?:fraud\s+)?risk\s+score\b",
            r"\bcontributes?\s+to\s+the\s+(?:overall\s+)?(?:fraud\s+)?risk\s+score\b",
            r"\bcontributes?\s+to\s+the\s+overall\s+score\b",
            r"\baffects?\s+the\s+(?:overall\s+)?(?:fraud\s+)?risk\s+score\b",
            r"\binfluences?\s+the\s+(?:overall\s+)?(?:fraud\s+)?risk\s+score\b",
            r"\bimpact\s+on\s+the\s+(?:overall\s+)?(?:fraud\s+)?risk\s+score\b",
        ),

        "factor_weighting": (
            r"\bweighted\s+more\s+heavily\b",
            r"\bweighted\s+less\s+heavily\b",
            r"\bincrease\s+the\s+weight\b",
            r"\breduce\s+the\s+weight\b",
            r"\bweight\s+assigned\s+to\b",
            r"\brelative\s+weight\b",
        ),

        "conditional_logic": (
            r"\binternal\s+conditional\s+logic\b",
            r"\bproprietary\s+conditional\s+logic\b",
            r"\binternal\s+conditions?\b",
            r"\bproprietary\s+conditions?\b",
            r"\binternal\s+rules?\b",
            r"\bproprietary\s+rules?\b",
            r"\bdecision\s+rules?\b",
            r"\bscoring\s+rules?\b",
        ),

        "interaction_logic": (
            r"\binteraction\s+rules?\b",
            r"\brisk\s+factor\s+interaction\b",
            r"\bsignal\s+interaction\b",
            r"\bcombination\s+of\s+risk\s+factors\b",
            r"\bcombination\s+of\s+signals\b",
            r"\bcombined\s+effect\b",
            r"\bcollectively\s+result\b",
            r"\bcollectively\s+contribute\b",
        ),

        "override_logic": (
            r"\boverride\s+mechanism\b",
            r"\boverride\s+logic\b",
            r"\boverride\s+condition\b",
            r"\binternal\s+override\b",
            r"\bcalculation\s+is\s+overridden\b",
        ),

        "exception_logic": (
            r"\bedge[-\s]?case\s+logic\b",
            r"\bedge[-\s]?case\s+handling\b",
            r"\bexception\s+logic\b",
            r"\bspecial\s+case\s+logic\b",
        ),

        "decision_path": (
            r"\binternal\s+decision\s+logic\b",
            r"\bproprietary\s+decision\s+logic\b",
            r"\binternal\s+decision\s+path\b",
            r"\bproprietary\s+decision\s+path\b",
            r"\bdecision\s+mechanism\b",
        ),
    }

    # =========================================================
    # 3. Factor-level scoring language
    #
    # This is the important part for the response you showed.
    #
    # Normal:
    #   "Device risk is one factor considered by the system."
    #
    # Sensitive:
    #   "Device risk contributes moderately to the overall score."
    #
    # The second one reveals internal scoring behavior.
    # =========================================================

    FACTOR_TERMS = (
        r"transaction\s+amount",
        r"transaction\s+velocity",
        r"device\s+risk",
        r"behavioral\s+anomaly",
        r"geographic\s+risk",
        r"account\s+history",
        r"location",
        r"risk\s+factor",
        r"risk\s+factors",
        r"risk\s+signal",
        r"risk\s+signals",
    )

    CONTRIBUTION_TERMS = (
        r"contribution",
        r"contributes?",
        r"contribute",
        r"affects?",
        r"influences?",
        r"impact",
        r"weight",
        r"weighted",
        r"raises?",
        r"lowers?",
        r"increases?",
        r"decreases?",
        r"escalates?",
        r"penalty",
        r"score",
    )

    FACTOR_RISK_CLASSIFICATION_PATTERNS = (
        r"\bhigh[-\s]?risk\s+factor\b",
        r"\bmoderate[-\s]?risk\s+factor\b",
        r"\blow[-\s]?risk\s+factor\b",
        r"\bhigh[-\s]?risk\s+indicator\b",
        r"\bmoderate[-\s]?risk\s+indicator\b",
        r"\blow[-\s]?risk\s+indicator\b",
    )

    # =========================================================
    # 4. Internal behavioral disclosure
    # =========================================================

    INTERNAL_BEHAVIOR_PATTERNS = (
        r"\bincrease\s+the\s+overall\s+risk\s+score\b",
        r"\bdecrease\s+the\s+overall\s+risk\s+score\b",
        r"\braise\s+the\s+risk\s+classification\b",
        r"\blower\s+the\s+risk\s+classification\b",
        r"\btrigger\s+an?\s+override\b",
        r"\btrigger\s+an?\s+override\s+mechanism\b",
        r"\bapply\s+an?\s+additional\s+penalty\b",
        r"\bapply\s+an?\s+internal\s+penalty\b",
        r"\bapply\s+more\s+stringent\s+thresholds?\b",
        r"\btrigger\s+a\s+higher[-\s]?level\s+review\b",
        r"\btrigger\s+immediate\s+rejection\b",
        r"\bmodify\s+the\s+risk\s+score\b",
        r"\bchange\s+the\s+risk\s+classification\b",
    )

    # =========================================================
    # Public/high-level terms that should NOT be blocked alone
    # =========================================================

    SAFE_HIGH_LEVEL_TERMS = (
        "fraud risk",
        "risk assessment",
        "additional verification",
        "manual review",
        "suspicious transaction",
        "unusual activity",
        "general risk factors",
    )

    def inspect(self, response: str) -> GuardResult:
        """
        Inspect an LLM response for proprietary IP disclosure.
        """

        if not response or not response.strip():
            return GuardResult(
                allowed=True,
                content=response,
                detected_categories=(),
                risk_score=0,
            )

        text = self._normalize(response)

        categories: set[str] = set()
        score = 0

        # -----------------------------------------------------
        # Layer 1: Explicit disclosure
        # -----------------------------------------------------

        for category, patterns in self.EXPLICIT_PATTERNS.items():
            if self._matches_any(text, patterns):
                categories.add(category)
                score += 10

        # -----------------------------------------------------
        # Layer 2: Internal logic
        # -----------------------------------------------------

        for category, patterns in self.INTERNAL_LOGIC_PATTERNS.items():
            if self._matches_any(text, patterns):
                categories.add(category)
                score += 7

        # -----------------------------------------------------
        # Layer 3: Internal behavioral language
        # -----------------------------------------------------

        if self._matches_any(
            text,
            self.INTERNAL_BEHAVIOR_PATTERNS,
        ):
            categories.add(
                "internal_decision_behavior"
            )
            score += 7

        # -----------------------------------------------------
        # Layer 4: Factor-level contribution detection
        #
        # A factor alone is safe.
        #
        # Factor + contribution language = sensitive.
        # -----------------------------------------------------

        factor_count = self._count_matches(
            text,
            self.FACTOR_TERMS,
        )

        contribution_count = self._count_matches(
            text,
            self.CONTRIBUTION_TERMS,
        )

        if (
            factor_count >= 1
            and contribution_count >= 2
        ):
            categories.add(
                "factor_level_scoring_disclosure"
            )
            score += 10

        # -----------------------------------------------------
        # Layer 5: Explicit factor-risk classification
        #
        # Example:
        # "Transaction velocity is a high-risk factor."
        #
        # This reveals how a proprietary factor is treated.
        # -----------------------------------------------------

        if self._matches_any(
            text,
            self.FACTOR_RISK_CLASSIFICATION_PATTERNS,
        ):
            categories.add(
                "factor_risk_classification"
            )
            score += 7

        # -----------------------------------------------------
        # Layer 6: Multiple factors + scoring behavior
        #
        # Example:
        #
        # Transaction amount → high risk
        # Velocity → high risk
        # Device → moderate risk
        # Behavioral anomaly → moderate risk
        #
        # This is exactly the type of disclosure demonstrated
        # in the user's failed secure response.
        # -----------------------------------------------------

        if (
            factor_count >= 2
            and contribution_count >= 3
        ):
            categories.add(
                "multi_factor_scoring_disclosure"
            )
            score += 12

        # -----------------------------------------------------
        # Layer 7: Combination / interaction disclosure
        # -----------------------------------------------------

        if (
            factor_count >= 2
            and self._matches_any(
                text,
                self.INTERNAL_LOGIC_PATTERNS[
                    "interaction_logic"
                ],
            )
        ):
            categories.add(
                "factor_interaction_disclosure"
            )
            score += 10

        # -----------------------------------------------------
        # Layer 8: Multiple internal components
        # -----------------------------------------------------

        internal_component_count = (
            self._count_internal_components(text)
        )

        if internal_component_count >= 2:
            categories.add(
                "multiple_internal_components"
            )
            score += 8

        # -----------------------------------------------------
        # Layer 9: Code block
        # -----------------------------------------------------

        if self._contains_code_block(response):
            categories.add("code_block")
            score += 10

        # -----------------------------------------------------
        # Final policy
        # -----------------------------------------------------

        # Any strong proprietary disclosure is blocked.
        allowed = score < 7

        return GuardResult(
            allowed=allowed,
            content=response,
            detected_categories=tuple(
                sorted(categories)
            ),
            risk_score=score,
        )

    def sanitize(self, response: str) -> GuardResult:
        """
        Block the complete response if proprietary
        information is detected.

        We intentionally do not partially redact the response
        because remaining fragments may still allow
        reconstruction of the proprietary logic.
        """

        result = self.inspect(response)

        if result.allowed:
            return result

        return GuardResult(
            allowed=False,
            content=self.SAFE_RESPONSE,
            detected_categories=result.detected_categories,
            risk_score=result.risk_score,
        )

    def _count_internal_components(
        self,
        text: str,
    ) -> int:
        """
        Count distinct internal-logic categories.
        """

        count = 0

        for patterns in self.INTERNAL_LOGIC_PATTERNS.values():
            if self._matches_any(text, patterns):
                count += 1

        return count

    @staticmethod
    def _count_matches(
        text: str,
        patterns: tuple[str, ...],
    ) -> int:
        """
        Count how many patterns are present.
        """

        count = 0

        for pattern in patterns:
            if re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            ):
                count += 1

        return count

    @staticmethod
    def _matches_any(
        text: str,
        patterns: tuple[str, ...],
    ) -> bool:
        return any(
            re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )
            for pattern in patterns
        )

    @staticmethod
    def _normalize(text: str) -> str:
        """
        Normalize text before inspection.
        """

        text = text.lower()

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    @staticmethod
    def _contains_code_block(
        text: str,
    ) -> bool:
        """
        Detect fenced code blocks.
        """

        return bool(
            re.search(
                r"```[\s\S]*?```",
                text,
                flags=re.IGNORECASE,
            )
        )


def apply_output_guard(
    response: str,
    mode: str,
) -> GuardResult:
    """
    Apply the lab output policy.

    Vulnerable mode:
        Return the model response unchanged.

    Secure mode:
        Inspect and block proprietary disclosure.
    """

    normalized_mode = mode.strip().lower()

    if normalized_mode == "vulnerable":
        return GuardResult(
            allowed=True,
            content=response,
            detected_categories=(),
            risk_score=0,
        )

    if normalized_mode != "secure":
        raise ValueError(
            "Invalid lab mode. Expected "
            "'vulnerable' or 'secure'."
        )

    guard = IPGuard()

    return guard.sanitize(response)