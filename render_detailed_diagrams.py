"""Build printable versions of the five diagrams in LUONG-XUONG-SONG.md."""
from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "diagrams"
OUTPUT.mkdir(exist_ok=True)
FONT_DIR = Path("C:/Windows/Fonts")

# Each line is a level in the reading order. Node IDs also identify edges.
GRAPHS = {
    "kien-truc": (
        "Một thao tác đi qua những tầng nào",
        [["view|Vue Router / View\nHiển thị và nhận thao tác", "job|Scheduler\nKích hoạt tác vụ nền"],
         ["axios|Pinia / Axios\nTrạng thái và JWT", "ipn|Webhook / IPN\nThông báo bên ngoài"],
         ["security|Vite proxy → Spring Security\nChuyển request và kiểm tra quyền"],
         ["ctrl|Controller\nĐọc request và trả JSON"],
         ["svc|Service\nÁp dụng nghiệp vụ", "ui|View\nHiện kết quả hoặc lỗi"],
         ["db|Repository → SQL Server\nĐọc và ghi dữ liệu"]],
        "view>axios;axios>security;ipn>security;security>ctrl;ctrl>svc;ctrl>ui;job>svc;svc>db",
    ),
    "don-hang": (
        "Đơn hàng từ giỏ tới sau mua",
        [["cart|Sản phẩm → giỏ → checkout\nKiểm tra giỏ và phí giao"],
         ["account|Có tài khoản\nPOST /api/orders", "guest|Khách vãng lai\nPOST /api/public/checkout · COD"],
         ["order|OrderService.place\nKiểm tra nghiệp vụ và lưu đơn", "track|Tra cứu bằng mã đơn"],
         ["error|Dữ liệu sai\nTrả lỗi về checkout", "online|Trực tuyến\nChờ xác nhận tiền", "cod|COD\nChờ vận hành"],
         ["deliver|Xác nhận → giao → hoàn tất"],
         ["after|Hóa đơn, điểm và đổi trả\nKhi đủ điều kiện"]],
        "cart>account;cart>guest;account>order;guest>track;order>error;order>online;order>cod;online>deliver;cod>deliver;deliver>after",
    ),
    "tien-ve": (
        "Xác nhận tiền về và đối soát",
        [["select|Khách chọn kênh đang bật", "gateway|Ngân hàng hoặc cổng thanh toán"],
         ["url|PaymentController trả QR / URL", "notify|Webhook / IPN tới PaymentController"],
         ["confirm|PaymentConfirmationService\nKiểm tra trùng và khóa đơn"],
         ["reject|Trùng, đơn đã trả/hủy\nhoặc số tiền không hợp lệ", "apply|Khớp điều kiện\nOrderService.pay và lưu giao dịch"],
         ["status|Frontend tra trạng thái theo mã đơn"]],
        "select>url;gateway>notify;notify>confirm;confirm>reject;confirm>apply;apply>status;reject>status",
    ),
    "dau-gia": (
        "Đấu giá từ mở phiên tới kết thúc",
        [["admin|Admin tạo phiên\nKhách mở chi tiết"],
         ["bid|Đặt thủ công\nPOST /auctions/:id/bids", "auto|Đặt trần tự động\nPOST /auctions/:id/auto-bid"],
         ["service|AuctionService\nKiểm tra phiên và ghi lượt"],
         ["close|Kết thúc phiên"],
         ["winner|Có người thắng\nGhi kết quả và tạo đơn", "empty|Không có người thắng\nĐóng phiên"]],
        "admin>bid;admin>auto;bid>service;auto>service;service>close;close>winner;close>empty",
    ),
    "bao-ares": (
        "Báo ARES từ bản nháp tới độc giả",
        [["editor|AdminJournal.vue\nViết bài và tải bìa"],
         ["save|POST / PUT /api/admin/journal\nLưu JournalArticle"],
         ["draft|Chưa công khai\nLuồng biên tập", "public|Đã xuất bản\nGET /api/public/journal"],
         ["read|Journal.vue → JournalDetail.vue\nLá Át, số báo và slug bài"],
         ["comment|Bình luận\nLưu JournalComment", "mark|Dấu trang\nLưu trong trình duyệt"]],
        "editor>save;save>draft;save>public;public>read;read>comment;read>mark",
    ),
}


def render(key, title, levels, edges):
    width, top, step, box_height = 1440, 120, 138, 98
    image = Image.new("RGB", (width, top + step * len(levels) - 20), "#f1f6f2")
    draw = ImageDraw.Draw(image)
    fonts = {kind: ImageFont.truetype(str(FONT_DIR / file), size)
             for kind, file, size in [("title", "arialbd.ttf", 40), ("node", "arial.ttf", 24)]}
    draw.text((42, 38), title, fill="#132a30", font=fonts["title"])
    boxes = {}
    for rank, level in enumerate(levels):
        columns = len(level)
        for index, entry in enumerate(level):
            key_node, label = entry.split("|")
            x = width * (index + 0.5) / columns
            y = top + rank * step
            half = min(250, width / columns / 2 - 22)
            boxes[key_node] = (x, y, half, label)
    for connection in edges.split(";"):
        first, second = connection.split(">")
        x1, y1, _, _ = boxes[first]
        x2, y2, _, _ = boxes[second]
        start, end = (x1, y1 + box_height), (x2, y2)
        if y2 - y1 > step:
            # Long links pass around the outside of intervening levels.
            side = width - 20 if x1 >= width / 2 else 20
            points = [start, (x1, start[1] + 15), (side, start[1] + 15),
                      (side, end[1] - 17), (x2, end[1] - 17), end]
        else:
            middle = (start[1] + end[1]) / 2
            points = [start, (x1, middle), (x2, middle), end]
        draw.line(points, fill="#44756e", width=4, joint="curve")
        draw.polygon([end, (x2 - 8, y2 - 13), (x2 + 8, y2 - 13)], fill="#44756e")
    for x, y, half, label in boxes.values():
        draw.rounded_rectangle((x-half, y, x+half, y+box_height), radius=14,
                               fill="#ffffff", outline="#79a49a", width=3)
        draw.multiline_text((math.floor(x), y + box_height / 2), label.replace("\\n", "\n"),
                            anchor="mm", align="center", spacing=7, fill="#182e36", font=fonts["node"])
    image.save(OUTPUT / f"{key}.png", optimize=True)


if __name__ == "__main__":
    for key, (title, levels, edges) in GRAPHS.items():
        render(key, title, levels, edges)
