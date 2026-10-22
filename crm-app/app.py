import os
import time
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from db import get_db_cursor, check_db_health, get_pool
from metrics import REQUEST_COUNT, REQUEST_LATENCY, update_business_metrics, generate_latest, CONTENT_TYPE_LATEST

# Structured JSON Logger for Loki & Promtail
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": "crm-app",
            "message": record.getMessage()
        }
        if hasattr(record, "props"):
            log_obj.update(record.props)
        return json.dumps(log_obj, ensure_ascii=False)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("crm-app")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "SuperSecretKey_CRM_ICTU_2026_Secure!")

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def log_and_record_metrics(response):
    if request.path.startswith('/static'):
        return response

    duration = time.time() - getattr(request, 'start_time', time.time())
    endpoint = request.endpoint or 'unknown'
    status = response.status_code

    REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, http_status=status).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)

    logger.info(
        f"{request.method} {request.path} {status} {duration*1000:.1f}ms",
        extra={"props": {
            "method": request.method,
            "path": request.path,
            "status": status,
            "duration_ms": round(duration * 1000, 2),
            "client_ip": request.headers.get("X-Forwarded-For", request.remote_addr)
        }}
    )
    return response

# ----------------- ROUTES -----------------

@app.route('/')
def dashboard():
    with get_db_cursor() as cur:
        # Total counts
        cur.execute("SELECT COUNT(*) FROM customers")
        total_customers = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM customers WHERE status = 'VIP'")
        vip_customers = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM interactions")
        total_interactions = cur.fetchone()[0]

        cur.execute("SELECT COALESCE(SUM(expected_revenue), 0) FROM customers")
        total_revenue = cur.fetchone()[0]

        # Status distribution
        cur.execute("SELECT status, COUNT(*) FROM customers GROUP BY status")
        status_data = dict(cur.fetchall())

        # Interaction by type
        cur.execute("SELECT type, COUNT(*) FROM interactions GROUP BY type")
        type_data = dict(cur.fetchall())

        # Recent 5 interactions
        cur.execute("""
            SELECT i.id, c.name, i.type, i.summary, i.outcome, i.agent_name, i.interaction_date
            FROM interactions i
            JOIN customers c ON i.customer_id = c.id
            ORDER BY i.interaction_date DESC
            LIMIT 5
        """)
        recent_interactions = cur.fetchall()

    return render_template(
        'dashboard.html',
        total_customers=total_customers,
        vip_customers=vip_customers,
        total_interactions=total_interactions,
        total_revenue=total_revenue,
        status_data=status_data,
        type_data=type_data,
        recent_interactions=recent_interactions
    )

@app.route('/customers')
def customers():
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = "SELECT id, name, contact_person, email, phone, address, status, expected_revenue, created_at FROM customers WHERE 1=1"
    params = []

    if search:
        query += " AND (name ILIKE %s OR email ILIKE %s OR phone ILIKE %s OR contact_person ILIKE %s)"
        s = f"%{search}%"
        params.extend([s, s, s, s])

    if status_filter:
        query += " AND status = %s"
        params.append(status_filter)

    query += " ORDER BY id DESC"

    with get_db_cursor() as cur:
        cur.execute(query, params)
        customer_list = cur.fetchall()

    return render_template('customers.html', customers=customer_list, search=search, status_filter=status_filter)

@app.route('/customers/add', methods=['POST'])
def add_customer():
    name = request.form.get('name', '').strip()
    contact_person = request.form.get('contact_person', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    status = request.form.get('status', 'LEAD')
    expected_revenue = float(request.form.get('expected_revenue', 0) or 0)

    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO customers (name, contact_person, email, phone, address, status, expected_revenue)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, contact_person, email, phone, address, status, expected_revenue))

    logger.info(f"ACTION: ADD_CUSTOMER name={name} status={status}")
    flash(f"Đã thêm khách hàng '{name}' thành công!", "success")
    return redirect(url_for('customers'))

