# `nhaccu` — mỗi nhạc cụ một file `.py`

Tách từ `/Volumes/samwinchester/geese-3d-country`. **106 nhạc cụ**, mỗi cái một
file, code copy nguyên văn từ repo gốc — không viết lại, không "cải tiến", nên
âm thanh ra giống hệt.

Danh sách nhạc cụ và bài nào dùng cái gì: xem [`../NHAC-CU.md`](../NHAC-CU.md).

## Dùng

```python
from nhaccu._core import configure, buf, set_hum, Hum
from nhaccu.guitar.fuzz import fuzz          # đường dẫn đầy đủ
from nhaccu import mellotron                 # hoặc gọn thế này

configure(120, 120, end=16)      # bpm đầu, bpm cuối, số phách của bài
set_hum(Hum(seed=1))             # độ "người" — seed=None thì máy đánh đều tăm tắp

b = buf()                        # một stem, mảng mono numpy
fuzz(b, 1.0, 'E3', 0.9)          # (buffer, giây, nốt, độ dài giây)
mellotron(b, 1.0, ['E3','G3','B3'], 2.0)
```

Nghe thử tất cả:

```bash
python3 -m nhaccu.demo            # 94 file wav vào demo_out/
python3 -m nhaccu.demo fuzz banjo # chỉ vài cái
python3 -m nhaccu.demo --list     # liệt kê tên
```

## Chữ ký hàm

Đọc docstring từng file là chắc nhất, nhưng phần lớn rơi vào mấy dạng sau:

| dạng | ví dụ | nhạc cụ |
|---|---|---|
| `fn(b_, t0, m, dur, g=…)` | `fuzz(b, 1.0, 'E3', 0.9)` | hầu hết nhạc cụ đơn âm |
| `fn(b_, t0, notes, dur, g=…)` | `organ(b, 1.0, ['C3','E3','G3'], 2.0)` | hợp âm: `organ`, `strings_ch`, `wall`, `section`… |
| `fn(b_, t0, m_from, m_to, dur)` | `slidegtr(b, 1.0, 'E3', 'B3', 1.5)` | `slidegtr` |
| `fn(b_, t0, dur=…)` | `gong(b, 1.0)` | gõ một tiếng: `gong`, `washboard`, `bones`, `march_bass` |
| `fn(b_, bar0, cells, …)` | `lead(b, 0, [(0,1,'E3','hey',1.0), …])` | giọng hát; `cells` = `(offset, dur, nốt, âm tiết, vel)` |
| `fn(b_, bar0, cells, chords)` | `choir_satb(b, 0, cells, ['C','G'])` | bè có hoà thanh |
| `fn(P, bar_beat, pat)` | `bar_drums(P, 0, {'K':'K...','S':'....S...'})` | trống |

`t0` tính bằng **giây**, `bar0`/`bar_beat` tính bằng **phách**. Đổi qua lại bằng
`T(beat)` trong `nhaccu._core`.

Cân bằng âm lượng: dùng bảng đo sẵn thay vì chỉnh mò —
`from nhaccu import LVL, lvl` rồi `g=lvl('fuzz', 0.8)`.

## Cấu trúc

```
nhaccu/
  _dsp.py       lọc, envelope, saturation, reverb…  (copy nguyên greeplib/dsp.py)
  _core.py      tempo, nốt ↔ Hz, buffer, humanize   (copy nguyên greeplib/core.py)
  _harmony.py   hợp âm, voicing                     (copy nguyên greeplib/harmony.py)
  _lib/         helper dùng chung, tách theo đúng module gốc để không đụng tên
                (inst, gtr, keys, folk, horns, singer, voice, drums, latin)
  bass/           natbass fretless upright moogbass jugbass BassPlayer pluck walk amp
  guitar/         acgtr nylon jazzbox jangle leadgtr crunch fuzz octafuzz wall
                  tremgtr slidegtr pedalsteel twelve baritone ebow
  keys/           piano pno saloon tack rhodes rhodes_ch wurli clav organ voxorgan
                  combo_organ pipeorgan harmonium accordion melodica mellotron
                  mellotron_flute arp2600 polysynth theremin
  mallet/         vibes marimba bell glass glocken celeste
  string_section/ strings strings_ch pizz
  folk/           banjo banjo_roll fiddle gong washboard bones march_bass fairorgan
  horns/          horn section stabs unison pad
  voice/          sing phon g2p vline vdouble vharm gang spoken oohs choir_satb
                  gospel falsetto_stack preacher crowd lead lead_soft lead_double
  drums/          Kit Performer bar_drums merge mix_kit drum_bus
  percussion/     LatinKit congas bongos clave_23 bossa_clave cascara_pattern
                  mambo_bell samba_perc partido_alto baiao bossa_perc songo guaguanco
  fx/             riser drop clap_track stomp_track
  demo.py         render thử mỗi nhạc cụ một file wav
```

Quy tắc đặt helper: hàm phụ chỉ một nhạc cụ dùng thì nằm luôn trong file nhạc cụ
đó; từ hai nhạc cụ trở lên thì vào `_lib/<module gốc>.py`. Tách `_lib` theo module
gốc chứ không gộp một file, vì `geeselib/gtr.py`, `geeselib/keys.py` và
`geeselib/folk.py` đều có một biến tên `_T` với nội dung khác nhau — gộp lại thì
cái sau đè cái trước và `banjo` sẽ đi tra bảng của `fuzz`.

## Đã đối chiếu

`tools/verify_against_source.py` gọi từng nhạc cụ ở cả hai bên (repo gốc và
`nhaccu/`) với cùng seed rồi so tổng biên độ, đỉnh và số mẫu khác 0:

```
giống: 91 | khác: 0 | bỏ qua: 11 (class/chữ ký lạ) | lỗi giống nhau cả hai bên: 4
```

Chạy lại: `PYTHONHASHSEED=0 python3 tools/verify_against_source.py`

**Phải đặt `PYTHONHASHSEED=0`.** `horn()` trong repo gốc lấy seed từ
`hash(voice) % 1000`, mà Python băm chuỗi khác nhau mỗi lần chạy — nên `horn` và
`section` cho kết quả khác nhau giữa hai lần chạy *ngay cả trong repo gốc*. Đây
là tính chất của engine gốc, không phải lỗi khi tách.

## Sinh lại

File trong đây sinh tự động — sửa ở repo gốc rồi tách lại, đừng sửa tay:

```bash
python3 tools/extract_instruments.py
```

Script phân tích AST của `greeplib/` và `geeselib/`, lần theo phụ thuộc của từng
hàm, rồi ghi ra từng file kèm đúng các lệnh `import` cần thiết (kể cả những lệnh
`import` nằm bên trong thân hàm, vốn phải viết lại đường dẫn).
