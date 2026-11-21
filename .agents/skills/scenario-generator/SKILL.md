---
name: scenario-generator
description: "Generate and validate custom test scenarios for edge cases in gather and quan simulation modes."
---

# Scenario Generator Skill

Dùng skill này khi cần sinh kịch bản biên để test các tình huống đặc biệt (nhiều cá, thiếu oxy, kho hết hàng, khách dồn dập).

## Quy chuẩn kịch bản

1. **Kịch bản Gather (`gather`)**:
   - `fish`: danh sách cá với `id`, `kind` (`ca_linh` hoặc `ca_loc`), `pos: [x, d]` (`0 <= x <= 100`, `0 <= d <= 30`), `heading_deg`.
   - `nodes`: danh sách nút hái với `id`, `kind` (`bong_dien_dien` hoặc `bong_sung`), `pos: [x, 0]`.
   - `player`: `pos`, `vel`, `oxygen_ticks`, `hp`.

   *Ví dụ lưu tại `scenarios/gather-many-fish.json`*:
   ```json
   {
     "gather": {
       "fish": [
         {"id": "F1", "kind": "ca_linh", "pos": [15, 5], "heading_deg": 0},
         {"id": "F2", "kind": "ca_loc", "pos": [30, 10], "heading_deg": 180}
       ]
     }
   }
   ```

2. **Kịch bản Quán (`quan`)**:
   - `stock`: kho nguyên liệu ban đầu.
   - `customers`: danh sách khách xếp sẵn với `id`, `table_id`, `state`, `dish_id`.
   - `stoves`: trạng thái bếp.

## Kiểm thử kịch bản với headless
```bash
python3 -m chonoi.headless --mode gather --seed 42 --ticks 300 --scenario scenarios/gather-many-fish.json --out out.jsonl
```
