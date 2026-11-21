# Phân công công việc

## Mục tiêu

Hoàn thiện luật chơi còn TODO của hai chế độ `gather` và `quan`, kiểm chứng luồng kho từ Gather sang Quán, và lưu bằng chứng chạy test. Mọi thông số gameplay phải đọc từ `game.contract.json`; không tự đặt hằng số thay cho tuning.

## Phân công

### Chiêm — Người 1: Gather

**Phạm vi sở hữu:** `chonoi/sim/gather.py` và test riêng `tests/test_gather_sim.py`.

- Hoàn thiện oxy theo độ sâu: lặn/nổi, oxy cạn, đếm ngạt, mất máu và ngất.
- Phát đúng event tương ứng; khi ngất phải kết thúc với lý do `fainted` và làm rỗng giỏ.
- Hoàn thiện hái nút ở mặt nước, kiểm tra bán kính, chọn nút gần nhất (hòa thì theo ID), giỏ đầy và thời gian mọc lại.
- Hoàn thiện bắt cá dưới nước, kiểm tra bán kính, giỏ đầy và hồi chiêu.
- Giữ đúng thứ tự xử lý sẵn có: di chuyển và oxy trước tương tác; cập bến trước hái; xử lý bắt cá và hết giờ đúng quy ước.
- Viết test cho các nhánh chính và biên: mặt nước/dưới nước, giỏ đầy, nút chưa sẵn sàng, bắt cá sai điều kiện, ngạt/ngất.

**Hoàn thành khi:** test riêng đạt; test hiện có về di chuyển, cập bến và ghi kho vẫn đạt.

### Tùng — Người 2: Quán

**Phạm vi sở hữu:** `chonoi/sim/quan.py` và test riêng `tests/test_quan_sim.py`.

- Hoàn thiện trạng thái khách: lịch đến, bàn, món có thể nấu, giữ chỗ nguyên liệu và kiên nhẫn.
- Xử lý khách bỏ đi, `no_dish` và thứ tự xử lý khách theo yêu cầu.
- Hoàn thiện nấu tại bếp, món chín, lấy món, phục vụ tại bàn và vòng đời ăn.
- Hoàn thiện thanh toán, tiền/thu nhập, boa và uy tín theo tuning.
- Hoàn thiện kết thúc ca và event `quan_end`.
- Giới hạn tối đa một tương tác mỗi bước; chọn đối tượng theo khoảng cách, ưu tiên bếp trước bàn rồi theo ID.
- Viết test cho luồng phục vụ thành công và các trường hợp thiếu nguyên liệu/món, khách hết kiên nhẫn, hết ca.

**Hoàn thành khi:** test riêng đạt; snapshot và event giữ đúng hình dạng mà runner/headless đang dùng.

### Minh — Người 3: QA, tích hợp và bằng chứng

**Phạm vi sở hữu:** `tests/test_smoke_p1.py`, kiểm tra tích hợp, `docs/verification/` và phần ghi chép liên quan. Không sửa trực tiếp luật trong `chonoi/sim/gather.py` hoặc `chonoi/sim/quan.py`.

- Rà soát test contract hiện có và bổ sung test hộp đen/integration phù hợp trong `tests/test_smoke_p1.py`.
- Kiểm tra Gather ghi kho đúng một lần, Quán đọc đúng kho; xác nhận schema và event/end line qua headless.
- Chạy test riêng của Chiêm và Tùng, sau đó chạy toàn bộ lệnh:
  `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`
- Chơi thử `python3 -m chonoi.live --mode gather` và `python3 -m chonoi.live --mode quan` nếu môi trường cho phép.
- Ghi chính xác lệnh và kết quả đạt/chưa đạt vào `docs/verification/phase-1.md`; không ghi đạt nếu chưa chạy.
- Báo nhóm nếu cần sửa runner, input, schema hoặc contract; chỉ thay đổi các phần khung sau khi thống nhất.

**Hoàn thành khi:** test tích hợp và test suite đạt hoặc có lỗi được ghi rõ; bằng chứng phản ánh đúng kết quả thực tế.

## Phụ thuộc và cách phối hợp

1. **Chiêm và Tùng có thể làm song song** vì sở hữu hai module luật khác nhau.
2. **Minh có thể chuẩn bị test tích hợp song song**, nhưng chỉ xác nhận kết quả sau khi có thay đổi của cả Chiêm và Tùng.
3. Nếu test của Minh phát hiện lỗi luật, Minh ghi test tái hiện và giao lại đúng người sở hữu module; không tự vá chéo vào module đó.
4. Trước khi tích hợp, Chiêm và Tùng cần thống nhất cách đặt tên event, payload và thứ tự xử lý trong mỗi tick với Minh.
5. Mỗi người chỉ sửa file thuộc phạm vi của mình. Tránh cùng sửa một test hoặc cùng sửa file mô phỏng; báo trước nếu cần đổi phạm vi.

## Điểm dễ conflict / cần thống nhất trước

- **`game.contract.json` và `docs/contracts/`:** là hợp đồng dùng chung; không tự ý đổi tuning, schema hoặc yêu cầu. Nếu phát hiện thiếu/sai, ghi câu hỏi vào `docs/clarify.md` và thống nhất trước.
- **Khung dùng chung** như `runner.py`, `inputs.py`, `inventory.py`, `headless.py` và `live.py`: không sửa nếu chưa báo cả nhóm; đây không phải phạm vi mặc định của ba người.
- **Test:** Chiêm chỉ sở hữu `tests/test_gather_sim.py`; Tùng chỉ sở hữu `tests/test_quan_sim.py`; Minh sở hữu `tests/test_smoke_p1.py` và kiểm tra tích hợp. Báo nhau trước nếu cần sửa test của người khác.
- **Roster:** repo hiện khai báo `team_size: 4`, trong khi phân công này có ba người. Minh ghi nhận và hỏi nhóm/PO để thống nhất roster; không tự đổi `game.contract.json`.
- **Git:** mỗi người làm commit có nội dung trong phạm vi được giao; chạy test phù hợp trước khi bàn giao và nêu rõ lệnh/kết quả trong mô tả commit hoặc bằng chứng.

## Tiêu chí bàn giao chung

- Không hard-code thông số gameplay; dùng tuning từ `game.contract.json`.
- Tính xác định và cấu trúc output của headless không bị phá vỡ.
- Cả ba báo phần đã xong, test đã chạy, kết quả và việc còn vướng trước khi gắn tag phase.
