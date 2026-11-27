"""Refresh the offline learning map from a local CarShowroom checkout."""
import argparse
import collections
import html
import json
import re
import subprocess
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--source", type=Path, required=True)
parser.add_argument("--reuse-index", action="store_true", help="Reuse the existing HTML inventory")
args = parser.parse_args()
root = args.source.resolve()
target = Path(__file__).resolve().parent
if not args.reuse_index:
    subprocess.run([sys.executable, root / "scripts/build_project_map.py"], cwd=root, check=True)
original = (root / "docs/carshowroom-project-map.html").read_text(encoding="utf-8")
inventory = re.search(r'(<script id="project-data" type="application/json">)(.*?)(</script>)', original, re.S)
data = json.loads(inventory[2])

scopes = {
    "frontend/src/": "Frontend · mã ứng dụng",
    "backend/src/main/": "Backend · mã ứng dụng",
    "backend/src/test/": "Backend · kiểm thử",
    "database/": "SQL lịch sử và seed",
    "scripts/": "Công cụ vận hành",
}
extensions = {".java", ".vue", ".js", ".ts", ".css", ".html", ".xml", ".properties", ".sql", ".ps1", ".py", ".bat"}
selected = subprocess.check_output(
    ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard",
     "frontend/src", "backend/src", "database", "scripts", "frontend/vite.config.js",
     "frontend/index.html", "backend/pom.xml", "RUN_ALL.bat", "RUN_BACKEND.bat", "RUN_FRONTEND.bat"]
).decode("utf-8").split("\0")
areas = collections.defaultdict(lambda: [0, 0, 0])
files = []
for name in sorted(set(selected) - {""}):
    file = root / name
    if not file.is_file() or file.suffix.lower() not in extensions:
        continue
    lines = file.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    size = len(lines)
    nonblank = sum(bool(line.strip()) for line in lines)
    area = next((label for prefix, label in scopes.items() if name.startswith(prefix)), "Cấu hình và khởi chạy")
    totals = areas[area]
    totals[0] += size
    totals[1] += nonblank
    totals[2] += 1
    files.append((size, name, area))

