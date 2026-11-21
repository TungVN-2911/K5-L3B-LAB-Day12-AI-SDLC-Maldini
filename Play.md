# Hướng dẫn chơi — Quán Ăn Chợ Nổi

Một ngày ở miền Tây: **sáng lặn sông bắt cá, hái bông**, **tối mở quán trên ghe bán cho khách**, rồi sáng hôm sau ra sông tiếp. Mục tiêu: kiếm thật nhiều tiền và giữ uy tín quán cao.

---

## 1. Cài đặt và chạy

Chỉ cần **Python 3.10+**, không cần cài thêm thư viện nào.

```powershell
python -m chonoi.live --mode day
```

Mở trình duyệt vào địa chỉ in ra (mặc định `http://127.0.0.1:8000/`). Muốn tắt game thì bấm `Ctrl+C` ở cửa sổ terminal.

| Muốn… | Lệnh |
|---|---|
| Đổi bản đồ ngẫu nhiên (vị trí buff, món khách gọi…) | `python -m chonoi.live --mode day --seed 7` |
| Cổng 8000 đang bận | `python -m chonoi.live --mode day --port 8080` |
| Chỉ chơi phần lặn (luật gốc, không buff / cá lớn) | `python -m chonoi.live --mode gather --inventory-out kho.json` |
| Chỉ chơi phần quán (luật gốc, nhìn từ trên xuống) | `python -m chonoi.live --mode quan --inventory kho.json` |

> Hướng dẫn bên dưới là cho chế độ **`--mode day`** (đầy đủ nhất).

---

## 2. Phím điều khiển

| Phím | Buổi sáng (lặn) | Buổi tối (quán) |
|---|---|---|
| `W A S D` / mũi tên | Bơi lên / trái / xuống / phải | Đi trái / phải sau quầy |
| `E` | Hái bông (ở mặt nước) · Cập bến | Mở bếp · Lấy món xong · Phục vụ khách |
| `Space` | Bắt cá · Đánh cá lớn · Bắn súng xiên | — |
| `1`–`8` | — | **Nấu nhanh** phiếu order thứ 1–8 |
| Chuột trái | — | Bấm phiếu order / bảng món để **nấu nhanh**; bấm trong bảng nấu |
| `Q` | — | Bỏ món đang cầm trên tay |
| `R` | Chơi lại từ đầu | Chơi lại từ đầu |
| `M` | Tắt / bật âm thanh | Tắt / bật âm thanh |
| `` ` `` hoặc `F2` | Chế độ debug (id, sự kiện, fps) | như bên trái |

**Trong bảng nấu** (mở bằng `E` ở bếp trống): `Tab` đổi cách nấu · `1`–`9` chọn · `Shift`+số lấy bớt nguyên liệu ra · `Backspace` bỏ nguyên liệu vừa thêm · `Enter` nấu · `Esc` đóng.

---

## 3. Vòng lặp một ngày

```
 SÁNG (180 giây)                                TỐI (150 giây)
 Lặn sông: hái bông, bắt cá, đánh cá lớn   ──►  Mở quán: nấu, phục vụ, thu tiền
        │  Cập bến (E) / hết giờ / ngất              │  Hết giờ / HẾT HÀNG ĐỂ BÁN
        ▼                                             ▼
 Màn chuyển cảnh: mẻ sáng nay + kho           Màn chuyển cảnh: tiền thu + kho còn lại
                                                      │
                     ◄──────────── Sáng hôm sau ──────┘
