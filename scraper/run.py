import sys
from . import jobvision, korea, db

try:
    ir = jobvision.fetch()
except Exception as e:
    print("jobvision FAILED:", repr(e))
    ir = []

kr = korea.fetch()

db.upsert(kr)   # اگر خالی باشد، دیتای قبلی دست‌نخورده می‌ماند
db.upsert(ir)
print(f"saved IR={len(ir)} KR={len(kr)}")

if not ir:
    sys.exit("Jobvision returned 0 jobs; old data kept")