flows = [
    ["Vòng đời đơn hàng",
     ["ProductDetail · chọn sản phẩm và biến thể", "Pinia cart · lưu giỏ", "Checkout · kiểm tra giỏ, voucher và phí",
      "Tách khách COD / người có tài khoản", "OrderService.place · giá, tồn, chiết khấu", "Thanh toán → điều phối → sau mua"],
     "Checkout gửi /api/orders nếu đã đăng nhập hoặc /api/public/checkout với khách COD. Nếu yêu cầu bị từ chối, frontend hiện lỗi. Sau khi tạo đơn, các thao tác thanh toán, hủy, giao hàng và đổi trả phụ thuộc trạng thái, phương thức và quyền.",
     ["frontend/src/views/ProductDetail.vue", "frontend/src/stores/cart.js", "frontend/src/views/Checkout.vue",
      "backend/src/main/java/com/ares/shop/web/OrderController.java", "backend/src/main/java/com/ares/shop/service/OrderService.java"]],
    ["Xác nhận tiền về",
     ["Trang thanh toán lấy cấu hình kênh", "QR hoặc URL cổng", "Webhook/IPN xác thực", "Kiểm tra trùng và khóa đơn",
      "So số tiền phải trả", "Ghi giao dịch và cập nhật đơn"],
     "Đơn đã hủy, đã trả hoặc số tiền sai có kết quả riêng. Kênh cổng so số tiền chính xác, chuyển khoản ngân hàng kiểm tiền thiếu. Giao dịch trùng chạy song song có nhánh rollback.",
     ["backend/src/main/java/com/ares/shop/web/PaymentController.java",
      "backend/src/main/java/com/ares/shop/service/payment/PaymentConfirmationService.java"]],
    ["Báo ARES từ bản nháp tới độc giả",
     ["Bìa và nội dung", "API admin lưu nháp", "Gán số, chuyên mục và xuất bản", "API công khai lọc bài đã phát hành",
      "Lá Át mở bài theo slug", "Bình luận về DB · dấu trang về trình duyệt"],
     "Bài nháp đọc qua quyền biên tập. Phần Kho số và Sổ tay hoạt động trong Journal.vue. Migration của báo xử lý cột SQL Server lưu tiếng Việt.",
     ["frontend/src/views/admin/AdminJournal.vue", "frontend/src/views/Journal.vue", "frontend/src/views/JournalDetail.vue",
      "frontend/src/journal.js", "backend/src/main/java/com/ares/shop/web/JournalController.java",
      "backend/src/main/java/com/ares/shop/config/JournalUnicodeMigration.java"]],
]
data["flows"] = [data["flows"][0], *flows, *data["flows"][1:]]
stat = lambda n: f"{n:,}".replace(",", ".")
total = sum(row[0] for row in areas.values())
app = sum(row[0] for label, row in areas.items() if label.endswith("mã ứng dụng"))
peak = max((row[0] for row in areas.values()), default=1)
bars = "".join(
    f'<li><div><strong>{html.escape(label)}</strong><span>{stat(n)} dòng · {stat(f)} tệp</span></div>'
    f'<meter min="0" max="{peak}" value="{n}" aria-label="{html.escape(label)}">{n}</meter>'
    f'<small>{stat(nb)} dòng không trống</small></li>'
    for label, (n, nb, f) in sorted(areas.items(), key=lambda x: -x[1][0])
)
top = "".join(f"<li><code>{html.escape(name)}</code><b>{stat(n)}</b></li>" for n, name, _ in sorted(files, reverse=True)[:12])
scope = f"""
<section id="quy-mo"><h2>Quy mô mã nguồn</h2>
<p class="lede"><b>{stat(app)} dòng trong frontend/src và backend/src/main</b> · {stat(total)} dòng toàn phạm vi đo · {stat(len(files))} tệp</p>
<div class="run"><div class="panel"><h3>Phân bố theo tầng</h3><ul class="source-bars">{bars}</ul></div>
<div class="panel"><h3>12 tệp dài nhất</h3><ol class="large-files">{top}</ol></div></div>
<p class="lede">Số đo là dòng vật lý, gồm chú thích và dòng trống. Phạm vi gồm mã ứng dụng, kiểm thử, script, cấu hình khởi chạy và SQL được theo dõi hoặc chưa commit trong các thư mục kiểm kê. Loại thư viện, build, ảnh, tài liệu, lockfile và tệp môi trường. SQL lịch sử được tách riêng để thấy quy mô ứng dụng.</p>
<p><a href="LUONG-XUONG-SONG.md">Sơ đồ Mermaid chi tiết</a> · <a href="Ban-do-du-an-CarShowroom.docx">Tải bản Word tham khảo</a></p></section>"""
styles = """<style>
.source-bars,.large-files{padding:0;margin:12px 0;list-style:none}.source-bars li+li{margin-top:10px}
.source-bars li div,.large-files li{display:flex;justify-content:space-between;align-items:baseline;gap:10px}
.source-bars span,.source-bars small{color:var(--muted);font-size:13px}
.source-bars meter{width:100%;height:15px;accent-color:var(--green)}
.large-files li{padding:5px 0;border-bottom:1px solid var(--line)}
.large-files b{white-space:nowrap;color:var(--green)}
</style>"""
output = original[:inventory.start(2)] + json.dumps(data, ensure_ascii=False).replace("<", "\\u003c") + original[inventory.end(2):]
output = output.replace("</head>", styles + "</head>", 1).replace(
    '<a href="#chay">Khởi chạy</a>', '<a href="#quy-mo">Quy mô</a><a href="#chay">Khởi chạy</a>', 1
).replace('<section id="chay">', scope + '<section id="chay">', 1)
output = output.replace("link.href = '../' + file.split", """if (location.protocol !== 'file:') {
    return node('span', link.textContent, 'file-primary');
  }
  link.href = '../' + file.split""", 1)
(target / "index.html").write_text(output, encoding="utf-8")
print(f"{app:,} application lines; {total:,} total measured lines; {len(files)} files")
