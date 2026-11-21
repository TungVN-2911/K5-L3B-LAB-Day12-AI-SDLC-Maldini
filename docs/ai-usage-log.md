# Nhật ký dùng AI (theo phase và theo người)

| Phase | Người | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|---|
| Phase 1 | Chiêm | Claude Code (Opus 5.5) | Sinh khung xử lý oxy, đếm ngạt và bắt cá | ~25k tokens | AI nhầm thứ tự kiểm tra cập bến với hái cây; đã đảo lại thứ tự đúng spec. |
| Phase 1 | Tùng | Claude Code / Antigravity | Triển khai Quán: xử lý state khách, nấu, phục vụ | ~35k tokens | AI bỏ sót hoàn trả nguyên liệu khi khách bỏ về; đã bổ sung vào `_customer_left`. |
| Phase 1 | Minh | Antigravity (Gemini 3.8) | Sinh smoke test tích hợp kho, rà soát contract | ~20k tokens | AI ban đầu giả định team_size là 4; đã hiệu chỉnh lại theo team_size 3. |
