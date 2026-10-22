# HƯỚNG DẪN TRUY VẤN NHẬT KÝ VỚI LOGQL (LOKI + PROMTAIL)
### HỆ THỐNG CRM CHĂM SÓC KHÁCH HÀNG - ĐỀ 4
**Sinh viên: Phàn Ngọc Anh - Mã SV: DTC245200964 - GVHD: Vũ Việt Dũng - ICTU**

---

## 1. Tổng quan về Hệ thống Log tập trung
Hệ thống sử dụng **Loki** làm trung tâm lưu trữ và đánh chỉ mục metadata của log, kết hợp **Promtail** tự động thu thập nhật ký từ toàn bộ các Docker containers (`crm-app`, `crm-nginx`, `crm-db`, `crm-pgadmin`, `crm-prometheus`, v.v.).

Truy vấn LogQL được thực hiện trực tiếp trên giao diện **Grafana Explore** (`https://192.168.102.129/grafana/explore` -> Chọn Data Source: **Loki**).

---

## 2. Danh mục các câu truy vấn LogQL mẫu

### Truy vấn 1: Giám sát toàn bộ HTTP Request qua Nginx Reverse Proxy
* **Mục đích**: Theo dõi tất cả các lượt truy cập từ người dùng và client vào hệ thống CRM qua cổng Web 80/443.
* **Cú pháp LogQL**:
```logql
{container="crm-nginx"} |= "HTTP"
```
* **Mẫu kết quả thu được**:
```json
{"timestamp":"2026-10-23T01:59:25+07:00","client_ip":"192.168.102.1","method":"GET","uri":"/","status":200,"body_bytes_sent":18995,"request_time":0.035,"http_user_agent":"Mozilla/5.0"}
```

---

### Truy vấn 2: Lọc các Request gặp lỗi HTTP Client (4xx) hoặc Server (5xx)
* **Mục đích**: Phát hiện sớm các lỗi truy cập trang không tồn tại (404), lỗi phân quyền (403), hoặc lỗi sập ứng dụng (500, 502 Bad Gateway).
* **Cú pháp LogQL**:
```logql
{container="crm-nginx"} | json | status >= 400
```
*Hoặc truy vấn dạng text:*
```logql
{container="crm-nginx"} |= " 404 " or " 500 " or " 502 "
```
* **Ý nghĩa thực tế**: Giúp DevOps và quản trị viên phát hiện các nỗ lực tấn công quét lỗ hổng hoặc sự cố kết nối giữa Nginx và CRM App.

---

### Truy vấn 3: Theo dõi hoạt động Nghiệp vụ Chăm sóc Khách hàng (CRM Action Log)
* **Mục đích**: Kiểm tra nhật ký khi chuyên viên thực hiện các thao tác: Thêm khách hàng, Ghi nhận cuộc gọi/họp/email tương tác, Cập nhật tiến độ đàm phán.
* **Cú pháp LogQL**:
```logql
{container="crm-app"} |= "ACTION:"
```
*Hoặc lọc chi tiết hành động tương tác:*
```logql
{container="crm-app"} |= "LOG_INTERACTION"
```
* **Mẫu kết quả thu được**:
```text
{"timestamp": "2026-10-23T02:00:15Z", "level": "INFO", "service": "crm-app", "message": "ACTION: LOG_INTERACTION type=MEETING customer_id=1 outcome=POSITIVE agent=Phàn Ngọc Anh"}
{"timestamp": "2026-10-23T02:01:10Z", "level": "INFO", "service": "crm-app", "message": "ACTION: ADD_CUSTOMER name=Công ty Cổ phần FPT status=VIP"}
```

---

### Truy vấn 4: Phát hiện Cảnh báo và Lỗi Nghiệp vụ Ứng dụng CRM
* **Mục đích**: Tìm kiếm các dòng log chứa từ khóa `ERROR`, `WARNING`, `EXCEPTION` trong ứng dụng Flask để xử lý sự cố kịp thời.
* **Cú pháp LogQL**:
```logql
{container="crm-app"} |= "ERROR"
```
*Hoặc kết hợp parser JSON:*
```logql
{container="crm-app"} | json | level = "ERROR"
```

---

### Truy vấn 5: Thống kê Tốc độ sinh Log của Nginx theo thời gian (Metric Query)
* **Mục đích**: Chuyển đổi dữ liệu nhật ký thô thành đồ thị số lượng request mỗi giây (Rate) để hiển thị trên Dashboard Grafana.
* **Cú pháp LogQL**:
```logql
sum(rate({container="crm-nginx"}[1m]))
```
* **Ý nghĩa thực tế**: Giúp theo dõi lưu lượng truy cập đỉnh điểm (traffic spike) hoặc cảnh báo dấu hiệu tấn công DoS/DDoS.

---

### Truy vấn 6: Giám sát Hoạt động Cơ sở dữ liệu PostgreSQL
* **Mục đích**: Theo dõi nhật ký khởi động, kết nối và giao dịch của hệ quản trị cơ sở dữ liệu PostgreSQL.
* **Cú pháp LogQL**:
```logql
{container="crm-db"} |= "database system is ready to accept connections"
```
*Hoặc theo dõi tất cả sự kiện checkpoint và kết nối:*
```logql
{container="crm-db"} |= "checkpoint"
```

---

## 3. Các bước Demo Thực tế cho Giảng viên
1. Mở trình duyệt truy cập: `https://192.168.102.129/grafana/`
2. Đăng nhập với tài khoản: `admin` / `GrafanaAdmin_2026!`
3. Ở menu thanh bên trái, chọn biểu tượng **Explore** (hình la bàn).
4. Chọn Data Source: **Loki**.
5. Nhập lần lượt các câu truy vấn LogQL ở mục 2 và bấm **Run Query** (hoặc `Shift + Enter`).
6. Trình duyệt hiển thị luồng log trực tiếp dạng thời gian thực (Live Streaming) và các đồ thị phân bố log theo thời gian.
