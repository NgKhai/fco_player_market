# E2E Test Scenarios — FC Online Player Market

## Phạm vi

Kiểm thử các luồng quan trọng trên web tại `http://localhost:8080`:

| ID | Scenario | Loại | Expected result |
|---|---|---|---|
| E2E-001 | Mở trang database | Automated | Hiển thị danh sách cầu thủ |
| E2E-002 | Tìm cầu thủ theo tên | Automated | Kết quả chứa đúng cầu thủ |
| E2E-003 | Lọc database theo vị trí | Automated | Card chỉ chứa vị trí đã chọn |
| E2E-004 | Thay đổi thứ tự sắp xếp | Automated | Select nhận đúng sort option |
| E2E-005 | Mở/đóng chi tiết cầu thủ | Automated | Modal chi tiết hiển thị và đóng được |
| E2E-006 | Login Garena khi bỏ trống | Automated | Hiển thị validation, không gửi login |
| E2E-007 | Đổi formation | Automated | Formation đổi và có đủ 11 slot |
| E2E-008 | Chọn cầu thủ cho slot | Automated | Cầu thủ được gán vào pitch |
| E2E-009 | Reset squad builder | Automated | Toàn bộ assignment bị xóa |
| E2E-010 | Token Garena hợp lệ | Manual/Security | Không commit token; chỉ kiểm tra trên máy local |
| E2E-011 | Giá TTCN VN khi có session | Manual/Security | Chỉ kiểm tra sau khi đăng nhập tài khoản phụ/token riêng |
| E2E-012 | Miniface lỗi tải ảnh | Manual/Visual | UI dùng fallback, không vỡ layout |
| E2E-013 | Formation mapping tường minh | Automated | `4-1-2-1-2` hiển thị GK, LB, CB, CB, RB, CDM, LM, RM, CAM, ST, ST |
| E2E-014 | Khôi phục formation sau reload | Automated | Formation đã chọn và assignment tương thích vẫn được khôi phục |
| E2E-015 | Lưu nhiều squad có tên | Automated | Có thể lưu squad mới, chọn squad khác và xóa squad |
| E2E-016 | Chi tiết cầu thủ không tồn tại | Automated/API | API trả 404/status error; UI hiển thị lỗi rõ ràng |

## Cách chạy

```bash
npm install
npx cypress install
run_web.bat
npm run test:e2e
```

Chạy riêng bộ critical:

```bash
npx cypress run --spec cypress/e2e/web-critical.cy.js --browser electron
```

## Kết quả chạy

| Run date | Spec | Result | Pass/Fail |
|---|---|---|---|
| 2026-09-13 | `squad-builder.cy.js` | Formation picker, mapping vị trí, lọc GK, lưu/khôi phục, nhiều squad, reset, responsive | PASS (10/10) |
| 2026-09-13 | `web-critical.cy.js` | Database, search, filter, sort, detail, detail 404, local source, miniface, formation, assignment/reset | PASS (13/13) |

**Mốc trước P2:** PASS — 22/22 test tự động, 0 failure.

**Mốc hiện tại sau khi thêm scenario P2:** PASS — 23/23 test tự động, 0 failure.

## Audit dữ liệu builder

| Thông tin | Kết luận |
|---|---|
| Team stats | Chưa đủ: `team_name` từ dữ liệu import là nhãn mùa thẻ; nhánh `players` cũng chưa trả field này cho builder. |
| Position points | Đã có `pos1val`/`pos2val` ở dữ liệu import và builder đang dùng để tính OVR theo vị trí; không có bảng điểm riêng cần thêm. |
| Bonus/team color | Chưa có field hoặc domain rule; không hiển thị giả. |
| Cấp độ thẻ | Chưa có `grade` trong dữ liệu builder; `skill_level` là cấp skill, không suy diễn thành cấp thẻ. |
| Substitutes | Chưa có data model hoặc UI; để lượt sau. |
