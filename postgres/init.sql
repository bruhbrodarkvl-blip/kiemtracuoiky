-- Database & Schema Initialization for CRM System
-- Đề 4: Hệ thống CRM Chăm sóc Khách hàng
-- Sinh viên: Phàn Ngọc Anh - DTC245200964 - ICTU

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: customers
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(150),
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    address TEXT,
    status VARCHAR(50) DEFAULT 'LEAD', -- LEAD, PROSPECT, CUSTOMER, VIP, INACTIVE
    expected_revenue NUMERIC(15, 2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table: contacts
CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    full_name VARCHAR(150) NOT NULL,
    position VARCHAR(100),
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table: interactions
CREATE TABLE IF NOT EXISTS interactions (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE SET NULL,
    type VARCHAR(50) NOT NULL, -- CALL, MEETING, EMAIL, DEMO, QUOTE, SUPPORT
    summary TEXT NOT NULL,
    outcome VARCHAR(50) DEFAULT 'PENDING', -- POSITIVE, PENDING, NEGATIVE
    agent_name VARCHAR(100) DEFAULT 'Phàn Ngọc Anh',
    interaction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Query Performance & Log Search
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_contacts_customer ON contacts(customer_id);
CREATE INDEX IF NOT EXISTS idx_interactions_customer ON interactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_interactions_type ON interactions(type);
CREATE INDEX IF NOT EXISTS idx_interactions_date ON interactions(interaction_date);

-- Seed Data: Enterprise & SME Vietnamese Clients
INSERT INTO customers (name, contact_person, email, phone, address, status, expected_revenue) VALUES
('Công ty Cổ phần Viễn thông FPT (FPT Telecom)', 'Nguyễn Văn Hải', 'contact@fpt.vn', '024 7300 2222', 'Tòa nhà FPT, Phố Duy Tân, Cầu Giấy, Hà Nội', 'VIP', 1200000000.00),
('Tập đoàn Công nghiệp - Viễn thông Quân đội (Viettel)', 'Trần Thị Thu Trang', 'info@viettel.com.vn', '18008098', 'Lô D26, KĐT Mới Cầu Giấy, Yên Hòa, Cầu Giấy, Hà Nội', 'VIP', 2500000000.00),
('Ngân hàng TMCP Ngoại thương Việt Nam (Vietcombank)', 'Lê Đức Minh', 'contact@vietcombank.com.vn', '1900545413', '198 Trần Quang Khải, Hoàn Kiếm, Hà Nội', 'VIP', 1800000000.00),
('Công ty Cổ phần Tập đoàn Masan', 'Vũ Quốc Khánh', 'info@masangroup.com', '028 6256 3862', 'Tầng 8, Central Plaza, 17 Lê Duẩn, Quận 1, TP. HCM', 'CUSTOMER', 650000000.00),
('Tập đoàn Bưu chính Viễn thông Việt Nam (VNPT)', 'Phạm Hoàng Nam', 'vanphong@vnpt.vn', '18001091', 'Tòa nhà VNPT, 57 Huỳnh Thúc Kháng, Đống Đa, Hà Nội', 'CUSTOMER', 850000000.00),
('Công ty Cổ phần Chứng khoán SSI', 'Bùi Ngọc Linh', 'support@ssi.com.vn', '1900545471', '72 Nguyễn Huệ, P. Bến Nghé, Quận 1, TP. HCM', 'PROSPECT', 420000000.00),
('Công ty TNHH Phần mềm Misa', 'Đặng Thùy Dương', 'contact@misa.vn', '024 3795 9595', 'Tòa nhà MISA, Lô 5, CVPM Quang Trung, Quận 12, TP. HCM', 'PROSPECT', 300000000.00),
('Công ty Cổ phần Thế Giới Di Động (MWG)', 'Hoàng Văn Bách', 'mwg@thegioididong.com', '028 3812 5960', 'Tòa nhà MWG, Lô T2-1.2, Đường D1, Khu Công nghệ cao, TP. Thủ Đức', 'CUSTOMER', 920000000.00),
('Ngân hàng TMCP Quân đội (MBBank)', 'Trần Minh Tuấn', 'mbbank@mbbank.com.vn', '1900545426', 'Tòa nhà MB, 18 Lê Văn Lương, Cầu Giấy, Hà Nội', 'VIP', 1500000000.00),
('Công ty Cổ phần Sữa Việt Nam (Vinamilk)', 'Nguyễn Mai Chi', 'vinamilk@vinamilk.com.vn', '028 5415 5555', 'Số 10 Tân Trào, Phường Tân Phú, Quận 7, TP. HCM', 'CUSTOMER', 780000000.00),
('Công ty TNHH Giải pháp Phần mềm Thái Nguyên', 'Lê Hữu Đạt', 'datlh@tnsolution.vn', '0208 3855 999', 'Số 120 Đường Hoàng Văn Thụ, TP. Thái Nguyên', 'LEAD', 150000000.00),
('Trung tâm CNTT & Truyền thông Thái Nguyên', 'Đỗ Thành Vinh', 'vinhdt@ict-thainguyen.gov.vn', '0208 3656 888', 'Số 5 Đường Đội Cấn, TP. Thái Nguyên', 'LEAD', 90000000.00);

-- Seed Data: Contacts
INSERT INTO contacts (customer_id, full_name, position, email, phone, notes) VALUES
(1, 'Nguyễn Văn Hải', 'Giám đốc Trung tâm Hạ tầng', 'hai.nv@fpt.vn', '0912 345 678', 'Phụ trách đàm phán giải pháp CRM tích hợp Cloud'),
(1, 'Lê Thị Thu Hằng', 'Trưởng phòng Mua sắm Thiết bị', 'hang.ltt@fpt.vn', '0983 111 222', 'Cần gửi báo giá định kỳ hàng quý'),
(2, 'Trần Thị Thu Trang', 'Phó TGĐ Khối Khách hàng Doanh nghiệp', 'trangttt@viettel.com.vn', '0977 888 999', 'Quan tâm tính năng giám sát hạ tầng và bảo mật dữ liệu'),
(2, 'Đỗ Khắc Tuấn', 'Trưởng phòng Kỹ thuật Phần mềm', 'tuandk@viettel.com.vn', '0989 222 333', 'Yêu cầu kiểm tra tuân thủ CIS benchmark và Docker hardening'),
(3, 'Lê Đức Minh', 'Giám đốc Khối Công nghệ Thông tin', 'minhld@vietcombank.com.vn', '0903 456 789', 'Ưu tiên cơ sở dữ liệu PostgreSQL bảo mật cao, mã hóa kết nối'),
(4, 'Vũ Quốc Khánh', 'Quản lý Dự án Số hóa Chuỗi cung ứng', 'khanhvq@masangroup.com', '0918 555 666', 'Đang thử nghiệm giải pháp quản lý tương tác đại lý'),
(5, 'Phạm Hoàng Nam', 'Trưởng ban Công nghệ VNPT Media', 'namph@vnpt.vn', '0944 666 777', 'Hẹn họp demo trực tiếp tại trụ sở');

-- Seed Data: Interactions
INSERT INTO interactions (customer_id, type, summary, outcome, agent_name, interaction_date) VALUES
(1, 'MEETING', 'Họp trao đổi kỹ thuật về triển khai module CRM Chăm sóc Khách hàng trên nền tảng Docker Compose. Khách hàng đánh giá cao kiến trúc phân tầng an toàn.', 'POSITIVE', 'Phàn Ngọc Anh', NOW() - INTERVAL '5 days'),
(1, 'QUOTE', 'Gửi bảng báo giá chi tiết gói phần mềm CRM Quản lý tương tác và dịch vụ hỗ trợ SLA 24/7.', 'POSITIVE', 'Phàn Ngọc Anh', NOW() - INTERVAL '3 days'),
(2, 'DEMO', 'Buổi Demo giải pháp giám sát Prometheus + Grafana kết hợp lưu trữ log tập trung Loki cho khối viễn thông.', 'POSITIVE', 'Phàn Ngọc Anh', NOW() - INTERVAL '4 days'),
(2, 'CALL', 'Gọi điện thoại cập nhật tiến độ phê duyệt hồ sơ thầu dự án CRM nội bộ Viettel Solution.', 'PENDING', 'Nguyễn Văn A', NOW() - INTERVAL '2 days'),
(3, 'MEETING', 'Làm việc với đội ngũ An toàn thông tin Vietcombank về chính sách Nginx SSL, security headers và cô lập mạng backend PostgreSQL.', 'POSITIVE', 'Phàn Ngọc Anh', NOW() - INTERVAL '6 days'),
(4, 'CALL', 'Khảo sát nhu cầu mở rộng quy mô quản lý tương tác với hơn 100 đối tác phân phối Masan.', 'POSITIVE', 'Lê Thị B', NOW() - INTERVAL '1 day'),
(5, 'EMAIL', 'Gửi tài liệu kiến trúc kỹ thuật và hướng dẫn sử dụng giao diện quản lý khách hàng cho VNPT.', 'PENDING', 'Phàn Ngọc Anh', NOW() - INTERVAL '8 hours'),
(6, 'MEETING', 'Gặp mặt thảo luận về nhu cầu quản lý danh bạ nhà đầu tư VIP và lịch sử chăm sóc tài khoản SSI.', 'PENDING', 'Phàn Ngọc Anh', NOW() - INTERVAL '12 hours'),
(7, 'CALL', 'Trao đổi qua điện thoại về tích hợp API dữ liệu giữa CRM và phần mềm kế toán.', 'PENDING', 'Nguyễn Văn A', NOW() - INTERVAL '1 day'),
(11, 'CALL', 'Liên hệ làm quen và giới thiệu giải pháp CRM cho doanh nghiệp phần mềm tại Thái Nguyên.', 'POSITIVE', 'Phàn Ngọc Anh', NOW() - INTERVAL '2 days'),
(12, 'EMAIL', 'Gửi thư mời tham gia hội thảo chuyển đổi số và demo ứng dụng CRM nguồn mở trên hạ tầng đám mây.', 'PENDING', 'Phàn Ngọc Anh', NOW() - INTERVAL '3 hours');
