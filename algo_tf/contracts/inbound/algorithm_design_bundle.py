from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BundleInstrument(BaseModel):
    model_config = ConfigDict(extra="allow")

    symbol: str = Field(min_length=1)
    asset_class: Literal["ETF", "EQUITY", "OPTION"]
    direction: Literal["LONG", "SHORT"]
    session: str


class StrategySpecification(BaseModel):
    model_config = ConfigDict(extra="allow")

    instrument: BundleInstrument


class RiskMandate(BaseModel):
    model_config = ConfigDict(extra="allow")

    max_dollar_risk: float = Field(gt=0)
    max_notional: float = Field(gt=0)
    calculate_quantity: bool

    @model_validator(mode="after")
    def notional_exceeds_risk(self) -> RiskMandate:
        if self.max_notional <= self.max_dollar_risk:
            raise ValueError("max_notional must exceed max_dollar_risk")
        if not self.calculate_quantity:
            raise ValueError("risk-based quantity calculation is required")
        return self


class ExecutionOrder(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: Literal["LIMIT"]
    tranches: int = Field(ge=1, le=1)
    max_replaces: int = Field(ge=0, le=0)
    max_spread_bps: float = Field(gt=0)
    max_slippage_bps: float = Field(gt=0)


class ExecutionMandateDesign(BaseModel):
    model_config = ConfigDict(extra="allow")

    order: ExecutionOrder
    broker_boundary: Literal["ROOT_EXECUTION_ENGINE_ONLY"]
    auto_send: Literal[False]


class TestingEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    backtest: bool
    out_of_sample: bool
    costs: bool
    sensitivity: bool
    scenarios: bool
    paper: bool
    shadow: bool


class AlgorithmDesignBundle(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_name: Literal["algo-tf.algorithm-design-bundle.v4"] = Field(alias="schema")
    bundle_id: str = Field(min_length=1)
    created_at: datetime
    status: Literal["PROPOSAL_READY"]
    effective_mode: Literal["REPLAY", "PAPER", "SHADOW", "LIMITED_LIVE"]
    strategy_specification: StrategySpecification
    risk_mandate: RiskMandate
    execution_mandate: ExecutionMandateDesign
    testing: TestingEvidence