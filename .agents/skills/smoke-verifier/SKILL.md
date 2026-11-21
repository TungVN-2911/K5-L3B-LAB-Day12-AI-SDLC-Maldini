---
name: smoke-verifier
description: "Verify all unit tests, headless simulation contract, and inventory pipeline compliance before committing code."
---

# Smoke Verifier Skill

Dùng skill này khi chuẩn bị tích hợp code giữa các module (`gather`, `quan`) hoặc trước khi commit/push code lên repo.

## Các bước kiểm tra

1. **Chạy toàn bộ unit tests**:
   ```bash
   PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
   ```
   Tất cả 70 tests phải đạt (OK), không có failure hoặc error.

2. **Kiểm tra tính xác định (determinism) của chế độ headless**:
   ```bash
   python3 -m chonoi.headless --mode gather --seed 1 --ticks 300 --out /tmp/out1.jsonl
   python3 -m chonoi.headless --mode gather --seed 1 --ticks 300 --out /tmp/out2.jsonl
   cmp /tmp/out1.jsonl /tmp/out2.jsonl
   ```
   Hai file jsonl sinh ra phải khớp từng byte.

3. **Kiểm tra luồng xuất/nhập kho (inventory pipe)**:
   ```bash
   python3 -m chonoi.headless --mode gather --seed 1 --ticks 600 --inventory-out /tmp/kho.json
   python3 -m chonoi.headless --mode quan --seed 1 --ticks 600 --inventory /tmp/kho.json
   ```
   Xác nhận file kho chứa đúng định dạng `{"items": {...}}` và simulation `quan` tải thành công kho.

4. **Kiểm tra thông tin đội ngũ**:
   ```bash
   python3 tools/check_team.py
   ```
