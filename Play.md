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
| `E` | Hái bông · **Mở tiệm đồ lặn** · Cập bến (đều ở mặt nước) | Mở bếp · Lấy món xong · Phục vụ khách |
| `Space` | Bắt cá · Đánh cá khủng · Bắn súng xiên (khi có súng) | — |
| `1`–`8` | — | **Nấu nhanh** phiếu order thứ 1–8 |
| Chuột trái | — | Bấm phiếu order / bảng món để **nấu nhanh**; bấm trong bảng nấu |
| `Q` | — | Bỏ món đang cầm trên tay |
| `R` | Chơi lại từ đầu | Chơi lại từ đầu |
| `M` | Tắt / bật âm thanh | Tắt / bật âm thanh |
| `` ` `` hoặc `F2` | Chế độ debug (id, sự kiện, fps) | như bên trái |

**Trong tiệm đồ lặn**: `1`–`7` mua · `Shift`+`1`–`5` bán lại đồ ở ô đó · `Esc` đóng.

**Trong bảng nấu** (mở bằng `E` ở bếp trống): `Tab` đổi cách nấu · `1`–`9` chọn · `Shift`+số lấy bớt nguyên liệu ra · `Backspace` bỏ nguyên liệu vừa thêm · `Enter` nấu · `Esc` đóng.

---

## 3. Vòng lặp một ngày

```
 SÁNG (180 giây)                                TỐI (150 giây)
 Mua đồ ở tiệm, lặn sông: hái bông,        ──►  Mở quán: nấu, phục vụ, thu tiền
 bắt cá, đánh cá khủng
        │  Cập bến (E) / hết giờ / ngất              │  Hết giờ / HẾT HÀNG ĐỂ BÁN
        ▼                                             ▼
 Màn chuyển cảnh: mẻ sáng nay + kho           Màn chuyển cảnh: tiền thu + kho còn lại
                                                      │
                     ◄──────────── Sáng hôm sau ──────┘
