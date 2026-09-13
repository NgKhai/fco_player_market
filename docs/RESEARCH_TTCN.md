# Nghiên cứu lấy giá TTCN FC Online Việt Nam

Ngày kiểm tra: 2026-09-14
Phạm vi: nguồn chính thức Garena/Nexon và code hiện có trong repo. Không dùng credential/token thật, không gọi luồng đăng nhập, không reverse-engineer client và không sửa code.

## Kết luận ngắn

1. **Nexon Open API không phải nguồn giá TTCN VN.** Danh mục FC Online chính thức hiện có account, match, ranker, metadata và image; không liệt kê market/price. Các API game trong hướng dẫn yêu cầu API key, có giới hạn và nghĩa vụ cập nhật dữ liệu tối đa 30 ngày một lần; static metadata là ngoại lệ chưa được xác minh live. ([FC Online API catalog](https://openapi.nexon.com/game/fconline/), [Using the API](https://openapi.nexon.com/guide/request-api/), [Getting Started](https://openapi.nexon.com/guide/prepare-in-advance/))
2. **Đối với giá server VN, Garena là nguồn authoritative cần ưu tiên**, nhưng trong tài liệu công khai đã kiểm tra không có developer API/SDK hay schema cho giá TTCN. Garena chỉ xác nhận TTCN là tính năng trong game và FC Online Mobile đồng bộ dữ liệu, bao gồm mua/bán cầu thủ. ([TTCN guide](https://fconline.garena.vn/thi-truong-chuyen-nhuong-trong-fifa-online-4/), [PC/Mobile installation guide](https://fconline.garena.vn/huong-dan-tai-va-cai-dat-fc-online/), [official Data Center link](https://dc.fconline.garena.vn/))
3. **Phương án thực dụng hiện tại** là session/token Garena do người dùng cung cấp + cache cục bộ, nhưng đây là integration không được tài liệu hóa và không nên gọi là “official API”. Phương án sản xuất đúng là xin quyền truy cập/API bằng văn bản từ Garena; nếu không có, chỉ nên dùng giá tham chiếu/cache/manual import.

## Những gì repo đang làm

Đã xác minh từ source code, chưa coi là xác minh live với máy chủ:

- `core/garena_vn_client.py:16` đặt base URL `https://fcom.garena.vn/api`.
- `core/garena_vn_client.py:103-144` gọi `GET /market/card_price?spid=<SPID>` với `Authorization: Bearer <token>`, `X-GARENA-UID`, `Referer` và `Origin`; kỳ vọng JSON có `code == 0`, `data.prices`, rồi chuẩn hóa grade `1..10` thành `vn1..vn10`.
- `core/garena_vn_client.py:107-111` dùng cache trước khi gọi live, tối đa 1.800 giây; `force_refresh=True` mới bỏ qua cache.
- `core/db_builder.py:68-87,181-227` lưu giá vào `market_prices_vn`, khóa `(spid, grade)`, cùng `updated_at`; token và UID nằm trong `app_settings`.
- `web/server.py:325-356` chỉ lấy giá VN khi query có `spid` dạng số; nếu không có giá VN thì trả `active_server = "KR"`. Web route hiện không truyền `force_refresh`, nên UI dùng cache 30 phút.
- `core/garena_vn_client.py:41-101` còn có luồng gửi thông tin đăng nhập tới `https://auth.garena.com/oauth/token/grant`; code không chứng minh endpoint này còn hoạt động hay được Garena hỗ trợ.
- `core/fifaaddict_client.py:16-85` dùng session handshake riêng (`X-ARAIWA`) với FIFAAddict để tìm kiếm/chi tiết cầu thủ. Đây là nguồn bên thứ ba, không phải nguồn chính thức của Garena/Nexon.
- `config.py:22-26` dùng các static metadata URL chính thức của Nexon; `core/nexon_client.py` hiện không gửi `x-nxopen-api-key`, trong khi hướng dẫn Open API nói request Open API cần header API key. Việc static metadata có được miễn key hay không chưa được kiểm tra live trong nghiên cứu này.

## So sánh phương án

| Phương án | Trạng thái tài liệu chính thức | Độ phù hợp với giá TTCN VN | Rủi ro/vận hành | Đánh giá |
|---|---|---:|---|---|
| **Garena API/partner access bằng văn bản** | Chưa tìm thấy docs public; cần Garena cấp contract, auth và rate limit | Cao nhất | Phụ thuộc phê duyệt nhưng có đường nâng cấp ổn định | **Nên chọn cho production** |
| **Endpoint Garena session hiện có trong repo** | Domain Garena nhưng endpoint/schema chưa được tài liệu hóa công khai | Cao nếu session còn hợp lệ; chưa live-verified | Token hết hạn, schema đổi, rate limit/khóa tài khoản; không có SLA | Chỉ dùng local/experimental, không quảng bá là official API |
| **Nexon Open API** | Có docs và API key flow chính thức; danh mục FC Online không có market/price | Thấp cho mục tiêu giá VN; tốt cho metadata/account/match | API key, quota, attribution và điều khoản sử dụng | Dùng cho metadata, **không thay thế giá TTCN** |
| **FC Online Mobile session** | Garena xác nhận Mobile đồng bộ dữ liệu và hỗ trợ TTCN | Có thể có dữ liệu đúng server VN | Không có public API contract; phụ thuộc session/app version | Không tự động hóa khi chưa có quyền/contract |
| **Web/client session** | Chỉ là giao diện người dùng chính thức, không phải API public | Có thể truy cập đúng dữ liệu nếu người dùng đã đăng nhập | Fragile; dễ đụng CAPTCHA, anti-bot và điều khoản; không reverse-engineer | Không chọn làm backend crawler |
| **Garena Data Center public UI** | Link Data Center được đặt trên trang FC Online chính thức | Có thể hữu ích cho người dùng xem thủ công | Trang công khai không đồng nghĩa có export/API; chưa có tài liệu endpoint | Chỉ dùng thủ công nếu chưa có API contract |
| **Crawler/public data bên thứ ba** | Không phải primary source | Có thể có giá/chi tiết tham chiếu | Sai khác server, trễ, điều khoản và độ bền thấp | Fallback hiển thị “tham khảo”, không ghi là giá live VN |
| **Manual token + SQLite cache** | Không cần API public mới | Tốt cho bản local và traffic thấp | Token plaintext trong DB, thao tác thủ công, hết hạn; không phù hợp dịch vụ nhiều người dùng | **Phương án ngắn hạn ít code nhất** |

## Khuyến nghị triển khai

### Ngắn hạn

- Giữ metadata Nexon và cache giá hiện có.
- Nếu tiếp tục dùng session Garena, chỉ hỗ trợ **dán token/UID do chính người dùng lấy từ kênh chính thức**, không lưu hoặc nhận mật khẩu trong frontend/backend.
- Trả rõ trạng thái `live`, `cache`, `stale` hoặc `unavailable`; không fallback giá KR rồi gắn nhãn như giá VN.
- Không đưa token vào log, test fixture, commit hoặc response API không cần thiết.

Garena cảnh báo người chơi không cung cấp mật khẩu cấp 1/2/3, OTP hay thông tin tài khoản cho bất kỳ ai; vì vậy luồng `/api/garena/login` hiện có là điểm cần xem xét lại trước khi phát hành công khai, dù code đang hash password trước khi gửi. ([Garena account-safety warning](https://fconline.garena.vn/canh-bao-lua-dao-va-cach-bao-ve-tai-khoan-fc-online/), [Garena support fraud FAQ](https://hotro.ff.garena.vn/faq/tiep-nhan-thong-tin-lua-dao_330/))

### Production

1. Gửi yêu cầu Garena xin API/partner access cho mục đích tra cứu giá TTCN, gồm server VN, SPID, grade `+1..+10`, quota, cache/redistribution và attribution.
2. Chỉ sau khi có contract mới thay endpoint/session bằng client chính thức có timeout, retry, rate limit và schema validation.
3. Nếu Garena không cấp quyền, công bố sản phẩm theo hướng **metadata + giá người dùng nhập/cache tham chiếu**, không crawler giá live từ client.

Nexon cũng yêu cầu dùng API đúng tài liệu/điều khoản; terms cấm truy cập thêm dữ liệu ngoài API, can thiệp cơ chế vận hành/bảo mật và reverse-engineer/circumvent protection. ([Nexon API Terms](https://openapi.nexon.com/support/terms/))

## Điểm chưa xác minh

- `fcom.garena.vn/api/market/card_price` có còn hoạt động, response thực tế, mã lỗi, TTL token và rate limit: **chưa gọi live**.
- `auth.garena.com/oauth/token/grant` với `client_id=100067` có còn được hỗ trợ cho FC Online VN: **chưa xác minh**.
- Có hay không API/export chính thức riêng cho Data Center: **không thấy trong tài liệu public đã kiểm tra**.
- Session của FC Online Mobile và web có được Garena cho phép dùng ngoài app/client hay không: **không có tài liệu public xác nhận**.
- Giá FIFAAddict có trùng server VN, độ trễ và quyền tái phân phối: **chưa xác minh; không dùng làm primary source**.

## Nguồn chính thức đã kiểm tra

- [Nexon FC Online API catalog](https://openapi.nexon.com/game/fconline/)
- [Nexon Open API — Getting Started](https://openapi.nexon.com/guide/prepare-in-advance/)
- [Nexon Open API — Using the API](https://openapi.nexon.com/guide/request-api/)
- [Nexon Open API Terms of Service](https://openapi.nexon.com/support/terms/)
- [Nexon notice: old API to new Open API migration](https://openapi.nexon.com/ko/support/notice/2513000/)
- [Garena FC Online — TTCN guide](https://fconline.garena.vn/thi-truong-chuyen-nhuong-trong-fifa-online-4/)
- [Garena FC Online — PC/Mobile installation guide](https://fconline.garena.vn/huong-dan-tai-va-cai-dat-fc-online/)
- [Garena FC Online — Summer 2026 update](https://fconline.garena.vn/ban-tin-cap-nhat-mua-he-2026/)
- [Garena FC Online — account-safety warning](https://fconline.garena.vn/canh-bao-lua-dao-va-cach-bao-ve-tai-khoan-fc-online/)
- [Garena support — TTCN FAQ](https://hotro.ff.garena.vn/faq/thi-truong-chuyen-nhuong_387/)
- [Garena support — fraud FAQ](https://hotro.ff.garena.vn/faq/tiep-nhan-thong-tin-lua-dao_330/)
