from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from db import get_db_cursor

REQUEST_COUNT = Counter(
    'crm_http_requests_total',
    'Total HTTP requests processed by CRM App',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'crm_http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['endpoint']
)

CUSTOMERS_GAUGE = Gauge(
    'crm_customers_total',
    'Total customers in CRM by status',
    ['status']
)

INTERACTIONS_GAUGE = Gauge(
    'crm_interactions_total',
    'Total customer interactions logged',
    ['outcome']
)

REVENUE_GAUGE = Gauge(
    'crm_expected_revenue_total_vnd',
    'Total expected revenue in VND'
)

def update_business_metrics():
    try:
        with get_db_cursor() as cur:
            # Customers by status
            cur.execute("SELECT status, COUNT(*) FROM customers GROUP BY status")
            statuses = {'LEAD': 0, 'PROSPECT': 0, 'CUSTOMER': 0, 'VIP': 0, 'INACTIVE': 0}
            for row in cur.fetchall():
                statuses[row[0]] = row[1]
            for s, count in statuses.items():
                CUSTOMERS_GAUGE.labels(status=s).set(count)

            # Interactions by outcome
            cur.execute("SELECT outcome, COUNT(*) FROM interactions GROUP BY outcome")
            outcomes = {'POSITIVE': 0, 'PENDING': 0, 'NEGATIVE': 0}
            for row in cur.fetchall():
                outcomes[row[0]] = row[1]
            for o, count in outcomes.items():
                INTERACTIONS_GAUGE.labels(outcome=o).set(count)

            # Total revenue
            cur.execute("SELECT COALESCE(SUM(expected_revenue), 0) FROM customers WHERE status IN ('CUSTOMER', 'VIP', 'PROSPECT')")
            rev = cur.fetchone()[0]
            REVENUE_GAUGE.set(float(rev))
    except Exception as e:
        print(f"Error updating business metrics: {e}")
