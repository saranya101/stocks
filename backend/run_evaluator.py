from app.database import SessionLocal

from app.services.performance_service import (
    evaluate_signals
)

db = SessionLocal()

result = evaluate_signals(db)

print(result)

db.close()