```

- **Kho mang ra quán** = nguyên liệu còn dư từ hôm trước + giỏ vừa bắt được.
- Nếu kho **không đủ nấu món nào** → bỏ qua buổi tối, sang thẳng sáng hôm sau.
- Khi tối mà **hết nguyên liệu bán được** (không nấu thêm món nào, không còn món trên bếp / trên tay, không còn khách đang ăn) → hiện thông báo **"Hết hàng để bán! Ra sông bắt cá thôi"** và chuyển sang sáng.
- **Tiền và uy tín được cộng dồn** qua các ngày. Góc trên phải luôn hiện `Ngày N · Két …k`.

---

## 4. Buổi sáng — Lặn sông

### 4.1 Màn hình

- **Đồng hồ** (góc trên trái): thời gian còn lại của buổi sáng.
- **3 trái tim**: Máu. Hết Máu là **ngất** → mất sạch giỏ.
- **Thanh Oxy**: dưới nước tụt dần (tối đa 30 giây). Ngoi lên mặt nước thì hồi rất nhanh.
- **↓ x m**: độ sâu hiện tại.
- **Bản đồ nhỏ "Sông"**: chấm cam là bạn, chấm hồng/vàng là bông, chấm trắng/xanh là cá, ô vuông màu là vật phẩm buff, chấm đỏ là cá lớn.
- **Giỏ x/12** (góc dưới trái): những gì đã bắt được (tối đa 12 món).
- **Hàng buff** (dưới bảng trên trái): buff đang có, kèm số đạn / số giây còn lại.

### 4.2 Hái bông (ở mặt nước)

- Bơi tới cạnh **bông súng** (hoa hồng trên lá) hoặc **bông điên điển** (cụm hoa vàng) khi đang ở mặt nước.
- Khi hiện nhắc `E Hái …` thì bấm `E` → +1 vào giỏ.
- Bông đã hái sẽ **mọc lại sau 20 giây** (có vòng đếm ngược trên cây).

### 4.3 Bắt cá (dưới nước)

- Lặn xuống gần đàn cá (trong vòng tròn mờ quanh người). Khi hiện `Space Bắt …` thì bấm `Space`.
- **Cá linh** cho **3** con một lần, **cá lóc** cho **1** con. Bắt xong phải chờ 0,5 giây mới bắt tiếp.
- Cá nhỏ **sinh thêm** theo thời gian, nên sông không bị cạn.

### 4.4 Oxy và ngạt

- Oxy về 0 khi đang dưới nước → màn hình viền đỏ, **cứ mỗi giây mất 1 tim**.
- Thấy thanh oxy **nhấp nháy đỏ** (dưới 25%) thì ngoi lên ngay.

### 4.5 Vật phẩm buff (quả cầu phát sáng dưới nước)

Cứ khoảng 9 giây lại xuất hiện một vật phẩm (tối đa 4 cái cùng lúc). **Bơi chạm vào là nhặt.**

| Buff | Tác dụng |
|---|---|
| **Bình oxy** (cầu xanh) | Nạp **đầy oxy** + **khiên oxy 10 giây** (oxy không tụt) |
| **Lưới lớn** (cầu vàng) | 15 giây: tầm bắt rộng **gấp 1,8 lần**, một lần `Space` **bắt hết cá trong tầm** |
| **Súng xiên** (cầu cam) | +8 mũi xiên (tối đa 16). `Space` **bắn theo hướng đang bơi** (có vạch ngắm). Mũi xiên trúng cá nhỏ thì bắt luôn, trúng cá lớn thì gây 2 sát thương |

> Khi đang có súng xiên, `Space` luôn là **bắn**. Hết đạn thì `Space` quay về bắt / đánh như bình thường.

### 4.6 Cá lớn — chiến đấu

| Cá | Máu | Vùng sống | Rơi ra |
|---|---|---|---|
| **Cá đuối** | 4 | Giữa sông (x ≈ 30–52, sâu ~18 m) | 1 cá đuối |
| **Cá bông lau** | 7 | Cuối sông (x ≈ 66–96, sâu ~23 m) | 1 cá bông lau |

- Cá lớn bơi tuần tra. Khi bạn tới gần (~5 m), nó **đuổi theo** (mắt đỏ, tên có dấu ⚠).
- **Bị cắn: mất 1 tim**, bị đẩy lùi, được **bất tử 2 giây** (nhân vật nhấp nháy). Cắn xong cá bơi ra xa khoảng 2,5 giây.
- **Cách đánh:**
  - **Cận chiến:** tới gần, khi hiện `Space Đánh …` thì bấm `Space` (1 sát thương, nghỉ 0,5 giây giữa hai đòn).
  - **Súng xiên:** đứng xa, quay mặt về phía cá (bơi một chút về hướng đó), rồi bấm `Space` (2 sát thương mỗi phát).
- Thanh máu trên đầu cá: xanh → vàng → đỏ. Hạ được thì nguyên liệu quý **rơi thẳng vào giỏ** (giỏ phải còn chỗ). Cá hồi sinh sau 30–40 giây.
- Cá lớn **không lên mặt nước**: bị đuổi gấp thì ngoi lên để thoát. Bạn bơi nhanh hơn chúng.

### 4.7 Cập bến

- Bơi về **bến** (nhà sàn bên trái, vòng nét đứt). Khi hiện `E Cập bến bán hàng` thì bấm `E` → kết thúc buổi sáng, giữ nguyên giỏ.
- Hết giờ cũng giữ giỏ. **Chỉ có ngất mới mất giỏ.**

---

## 5. Buổi tối — Mở quán

### 5.1 Màn hình quán

- **Quầy bar 8 ghế** (S1–S8, từ trái sang phải). Khách ngồi quay lưng về phía bạn.
- **Bạn là đầu bếp đội nón lá**, đi sau quầy (chỉ đi trái / phải bằng `A` / `D`).
- **Khu bếp** bên phải: **3 bếp lò B1, B2, B3**.
- **Bảng món treo trên vách**: mỗi tấm là một món, ghi **"còn N"** (kho đủ nấu N phần) hoặc **"hết"**, kèm giá. Tấm nào **viền vàng nhấp nháy** là món có khách đang chờ và còn nấu được.
- **Phiếu order** (góc trên phải): danh sách khách đang chờ món, **khách gấp nhất ở trên cùng**.
- **Kho** (góc dưới trái) và **Trên tay** (món đang cầm).
- Thông báo / lời nhận xét của khách hiện ở **bên trái**, dưới bảng tiền.

### 5.2 Khách đến và gọi món

- Khoảng **8 giây** có một khách mới, bước vào từ cửa trái và ngồi ghế trống.
- Mỗi khách gọi **1 món**. Bong bóng trên đầu là món họ muốn. **Vòng quanh bong bóng là độ kiên nhẫn** (tối đa 60 giây).
- **Khách thường gọi món mà kho còn nấu được**, nhưng thỉnh thoảng (khoảng 1/5 số khách) sẽ **gọi đúng món đang hết** (xem 5.7).

### 5.3 Phiếu order (bên bếp)

Mỗi dòng gồm: số thứ tự · món · ghế · thanh kiên nhẫn · mặt cảm xúc · trạng thái:

| Trạng thái | Nghĩa |
|---|---|
| **Nấu nhanh** (vàng) | Chưa ai nấu, kho đủ. **Bấm vào dòng này** hoặc bấm **phím số** đứng đầu dòng để nấu ngay |
| **đang nấu** | Đã có một bếp đang nấu món này cho khách |
| **xong · lấy món** | Món đã chín trên bếp, ra lấy rồi mang tới khách |
| **trên tay** | Bạn đang cầm món này, mang tới đúng ghế |

> Phím số chỉ đánh số cho các dòng **"Nấu nhanh"**: `1` là phiếu gấp nhất còn chưa nấu.

### 5.4 Ba cách nấu

| Cách | Làm thế nào | Phải đi tới bếp? | Thời gian | Chất lượng |
|---|---|---|---|---|
| **① Nấu nhanh** | Bấm **phiếu order**, hoặc **phím số 1–8**, hoặc bấm **tấm bảng món** trên vách | **Không**, bếp trống đầu tiên tự nấu | Chậm (×1,6) | Ngon vừa |
| **② Bếp tự nấu** | Đi tới bếp trống → `E` → tab **"Bếp tự nấu"** → bấm món (hoặc số) | Có | Chậm (×1,6) | Ngon vừa |
| **③ Tự chọn nguyên liệu** | Đi tới bếp trống → `E` → tab **"Tự chọn nguyên liệu"** → bấm số để bỏ từng nguyên liệu vào **Nồi** → `Enter` | Có | **Nhanh** (thời gian chuẩn) | **Ngon nhất ★** |

- Cách ③ **sai công thức** → **hỏng món, mất hết nguyên liệu đã bỏ vào nồi**. Hãy xem **Sổ công thức** ở cột phải của bảng nấu.
- Nếu cả 3 bếp đều bận thì nấu nhanh sẽ báo *"Cả 3 bếp đang bận"*.
- Thanh tiến độ trên bếp: **vàng** = bếp tự nấu, **xanh** = bạn tự nấu.

### 5.5 Công thức

| Món | Nguyên liệu | Nấu chuẩn | Giá |
|---|---|---|---|
| Gỏi bông súng | 2 bông súng | 4 s | 40k |
| Cá lóc nướng trui | 1 cá lóc | 6 s | 60k |
| Canh chua cá lóc | 1 cá lóc + 1 bông súng | 7 s | 90k |
| Lẩu cá linh điên điển | 3 cá linh + 1 bông điên điển | 10 s | 120k |
| Cá đuối nướng muối ớt | 1 cá đuối *(hạ cá đuối)* | 6 s | 140k |
| Lẩu cá bông lau | 1 cá bông lau *(hạ cá bông lau)* + 1 bông điên điển | 9 s | 200k |

(Bếp tự nấu / nấu nhanh mất gấp 1,6 lần thời gian ở cột "Nấu chuẩn".)

### 5.6 Lấy món và phục vụ

1. Bếp hiện bong bóng món + chữ **"xong"** (hoặc **"★ ngon"**) → đi tới bếp, bấm `E` để **lấy món**.
2. Đi tới ghế khách đã gọi món đó (nhắc `E Phục vụ`) → bấm `E`.
   - Mang tới khách gọi món khác: hiện *"Khách gọi món khác!"*, không phục vụ được.
   - Món không còn ai cần (khách đã bỏ về): bấm `Q` để bỏ món.
3. **Món để trên bếp quá 10 giây sẽ nguội** (chữ "nguội"): vẫn bán được nhưng khách kém hài lòng.
4. Khách ăn khoảng 7 giây (thanh xanh dưới bong bóng) rồi **trả tiền**: hiện `+…k`, đồng xu và một lời nhận xét ở góc trái.

### 5.7 Hết nguyên liệu: khách được báo và rời quán

Khi món khách gọi **không còn đủ nguyên liệu**, ví dụ:
- khách vừa vào đã gọi đúng món đang **"hết"**, hoặc
- bạn vừa nấu hỏng / nấu món khác làm **hụt nguyên liệu** của món khách đang chờ,

thì ngay lập tức:
- trên đầu khách hiện **bong bóng món bị gạch chéo đỏ**, chữ **"Hết món!"** và **mặt thất vọng 😢** (mặt xanh, có giọt nước mắt);
- góc trái hiện thông báo: *"Ghế S3 gọi Canh chua cá lóc — hết nguyên liệu, khách thất vọng ra về"*;
- sau khoảng **2,5 giây** khách đứng dậy, **đi ra cửa với mặt thất vọng**. Uy tín **giảm nhẹ (−0,1)**.

> Mẹo: nhìn **bảng món trên vách**. Món nào ghi **"hết"** thì khách gọi món đó sẽ bỏ về. Hãy ưu tiên lặn bắt nguyên liệu cho các món hay hết.

### 5.8 Cảm xúc của khách

**Lúc đang chờ** (mặt nhỏ cạnh bong bóng và trong phiếu order):

| Mặt | Kiên nhẫn còn |
|---|---|
| 🙂 Vui | trên 60% |
| 😐 Bình thường | 30–60% |
| 😠 Giận (có 💢, bong bóng rung) | dưới 30% |

Hết kiên nhẫn → khách **giận dữ bỏ về** (mặt giận đi ra cửa, *"Đợi hoài không thấy món!"*), uy tín **−0,5**.

**Lúc ăn / trả tiền**: điểm hài lòng = **điểm món + điểm chờ**:
- Điểm món: ★ ngon (tự chọn nguyên liệu) = 2 · ngon vừa (bếp tự nấu / nấu nhanh) = 1 · nguội = 0
- Điểm chờ: phục vụ khi kiên nhẫn còn ≥ 60% = 2 · ≥ 30% = 1 · ít hơn = 0

| Tổng điểm | Cảm xúc | Tip | Uy tín |
|---|---|---|---|
| 4 | 😍 **Rất hài lòng** (mắt trái tim) | +30% giá món | +0,3 |
| 2–3 | 🙂 **Hài lòng** | +15% | +0,1 |
| 1 | 😐 **Tạm được** | 0 | 0 |
| 0 | 😞 **Không hài lòng** | 0 | −0,2 |
| — | 😢 **Thất vọng** (hết món) | — | −0,1 |
| — | 😠 **Giận, bỏ về** (chờ quá lâu) | — | −0,5 |

> Muốn khách **rất hài lòng** thì phải **tự chọn nguyên liệu đúng công thức** và **phục vụ nhanh**. Nấu nhanh tiện nhưng cao nhất chỉ đạt "Hài lòng".

### 5.9 Kết thúc buổi tối

- **Hết giờ** (150 giây), hoặc
- **Hết hàng để bán** (xem mục 3) → *"Hết hàng để bán! Ra sông bắt cá thôi"*.

Màn chuyển cảnh hiện **tiền thu ca tối** và **kho còn lại**, rồi sang sáng hôm sau.

---

## 6. Điểm số

```
Điểm = tổng tiền đã thu + 100 × (phần nguyên của uy tín)
```

Uy tín từ 0 đến 5 sao (bắt đầu 3 sao), hiện ở thanh trên cùng buổi tối.

---

## 7. Mẹo chơi

1. **Buổi sáng:** hái bông ở mặt nước trước (an toàn, không tốn oxy), rồi mới lặn bắt cá. Luôn để ý thanh oxy.
2. **Cá linh** cho 3 con một lần nhưng chiếm 3 ô giỏ. Giỏ chỉ có 12 ô, hãy tính theo món định bán: lẩu cá linh cần 3 cá linh + 1 bông điên điển.
3. **Nhặt súng xiên rồi mới đi săn cá lớn.** Cá đuối 4 Máu = 2 phát xiên. Món cá đuối (140k) và lẩu cá bông lau (200k) là món đắt nhất.
4. **Buổi tối:** dùng **nấu nhanh (phím số)** để giữ bếp luôn chạy, còn bạn thì lo **lấy món và phục vụ**. Khi rảnh, tự chọn nguyên liệu cho khách mới để lấy tip 30%.
5. Đừng để món nằm trên bếp quá 10 giây (nguội).
6. Nhìn **bảng món trên vách** để biết món nào sắp hết, sáng hôm sau ưu tiên bắt nguyên liệu đó.
7. Đừng nấu bừa bằng tay: sai công thức sẽ hỏng nguyên liệu và có thể làm khách đang chờ **hết món, bỏ về**.

---

## 8. Gặp lỗi?

| Hiện tượng | Cách xử lý |
|---|---|
| Trang báo *"Mất kết nối tới máy chủ"* | Cửa sổ terminal đã tắt. Chạy lại lệnh ở mục 1 |
| `không mở được cổng 8000` | Thêm `--port 8080` (hoặc một cổng khác) |
| *"Luật của nhóm báo lỗi — xem terminal"* | Xem lỗi in ở terminal, bấm `R` để chơi lại |
| Không nghe tiếng | Bấm vào trang hoặc một phím bất kỳ trước (trình duyệt chặn âm thanh khi chưa tương tác), kiểm tra `M` |
| Phím không ăn | Bấm chuột vào trang game cho trang nhận phím |

Số liệu của phần mở rộng (buff, cá lớn, tốc độ khách, công thức thêm…) nằm trong `chonoi/data/extras.json`, có thể chỉnh để cân bằng lại game.
