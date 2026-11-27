"""Feature assignments and study paths for the CarShowroom team."""

MEMBERS = {
    "Ngọc Anh": {
        "role": "Nhóm trưởng · Danh mục, giao diện và ưu đãi",
        "screens": """Home About Products ProductDetail Wishlist Compare SharedWishlist Collections
            CollectionDetail ScaleFinder AdminProducts AdminMedia AdminCatalog AdminBanners AdminHomeLayout
            AdminMediaLayout AdminAppearance AdminReviews Promotions AdminPromotions AdminFlash NotFound""",
        "steps": [
            "Mở trang chủ, thử tìm một mẫu xe, lọc theo hãng và chọn một biến thể.",
            "Lần từ Products.vue và ProductDetail.vue đến CatalogController, rồi xem dữ liệu sản phẩm và biến thể.",
            "Trong admin, tạo dữ liệu thử, đổi banner hoặc bố cục và xem thay đổi ngoài trang chủ.",
            "Tạo một voucher hoặc flash sale thử. Chốt với Mạnh cách checkout nhận điều kiện và từ chối ưu đãi hết hạn.",
        ],
        "exercise": "Demo từ tạo sản phẩm và ưu đãi đến khách tìm thấy mẫu rồi chọn biến thể. Gom một sơ đồ chung, phân công ai trình bày mỗi điểm giao và chạy thử toàn bộ demo trước buổi học.",
        "handoff": "Giao SKU, biến thể, giá và điều kiện ưu đãi cho Mạnh và Nam. Kiểm tra các route, API và mục dùng chung với cả nhóm.",
        "flows": ["Danh mục từ quản trị tới cửa hàng", "Ưu đãi từ cấu hình tới checkout", "Kiến trúc tổng thể"],
    },
    "Mạnh": {
        "role": "Giỏ hàng, đơn hàng và thanh toán",
        "screens": """Cart Checkout PayMock Invoice Track OrderDetail PackingSlips ShippingLabels GiftCards
            Bundles AdminBundles AdminOrders AdminOrderDetail AdminReturns AdminCarts AdminIntelligence""",
        "steps": [
            "Thêm một biến thể vào giỏ, thay đổi số lượng và xem cart.js giữ trạng thái ở đâu.",
            "Mở Checkout.vue, đối chiếu POST /api/orders và /api/public/checkout, rồi theo hàm OrderService.place.",
            "Theo một giao dịch từ chọn kênh đến PaymentConfirmationService. Phân biệt trả về từ cổng với xác nhận đã thu tiền.",
            "Mở chi tiết đơn và thử hợp lệ các luồng tra cứu, đóng gói, in hóa đơn, hủy và đổi trả trên dữ liệu thử.",
        ],
        "exercise": "Demo đơn COD từ giỏ đến quản trị, sau đó giải thích bằng sơ đồ cách xử lý tiền thiếu hoặc thông báo thanh toán trùng. Dùng dữ liệu thử và kênh sandbox khi cần.",
        "handoff": "Nhận danh mục và ưu đãi từ Ngọc Anh. Đối chiếu thay đổi tồn và giao dịch tại quầy với Nam.",
        "flows": ["Vòng đời đơn hàng", "Xác nhận tiền về", "Tiền về và đối soát", "Vận hành cửa hàng"],
    },
    "Nam": {
        "role": "Kho, POS, báo cáo và đấu giá",
        "screens": """Auctions AuctionDetail Upcoming AdminAuctions AdminInventory AdminPurchasing AdminPreorders
            AdminWarehouses AdminPos AdminSalesChannels Dashboard AdminReports AdminAnalytics AdminStaffDebts
            AdminCollections router""",
        "steps": [
            "Mở tồn kho, kho hàng và nhập hàng. Theo một biến động số lượng từ admin xuống repository.",
            "Thực hiện một giao dịch POS trên dữ liệu thử, sau đó kiểm tra kênh bán, tồn và báo cáo.",
            "Mở phiên đấu giá, đối chiếu đặt giá với đặt trần. Theo AuctionService đến bước kết thúc phiên.",
            "Thử duyệt bộ sưu tập trong admin, xem đặt trước và kiểm tra trạng thái thể hiện ngoài cửa hàng.",
        ],
        "exercise": "Demo nhập kho → POS → kiểm tra số liệu. Vẽ thêm nhánh phiên đấu giá kết thúc có và không có người thắng.",
        "handoff": "Chốt mã hàng và danh mục với Ngọc Anh. Bàn giao đơn từ POS hoặc đấu giá và biến động tồn cho Mạnh.",
        "flows": ["Kho, bán tại quầy và báo cáo", "Đấu giá", "Vận hành cửa hàng", "Vòng đời đơn hàng"],
    },
    "Minh": {
        "role": "Tài khoản, phân quyền và hỗ trợ",
        "screens": """Support TicketDetail Faq Login Register ForgotPassword OAuthCallback Account AdminLayout
            AdminCustomers AdminQuestions AdminTickets AdminChat AdminAudit AdminEmails AdminChatbot
            AdminStaff AdminPermissions""",
        "steps": [
            "Đăng nhập bằng tài khoản thử, đọc auth.js và api.js để thấy JWT đi cùng yêu cầu.",
            "Theo router, SecurityConfig và StaffPermissionInterceptor để phân biệt quyền vào trang và quyền gọi API.",
            "Tạo một phiếu hỗ trợ thử, mở luồng trả lời ở admin rồi quay lại tài khoản khách kiểm tra.",
            "Đọc luồng quên mật khẩu và OAuth. Tách phần có thể chạy cục bộ khỏi phần cần nhà cung cấp.",
        ],
        "exercise": "Demo một tài khoản STAFF được phép dùng hỗ trợ nhưng bị từ chối ở mục quản trị đã tắt quyền. Giải thích backend kiểm tra ở đâu.",
        "handoff": "Cung cấp tài khoản và quyền thử cho cả nhóm. Kiểm tra quyền biên tập báo với Thịnh và quyền vận hành kho với Nam.",
        "flows": ["Tài khoản và quyền", "Từ phiếu hỗ trợ tới phản hồi", "Kiến trúc tổng thể"],
    },
    "Thịnh": {
        "role": "Báo ARES, cộng đồng và dịch vụ RC",
        "screens": """ShelfStudio Garage PublicGarage TradeMarket RcBuilder Journal JournalDetail Workshop
            Certificate CommunityHub Rewards Notifications AdminTrade AdminJournal AdminWorkshop AdminSegments
            AdminBroadcast AdminJobs""",
        "steps": [
            "Viết bài thử trong AdminJournal.vue, lưu nháp, gán số báo và kiểm tra lúc nào độc giả nhìn thấy.",
            "Mở Journal.vue, rút lá Át, thử tìm theo số, lưu bài rồi đối chiếu đâu là dữ liệu API và đâu là localStorage.",
            "Chọn một mẫu RC, thử garage, cấu hình hoặc một lịch hẹn. Theo handler từ màn hình khách đến điều phối admin.",
            "Tra community, thông báo và tác vụ nền. Ghi rõ trigger nào đến từ người dùng và trigger nào từ lịch.",
        ],
        "exercise": "Demo nháp → xuất bản → mở lá Át → đọc và lưu bài. Sau đó theo một ca xưởng RC từ lúc gửi yêu cầu đến khi admin cập nhật trạng thái.",
        "handoff": "Xin quyền biên tập thử từ Minh. Bàn giao vị trí menu và cách điều hướng vào Báo ARES cho Ngọc Anh.",
        "flows": ["Báo ARES từ bản nháp tới độc giả", "Biên tập Báo ARES", "Cộng đồng và dịch vụ RC", "Tác vụ nền và thông báo"],
    },
}
