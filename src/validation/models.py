from dataclasses import dataclass


@dataclass(slots=True)
class ClaimResult:
    claim: str
    supported: bool
    evidence_ids: list[int]


@dataclass(slots=True)
class ValidationResult:
    valid: bool
    claims: list[ClaimResult]
    reason: str = ""