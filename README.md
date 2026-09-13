# ⚽ FC Online Data Extractor & Market Tool

Bộ công cụ tự động thu thập, trích xuất và quản lý dữ liệu cầu thủ, mùa thẻ, chỉ số chi tiết, ảnh Miniface HD và giá Thị Trường Chuyển Nhượng (TTCN) cho **FC Online**.

---

## 📁 Cấu trúc thư mục dự án

```text
D:\Coding\ToolFCO\
├── core/
│   ├── db_builder.py          # Quản lý SQLite Database & xuất JSON
│   ├── nexon_client.py        # Thu thập Metadata toàn cầu từ Nexon API (88.000+ cầu thủ)
│   ├── fifaaddict_client.py   # Thu thập chỉ số chi tiết, Tiếng Việt & giá TTCN từ FIFAAddict
│   └── miniface_downloader.py # Tải ảnh chân dung Miniface HD đa luồng
├── output/
│   ├── database/
│   │   ├── fconline.sqlite    # Cơ sở dữ liệu SQLite chuẩn
│   │   └── players_db.json    # File xuất JSON sạch
│   ├── minifaces/
│   │   ├── action/            # Ảnh Action Miniface HD ({spid}.png)
│   │   └── base/              # Ảnh chân dung Base Avatar ({pid}.png)
│   └── localization/          # Bản dịch tiếng Việt
├── config.py                  # Cấu hình đường dẫn và API
├── main.py                    # Menu điều khiển chính (CLI)
└── run.bat                    # Chạy nhanh công cụ với 1 click
```

---

## 🚀 Hướng dẫn sử dụng

Chỉ cần chạy file `run.bat` hoặc gõ lệnh:
```bash
python main.py
```

### Các tính năng chính trong Menu:
1. **🔄 Đồng bộ toàn bộ Metadata:** Tải hơn 88.000 cầu thủ, 152 mùa giải (Seasons) và 29 vị trí thi đấu vào SQLite Database.
2. **🖼️ Tải kho ảnh Miniface HD:** Tải ảnh chân dung (Action & Base PNG) cho cầu thủ theo mùa giải (ICON TM, 24TOTY...), top cầu thủ hoặc mã SPID tùy chọn.
3. **🔍 Tra cứu cầu thủ:** Tìm kiếm nhanh theo tên tiếng Anh / Hàn / Việt hoặc ID.
4. **🇻🇳 Lấy chi tiết & Giá TTCN:** Lấy toàn bộ chỉ số OVR, lương, thể hình, kỹ năng ẩn và giá TTCN từ nấc thẻ +1 đến +10.
5. **💾 Xuất Database JSON:** Xuất toàn bộ dữ liệu sạch ra `output/database/players_db.json` phục vụ cho việc làm website hoặc API riêng.

## 🧪 Chạy E2E với Cypress

```bash
npm install
npx cypress install
run_web.bat
npm run test:e2e
```

Muốn mở giao diện Cypress để debug:

```bash
npm run test:e2e:open
```

Cấu hình nằm ở `cypress.config.js`, test ở `cypress/e2e/`. Server Laravel phải chạy tại `http://127.0.0.1:8080`.
