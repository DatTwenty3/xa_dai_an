# HƯỚNG DẪN TÁI SỬ DỤNG BẢN ĐỒ GIS CHO XÃ KHÁC

Tài liệu này hướng dẫn bạn cách chuyển đổi trang web bản đồ số tương tác này sang một xã/phường/thị trấn mới từ A-Z một cách nhanh chóng và tự động hóa.

Hệ thống đã được chuyển đổi sang kiến trúc **hướng cấu hình (configuration-driven)**. Bạn không cần phải chỉnh sửa mã nguồn JavaScript (`js/app.js`) hay HTML (`index.html`) thủ công nữa. Thay vào đó, toàn bộ quy trình được tự động hóa thông qua các file cấu hình và kịch bản Python.

---

## 1. Cấu trúc thư mục dữ liệu

Khi chuẩn bị dữ liệu cho xã mới, bạn chỉ cần quan tâm và cập nhật các thư mục/file sau:

*   `commune-config.json` *(Mới)*: File cấu hình thông tin chung của xã mới.
*   `map data/`: Thư mục chứa các file GeoJSON của các **Ấp mới** (ví dụ: `Ấp 1.geojson`, `Ấp Xóm Lớn.geojson`).
*   `map data/ranh gioi ap cu/`: Thư mục chứa các file GeoJSON của các **Ấp cũ trước sáp nhập** (nếu có).

---

## 2. Các bước chuẩn bị dữ liệu

### Bước 2.1: Khai báo thông tin xã mới
Mở file `commune-config.json` ở thư mục gốc của dự án và điền thông tin của xã mới:

```json
{
  "commune_name": "Cầu Kè",         // Tên xã (ví dụ: "Cầu Kè", "Tam Ngãi")
  "province_name": "Vĩnh Long",     // Tên tỉnh/thành phố (ví dụ: "Trà Vinh")
  "year": "2026",                   // Năm thực hiện dự án
  "month": "5",                     // Tháng thực hiện dự án
  "company_name": "CÔNG TY ÂU LẠC",  // Tên đơn vị thiết kế bản đồ số
  "voice": "vi-VN-HoaiMyNeural",    // Giọng nói TTS (Mặc định: vi-VN-HoaiMyNeural)
  "tts_rate": "+15%",               // Tốc độ đọc (Mặc định: +15%)
  "default_zoom": 13                // Mức thu phóng mặc định của bản đồ
}
```

### Bước 2.2: Chuẩn bị file GeoJSON cho các Ấp mới
Xóa các file GeoJSON cũ trong thư mục `map data/` (giữ lại thư mục `ranh gioi ap cu` bên trong). Đưa các file GeoJSON của các ấp mới vào thư mục này.

> [!IMPORTANT]
> **Quy định thuộc tính (Properties) trong mỗi file GeoJSON của Ấp mới:**
> Mỗi file GeoJSON của ấp mới chỉ nên chứa **1 Feature** duy nhất đại diện cho ấp đó. Thuộc tính (`properties`) của Feature bắt buộc phải chứa các trường dữ liệu sau:
> 
> *   `ten`: Tên hiển thị của ấp (ví dụ: `"Ấp 1"`, `"Ấp Thông Thảo"`)
> *   `ma`: Mã định danh duy nhất của ấp (chỉ gồm số, dùng để sinh file audio thuyết minh, ví dụ: `"3005001"`)
> *   `loai`: Loại hình đơn vị hành chính (ví dụ: `"Ấp"` hoặc `"Khu phố"`)
> *   `dien_tich_ha`: Diện tích ấp (đơn vị: héc-ta, ví dụ: `385.91`)
> *   `so_ho`: Tổng số hộ dân trong ấp (ví dụ: `571`)
> *   `dan_so`: Tổng dân số trong ấp (ví dụ: `2421`)
> *   `sap_nhap_tu`: Mảng chứa danh sách tên các ấp cũ được sáp nhập thành ấp mới này.
>     *   *Trường hợp ấp giữ nguyên ranh giới:* `["Ấp Thông Thảo"]`
>     *   *Trường hợp sáp nhập từ nhiều ấp cũ:* `["Ấp 1", "Ấp 2", "Ấp 3"]`

