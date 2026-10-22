# HỆ THỐNG CRM CHĂM SÓC KHÁCH HÀNG (ĐỀ 4)
### MÔN HỌC: TRIỂN KHAI VÀ QUẢN TRỊ HỆ THỐNG PHẦN MỀM
**Trường Đại học Công nghệ Thông tin và Truyền thông - Đại học Thái Nguyên (ICTU)**

* **Sinh viên thực hiện**: Phan Ngọc Ánh
* **Mã sinh viên**: DTC245200964
* **Email**: dtc245200964@ictu.edu.vn
* **Repository**: https://github.com/bruhbrodarkvl-blip/kiemtracuoiky

---

## 1. Giới thiệu Đề tài
Dự án triển khai hoàn chỉnh một hệ thống phần mềm **CRM Chăm sóc Khách hàng**, đáp ứng trọn vẹn nghiệp vụ quản lý khách hàng, danh bạ người liên hệ và lịch sử tương tác chăm sóc khách hàng đa kênh. Toàn bộ hệ thống được container hóa bằng **Docker Compose**, bảo vệ bởi **Nginx Reverse Proxy (SSL/HTTPS)**, giám sát toàn diện qua **Prometheus + Grafana**, quản lý log tập trung với **Loki + Promtail**, và áp dụng các biện pháp **Hardening** an toàn hệ thống.

---

## 2. Kiến trúc Hệ thống Giám sát (Monitoring Architecture)
Hệ thống sử dụng mô hình giám sát toàn diện với **Prometheus** làm trung tâm thu thập dữ liệu time-series và **Grafana** trực quan hóa bảng điều khiển:
1. **Ứng dụng CRM Web App** (`crm-app:5000/metrics`): Đo đếm tổng số HTTP requests, độ trễ xử lý (latency), tổng khách hàng theo phân hạng, lượt tương tác và doanh thu dự kiến.
2. **PostgreSQL Exporter** (`postgres-exporter:9187`): Thu thập chỉ số cơ sở dữ liệu (Active connections, transactions commit/rollback, cache hit ratio, locks).
3. **Nginx Exporter** (`nginx-exporter:9113`): Thu thập số lượng kết nối đang mở, throughput request/giây từ `/stub_status`.
4. **cAdvisor** (`cadvisor:8080`): Giám sát mức tiêu thụ tài nguyên thời gian thực (CPU, RAM, Network I/O) của từng container Docker.
5. **Node Exporter** (`node-exporter:9100`): Giám sát chỉ số phần cứng của máy chủ Linux (CPU load, RAM free, Disk usage).
6. **Grafana** (`Port 3000` / `/grafana/`): Tự động nạp sẵn Dashboard `CRM System Overview & Monitoring Dashboard`.

---

## 3. Hướng dẫn Khởi chạy Hệ thống
### Bước 1: Sao chép mã nguồn
```bash
git clone https://github.com/bruhbrodarkvl-blip/kiemtracuoiky.git
cd kiemtracuoiky
```

### Bước 2: Tạo chứng chỉ SSL cho Nginx
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/server.key \
    -out nginx/ssl/server.crt \
    -subj "/C=VN/ST=ThaiNguyen/L=ThaiNguyen/O=ICTU/OU=DTC245200964/CN=192.168.102.129" \
    -addext "subjectAltName=DNS:localhost,DNS:crm.local,IP:192.168.102.129,IP:127.0.0.1"
```

### Bước 3: Khởi chạy toàn bộ hệ thống
```bash
docker compose up -d --build
```

---

## 4. Danh mục Dịch vụ và Cổng truy cập
| Dịch vụ | Địa chỉ truy cập | Tài khoản mặc định | Vai trò |
| :--- | :--- | :--- | :--- |
| **CRM Web App** | `https://192.168.102.129` | Không yêu cầu đăng nhập | Giao diện CRM Quản lý Khách hàng |
| **pgAdmin 4** | `https://192.168.102.129/pgadmin/` | `dtc245200964@ictu.edu.vn` / `PgAdminStrongPass_2026!` | Quản trị PostgreSQL trực quan |
| **Grafana** | `https://192.168.102.129/grafana/` | `admin` / `GrafanaAdmin_2026!` | Bảng điều khiển Giám sát Đồ họa |
| **Prometheus** | `http://192.168.102.129:9090` | Không yêu cầu | Thu thập và truy vấn Metrics |
| **App Metrics** | `https://192.168.102.129/metrics` | — | Prometheus App Metrics |
| **App Health** | `https://192.168.102.129/health` | — | Kiểm tra tình trạng kết nối DB |
