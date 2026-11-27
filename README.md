# Bản đồ học dự án CarShowroom

Mở `MO-BAN-DO.bat` trên Windows để vào bản đồ trong trình duyệt mặc định. Trên hệ khác, mở `index.html`. Bản đồ chạy offline và không cần Node, Maven, SQL Server hay tài khoản.

| Tài liệu | Dùng để |
|---|---|
| [Bản đồ tương tác](index.html) | Tra tính năng, route, API, tệp và xem phân bố dòng mã |
| [Luồng xương sống](LUONG-XUONG-SONG.md) | Đọc sơ đồ chi tiết trên GitHub và theo dõi từng nhánh xử lý |
| [Bản Word](Ban-do-du-an-CarShowroom.docx) | Đọc, tìm kiếm hoặc in bản tham khảo |

## Học theo một lát cắt

1. Xem **Quy mô mã nguồn** để phân biệt frontend, backend, kiểm thử và SQL lịch sử.
2. Mở **Vòng đời đơn hàng** và theo một thao tác từ Vue qua Axios, HTTP, controller, service, repository và SQL Server.
3. Lặp lại với **Xác nhận tiền về**, **Đấu giá** hoặc **Báo ARES** để thấy giao dịch, tác vụ nền và luồng quản trị.
4. Dùng ô tìm kiếm để lần theo đường dẫn và tên hàm. Đường dẫn mã tính từ thư mục gốc CarShowroom.

## Học theo thành viên

Mở mục **Học theo tên** rồi chọn tên để xem thứ tự học, bài thực hành, người cần phối hợp và **tất cả sơ đồ liên quan**. Sơ đồ đầu tiên mở sẵn, các sơ đồ còn lại mở ngay bên dưới. Các luồng xương sống có ảnh phân nhánh mở được offline và có thể bấm để phóng to. Có thể nhập đúng tên ngay trong bảng hoặc chọn tên ở bộ lọc. Bật **Kèm API và tệp liên quan** khi cần mở rộng từ màn hình sang mã dùng chung.

| Thành viên | Phần phụ trách | Điểm vào |
|---|---|---:|
| Ngọc Anh | Nhóm trưởng, danh mục, giao diện, ưu đãi và ghép demo | 22 |
| Mạnh | Giỏ hàng, đơn hàng và thanh toán | 16 |
| Nam | Kho, POS, báo cáo và đấu giá | 16 |
| Minh | Tài khoản, phân quyền và hỗ trợ | 18 |
| Thịnh | Báo ARES, cộng đồng và dịch vụ RC | 18 |

Điểm vào gồm màn hình và đường dẫn chuyển hướng. API, controller và thành phần dùng chung có thể liên quan đến nhiều thành viên.

Nếu clone repo này ngay bên trong thư mục CarShowroom, các liên kết tệp có thể mở bản mã nguồn cùng máy. Repo này mang theo tài liệu học, không chứa ứng dụng CarShowroom và không đòi hỏi chạy ứng dụng để tra cứu.

## Cập nhật bản đồ

Trên máy có mã nguồn gốc và Python 3, chạy `python build_learning_map.py --source <thu-muc-CarShowroom>`. Công cụ dùng trình tạo bản đồ có sẵn trong CarShowroom, sau đó đo tệp theo quy tắc ghi trên trang. Bản Word có năm sơ đồ phân nhánh và các bảng tra cứu tại thời điểm xuất tài liệu.
