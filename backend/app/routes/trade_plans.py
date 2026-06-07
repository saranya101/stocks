from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any
from app.services.ai_trade_memo_service import generate_ai_trade_memo

from app.database import SessionLocal
from app.models.trade_plan import TradePlan

router = APIRouter(prefix="/trade-plans", tags=["trade-plans"])


class TradePlanCreate(BaseModel):
    market: str = "us"
    trade: dict[str, Any]


class TradePlanStatusUpdate(BaseModel):
    status: str
    decision_note: Optional[str] = None


@router.post("")
def create_trade_plan(payload: TradePlanCreate):
    db = SessionLocal()

    try:
        trade = payload.trade
        ai_memo = generate_ai_trade_memo(trade)

        plan = TradePlan(
            market=payload.market,
            ticker=trade.get("ticker"),
            direction=trade.get("direction"),
            conviction=trade.get("conviction"),
            probability=trade.get("probability"),
            grade=trade.get("grade"),
            recommendation=trade.get("recommendation"),
            entry_price=trade.get("entry_price"),
            stop_loss=trade.get("stop_loss"),
            take_profit=trade.get("take_profit"),
            risk_reward=trade.get("risk_reward"),
            expected_hold_days=trade.get("expected_hold_days"),
            shares=trade.get("shares"),
            risk_amount=trade.get("risk_amount"),
            risk_per_share=trade.get("risk_per_share"),
            position_value=trade.get("position_value"),
            technical_score=trade.get("technical_score"),
            backtest_score=trade.get("backtest_score"),
            news_score=trade.get("news_score"),
            volume_score=trade.get("volume_score"),
            rsi=trade.get("rsi"),
            reasons=trade.get("reasons", []),
            raw_data={
                **trade,
                "ai_investment_memo": ai_memo,
            },
            status="PENDING",
        )

        db.add(plan)
        db.commit()
        db.refresh(plan)

        return {
            "message": "Trade plan created",
            "trade_plan_id": plan.id,
            "status": plan.status,
            "ticker": plan.ticker,
        }

    finally:
        db.close()


@router.get("")
def get_trade_plans(status: Optional[str] = None):
    db = SessionLocal()

    try:
        query = db.query(TradePlan).order_by(TradePlan.created_at.desc())

        if status:
            query = query.filter(TradePlan.status == status.upper())

        plans = query.all()

        return {
            "count": len(plans),
            "trade_plans": [
                {
                    "id": plan.id,
                    "ticker": plan.ticker,
                    "market": plan.market,
                    "direction": plan.direction,
                    "conviction": plan.conviction,
                    "probability": plan.probability,
                    "grade": plan.grade,
                    "recommendation": plan.recommendation,
                    "entry_price": plan.entry_price,
                    "stop_loss": plan.stop_loss,
                    "take_profit": plan.take_profit,
                    "risk_reward": plan.risk_reward,
                    "expected_hold_days": plan.expected_hold_days,
                    "shares": plan.shares,
                    "ai_investment_memo": plan.raw_data.get("ai_investment_memo"),
                    "risk_amount": plan.risk_amount,
                    "risk_per_share": plan.risk_per_share,
                    "position_value": plan.position_value,
                    "technical_score": plan.technical_score,
                    "backtest_score": plan.backtest_score,
                    "news_score": plan.news_score,
                    "volume_score": plan.volume_score,
                    "rsi": plan.rsi,
                    "reasons": plan.reasons,
                    "status": plan.status,
                    "decision_note": plan.decision_note,
                    "created_at": plan.created_at,
                    "updated_at": plan.updated_at,
                    "raw_data": plan.raw_data,
                    "ai_investment_memo": plan.raw_data.get("ai_investment_memo"),
                    "company_name": plan.raw_data.get("company_name"),
                    "sector": plan.raw_data.get("sector"),
                    "industry": plan.raw_data.get("industry"),
                    "market_cap": plan.raw_data.get("market_cap"),
                    "country": plan.raw_data.get("country"),
                    "website": plan.raw_data.get("website"),
                    "description": plan.raw_data.get("description"),
                    "yahoo_url": plan.raw_data.get("yahoo_url"),
                }
                for plan in plans
            ],
        }

    finally:
        db.close()


@router.patch("/{plan_id}/status")
def update_trade_plan_status(
    plan_id: int,
    payload: TradePlanStatusUpdate,
):
    allowed = ["PENDING", "APPROVED", "REJECTED", "SNOOZED", "EXECUTED"]

    new_status = payload.status.upper()

    if new_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of {allowed}",
        )

    db = SessionLocal()

    try:
        plan = db.query(TradePlan).filter(TradePlan.id == plan_id).first()

        if not plan:
            raise HTTPException(status_code=404, detail="Trade plan not found")

        plan.status = new_status
        plan.decision_note = payload.decision_note

        db.commit()
        db.refresh(plan)

        return {
            "message": "Trade plan updated",
            "id": plan.id,
            "ticker": plan.ticker,
            "status": plan.status,
            "decision_note": plan.decision_note,
        }

    finally:
        db.close()