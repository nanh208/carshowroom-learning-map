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

Nếu clone repo này ngay bên trong thư mục CarShowroom, các liên kết tệp có thể mở bản mã nguồn cùng máy. Repo này mang theo tài liệu học, không chứa ứng dụng CarShowroom và không đòi hỏi chạy ứng dụng để tra cứu.

## Cập nhật bản đồ

Trên máy có mã nguồn gốc và Python 3, chạy `python build_learning_map.py --source <thu-muc-CarShowroom>`. Công cụ dùng trình tạo bản đồ có sẵn trong CarShowroom, sau đó đo tệp theo quy tắc ghi trên trang. Word là ảnh chụp tài liệu trước khi thêm phần số liệu và sơ đồ chi tiết.
