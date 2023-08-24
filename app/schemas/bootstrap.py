"""Schema for frontend bootstrap data."""

from pydantic import BaseModel


class FeatureFlags(BaseModel):
    """Feature Flags."""

    MFA_ENABLED: bool
    JOURNAL_PDF_EXPORT_ENABLED: bool


class BootstrapResponse(BaseModel):
    """Bootstrap Response."""

    metadata: dict
    feature_flags: FeatureFlags
