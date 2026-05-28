from app.database import SessionLocal

from app.engines.performance_engine import (
    evaluate_signals
)

db = SessionLocal()

result = evaluate_signals(db)

print(result)

db.close()