# Kế hoạch Phase 1 (≤ 1 trang)

- **Mục tiêu:**
  - Hoàn thiện luật chơi cốt lõi cho hai chế độ `gather` (lặn hái bông, bắt cá, quản lý oxy, cập bến, xuất kho) và `quan` (khách đến, đặt món, nấu ăn, phục vụ, tính tiền, đánh giá uy tín).
  - Đảm bảo tính xác định (determinism) của chế độ headless và luồng chuyển giao kho `kho.json` từ Gather sang Quán.
  - Toàn bộ thông số tuân thủ nghiêm ngặt `game.contract.json`.

- **Việc / người / phụ thuộc:**
  1. **Phạm Văn Chiêu (pvchiu) — Module Gather (`chonoi/sim/gather.py`)**:
     - Hoàn thiện oxy theo độ sâu, đếm ngạt, mất máu và ngất (`fainted`).
     - Hái nút mặt nước, kiểm tra bán kính, kẹp dung lượng giỏ, mọc lại.
     - Bắt cá dưới nước, kiểm tra hồi chiêu và dung lượng giỏ.
     - Viết test unit `tests/test_gather_sim.py`.
  2. **Vũ Ngọc Tùng (TungVN-2911) — Module Quán (`chonoi/sim/quan.py`)**:
     - Quản lý trạng thái khách (`waiting`, `assigned`, `eating`), chọn món khả dụng, giữ chỗ kho (`reserved`).
     - Nấu bếp, chín món, bưng món, phục vụ tại bàn, thanh toán + tip + uy tín.
     - Khách bỏ về khi hết kiên nhẫn, xử lý `no_dish`, kết thúc ca `quan_end`.
     - Viết test unit `tests/test_quan_sim.py`.
  3. **Triệu Tuấn Minh (2A202604123) — QA & Tích hợp (`tests/test_smoke_p1.py`, `docs/`)**:
     - Kiểm thử hộp đen contract, kiểm tra luồng kho `kho.json` từ gather sang quán.
     - Chạy toàn bộ test suite (`PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`).
     - Lập ma trận truy vết và lưu bằng chứng kiểm thử tại `docs/verification/` và `docs/proof/`.

- **Phụ thuộc:** Chiêm và Tùng làm song song; Minh chuẩn bị smoke test song song và tích hợp sau khi hai module sẵn sàng.

- **Rủi ro:**
  - Lệch schema kho hoặc sai định dạng event làm hỏng chế độ headless.
  - Không đọc tuning từ `game.contract.json` dẫn đến sai lệch thông số test contract.
