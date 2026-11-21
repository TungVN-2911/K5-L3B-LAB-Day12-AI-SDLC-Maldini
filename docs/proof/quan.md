# Bằng chứng kiểm thử — Quán

- **Phạm vi:** Vòng đời khách (`waiting`, `assigned`, `eating`), giữ nguyên liệu kho, trường hợp không đủ món (`no_dish`), nấu tại bếp, chín món, lấy món, phục vụ tại bàn, thanh toán + tip + uy tín, khách bỏ về khi hết kiên nhẫn, kết thúc ca (`quan_end`).
- **Test tập trung:** `python -m unittest tests.test_quan_sim -v` — Đạt, 7 tests.
  - `test_arrival_assigns_feasible_dish_and_reserves_stock`: Đạt
  - `test_arrival_without_cookable_dish_emits_no_dish`: Đạt
  - `test_assigned_customer_requires_a_dish`: Đạt
  - `test_cook_serve_eat_and_pay`: Đạt
  - `test_customer_leaving_releases_reserved_stock_and_lowers_reputation`: Đạt
  - `test_eating_scenario_requires_price_and_tip`: Đạt
  - `test_shift_ends_once`: Đạt
- **Toàn bộ test suite:** `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v` — Đạt 70/70 tests.
- **Tích hợp kho:** Đọc file `kho.json` từ Gather thành công, khách gọi món đúng theo nguyên liệu hiện có trong kho.
