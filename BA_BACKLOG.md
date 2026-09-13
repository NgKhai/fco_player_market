# BA backlog — FCO Player Market

## Đã có

- Tra cứu theo mùa và từ khóa.
- Lọc vị trí, sắp xếp OVR/lương/tên.
- Xem chi tiết cầu thủ.
- Squad Builder: formation, chọn cầu thủ theo vị trí, đổi chỗ, tính OVR/lương.
- Laravel phục vụ web/API; Python chỉ chạy crawler, tải miniface và tác vụ `.bat`.

## Còn thiếu theo ưu tiên

### P0 — cần cho MVP

- Đồng bộ dữ liệu VN đầy đủ: `name_vi`, `name_en`, `main_pos`, chỉ số và giá TTCN.
- Trạng thái lỗi, retry và empty state cho từng request API.
- Kiểm tra dữ liệu đầu vào/giới hạn kết quả ở API search.
- Test E2E chạy theo URL Laravel `127.0.0.1:8000`.

### P1 — tăng giá trị người dùng

- Lưu/khôi phục đội hình và đặt tên đội hình.
- So sánh 2–3 cầu thủ cạnh nhau.
- Lọc kết hợp: mùa, vị trí, OVR, lương, chân thuận.
- Phân trang hoặc tải thêm thay vì giới hạn cứng 200 thẻ.
- Giá VN theo từng mức thẻ và thời điểm cập nhật.

### P2 — hoàn thiện sản phẩm

- Tài khoản người dùng và đồng bộ đội hình trên nhiều thiết bị.
- Xuất/chia sẻ đội hình bằng URL hoặc ảnh.
- Lịch sử giá và biểu đồ biến động.
- Trang quản trị chạy crawler, xem trạng thái đồng bộ và log.
- Rate limit, cache và observability cho môi trường production.

## Quyết định phạm vi hiện tại

Web không gọi Python runtime. Python vẫn là worker thủ công qua các file `.bat` để crawl dữ liệu và tải asset; Laravel chỉ đọc dữ liệu đã được worker ghi vào SQLite.
