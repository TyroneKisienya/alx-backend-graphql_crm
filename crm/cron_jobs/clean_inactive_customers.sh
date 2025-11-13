#!/bin/bash

LOG_FILE="/tmp/customer_cleanup_log.txt"

DELETED_COUNT=$(python3 manage.py shell -c "
from datetime import timedelta, datetime
from crm.models import Customer
from django.utils import timezone

one_year_ago= timezone.now() - timedelta(days=365)
inactive_customers= Customer.objects.filter(orders__isnull=True | Customer.objects.exclude(orders__date__gte=one_year_ago))
count= inactive_customers.count()
inactive_customers.delete()
print (count)
")

echo \"\$(date '+%Y-%m-%d %H:%m:%s') - Deleted \$DELETED_COUNT inactive customers\" >> \"$LOG_FILE\"