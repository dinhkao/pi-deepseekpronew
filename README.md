# Revolver Sessions — 10 bài hát lấy cảm hứng từ album *Revolver* (Beatles, 1966)

Mỗi bài là một folder `songs/songXX_*/` chứa modules Python tự chạy được.
Output trong `output/songXX_*/`: **mp3** (có hát), **mp3 instrumental**, **zip**
(modules Python). Nghiên cứu hòa âm đầy đủ trong [`RESEARCH.md`](RESEARCH.md).

## 10 bài

| # | Bài | DNA từ Revolver | Key/Tempo | Gimmick riêng |
|---|-----|-----------------|-----------|---------------|
| 1 | The Collector | Taxman | D Mixolydian, 132 | Không có hợp âm V; bass ostinato răng cưa; stab D maj/min; count-in; tăng dần tambourine→cowbell→bè "Collector!" |
| 2 | Paper Face | Eleanor Rigby | E Dorian, 104 | KHÔNG trống — string octet 4 bè; inner voice xuống nửa cung D-C#-C-B; mở đầu VI-i; appoggiatura 6-5 |
| 3 | Half-Dream Morning | I'm Only Sleeping | E minor, 96 | Guitar solo chơi NGƯỢC (render xuôi rồi đảo); refrain chord-stream G-Am-Bm-Am-Cmaj7; verse 9 ô nhịp; vamp "dừng thời gian"; falsetto "oo-doo" |
| 4 | Raga for the Restless | Love You To | C Dorian, 104 | Drone C + sitar + tanpura + tabla (nhạc cụ tự tổng hợp thêm); nhịp 3/4 chèn giữa 4/4; intro out-of-tempo; call-and-response |
| 5 | Every Little Window | Here, There and Everywhere | G major, 86 | Intro G-B♭ (♭III bất ngờ); hợp âm F#m7♭5; bridge deceptive sang B♭/Gm; bè "ooh"; finger snaps; plagal ending |
| 6 | Under the Orange Sea | Yellow Submarine | G major, 112 | Gang chorus đồng ca; hiệu ứng sóng/party/ban nhạc diễu hành chơi LỆCH hợp âm/tiếng tàu ngầm; mở đầu in-medias-res; echo thuyền trưởng |
| 7 | She Never Said | She Said She Said | B♭ Mixolydian, 124 | Chỉ 4 hợp âm cả bài; break đổi nhịp 4+4 / 3+3+3 / 6+3 / 6+3; nén nặng (limiting); organ trộn rất nhỏ; coda canon 8ths đều |
| 8 | Sunshower Sunday | Good Day Sunshine | A major, 120 | Chuỗi V-of-V (A-F#7-B7-E7); refrain nhấn 3+3+2; intro E open-fifth cơ học; piano solo pivot sang D; coda F7 LÊN NỬA CUNG + echo thác đổ |
| 9 | Perpetual Motion | And Your Bird Can Sing + For No One | E major, 138 | Riff baroque even-8ths 2 guitar quãng 3/6; bridge bass chromatic đi xuống; horn solo kiểu For No One (french horn + tack piano + walking bass); kết IV 6/4 bất ngờ |
| 10 | The Long Goodbye | Tomorrow Never Knows + Got To Get You Into My Life | C (drone), 110 | MỘT hợp âm C + B♭; trống syncopate "three-and"; tape-loop ostinato C-D-E-F-E-C; brass stabs; bass chromatic descent B-B♭-A-G#; giọng Leslie từ nửa sau; beep giữa bài; outro tan rã + tack piano |

## Quy trình kiểm tra tone (mỗi bài, trước khi render)

1. **Audit hòa âm** (`audit` trong `songs/_engine.py`): từng nốt hát phải nằm
   trong scale + hợp âm đang chơi; nốt nhấn trên downbeat phải là chord tone
   (hoặc tension được khai báo: ♭7, sus4, added-6th kiểu Beatles); bass phải
   là root.
2. **Audit f0** (`audit_vocal_f0`): sau khi render giọng hát, đo năng lượng
   FFT của từng nốt — phải tập trung đúng tần số dự kiến (±4.5%).
3. **Gemini nghe thử** (`songs/_listen.py`): AI nghe file cuối, kiểm chứng
   không lệch tone + nhận xét mix.

Kết quả cuối: **cả 10 bài audit sạch 100%** (0 nốt ngoài scale, 0 nốt lệch
f0), Gemini xác nhận không lệch tone ở các bài đã review.

## Chạy lại

```bash
python3 songs/song01_the_collector/main.py   # vd; thay số 01..10
# -> output/songXX_*/songXX_*.mp3 (+ _instr.mp3 + .zip)
```

Yêu cầu: Python 3.14 + numpy + scipy + ffmpeg (encode mp3). Thư viện nhạc cụ
`nhaccu/` (106 nhạc cụ từ geese-3d-country) + `songs/_sitar.py` (sitar,
tanpura, tabla bổ sung cho bài 4).

## Cấu trúc

```
nhaccu/            thư viện nhạc cụ (106 instruments)
songs/
  _engine.py       mix stereo 1966, master, audit tone, encode mp3, zip
  _sitar.py        sitar + tanpura + tabla (bài 4)
  _listen.py       gửi mp3 cho Gemini nhận xét
  song01..10/      mỗi bài: song.py (sáng tác) + main.py (render)
output/song01..10/ mp3 + instrumental + zip của từng bài
RESEARCH.md        phân tích hòa âm 14 bài Revolver (Alan Pollack)
```
