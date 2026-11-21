# Ma trận truy vết Phase 1

| AC | Cách kiểm chứng | Bằng chứng (link `docs/proof/...`) | Kết quả (đạt / chưa đạt — ghi trung thực) |
|---|---|---|---|
| `AC-P1-01` Lặn/nổi & tiêu hao/hồi phục oxy | `tests/test_gather_sim.py::GatherOxygenTests` | [gather.md](file:///docs/proof/gather.md) | Đạt |
| `AC-P1-02` Ngạt & ngất xả giỏ | `test_faint_clears_hold_and_finishes` | [gather.md](file:///docs/proof/gather.md) | Đạt |
| `AC-P1-03` Hái bông súng & điên điển mặt nước | `test_nearest_node_is_gathered_and_regrows` | [gather.md](file:///docs/proof/gather.md) | Đạt |
| `AC-P1-04` Bắt cá dưới nước & hồi chiêu | `test_catch_requires_underwater_and_adds_yield` | [gather.md](file:///docs/proof/gather.md) | Đạt |

## Đánh giá ngắn
- **Yêu cầu nào đạt / chưa đạt:** Module Gather của Chiêm đã đạt toàn bộ 9/9 tests trong `tests/test_gather_sim.py`.
- **Điều cần chỉnh cho phase sau:** *(thành viên tự điền)*