@app.route('/customers/edit/<int:customer_id>', methods=['POST'])
def edit_customer(customer_id):
    name = request.form.get('name', '').strip()
    contact_person = request.form.get('contact_person', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    status = request.form.get('status', 'LEAD')
    expected_revenue = float(request.form.get('expected_revenue', 0) or 0)

    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE customers
            SET name=%s, contact_person=%s, email=%s, phone=%s, address=%s, status=%s, expected_revenue=%s, updated_at=NOW()
            WHERE id=%s
        """, (name, contact_person, email, phone, address, status, expected_revenue, customer_id))

    logger.info(f"ACTION: EDIT_CUSTOMER id={customer_id} name={name}")
    flash(f"Cập nhật thông tin khách hàng #{customer_id} thành công!", "success")
    return redirect(url_for('customers'))

@app.route('/customers/delete/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    with get_db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM customers WHERE id = %s", (customer_id,))

    logger.info(f"ACTION: DELETE_CUSTOMER id={customer_id}")
    flash(f"Đã xóa khách hàng #{customer_id} khỏi hệ thống!", "warning")
    return redirect(url_for('customers'))

@app.route('/contacts')
def contacts():
    customer_id = request.args.get('customer_id', type=int)
    with get_db_cursor() as cur:
        cur.execute("SELECT id, name FROM customers ORDER BY name ASC")
        all_customers = cur.fetchall()

        if customer_id:
            cur.execute("""
                SELECT c.id, c.full_name, c.position, c.email, c.phone, c.notes, cust.name as customer_name, cust.id as customer_id
                FROM contacts c
                JOIN customers cust ON c.customer_id = cust.id
                WHERE c.customer_id = %s
                ORDER BY c.id DESC
            """, (customer_id,))
        else:
            cur.execute("""
                SELECT c.id, c.full_name, c.position, c.email, c.phone, c.notes, cust.name as customer_name, cust.id as customer_id
                FROM contacts c
                JOIN customers cust ON c.customer_id = cust.id
                ORDER BY c.id DESC
            """,)
        contact_list = cur.fetchall()

    return render_template('contacts.html', contacts=contact_list, customers=all_customers, selected_customer_id=customer_id)

@app.route('/contacts/add', methods=['POST'])
def add_contact():
    customer_id = int(request.form.get('customer_id'))
    full_name = request.form.get('full_name', '').strip()
    position = request.form.get('position', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    notes = request.form.get('notes', '').strip()

    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO contacts (customer_id, full_name, position, email, phone, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (customer_id, full_name, position, email, phone, notes))

    logger.info(f"ACTION: ADD_CONTACT name={full_name} customer_id={customer_id}")
    flash(f"Đã thêm người liên hệ '{full_name}' thành công!", "success")
    return redirect(url_for('contacts'))

@app.route('/contacts/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    with get_db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM contacts WHERE id = %s", (contact_id,))
    logger.info(f"ACTION: DELETE_CONTACT id={contact_id}")
    flash(f"Đã xóa người liên hệ #{contact_id}!", "info")
    return redirect(url_for('contacts'))

@app.route('/interactions')
def interactions():
    customer_filter = request.args.get('customer_id', type=int)
    type_filter = request.args.get('type', '').strip()

    query = """
        SELECT i.id, cust.name as customer_name, i.type, i.summary, i.outcome, i.agent_name, i.interaction_date, cust.id as customer_id
        FROM interactions i
        JOIN customers cust ON i.customer_id = cust.id
        WHERE 1=1
    """
    params = []
    if customer_filter:
        query += " AND i.customer_id = %s"
        params.append(customer_filter)
    if type_filter:
        query += " AND i.type = %s"
        params.append(type_filter)

    query += " ORDER BY i.interaction_date DESC"

    with get_db_cursor() as cur:
        cur.execute("SELECT id, name FROM customers ORDER BY name ASC")
        all_customers = cur.fetchall()
        cur.execute(query, params)
        interaction_list = cur.fetchall()

    return render_template('interactions.html', interactions=interaction_list, customers=all_customers, customer_filter=customer_filter, type_filter=type_filter)

@app.route('/interactions/add', methods=['POST'])
def add_interaction():
    customer_id = int(request.form.get('customer_id'))
    itype = request.form.get('type', 'CALL')
    summary = request.form.get('summary', '').strip()
    outcome = request.form.get('outcome', 'PENDING')
    agent_name = request.form.get('agent_name', 'Phan Ngọc Ánh').strip()

    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO interactions (customer_id, type, summary, outcome, agent_name, interaction_date)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (customer_id, itype, summary, outcome, agent_name))

    logger.info(f"ACTION: LOG_INTERACTION type={itype} customer_id={customer_id} outcome={outcome} agent={agent_name}")
    flash("Đã ghi nhận tương tác chăm sóc khách hàng mới!", "success")
    return redirect(url_for('interactions'))

# ----------------- API ENDPOINTS -----------------

@app.route('/api/stats')
def api_stats():
    with get_db_cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM customers")
        total_c = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM interactions")
        total_i = cur.fetchone()[0]
        cur.execute("SELECT status, count(*) FROM customers GROUP BY status")
        status_dist = dict(cur.fetchall())
    return jsonify({
        "status": "success",
        "total_customers": total_c,
        "total_interactions": total_i,
        "status_distribution": status_dist
    })

# ----------------- HEALTH & METRICS -----------------

@app.route('/health')
def health():
    db_ok = check_db_health()
    status_code = 200 if db_ok else 503
    return jsonify({
        "status": "UP" if db_ok else "DOWN",
        "service": "crm-app",
        "database": "CONNECTED" if db_ok else "DISCONNECTED",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), status_code

@app.route('/metrics')
def metrics():
    update_business_metrics()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    get_pool()
    app.run(host='0.0.0.0', port=5000, debug=False)
