# Ma trận truy vết Phase 1

| AC | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| `AC-P1-01` Lặn/nổi & tiêu hao/hồi phục oxy | `tests/test_gather_sim.py::GatherOxygenTests` | [gather.md](file:///docs/proof/gather.md) | Đạt |
| `AC-P1-02` Ngạt & ngất xả giỏ | `test_faint_clears_hold_and_finishes` | [gather.md](file:///docs/proof/gather.md) | Đạt |
| `AC-P1-03` Hái bông súng & điên điển mặt nước | `test_nearest_node_is_gathered_and_regrows` | [gather.md](file:///docs/proof/gather.md) | Đạt |
| `AC-P1-04` Bắt cá dưới nước & hồi chiêu | `test_catch_requires_underwater_and_adds_yield` | [gather.md](file:///docs/proof/gather.md) | Đạt |
| `AC-P1-05` Khách đến, đặt món & giữ chỗ nguyên liệu | `tests/test_quan_sim.py::QuanSimTest` | [quan.md](file:///docs/proof/quan.md) | Đạt |
| `AC-P1-06` Bếp nấu, chín món, phục vụ & tính tiền | `test_cook_serve_eat_and_pay` | [quan.md](file:///docs/proof/quan.md) | Đạt |
| `AC-P1-07` Khách bỏ đi & hoàn trả nguyên liệu | `test_customer_leaving_releases_reserved_stock` | [quan.md](file:///docs/proof/quan.md) | Đạt |
| `AC-P1-08` Tích hợp xuất kho Gather và nạp kho Quán | `tests/test_smoke_p1.py::Integration` | [gather.md](file:///docs/proof/gather.md) | Đạt |
| `AC-P1-09` Tính xác định byte-to-byte headless | `tests/test_smoke_p1.py::Contract` | [gather.md](file:///docs/proof/gather.md) | Đạt |

## Đánh giá ngắn
- **Yêu cầu đạt:** Tất cả các tiêu chí nghiệm thu của Phase 1 (`gather`, `quan`, tích hợp kho, contract headless, kiểm tra đội ngũ 3 thành viên) đều đạt 100% (70/70 tests pass).
- **Điều cần chỉnh cho phase sau:** Tiếp tục duy trì quy tắc không hard-code hằng số ngoài `game.contract.json`, mở rộng kịch bản kiểm thử cho các tính năng nâng cao trong phase kế tiếp.
