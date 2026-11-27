# Luồng xương sống CarShowroom

## Một lần bấm đi qua những tầng nào

```mermaid
flowchart LR
    A["Vue Router<br/>route và màn hình"] --> B["View hoặc Pinia<br/>trạng thái và thao tác"]
    B --> C["Axios /api<br/>gắn JWT nếu có"]
    C --> D["Vite proxy 5173 → 8080"]
    D --> E["Spring Security<br/>JWT và quyền"]
    E --> F["Controller<br/>đọc yêu cầu"]
    F --> G["Service<br/>quy tắc nghiệp vụ"]
    G --> H["JPA Repository"]
    H --> I[("SQL Server")]
    F --> J["JSON hoặc lỗi API"]
    J --> B
    K["Scheduler"] --> G
    L["Webhook/IPN"] --> E
```

Một số controller xử lý nghiệp vụ trực tiếp. Mở `frontend/src/router.js`, `frontend/src/api.js`, `frontend/vite.config.js`, rồi tra lớp tương ứng trong `backend/src/main/java/com/ares/shop`. Frontend đọc JSON hoặc hiện lỗi từ backend. Tác vụ nền và thông báo thanh toán có thể đi vào hệ thống mà không cần mở trang.

## Vòng đời đơn hàng

```mermaid
flowchart TD
  A["ProductDetail.vue<br/>chọn mẫu và biến thể"] --> B["cart.js<br/>giỏ trong trình duyệt"]
  B --> C["Checkout.vue<br/>kiểm tra giỏ và lấy báo giá"]
  C --> D{"Khách đã đăng nhập?"}
  D -->|Có| E["POST /api/orders<br/>OrderController.place"]
  D -->|Không| F["POST /api/public/checkout<br/>luồng khách COD"]
  E --> G["OrderService.place<br/>kiểm tra giá, tồn và ưu đãi"]
  G --> H{"Dữ liệu hợp lệ?"}
  H -->|Không| X["Trả lỗi cho checkout"]
  H -->|Có| I[("Lưu đơn và chi tiết")]
  F --> Y["Theo dõi bằng mã đơn"]
  I --> J{"Phương thức"}
  J -->|COD| K["Chờ vận hành xác nhận"]
  J -->|Trực tuyến| L["Chọn kênh rồi chờ xác nhận tiền"]
  L -->|Thanh toán được áp dụng| K
  K --> M["CONFIRMED → SHIPPING → COMPLETED"]
  M --> N["Hóa đơn, điểm và các thao tác sau mua"]
  K --> O["Hủy nếu nghiệp vụ cho phép"]
  N --> P["Yêu cầu đổi trả nếu đủ điều kiện"]
```

Không xem số tiền hiển thị trong giỏ là số cuối cùng. Đọc nhánh ký tên trong `Checkout.vue`, handler tương ứng và `service/OrderService.java` để biết backend tái kiểm tra những gì. Phần admin nằm ở `AdminOrders.vue`, `AdminOrderDetail.vue` và `AdminReturns.vue`.

## Xác nhận tiền về

```mermaid
sequenceDiagram
    participant V as Checkout và trang thanh toán
    participant P as PaymentController
    participant G as Ngân hàng hoặc cổng thanh toán
    participant C as PaymentConfirmationService
    participant D as SQL Server
    V->>P: Lấy cấu hình, QR hoặc liên kết thanh toán
    P-->>V: Thông tin của kênh được bật
    G->>P: Webhook hoặc IPN
    P->>P: Kiểm tra thông báo theo từng kênh
    P->>C: applyGateway hoặc applyBankTransfer
    C->>D: Kiểm tra mã giao dịch và khóa đơn
    alt Trùng, đã trả, hủy hoặc sai số tiền
      C-->>P: Trả kết quả và ghi nhận khi phù hợp
    else Giao dịch hợp lệ
      C->>D: OrderService.pay và lưu giao dịch
      C-->>P: APPLIED
    end
    V->>P: Tra trạng thái theo mã đơn
    P-->>V: Trạng thái từ backend
```

VietQR và các kênh dùng thông báo xác thực để cập nhật đơn. Kênh cổng yêu cầu số tiền chính xác trong hàm đối soát chung. Chuyển khoản ngân hàng bị từ chối khi thiếu tiền. Giao dịch trùng chạy song song có nhánh rollback. Luồng chuyển trang về và luồng xác nhận tiền là hai sự kiện có thể đến khác thời điểm.

## Đấu giá

```mermaid
flowchart LR
    A["Admin tạo và mở phiên"] --> B["Auctions và AuctionDetail"]
    B --> C{"Cách đặt"}
    C -->|Thủ công| D["POST /auctions/:id/bids"]
    C -->|Tự động| E["POST /auctions/:id/auto-bid"]
    D --> F["AuctionService<br/>kiểm tra phiên và lượt"]
    E --> F
    F --> G[("Phiên và lượt đặt")]
    G --> H["Kết thúc phiên"]
    H --> I{"Có lượt thắng?"}
    I -->|Có| J["Ghi người thắng<br/>OrderService.auctionOrder"]
    I -->|Không| K["Đóng phiên"]
```

Đối chiếu `AuctionController.java`, `AuctionService.java` và `AutoBidBox.vue`. URL trong trình duyệt là `/auctions`. Endpoint Spring có tiền tố `/api`.

## Báo ARES

```mermaid
flowchart TD
    A["AdminJournal.vue"] --> B["Tải ảnh bìa và viết bản nháp"]
    B --> C["POST hoặc PUT /api/admin/journal"]
    C --> D[("JournalArticle")]
    D --> E{"Đã xuất bản?"}
    E -->|Chưa| F["Chỉ luồng biên tập truy cập"]
    E -->|Có| G["GET /api/public/journal"]
    G --> H["Journal.vue<br/>số báo, tìm kiếm, lá Át"]
    H --> I["JournalDetail.vue<br/>đọc theo slug"]
    I --> J["Bình luận → JournalComment"]
    I --> K["Dấu trang → localStorage"]
```

Tính năng báo ở `frontend/src/views/Journal.vue` và `JournalDetail.vue`. `journal.css` giữ bố cục in báo. `JournalController.java` phân biệt quyền đọc bài nháp và bài công khai. SQL Server chạy chuyển đổi cột lưu tiếng Việt qua `JournalUnicodeMigration.java`.

## Quyền và công việc chạy nền

| Nhánh | Luồng lần theo |
|---|---|
| Tài khoản | Login hoặc OAuth → backend cấp JWT → Pinia giữ phiên → Axios gắn token → Spring Security đọc token |
| Quyền nhân viên | Route admin kiểm tra quyền vào trang → API kiểm tra role → StaffPermissionInterceptor kiểm tra nhóm chức năng |
| Tác vụ nền | Scheduler → JobService → tạo JobRun → admin xem kết quả trong /admin/jobs |
| Ưu đãi và giữ chân | Voucher/flash sale thay đổi điều kiện checkout. Giỏ đồng bộ và tác vụ nhắc giỏ có thể hoạt động độc lập |
| Kho và POS | Admin tạo hàng/biến thể → nhập hoặc điều chỉnh tồn → POS hoặc đơn web → kiểm tra số liệu và lịch sử |
| Xưởng và cộng đồng | Khách gửi yêu cầu hoặc dữ liệu chia sẻ → controller của nhánh → admin duyệt hoặc cập nhật khi có bước vận hành |
