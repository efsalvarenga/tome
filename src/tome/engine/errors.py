from typing import ClassVar

from tome.engine.models import CONTRACT_VERSION, RunFailure


class RunError(Exception):
    code: ClassVar[str]

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def to_failure(self) -> RunFailure:
        return RunFailure(contract_version=CONTRACT_VERSION, code=self.code, message=self.message)


class InvalidRunRequestError(RunError):
    code = "INVALID_RUN_REQUEST"


class ProposalGenerationError(RunError):
    code = "PROPOSAL_GENERATION_FAILED"


class InvalidProposalError(RunError):
    code = "INVALID_PROPOSAL"


class PeerReviewError(RunError):
    code = "PEER_REVIEW_FAILED"


class UmpireReviewError(RunError):
    code = "UMPIRE_REVIEW_FAILED"


class UmpireResolutionError(RunError):
    code = "UMPIRE_RESOLUTION_FAILED"


class MechanicsError(RunError):
    code = "MECHANICS_FAILED"