### Bước 2.3: Chuẩn bị file GeoJSON cho các Ấp cũ (Nếu có)
Nếu xã mới có các khu vực sáp nhập hành chính và bạn có dữ liệu ranh giới của các ấp cũ:
1. Mở thư mục `map data/ranh gioi ap cu/` và xóa các file cũ.
2. Đặt các file GeoJSON ranh giới ấp cũ tương ứng vào thư mục này. Tên file GeoJSON của ấp cũ phải trùng khớp hoàn toàn với tên được liệt kê trong thuộc tính `sap_nhap_tu` của ấp mới (ví dụ: `Ấp Trà Bôn.geojson`).
3. Nếu bạn không có file GeoJSON ranh giới của các ấp cũ, **hệ thống vẫn hoạt động bình thường**. Script đồng bộ sẽ tự động phân bổ nhãn ấp cũ bao quanh tâm ấp mới để hiển thị các đường kết nối chấm bi đẹp mắt mà không làm lỗi bản đồ.

---

## 3. Quy trình đồng bộ hóa tự động

Sau khi chuẩn bị xong dữ liệu ở mục 2, hãy mở terminal tại thư mục dự án và chạy tuần tự hai lệnh sau:

### Lệnh 1: Đồng bộ hóa dữ liệu bản đồ và HTML
```bash
python scratch/sync_data.py
```
**Tác vụ tự động thực hiện:**
- Quét các file GeoJSON trong `map data/` để trích xuất và kiểm tra thuộc tính.
- Tự động cộng dồn số liệu diện tích, dân số, số hộ của tất cả các ấp để tính toán số liệu tổng của toàn xã.
- Tự động tính toán tọa độ tâm (centroid) địa lý của các ấp để đặt nhãn tên.
- Phân bổ bảng màu độ tương phản cao ngẫu nhiên cho các ấp mới để tránh trùng màu.
- Tự động ghi đè thông tin cấu hình xã mới vào `index.html` (Tiêu đề trang, Meta mô tả chuẩn SEO, Popup giới thiệu chào mừng và chân trang bản quyền).
- Tạo ra file cấu hình trung gian `map data/compiled-config.json` để trang web đọc động.

### Lệnh 2: Sinh tệp âm thanh thuyết minh tự động (TTS)
```bash
python generate_audio.py
```
**Tác vụ tự động thực hiện:**
- Kết nối tới dịch vụ thuyết minh thông minh Edge-TTS qua mạng.
- Tự động sinh file audio chào mừng chào đại biểu `audio/intro.mp3` bằng tên xã mới.
- Tự động phân tích xem ấp nào là ấp sáp nhập, ấp nào giữ nguyên và sinh văn bản thuyết minh chi tiết cho từng ấp, sau đó xuất ra tệp audio thuyết minh tương ứng dưới dạng `audio/{ma}.mp3` (ví dụ: `audio/3005001.mp3`).

---

## 4. Chạy thử trang web tại môi trường cục bộ

Sau khi hoàn tất quy trình ở mục 3, bạn có thể chạy thử dự án trên trình duyệt bằng cách chạy máy chủ Web cục bộ:

```bash
# Sử dụng Python để chạy Web server nhanh chóng
python -m http.server 8000
```
Sau đó truy cập địa chỉ [http://localhost:8000](http://localhost:8000) trên trình duyệt để kiểm tra thành quả của xã mới.

---

## 5. Tự động hóa hoàn toàn với AI (Gọi kỹ năng `skill.md`)

Nếu bạn đang làm việc với một trợ lý AI Code (như Antigravity / Gemini), bạn không cần chạy các lệnh thủ công bằng tay.

**Cách làm cực kỳ đơn giản:**
1. Chép dữ liệu GeoJSON ấp mới/cũ vào thư mục.
2. Sửa file `commune-config.json`.
3. Gửi yêu cầu cho AI trợ lý: 
   > *"Hãy thực hiện đồng bộ xã mới của tôi theo hướng dẫn trong file [skill.md](file:///d:/4.%20code/xa_cau_ke/skill.md) từ A-Z."*
   
Trợ lý AI sẽ đọc file `skill.md`, tự động chạy các script Python, kiểm tra lỗi cú pháp, xác thực cấu hình bản đồ và báo cáo lại kết quả hoàn thành cho bạn sau vài giây!
