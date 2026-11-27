"""Refresh the offline learning map from a local CarShowroom checkout."""
import argparse
import collections
import html
import json
import re
import subprocess
import sys
from pathlib import Path

from learning_teams import MEMBERS

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
entry_groups = {"Khách hàng", "Quản trị"}
owners = {}
for member, details in MEMBERS.items():
    for name in details["screens"].split():
        if name in owners:
            raise ValueError(f"Duplicate assignment for {name}: {owners[name]} and {member}")
        owners[name] = member

entries = [row for row in data["rows"] if row["group"] in entry_groups]
entry_names = {Path(row["file"]).stem for row in entries}
if entry_names != owners.keys() or len(entry_names) != len(entries):
    raise ValueError(f"Assignment mismatch: missing {entry_names - owners.keys()}, extra {owners.keys() - entry_names}")

references = collections.defaultdict(set)
api_owners = collections.defaultdict(set)
counts = collections.Counter()
for row in entries:
    member = owners[Path(row["file"]).stem]
    row["owner"] = member
    counts[member] += 1
    for file in [row["file"], *row["links"]]:
        references[file].add(member)
    for api in row["apis"]:
        normalized = re.sub(r"\$\{[^}]+\}", "{}", api.split("?", 1)[0]).rstrip("/")
        api_owners["/api" + normalized].add(member)

for row in data["rows"]:
    if row["group"] == "API":
        normalized = re.sub(r"\{[^}]+\}", "{}", row["route"]).rstrip("/")
        related = api_owners.get(normalized, set())
    else:
        related = references.get(row["file"], set())
    row["relatedOwners"] = [member for member in MEMBERS if member in related]

