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

## 2. Kiến trúc Hệ thống (Giai đoạn 1 - Core Services)
* **Web App CRM**: Python Flask + Gunicorn, chuẩn MVC, tích hợp Chart.js, xuất metrics Prometheus `/metrics`.
* **Database**: PostgreSQL 16 (tách biệt mạng nội bộ, tự động khởi tạo bảng và dữ liệu mẫu tiếng Việt).
* **Quản trị Database**: pgAdmin 4 (cấu hình sẵn kết nối tự động vào PostgreSQL).
* **Nginx Reverse Proxy**: Chuyển hướng HTTP sang HTTPS, chứng chỉ SSL tự ký, áp dụng 6 lớp Security Headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options...).

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

### Bước 3: Khởi chạy bằng Docker Compose
```bash
docker compose up -d --build
```

---

## 4. Truy cập Dịch vụ
| Dịch vụ | Địa chỉ truy cập | Tài khoản mặc định | Ghi chú |
| :--- | :--- | :--- | :--- |
| **CRM Web App** | `https://192.168.102.129` | Không yêu cầu đăng nhập | Giao diện Dashboard & CRUD |
| **pgAdmin 4** | `https://192.168.102.129/pgadmin/` | `admin@crm.local` / `PgAdminStrongPass_2026!` | Quản lý PostgreSQL trực quan |
| **App Health** | `https://192.168.102.129/health` | — | Kiểm tra tình trạng kết nối DB |
| **App Metrics** | `https://192.168.102.129/metrics` | — | Dữ liệu định dạng Prometheus |

---

*Lưu ý: Do sử dụng chứng chỉ SSL tự ký (self-signed certificate) trong môi trường Lab, trình duyệt sẽ hiển thị cảnh báo bảo mật. Vui lòng bấm chọn **Advanced (Nâng cao) -> Proceed (Tiếp tục truy cập)** để vào hệ thống.*