```

- **Kho mang ra quán** = nguyên liệu còn dư từ hôm trước + giỏ vừa bắt được.
- Nếu kho **không đủ nấu món nào** → bỏ qua buổi tối, sang thẳng sáng hôm sau.
- Khi tối mà **hết nguyên liệu bán được** (không nấu thêm món nào, không còn món trên bếp / trên tay, không còn khách đang ăn) → hiện thông báo **"Hết hàng để bán! Ra sông bắt cá thôi"** và chuyển sang sáng.
- **Tiền, uy tín và đồ nghề được giữ** qua các ngày. Góc trên phải luôn hiện `Ngày N · Két …k`. Tiền thu buổi tối dùng để mua đồ ở tiệm sáng hôm sau.

---

## 4. Buổi sáng — Lặn sông

### 4.1 Màn hình

- **Đồng hồ** (góc trên trái): thời gian còn lại của buổi sáng.
- **3 trái tim**: Máu. Hết Máu là **ngất** → mất sạch giỏ.
- **Thanh Oxy**: dưới nước tụt dần (30 giây, có **bình lặn** thì 50 giây). Ngoi lên mặt nước thì hồi rất nhanh.
- **↓ x m**: độ sâu hiện tại.
- **Bản đồ nhỏ "Sông"**: chấm cam là bạn, ô đỏ ở mép trái là **tiệm đồ lặn**, chấm hồng/vàng là bông, chấm trắng/xanh là cá, ô vuông xanh/hồng là buff, chấm đỏ to là cá khủng.
- **Giỏ x/12** (góc dưới trái): những gì đã bắt được. Nâng cấp giỏ ở tiệm thì chứa được tới 24.
- **Đồ nghề x/5** (góc dưới phải): 5 ô đồ đang mang. Súng xiên ghi số mũi còn lại (`×12`), giáp ghi số lần còn đỡ được (`◆◆◆`).
- **Hàng buff** (dưới bảng trên trái): buff tăng tốc đang có, kèm số giây.
- **Két** (góc trên phải): tiền hiện có, dùng để mua đồ.

### 4.2 Nhân vật và giỏ đeo hông

Thợ lặn quàng khăn rằn, đeo một **giỏ tre ở thắt lưng**. Giỏ phồng lên theo số đồ bên trong, cá/bông vừa bắt nhô lên ở miệng giỏ; giỏ đầy thì có chấm đỏ nhỏ. Đồ mua ở tiệm hiện ngay trên người:

| Đồ | Trông thế nào |
|---|---|
| Bình lặn | Bình vàng trên lưng, có ống thở nối vào miệng |
| Lưới lớn | Cuộn lưới đeo sau lưng; vòng tầm bắt quanh người thành **nét đứt vàng**, rộng hơn |
| Súng xiên | Cầm trước mặt; dưới nước có **vạch ngắm** chấm theo hướng bơi |
| Giáp bong bóng | Một bong bóng trong suốt bao quanh người |
| Chân vịt | Chân đeo chân vịt xanh lá |
| Dao găm | Dao giắt ở thắt lưng |

### 4.3 Hái bông (ở mặt nước)

- Bơi tới cạnh **bông súng** (hoa hồng trên lá) hoặc **bông điên điển** (cụm hoa vàng) khi đang ở mặt nước.
- Khi hiện nhắc `E Hái …` thì bấm `E` → +1 vào giỏ.
- Bông đã hái **mọc lại sau 20 giây** (có vòng đếm ngược trên cây).

### 4.4 Bắt cá nhỏ (dưới nước)

- Lặn xuống gần cá, khi hiện `Space Bắt …` thì bấm `Space`. Bắt xong phải chờ 0,5 giây mới bắt tiếp.
- Có **lưới lớn**: tầm bắt rộng ×1,8 và **một lần `Space` bắt hết cá trong tầm**.

| Cá nhỏ | Một lần bắt được | Ghi chú |
|---|---|---|
| Cá linh (đàn cá bạc) | 3 con | Chiếm 3 ô giỏ |
| Cá lóc (xanh rêu, đốm đen) | 1 con | |
| **Cá hề vàng** (cam sọc trắng) | 1 con | Cá lạ, ít gặp |
| **Cá tai tượng** (thân tròn hồng xám, râu dài) | 1 con | Cá lạ, ít gặp |

Cá nhỏ **sinh thêm** theo thời gian, sông không bị cạn.

### 4.5 Oxy và ngạt

- Oxy về 0 khi đang dưới nước → màn hình viền đỏ, **cứ mỗi giây mất 1 tim**.
- Thấy thanh oxy **nhấp nháy đỏ** (dưới 25%) thì ngoi lên ngay.

### 4.6 Buff dưới nước (quả cầu phát sáng)

Cứ khoảng 9 giây lại xuất hiện một buff (tối đa 4 cái). **Bơi chạm vào là nhặt.**

| Buff | Trông thế nào | Tác dụng |
|---|---|---|
| **Tăng tốc** | Cầu xanh lá, hình tia chớp | Bơi nhanh ×1,6 trong 8 giây |
| **Hồi máu** | Cầu hồng, hình trái tim | +1 tim. Đang đủ máu thì **không nhặt** (để dành lúc cần) |

### 4.7 Tiệm đồ lặn (ghe sọc đỏ trắng cạnh bến)

**Mở tiệm:** bơi ở **mặt nước** tới ghe **"TIỆM ĐỒ LẶN"** (ngay bên phải bến). Khi hiện `E Mua đồ lặn` thì bấm `E`. Đồng hồ buổi sáng **vẫn chạy** khi đang mua sắm; lặn xuống hoặc bơi xa thì tiệm tự đóng.

**Tiền:** ngày đầu có sẵn **150k**, sau đó là tiền bán quán buổi tối (hiện ở `Két`).

| Phím (trong tiệm) | Tác dụng |
|---|---|
| `1`–`6` hoặc bấm dòng | Mua món đồ tương ứng |
| `7` hoặc bấm dòng cuối | Nâng cấp giỏ |
| Bấm vào một ô đồ hoặc `Shift` + `1`–`5` | **Bán lại** món ở ô đó, được **nửa giá** |
| `Esc` / nút ✕ | Đóng tiệm |

| # | Đồ | Giá | Tác dụng |
|---|---|---|---|
| 1 | **Súng xiên** | 120k | `Space` bắn mũi xiên theo hướng đang bơi (tầm 10 m, 2 sát thương). **12 mũi mỗi buổi sáng**, sáng hôm sau tự nạp lại. Trúng cá nhỏ thì bắt luôn |
| 2 | **Lưới lớn** | 90k | Tầm bắt ×1,8, một lần bắt hết cá trong tầm |
| 3 | **Giáp bong bóng** | 70k | **Đỡ trọn 3 cú cắn của cá khủng** (không mất tim). Đỡ đủ 3 lần thì **vỡ** và biến mất khỏi ô đồ. **Chỉ mua được khi đang không mặc giáp**: vỡ rồi mới mua cái mới |
| 4 | **Bình lặn** | 100k | +20 giây oxy (30 → 50 giây) |
| 5 | **Chân vịt** | 80k | Bơi nhanh hơn 25% (cộng dồn với buff tăng tốc) |
| 6 | **Dao găm** | 60k | Đánh cận chiến 2 sát thương thay vì 1 |
| 7 | **Nâng cấp giỏ** | 80k → 150k → 250k | Mỗi cấp +4 ô giỏ (12 → 16 → 20 → 24). **Không chiếm ô đồ** |

**Luật 5 ô đồ:**
- Chỉ mang được **5 món đồ** (có 6 loại, phải chọn).
- **Mỗi loại chỉ có 1 cái**, không chồng (mua lại món đang có sẽ báo *"Đã có … rồi"*).
- **Hết ô thì không mua thêm được** (*"Hết ô đồ — bán bớt một món trước"*). Bán bớt một món để có chỗ.
- Đồ và tiền **giữ qua các ngày**, kể cả khi ngất (ngất chỉ mất giỏ cá).

### 4.8 Cá khủng — chiến đấu

| Cá | Máu | Cắn mất | Vùng sống (x, độ sâu) | Rơi ra |
|---|---|---|---|---|
| **Cá đuối** (dẹt, đuôi roi) | 4 | 1 ♥ | 30–52, ~18 m | Cá đuối |
| **Lươn điện** (dài, uốn lượn, tóe tia điện) | 5 | 1 ♥ | 50–68, ~12 m | Lươn |
| **Cá hải tượng** (rất dài, đuôi đỏ) | 10 | 1 ♥ | 62–84, ~16 m | Cá hải tượng |
| **Cá bông lau** (cá trê bạc, có râu) | 7 | 1 ♥ | 66–96, ~23 m | Cá bông lau |
| **Cá tra dầu** — trùm (khổng lồ, xám đậm) | 14 | **2 ♥** | 84–99, đáy sông ~27 m | Cá tra dầu |

- Cá khủng bơi tuần tra. Khi bạn tới gần (5–7 m), nó **đuổi theo** (mắt đỏ, tên có dấu ⚠).
- **Bị cắn:** giáp đỡ trước nếu có. Không có giáp thì mất tim. Sau đó bị đẩy lùi và được **bất tử 2 giây** (nhấp nháy); cá bơi ra xa khoảng 2,5 giây.
- **Cách đánh:**
  - **Cận chiến:** tới gần, khi hiện `Space Đánh …` thì bấm `Space` (1 sát thương, có dao găm thì 2).
  - **Súng xiên:** quay mặt về phía cá (bơi một chút về hướng đó), nhìn vạch ngắm rồi bấm `Space` (2 sát thương mỗi phát).
- Thanh máu trên đầu cá: xanh → vàng → đỏ. Hạ được thì nguyên liệu quý **rơi thẳng vào giỏ** (giỏ phải còn chỗ). Cá hồi sinh sau 30–60 giây.
- Cá khủng **không lên mặt nước**: bị đuổi gấp thì ngoi lên để thoát.

### 4.9 Cập bến

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
| Cá hề kho tộ | 1 cá hề vàng | 6 s | 80k |
| Cá tai tượng chiên xù | 1 cá tai tượng + 1 bông súng | 7 s | 110k |
| Cá đuối nướng muối ớt | 1 cá đuối *(hạ cá đuối)* | 6 s | 140k |
| Lươn xào sả ớt | 1 lươn *(hạ lươn điện)* + 1 bông điên điển | 8 s | 160k |
| Lẩu cá bông lau | 1 cá bông lau *(hạ cá bông lau)* + 1 bông điên điển | 9 s | 200k |
| Cá hải tượng nướng | 1 cá hải tượng *(hạ cá hải tượng)* | 9 s | 260k |
| Lẩu cá tra dầu | 1 cá tra dầu *(hạ trùm cá tra dầu)* + 1 bông súng | 10 s | 350k |

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

1. **Ngày đầu (150k):** mua **giáp bong bóng (70k) + dao găm (60k)** để đánh cá đuối / lươn điện an toàn, hoặc **bình lặn (100k)** để lặn lâu hơn.
2. **Buổi sáng:** hái bông ở mặt nước trước (an toàn, không tốn oxy), rồi mới lặn. Luôn để ý thanh oxy.
3. **Cá linh** cho 3 con một lần nhưng chiếm 3 ô giỏ. Tính theo món định bán; **nâng cấp giỏ** sớm nếu hay bị đầy.
4. **Săn cá khủng** khi đã có **súng xiên + giáp**. Cá hải tượng (260k) và cá tra dầu (350k) là món đắt nhất, nhưng **trùm cá tra dầu cắn mất 2 tim**: luôn mặc giáp, giữ đủ máu, nhặt buff hồi máu.
5. **5 ô đồ, 6 loại đồ:** đi săn thì mang súng + giáp + dao; đi bắt cá nhỏ thì mang lưới + bình lặn + chân vịt. Bán lại (½ giá) món ít dùng.
6. **Giáp vỡ** thì ghé tiệm mua cái mới trước khi xuống đáy sông.
7. **Buổi tối:** dùng **nấu nhanh (phím số)** để giữ bếp luôn chạy, còn bạn lo **lấy món và phục vụ**. Khi rảnh, tự chọn nguyên liệu cho khách mới để lấy tip 30%.
8. Đừng để món nằm trên bếp quá 10 giây (nguội). Nhìn **bảng món trên vách** để biết món nào sắp hết.
9. Đừng nấu bừa bằng tay: sai công thức sẽ hỏng nguyên liệu và có thể làm khách đang chờ **hết món, bỏ về**.

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
