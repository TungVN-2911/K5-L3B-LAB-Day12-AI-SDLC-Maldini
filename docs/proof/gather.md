# Bằng chứng kiểm thử — Gather

- **Phạm vi:** Quản lý oxy, ngạt thở, ngất (faint) xả giỏ, hái nút mặt nước, bắt cá dưới nước, kiểm tra hồi chiêu, dung lượng giỏ và cập bến ghi kho.
- **Test tập trung:** `python -m unittest tests.test_gather_sim -v` — Đạt, 9 tests.
  - `test_oxygen_decreases_underwater_and_recovers_at_surface`: Đạt
  - `test_faint_clears_hold_and_finishes`: Đạt
  - `test_nearest_node_is_gathered_and_regrows`: Đạt
  - `test_node_cannot_be_gathered_underwater`: Đạt
  - `test_dock_interaction_precedes_gathering`: Đạt
  - `test_catch_requires_underwater_and_adds_yield`: Đạt
  - `test_fish_must_be_in_range_and_cooldown_blocks_repeat`: Đạt
  - `test_hold_full_blocks_node_and_fish`: Đạt
  - `test_time_end_keeps_hold`: Đạt
- **Toàn bộ test suite:** `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v` — Đạt 70/70 tests.
- **Headless check:** `python -m chonoi.headless --mode gather --seed 1 --ticks 600 --inventory-out kho.json` — Sinh đúng schema `{"items": {...}}`.
