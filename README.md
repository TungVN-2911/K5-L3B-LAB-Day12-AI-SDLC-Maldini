# Day 12 — AI SDLC: Quán Ăn Chợ Nổi

> **Làm theo nhóm 3–6 người** · Dùng AI để xây game 2D qua **4 phase** trong **3 giờ**: Út Sen lặn bắt cá, hái rau trên mặt nước rồi tối mở quán phục vụ khách.
> **Yêu cầu từng phase mở đúng mốc giờ tại lab board:** **[Chợ Nổi Lab](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg)** (cần đăng nhập claude.ai; có trợ giảng AI cho từng phase).

## Bắt buộc (chỉ có thế)

Cách làm việc kỹ thuật là **tự do** (push thẳng, nhánh + PR, pair, có hay không CI…). Cái bắt buộc:

1. **Một repo chung:** trưởng nhóm **fork** repo này, đặt tên `K5-L3B-LAB-Day12-AI-SDLC-<ten-nhom>`, thêm mọi thành viên làm collaborator (*Settings → Collaborators*, quyền Write) và để repo **public** (giảng viên xem được, không cần mời).
2. **Cả nhóm cùng commit** bằng tài khoản GitHub của mình, mỗi người **≥ 3 commit có nội dung** (làm cặp thì ghi `Co-authored-by:`).
3. **Điền [`TEAM.md`](TEAM.md):** danh sách thành viên + thỏa thuận làm việc nhóm; sửa `team_size` trong [`game.contract.json`](game.contract.json). Commit của người không có trong `TEAM.md` không được tính.
4. **Gắn tag** `phase-1` … `phase-4` đúng hạn; chạy được tại từng tag.
5. **Ghi chép tối thiểu:** `docs/verification/phase-n.md`, `docs/clarify.md`, `docs/ai-usage-log.md`, `docs/retro.md`, `docs/members/<handle>.md`.

## Bắt đầu nhanh

```bash
git clone <fork-của-nhóm> && cd <fork-của-nhóm>
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v        # smoke test
python3 -m chonoi.live --mode gather                                # chơi thử trên trình duyệt (tùy chọn)
```

Game cần chế độ **headless** theo Test Contract (`python3 -m chonoi.headless --mode gather|quan …`) để được chạy và chấm tự động. **Công nghệ không ràng buộc**: khung Python trong `chonoi/` chỉ là gợi ý, chi tiết ở [`docs/STARTER.md`](docs/STARTER.md).

## Tự do sáng tạo

Ngoài phần đề yêu cầu, nhóm được **thêm** nhân vật, loài cá/cây, sinh vật, món, bản đồ, cơ chế, câu chuyện, đồ họa, âm nhạc… với ba điều kiện: **không phá phần cố định** (tắt ở headless), ghi mục **"Sáng tạo của nhóm"** trong README của nhóm, và **làm lõi đúng trước**.

## Lịch 3 giờ

| Mốc | Phase | Hạn tag |
|---|---|---|
| 0:00 | Phase 1 (PRD-0) | `phase-1` trước 1:00 |
| 1:00 | Phase 2 | `phase-2` trước 1:55 |
| 1:55 | Phase 3 | `phase-3` trước 2:30 |
| 2:30 | Phase 4 | `phase-4` + Release `v1.0.0` trước 3:00 |

Hết giờ mỗi phase thì gắn tag rồi đi tiếp; chỗ chưa xong ghi trung thực trong bằng chứng.

## Đánh giá (100 điểm)

| Hạng mục | Điểm |
|---|---|
| Test tự động ẩn (headless, gồm kiểm tra lại phase trước) | 25 |
| Làm việc nhóm (một repo chung, chia việc, tích hợp, đổi yêu cầu) | 25 |
| Kiểm chứng & bằng chứng | 15 |
| Harness AI (AGENTS.md, skill, nhật ký dùng AI) | 10 |
| Đánh giá & retro | 10 |
| Chất lượng sản phẩm (đúng yêu cầu, mở rộng/sáng tạo) | 10 |
| Demo | 5 |

## Quy định

- Dùng AI thoải mái; **không sao chép repo của nhóm khác**; bằng chứng phải thật.
- Nhân vật, bối cảnh là bản gốc của lab; asset ngoài chỉ dùng CC0/CC-BY/MIT hoặc tự tạo, ghi nguồn trong `CREDITS.md`. Không commit API key, token, `.env`.

## Sáng tạo của nhóm

