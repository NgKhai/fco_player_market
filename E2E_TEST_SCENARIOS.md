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
| 2026-09-13 | `squad-builder.cy.js` | Formation picker và suggest đúng vị trí GK | PASS (2/2) |
| 2026-09-13 | `web-critical.cy.js` | Database, search, filter, sort, detail, auth, formation, assignment/reset | PASS (8/8) |

**Tổng kết:** PASS — 10/10 test tự động, 0 failure.