data["team"] = {
    member: {key: value for key, value in details.items() if key != "screens"} | {"count": counts[member]}
    for member, details in MEMBERS.items()
}

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
    ["Danh mục từ quản trị tới cửa hàng",
     ["Khai báo hãng và danh mục", "Tạo sản phẩm và biến thể", "Chọn ảnh và bố cục",
      "CatalogController đọc danh mục", "Khách lọc, tìm và mở chi tiết"],
     "Tạo dữ liệu thử rồi kiểm tra cùng một SKU trên màn hình admin, danh mục và chi tiết. Lỗi lọc cần được đối chiếu từ tham số Vue đến API danh mục.",
     ["frontend/src/views/admin/AdminCatalog.vue", "frontend/src/views/admin/AdminProducts.vue",
      "frontend/src/views/admin/AdminMediaLayout.vue", "frontend/src/views/Products.vue",
      "frontend/src/views/ProductDetail.vue", "backend/src/main/java/com/ares/shop/web/CatalogController.java"]],
    ["Ưu đãi từ cấu hình tới checkout",
     ["Admin đặt điều kiện voucher hoặc flash sale", "Trang ưu đãi hiển thị chiến dịch",
      "Checkout gửi mã và giỏ", "OrderService kiểm tra điều kiện", "Áp dụng hoặc báo lỗi"],
     "Thử cùng một mã với giỏ đủ và thiếu điều kiện. Phân biệt hiển thị ưu đãi ngoài cửa hàng với lần kiểm tra khi tạo đơn.",
     ["frontend/src/views/admin/AdminPromotions.vue", "frontend/src/views/admin/AdminFlash.vue",
      "frontend/src/views/Promotions.vue", "frontend/src/views/Checkout.vue",
      "backend/src/main/java/com/ares/shop/service/OrderService.java"]],
    ["Kho, bán tại quầy và báo cáo",
     ["Dò SKU và biến thể", "Theo dõi nhập và tồn", "Lập giao dịch ở POS",
      "Kiểm tra tồn sau giao dịch", "Đối chiếu kênh bán và số liệu"],
     "Dùng một mẫu thử để đối chiếu số lượng trước và sau giao dịch. Khi số liệu khác nhau, kiểm tra khoảng ngày, kênh bán và kho được chọn.",
     ["frontend/src/views/admin/AdminInventory.vue", "frontend/src/views/admin/AdminPurchasing.vue",
      "frontend/src/views/admin/AdminPos.vue", "frontend/src/views/admin/AdminSalesChannels.vue",
      "backend/src/main/java/com/ares/shop/web/PosController.java"]],
    ["Từ phiếu hỗ trợ tới phản hồi",
     ["Khách mở trang hỗ trợ", "Tạo phiếu và nhận mã", "Nhân viên mở phiếu theo quyền",
      "Phản hồi hoặc cập nhật trạng thái", "Khách xem lại ở chi tiết phiếu"],
     "Thử bằng hai tài khoản để thấy dữ liệu hiển thị ở phía khách và phía quản trị. Tra quyền backend nếu nhân viên nhìn thấy menu nhưng gọi API bị từ chối.",
     ["frontend/src/views/Support.vue", "frontend/src/views/TicketDetail.vue",
      "frontend/src/views/admin/AdminTickets.vue", "backend/src/main/java/com/ares/shop/web/SupportController.java",
      "backend/src/main/java/com/ares/shop/config/StaffPermissionInterceptor.java"]],
    ["Tác vụ nền và thông báo",
     ["Sự kiện nghiệp vụ hoặc lịch chạy", "JobService hoặc NotifyService",
      "Ghi kết quả tác vụ hoặc thông báo", "Admin theo dõi và khách đọc"],
     "Dùng trang tác vụ để xem lần chạy. Phân biệt công việc nền với thông báo quản trị gửi chủ động. Kênh gửi bên ngoài phụ thuộc cấu hình.",
     ["frontend/src/views/admin/AdminJobs.vue", "frontend/src/views/admin/AdminBroadcast.vue",
      "frontend/src/views/Notifications.vue", "backend/src/main/java/com/ares/shop/service/JobService.java",
      "backend/src/main/java/com/ares/shop/service/NotifyService.java"]],
]
data["flows"] = [data["flows"][0], *flows, *data["flows"][1:]]
flow_titles = {flow[0] for flow in data["flows"]}
for member, details in MEMBERS.items():
    if missing := set(details["flows"]) - flow_titles:
        raise ValueError(f"Unknown diagrams for {member}: {missing}")
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
.team-people button{display:grid;gap:2px;text-align:left;min-width:135px;flex:1}
.team-people small{font-size:12px}
.team-detail ol{margin:10px 0 16px;padding-left:22px}
.team-detail li+li{margin-top:5px}
.team-detail .tabs{margin-bottom:0}
.member-diagrams{margin-top:18px;padding-top:12px;border-top:1px solid var(--line)}
.member-diagrams details{padding:8px 12px;border:1px solid var(--line);border-radius:8px;background:#f8fbf9}
.member-diagrams summary{font-size:15px;font-weight:650}
.member-diagrams .chain{padding:0;margin:10px 0}
.member-diagrams .chain li+li{margin-top:0}
.owner-filter{display:flex;align-items:center;gap:6px;color:var(--muted);font-size:14px}
.owner-filter input{flex:0}
</style>"""
team = """<section id="hoc-theo-ten"><h2>Học theo thành viên</h2>
<div class="tabs team-people" id="team-people" aria-label="Chọn thành viên"></div>
<div id="team-detail" class="panel team-detail"></div></section>"""
output = original[:inventory.start(2)] + json.dumps(data, ensure_ascii=False).replace("<", "\\u003c") + original[inventory.end(2):]
output = output.replace("</head>", styles + "</head>", 1).replace(
    '<a href="#chay">Khởi chạy</a>', '<a href="#hoc-theo-ten">Học theo tên</a><a href="#quy-mo">Quy mô</a><a href="#chay">Khởi chạy</a>', 1
).replace('<section id="chay">', team + scope + '<section id="chay">', 1)
output = output.replace(
    '<option value="">Tất cả nhóm</option></select>',
    '<option value="">Tất cả nhóm</option></select><select id="owner" aria-label="Thành viên phụ trách">'
    '<option value="">Tất cả thành viên</option></select><label class="owner-filter">'
    '<input id="include-related" type="checkbox"> Kèm API và tệp liên quan</label>', 1
).replace("Ví dụ: Báo ARES, checkout, webhook, kho…", "Ví dụ: Ngọc Anh, Mạnh checkout, Báo ARES…", 1)
output = output.replace(
    "row.description,...row.apis,...row.links", "row.description,row.owner,...row.relatedOwners,...row.apis,...row.links", 1
).replace(
    "  const results = data.rows.filter((row,i) => (!group || row.group === group) && words.every(word => index[i].includes(word)));",
    """  const owner = get('owner').value;
  const related = get('include-related').checked;
  const nameQuery = people.find(([name]) => normalize(name) === words.join(' '))?.[0];
  const matchesMember = (row, name) => row.owner === name || (related && row.relatedOwners.includes(name));
  const results = data.rows.filter((row,i) =>
    (!group || row.group === group) &&
    (!(nameQuery || owner) || matchesMember(row, nameQuery || owner)) &&
    (nameQuery || words.every(word => index[i].includes(word))));""", 1
).replace(
    "    if (row.route && row.group !== 'API')",
    """    if (row.owner) identity.append(node('span', 'Phụ trách · ' + row.owner, 'tag'));
    else if (row.relatedOwners.length) identity.append(node('span', 'Liên quan · ' + row.relatedOwners.join(', '), 'tag'));
    if (row.route && row.group !== 'API')""", 1
).replace(
    "for (const id of ['search','group'])",
    "for (const id of ['search','group','owner','include-related'])", 1
)
output = output.replace(
    "function showFlow(index) {\n  const [title, steps, description, files] = data.flows[index];",
    "function flowContent([, steps, description, files]) {", 1
).replace(
    "  get('active-flow').replaceChildren(node('h3', title), chain, node('p', description, 'flow-note'), links);",
    """  return [chain, node('p', description, 'flow-note'), links];
}
function showFlow(index) {
  const flow = data.flows[index];
  get('active-flow').replaceChildren(node('h3', flow[0]), ...flowContent(flow));""", 1
)
team_script = """
const people = Object.entries(data.team);
for (const [member, details] of people) {
  const option = node('option', member);
  option.value = member;
  get('owner').append(option);
  const button = node('button');
  button.type = 'button';
  button.append(node('strong', member), node('small', details.count + ' điểm vào'));
  button.onclick = () => showMember(member, true);
  get('team-people').append(button);
}
function showMember(member, filter) {
  const details = data.team[member];
  const steps = node('ol');
  steps.append(...details.steps.map(step => node('li', step)));
  const actions = node('div', '', 'tabs');
  const view = node('button', 'Xem các mục của ' + member);
  view.onclick = () => {
    showMember(member, true);
    get('tinh-nang').scrollIntoView();
  };
  actions.append(view);
  const diagrams = node('div', '', 'member-diagrams');
  diagrams.append(node('h3', 'Sơ đồ liên quan'));
  details.flows.forEach((title, index) => {
    const diagram = data.flows.find(([name]) => name === title);
    const disclosure = node('details');
    disclosure.open = index === 0;
    disclosure.append(node('summary', title), ...flowContent(diagram));
    diagrams.append(disclosure);
  });
  get('team-detail').replaceChildren(node('h3', member + ' · ' + details.role), steps,
    node('p', 'Thực hành · ' + details.exercise), node('p', 'Phối hợp · ' + details.handoff), actions, diagrams);
  people.forEach(([name], i) => get('team-people').children[i].setAttribute('aria-pressed', String(member === name)));
  if (filter) {
    get('group').value = '';
    get('search').value = '';
    get('owner').value = member;
    page = 0;
    render();
  }
}
get('owner').addEventListener('input', () => {
  const exactName = people.some(([name]) => normalize(name) === normalize(get('search').value.trim()));
  if (exactName) { get('search').value = ''; page = 0; render(); }
  if (get('owner').value) showMember(get('owner').value, false);
});
get('search').addEventListener('input', () => {
  const member = people.find(([name]) => normalize(name) === normalize(get('search').value.trim()));
  if (member) showMember(member[0], false);
});
showMember(people[0][0], false);
"""
output = output.replace("\nrender();\n</script>", "\n" + team_script + "\nrender();\n</script>", 1)
output = output.replace("link.href = '../' + file.split", """if (location.protocol !== 'file:') {
    return node('span', link.textContent, 'file-primary');
  }
  link.href = '../' + file.split""", 1)
(target / "index.html").write_text(output, encoding="utf-8")
print(f"{app:,} application lines; {total:,} total measured lines; {len(files)} files")
print("Team counts:", json.dumps(dict(counts), ensure_ascii=True))
