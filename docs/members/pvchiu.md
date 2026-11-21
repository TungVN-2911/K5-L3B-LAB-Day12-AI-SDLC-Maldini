# pvchiu — phản tư cá nhân (≤ 200 từ)

- Tôi đã làm (kèm link commit): Hoàn thiện `chonoi/sim/gather.py` (lặn/nổi, oxy, ngạt thở, ngất xả giỏ, hái nút sen/điên điển, bắt cá, cập bến và xuất kho) và viết bộ unit test `tests/test_gather_sim.py` (commit `45f4537`).
- Tôi đã review (kèm link): Đọc và kiểm tra tích hợp với module quán `chonoi/sim/quan.py`.
- AI sai ở đâu và tôi phát hiện thế nào: AI từng sinh sai thứ tự kiểm tra cập bến sau hái cây làm sai logic bến; tôi phát hiện qua đọc spec và đảo lại đúng thứ tự.
- Điều tôi học được: Quy trình TDD và tầm quan trọng của contract testing giữa các module trong dự án nhóm.