**Đồ họa 2D cho cửa sổ chơi** (`chonoi/web/index.html`). Chỉ là phần hiển thị phía client; luật, snapshot và headless không đổi.
- Hình đều tự vẽ bằng Canvas 2D, không có asset ngoài. Gather: sông buổi sáng có trời, mây, hàng dừa, nhà sàn, tia nắng dưới nước, rong và đáy bùn; bến ghe treo cây bẹo; bông súng, bông điên điển; cá lóc và đàn cá linh vẫy đuôi; thợ lặn quàng khăn rằn, đạp chân và sải tay. Quán: ghe nổi về đêm có sàn gỗ, đèn lồng, bếp lò có lửa và hơi nước, bàn có ghế đẩu, khách gọi món kèm vòng kiên nhẫn, đầu bếp đội nón lá bưng khay.
- Chơi mượt hơn: client giữ bộ đệm snapshot, đồng bộ nhịp 60 tick/s và **nội suy** vị trí (hiển thị trễ khoảng 3 tick). Camera đi theo người chơi một cách mượt; góc quay và hoạt ảnh làm mịn theo thời gian thực.
- Hiệu ứng theo sự kiện: hạt, chữ bay, rung màn hình, viền tối khi sắp hết oxy, thông báo tiếng Việt và âm thanh tổng hợp bằng WebAudio (phím `M` tắt/bật). Có gợi ý phím `E`/`Space` ngay tại vật đang trong tầm, bản đồ nhỏ của sông, phiếu gọi món và màn hình tổng kết.
- Phím `` ` `` (hoặc F2) bật chế độ debug: hiện id thực thể, nhật ký sự kiện thô, tick, fps.

**Chế độ "một ngày" liền mạch** — `python3 -m chonoi.live --mode day`. Hướng dẫn chơi chi tiết: [Play.md](Play.md). Đây chỉ là cửa sổ chơi; headless và Test Contract vẫn chạy `GatherSim`/`QuanSim` gốc.
- **Vòng lặp:** sáng lặn bắt cá → cập bến / hết giờ → màn chuyển cảnh → tối mở quán với kho = kho còn dư + giỏ vừa bắt → hết giờ hoặc **hết hàng để bán** → thông báo rồi quay lại sông vào ngày hôm sau. Nếu kho không đủ nấu món nào thì bỏ qua buổi tối. Tiền và uy tín cộng dồn qua các ngày.
- **Dưới nước** (`GatherPlus`):
  - Buff nhặt dưới nước: **Tăng tốc** (bơi nhanh 8 giây) và **Hồi máu** (+1 tim).
  - **Tiệm đồ lặn** (ghe cạnh bến, `E` ở mặt nước): súng xiên, lưới lớn, giáp bong bóng (đỡ 3 cú cắn, vỡ rồi mới mua lại), bình lặn, chân vịt, dao găm, cộng thêm nâng cấp giỏ.
    - **5 ô đồ**, mỗi món 1 cái, không chồng; hết ô thì không mua được, bán lại được nửa giá.
    - Tiền và đồ giữ qua các ngày.
  - Thợ lặn đeo **giỏ tre ở thắt lưng** (đầy dần theo số đồ bắt được); đồ mua được vẽ ngay trên người.
  - **Cá khủng có Máu:** cá đuối, lươn điện, cá hải tượng, cá bông lau, trùm cá tra dầu (cắn mất 2 tim). Có thêm **cá lạ** (cá hề vàng, cá tai tượng) và món mới cho từng loại.
- **Quán nhìn ngang** (`QuanPlus`):
  - Quầy bar 8 ghế, 3 bếp, nhiều khách cùng lúc. Bảng món trên vách cho biết mỗi món còn nấu được bao nhiêu phần.
  - Bấm E ở bếp trống để mở bảng nấu, có hai cách: **giao món cho bếp tự nấu** (chậm, ngon vừa) hoặc **tự chọn nguyên liệu** (đúng công thức thì nhanh và ngon nhất; sai thì hỏng món, mất nguyên liệu). Món để lâu trên bếp sẽ **nguội**.
  - **Nấu nhanh:** bấm vào **phiếu order** (bảng bên bếp, liệt kê món khách đã gọi) hoặc bấm **tấm bảng món** trên vách, hoặc phím số `1`–`8` → bếp trống đầu tiên tự nấu, không cần đi tới bếp.
- **Hết nguyên liệu cho món khách gọi:** khách được báo ("Hết món!", món bị gạch chéo), hiện mặt **thất vọng** rồi rời quán (uy tín −0,1).
- **Cảm xúc khách:** biểu tượng mặt hiện theo thời gian chờ. Sau khi phục vụ, mức hài lòng tính từ chất lượng món + thời gian chờ, quyết định tip và uy tín, kèm lời nhận xét. Khách bỏ về thì hiện mặt giận.
- Số liệu nằm trong `chonoi/data/extras.json`, luật trong `chonoi/sim/extras.py` và `chonoi/day.py`, test trong `tests/test_extras.py`.
- **Đã sửa file khung** `chonoi/live.py` (đã báo nhóm): thêm `--mode day` và `POST /action` (lệnh của bảng nấu). Hai chế độ `gather`/`quan` cũ giữ nguyên hành vi.

