# KỸ NĂNG AI: ĐỒNG BỘ DỮ LIỆU BẢN ĐỒ CHO XÃ MỚI (AUTOMATION SKILL)

Tệp này cung cấp kỹ năng tự động hóa đồng bộ từ A-Z cho AI Agent khi bạn muốn cập nhật dữ liệu xã mới. Trợ lý AI sẽ đọc tệp này để biết cách thực hiện công việc một cách chính xác mà không cần sự can thiệp thủ công từ bạn.

---

## 1. Mục tiêu hành động của AI (Agent Goal)
Đọc cấu hình xã mới, xử lý hình học GeoJSON của các ấp, tính toán tự động số liệu hành chính tổng thể, cập nhật giao diện `index.html` và sinh các tệp âm thanh thuyết minh (TTS) tương ứng cho xã mới.

---

## 2. Các bước thực hiện chi tiết cho AI Agent

### Bước 1: Kiểm tra cấu hình và tệp GeoJSON đầu vào
1. Đọc tệp [commune-config.json](file:///d:/4.%20code/xa_cau_ke/commune-config.json) ở thư mục gốc của dự án.
2. Kiểm tra xem các tệp GeoJSON mới đã được đặt trong thư mục `map data/` chưa.
3. Kiểm tra xem các ranh giới ấp cũ (nếu có) đã được đặt trong `map data/ranh gioi ap cu/` chưa.

### Bước 2: Chạy script đồng bộ hóa dữ liệu bản đồ
1. Thực thi kịch bản Python để biên dịch số liệu và cập nhật giao diện:
   ```powershell
   python scratch/sync_data.py
   ```
2. Đọc kết quả đầu ra (output) của lệnh trên. Xác nhận xem:
   - Các ấp mới đã được tính tâm (center) và gán màu thành công chưa.
   - Các ấp cũ và vị trí nhãn cũ đã được phân bổ thành công chưa.
   - File cấu hình đã biên dịch thành công ra [compiled-config.json](file:///d:/4.%20code/xa_cau_ke/map%20data/compiled-config.json) chưa.
   - File [index.html](file:///d:/4.%20code/xa_cau_ke/index.html) đã được cập nhật tiêu đề, mô tả và giới thiệu chào mừng khớp với cấu hình chưa.

### Bước 3: Gọi API sinh âm thanh thuyết minh tự động (TTS)
1. Thực thi kịch bản Python sinh âm thanh:
   ```powershell
   python generate_audio.py
   ```
2. Đọc kết quả đầu ra. Đảm bảo rằng:
   - Tệp loa phát thanh giới thiệu chung [intro.mp3](file:///d:/4.%20code/xa_cau_ke/audio/intro.mp3) đã được tạo mới.
   - Với mỗi mã ấp (`ma`) trong danh sách, tệp thuyết minh [audio/{ma}.mp3](file:///d:/4.%20code/xa_cau_ke/audio/) tương ứng đã được tạo thành công và kích thước > 0.
   - Không có lỗi kết nối mạng hoặc lỗi API Edge-TTS.

### Bước 4: Kiểm tra và xác thực chất lượng trang web (Verification)
1. Xác minh định dạng JSON của [compiled-config.json](file:///d:/4.%20code/xa_cau_ke/map%20data/compiled-config.json) là hợp lệ.
2. Kiểm tra xem mã nguồn JavaScript [app.js](file:///d:/4.%20code/xa_cau_ke/js/app.js) có lỗi cú pháp nào không.
3. Xác nhận xem tất cả các file MP3 thuyết minh có khớp đúng với các mã ấp được liệt kê trong `compiled-config.json` hay không.

### Bước 5: Báo cáo kết quả cho người dùng
Sau khi hoàn thành, AI Agent sẽ viết một báo cáo ngắn gọn tóm tắt:
- Tổng số ấp mới đã đồng bộ.
- Số liệu thống kê tổng hợp của xã mới (Tổng diện tích, Tổng dân số, Số hộ, Mật độ).
- Danh sách các file âm thanh đã sinh.
- Hướng dẫn người dùng lệnh khởi chạy Web server cục bộ để kiểm tra trực quan.
