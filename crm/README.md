# CRM Celery + Celery Beat Setup

## Overview
This setup generates a **weekly CRM report** using Celery Beat and logs it to `/tmp/crm_report_log.txt`.

## Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install celery django-celery-beat redis gql requests
---
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
---
python3 manage.py migrate
---
celery -A crm worker -l info
---
celery -A crm beat worker -l info

---

## Summary of File Changes

| File | Purpose |
|------|----------|
| `requirements.txt` | Added `celery`, `django-celery-beat`, `redis` |
| `crm/settings.py` | Added broker, beat schedule, and timezone |
| `crm/celery.py` | Initialized Celery app |
| `crm/__init__.py` | Loaded Celery automatically |
| `crm/tasks.py` | Defined GraphQL-based report task |
| `crm/README.md` | Added full setup documentation |

---