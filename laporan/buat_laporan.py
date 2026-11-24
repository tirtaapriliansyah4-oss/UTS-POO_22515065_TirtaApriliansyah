# -*- coding: utf-8 -*-
"""
Generator Laporan UTS POO - Tirta Apriliansyah (22515065)

Cara pakai (dari dalam folder 'laporan'):
    pip install reportlab pillow
    python buat_laporan.py

- Isi data diri / link pada file config.json (yang kosong tampil sebagai kotak kuning).
- Taruh gambar pada folder gambar/ dengan nama:
      uml_class_diagram.png, skenario_01.png ... skenario_16.png, logo.png (opsional)
  Gambar yang ada otomatis menggantikan kotak kosong. Jalankan ulang skrip setiap ada perubahan.
- Potongan kode di Bab 3 dan Bab 4 dibaca langsung dari ../src/hotel/*.java.
"""
import json
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Flowable, Frame, Image,
                                KeepTogether, NextPageTemplate, PageBreak,
                                PageTemplate, Paragraph, Preformatted, Spacer,
                                Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

BASE = Path(__file__).resolve().parent
SRC = BASE.parent / "src" / "hotel"
IMG = BASE / "gambar"
OUT = BASE / "Laporan_UTS-POO_22515065_TirtaApriliansyah.pdf"

# ------------------------------------------------------------------ konfigurasi
PLACEHOLDER = {
    "universitas": "NAMA UNIVERSITAS",
    "fakultas": "NAMA FAKULTAS",
    "prodi": "NAMA PROGRAM STUDI",
    "kelas": "kelas Anda",
    "github_url": "link repositori GitHub",
    "commit_hash": "hash commit terakhir (git rev-parse --short HEAD)",
    "video_url": "link video demo",
    "kota": "kota",
    "tanggal": "tanggal pengumpulan",
    "lingkungan_uji": "sistem operasi dan versi JDK yang Anda pakai",
}
cfg = {k: "" for k in PLACEHOLDER}
if (BASE / "config.json").exists():
    cfg.update(json.loads((BASE / "config.json").read_text(encoding="utf-8")))

NAMA, NIM = "Tirta Apriliansyah", "22515065"
DOSEN = "Muhammad Avied Bachmid, S.Kom., M.Kom."
JUDUL = "APLIKASI MANAJEMEN HOTEL MINI BERBASIS CONSOLE JAVA"


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def F(key):
    """Nilai config; bila kosong tampil sebagai penanda kuning [ISI: ...]."""
    v = str(cfg.get(key, "")).strip()
    if v:
        return esc(v)
    return '<font backColor="#FFF200">[ISI: %s]</font>' % PLACEHOLDER[key]


# ------------------------------------------------------------------ gaya
TNR, TNRB, TNRI, TNRBI = "Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic"
BODY = ParagraphStyle("BODY", fontName=TNR, fontSize=11, leading=16.5,
                      alignment=TA_JUSTIFY, spaceAfter=6)
BODYL = ParagraphStyle("BODYL", parent=BODY, alignment=TA_LEFT)
H1 = ParagraphStyle("H1", fontName=TNRB, fontSize=14, leading=19,
                    alignment=TA_CENTER, spaceAfter=16)
H2 = ParagraphStyle("H2", fontName=TNRB, fontSize=12, leading=16,
                    spaceBefore=12, spaceAfter=6, keepWithNext=1)
H3 = ParagraphStyle("H3", fontName=TNRBI, fontSize=11, leading=15,
                    spaceBefore=8, spaceAfter=4, keepWithNext=1)
CAP = ParagraphStyle("CAP", fontName=TNRB, fontSize=9.5, leading=12,
                     alignment=TA_CENTER, spaceBefore=4, spaceAfter=8)
CAPTOP = ParagraphStyle("CAPTOP", parent=CAP, spaceBefore=8, spaceAfter=4)
TD = ParagraphStyle("TD", fontName=TNR, fontSize=9, leading=11.2, alignment=TA_LEFT)
TH = ParagraphStyle("TH", fontName=TNRB, fontSize=9, leading=11.2, alignment=TA_CENTER)
TDC = ParagraphStyle("TDC", parent=TD, alignment=TA_CENTER)
BUL = ParagraphStyle("BUL", parent=BODY, leftIndent=20, bulletIndent=6, spaceAfter=3)
NOTE = ParagraphStyle("NOTE", fontName=TNRI, fontSize=9.5, leading=13, spaceAfter=6)
CODE = ParagraphStyle("CODE", fontName="Courier", fontSize=7.8, leading=9.4)
COVER_T = ParagraphStyle("COVER_T", fontName=TNRB, fontSize=17, leading=23, alignment=TA_CENTER)
COVER_S = ParagraphStyle("COVER_S", fontName=TNRB, fontSize=13, leading=18, alignment=TA_CENTER)
COVER_N = ParagraphStyle("COVER_N", fontName=TNR, fontSize=12, leading=17, alignment=TA_CENTER)

W = 15.5 * cm  # lebar area teks


def P(t, style=BODY):
    return Paragraph(t, style)


def B(items, style=BUL):
    return [Paragraph(i, style, bulletText="\u2022") for i in items]


def N(items, style=BUL):
    return [Paragraph(t, style, bulletText="%d." % (k + 1)) for k, t in enumerate(items)]


class Heading(Paragraph):
    def __init__(self, text, style, level, toc_text=None):
        Paragraph.__init__(self, text, style)
        self.level, self.toc_text = level, toc_text


def h1(num, title, toc=True):
    text = ("BAB %s<br/>%s" % (num, title)) if num else title
    return Heading(text, H1, 0, ("BAB %s  %s" % (num, title)) if (num and toc) else (title if toc else None))


def h2(t):
    return Heading(t, H2, 1, t)


def h3(t):
    return Paragraph(t, H3)


def cell(c, style=TD):
    return Paragraph(esc(c), style) if isinstance(c, str) else c


def table(header, rows, widths, center_cols=(), zebra=True):
    data = [[Paragraph(esc(h), TH) for h in header]]
    for r in rows:
        data.append([cell(c, TDC if i in center_cols else TD) for i, c in enumerate(r)])
    t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1)
    st = [("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#555555")),
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9D9D9")),
          ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
    if zebra:
        for i in range(2, len(data), 2):
            st.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F6F6F6")))
    t.setStyle(TableStyle(st))
    return t


def tabel(no, judul, header, rows, widths, center_cols=()):
    cap = Paragraph("Tabel %s %s" % (no, esc(judul)), CAPTOP)
    tb = table(header, rows, widths, center_cols)
    if len(rows) <= 9:   # tabel kecil: jaga agar tidak terpotong antarhalaman
        return [KeepTogether([cap, tb]), Spacer(1, 8)]
    return [CondPageBreak(3.5 * cm), cap, tb, Spacer(1, 8)]


# ------------------------------------------------------------------ potongan kode
def wrap_code(lines, limit=88):
    out = []
    for ln in lines:
        ln = ln.replace("\t", "    ")
        if len(ln) <= limit:
            out.append(ln)
            continue
        indent = len(ln) - len(ln.lstrip())
        cur = ln
        first = True
        while len(cur) > limit:
            cut = cur.rfind(" ", indent + 8, limit)
            if cut == -1:
                cut = limit
            out.append(cur[:cut])
            cur = " " * (indent + 8) + cur[cut:].lstrip()
            first = False
        out.append(cur)
    return out


def java_method(filename, signature):
    path = SRC / filename
    if not path.exists():
        return "// [file %s tidak ditemukan]" % filename
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, ln in enumerate(lines):
        if signature in ln:
            depth, started, j = 0, False, i
            while j < len(lines):
                depth += lines[j].count("{") - lines[j].count("}")
                started = started or "{" in lines[j]
                if started and depth <= 0:
                    break
                j += 1
            block = lines[i:j + 1]
            ind = len(block[0]) - len(block[0].lstrip())
            return "\n".join(wrap_code([b[ind:] for b in block]))
    return "// [potongan '%s' tidak ditemukan di %s]" % (signature, filename)


def code(text, chunk=14):
    """Blok kode berlatar abu-abu; dipecah per 14 baris agar boleh pindah halaman."""
    lines = text.split("\n")
    rows = [[Preformatted("\n".join(lines[i:i + chunk]), CODE)] for i in range(0, len(lines), chunk)]
    t = Table(rows, colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F3F3")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#9A9A9A")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("TOPPADDING", (0, 0), (-1, 0), 5), ("BOTTOMPADDING", (0, -1), (-1, -1), 5),
    ]))
    return [t, Spacer(1, 10)]


def jmeth(filename, *sigs):
    return code("\n\n".join(java_method(filename, s) for s in sigs))


def count_lines(name):
    p = SRC / name
    return len(p.read_text(encoding="utf-8").splitlines()) if p.exists() else 0


# ------------------------------------------------------------------ flowable khusus
class Placeholder(Flowable):
    def __init__(self, w, h, title, hint=""):
        Flowable.__init__(self)
        self.w, self.h, self.title, self.hint = w, h, title, hint
        self.hAlign = "CENTER"

    def wrap(self, aw, ah):
        return self.w, self.h

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(colors.HexColor("#FFFDEB"))
        c.setStrokeColor(colors.HexColor("#8A8A8A"))
        c.setDash(5, 3)
        c.setLineWidth(1)
        c.rect(0, 0, self.w, self.h, stroke=1, fill=1)
        c.setDash()
        c.setFillColor(colors.HexColor("#7A6A00"))
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(self.w / 2, self.h / 2 + 6, self.title)
        c.setFont("Helvetica", 8.5)
        c.setFillColor(colors.HexColor("#555555"))
        y = self.h / 2 - 8
        for ln in self.hint.split("\n"):
            c.drawCentredString(self.w / 2, y, ln)
            y -= 11
        c.restoreState()


def figure(filename, w, h, title, hint=""):
    path = IMG / filename
    if path.exists():
        iw, ih = ImageReader(str(path)).getSize()
        r = min(w / iw, h / ih)
        im = Image(str(path), width=iw * r, height=ih * r)
        im.hAlign = "CENTER"
        return im
    return Placeholder(w, h, title, hint)


class StackFigure(Flowable):
    """Gambar 4.1: tiga keadaan stack (kapasitas 5)."""
    states = [
        (["RSV-001", "RSV-002", "RSV-003"], "(a) Setelah 3 kali push"),
        (["RSV-001", "RSV-002"], "(b) Setelah 1 kali pop"),
        (["RSV-001", "RSV-002", "RSV-004", "RSV-005", "RSV-006"], "(c) Stack penuh"),
    ]

    def __init__(self):
        Flowable.__init__(self)
        self.w, self.h = W, 5.6 * cm
        self.hAlign = "CENTER"

    def wrap(self, aw, ah):
        return self.w, self.h

    def draw(self):
        c = self.canv
        col_w = self.w / 3
        slot_h, slot_w = 0.72 * cm, 2.5 * cm
        for s, (items, label) in enumerate(self.states):
            x0 = s * col_w + 0.7 * cm
            for i in range(5):
                y = 1.2 * cm + i * slot_h
                c.setLineWidth(0.8)
                c.setStrokeColor(colors.black)
                if i < len(items):
                    c.setFillColor(colors.HexColor("#CFE4FA"))
                    c.rect(x0, y, slot_w, slot_h, stroke=1, fill=1)
                    c.setFillColor(colors.black)
                    c.setFont("Helvetica-Bold", 8.5)
                    c.drawCentredString(x0 + slot_w / 2, y + 0.23 * cm, items[i])
                else:
                    c.setFillColor(colors.white)
                    c.setDash(2, 2)
                    c.rect(x0, y, slot_w, slot_h, stroke=1, fill=1)
                    c.setDash()
                    c.setFillColor(colors.HexColor("#999999"))
                    c.setFont("Helvetica-Oblique", 7.5)
                    c.drawCentredString(x0 + slot_w / 2, y + 0.23 * cm, "(kosong)")
                c.setFillColor(colors.black)
                c.setFont("Helvetica", 7.5)
                c.drawRightString(x0 - 0.12 * cm, y + 0.23 * cm, str(i))
            ty = 1.2 * cm + (len(items) - 1) * slot_h + 0.23 * cm
            c.setFont("Helvetica-Bold", 7.5)
            c.setFillColor(colors.HexColor("#B00020"))
            c.drawString(x0 + slot_w + 0.15 * cm, ty, "<- top = %d" % (len(items) - 1))
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 8.5)
            c.drawCentredString(x0 + slot_w / 2, 0.45 * cm, label)
        c.setFont("Helvetica-Oblique", 7.5)
        c.drawString(0, 0.02 * cm, "Angka di kiri kotak = indeks array. Kapasitas = 5.")


# ------------------------------------------------------------------ dokumen + TOC
class Doc(BaseDocTemplate):
    def afterFlowable(self, fl):
        if isinstance(fl, Heading) and fl.toc_text:
            self.notify("TOCEntry", (fl.level, fl.toc_text, self.page))


def on_main(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Italic", 9)
    canvas.setFillColor(colors.HexColor("#444444"))
    canvas.drawString(3 * cm, A4[1] - 1.6 * cm, "Laporan UTS Object Oriented Programming")
    canvas.drawRightString(A4[0] - 2.5 * cm, A4[1] - 1.6 * cm, "%s - %s" % (NAMA, NIM))
    canvas.setStrokeColor(colors.HexColor("#999999"))
    canvas.setLineWidth(0.5)
    canvas.line(3 * cm, A4[1] - 1.75 * cm, A4[0] - 2.5 * cm, A4[1] - 1.75 * cm)
    canvas.setFont("Times-Roman", 10)
    canvas.setFillColor(colors.black)
    canvas.drawCentredString(A4[0] / 2 + 0.25 * cm, 1.2 * cm, str(doc.page))
    canvas.restoreState()


def build_doc(path):
    doc = Doc(str(path), pagesize=A4, leftMargin=3 * cm, rightMargin=2.5 * cm,
              topMargin=2.5 * cm, bottomMargin=2.3 * cm,
              title="Laporan UTS POO - %s (%s)" % (NAMA, NIM), author=NAMA,
              subject="Aplikasi Manajemen Hotel Mini - ADT Stack")
    fr = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f", leftPadding=0,
               rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="cover", frames=[fr]),
                          PageTemplate(id="main", frames=[fr], onPage=on_main)])
    return doc


# ================================================================== ISI LAPORAN
story = []

# ------------------------------------------------------------------ SAMPUL
def cover():
    s = []
    s.append(P("LAPORAN UJIAN TENGAH SEMESTER", COVER_S))
    s.append(P("OBJECT ORIENTED PROGRAMMING", COVER_S))
    s.append(Spacer(1, 1.0 * cm))
    s.append(P(JUDUL, COVER_T))
    s.append(Spacer(1, 0.3 * cm))
    s.append(P("Penerapan Class, Enkapsulasi, Relasi Antarobjek, dan<br/>Abstract Data Type Stack",
               ParagraphStyle("cs", parent=COVER_N, fontName=TNRI)))
    s.append(Spacer(1, 0.9 * cm))
    s.append(figure("logo.png", 4 * cm, 4 * cm, "LOGO KAMPUS", "(opsional)\ngambar/logo.png"))
    s.append(Spacer(1, 0.9 * cm))
    rows = [
        ("Nama", NAMA), ("NIM", NIM), ("Kelas", F("kelas")),
        ("Topik", "Hotel (digit terakhir NIM = 5)"),
        ("ADT", "Stack (digit ke-2 dari belakang = 6; 6 mod 3 = 0)"),
        ("Dosen Pengampu", DOSEN),
        ("Repositori GitHub", F("github_url")),
        ("Hash commit terakhir", F("commit_hash")),
    ]
    data = [[Paragraph("<b>%s</b>" % k, ParagraphStyle("k", fontName=TNR, fontSize=11, leading=14)),
             Paragraph(":", TD),
             Paragraph(v if "<font" in v else esc(v),
                       ParagraphStyle("v", fontName=TNR, fontSize=11, leading=14))]
            for k, v in rows]
    t = Table(data, colWidths=[4.2 * cm, 0.5 * cm, 10.8 * cm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    s.append(t)
    s.append(Spacer(1, 1.6 * cm))
    for k in ("fakultas", "prodi", "universitas"):
        s.append(P("<b>%s</b>" % (F(k) if not cfg.get(k) else esc(str(cfg[k]).upper())), COVER_S))
    s.append(P("<b>2026</b>", COVER_S))
    return s


story += cover()
story += [NextPageTemplate("main"), PageBreak()]

# ------------------------------------------------------------------ DAFTAR ISI
story.append(h1(None, "DAFTAR ISI", toc=False))
toc = TableOfContents()
toc.levelStyles = [
    ParagraphStyle("T0", fontName=TNRB, fontSize=11, leading=15, spaceBefore=7, leftIndent=0),
    ParagraphStyle("T1", fontName=TNR, fontSize=10.5, leading=14, leftIndent=18),
]
story += [toc, PageBreak()]

# ================================================================== BAB 1
story.append(h1("1", "PENDAHULUAN DAN ANALISIS OOP"))
story.append(h2("1.1 Latar Belakang dan Deskripsi Sistem"))
story.append(P(
    "Hotel berskala kecil sering mencatat kamar, tamu, dan pemesanan secara manual pada buku atau lembar kerja. "
    "Pencatatan seperti ini mudah menimbulkan kesalahan: satu kamar dapat tercatat dipesan dua kali, biaya menginap "
    "salah dihitung, dan pembatalan pemesanan terakhir sulit ditelusuri. Project ini membangun aplikasi console "
    "berbasis Java bernama <b>Aplikasi Manajemen Hotel Mini</b> untuk mengatasi masalah tersebut dengan pendekatan "
    "pemrograman berorientasi objek (Object Oriented Programming, OOP)."))
story.append(P(
    "Melalui menu console, pengguna (misalnya resepsionis) dapat menambah dan menampilkan kamar, menambah dan "
    "menampilkan tamu, membuat reservasi yang menghubungkan tamu dengan kamar, mencari data, melakukan check-out, "
    "membatalkan reservasi terakhir menggunakan ADT Stack, dan melihat laporan ringkasan. Seluruh data disimpan di "
    "memori selama program berjalan. Sesuai ketentuan UTS, aplikasi tidak memakai database, GUI, maupun framework."))

story.append(h2("1.2 Penentuan Topik dan ADT Berdasarkan NIM"))
story.append(P("Topik dan ADT ditentukan dari NIM penulis, yaitu <b>22515065</b>, dengan perhitungan pada Tabel 1.1."))
story += tabel("1.1", "Penentuan topik dan ADT dari NIM", ["Langkah", "Perhitungan", "Hasil"], [
    ["Digit terakhir NIM", "NIM 22515065, digit terakhir = 5", "Topik: Hotel"],
    ["Digit kedua dari belakang", "NIM 22515065, digit kedua dari belakang = 6", "6 mod 3 = 0"],
    ["Pemetaan sisa bagi", "Sisa 0 sesuai tabel tugas", "ADT: Stack"],
    ["Class wajib topik Hotel", "Ditentukan soal", "Kamar, Tamu, Reservasi, Hotel"],
    ["Aturan wajib topik Hotel", "Ditentukan soal", "Kamar terisi tidak bisa dipesan; biaya = tarif x malam"],
    ["Penggunaan ADT Stack", "Ditentukan soal", "Riwayat reservasi terakhir (batalkan reservasi terakhir)"],
], [4.0, 6.0, 5.5])

story.append(h2("1.3 Ruang Lingkup dan Batasan"))
story += B([
    "Aplikasi berjalan pada console (terminal) dan berinteraksi lewat menu bernomor.",
    "Data disimpan di memori (ArrayList dan array); data hilang ketika program ditutup.",
    "Kapasitas riwayat reservasi (stack) dibatasi 5 elemen sebagai contoh kondisi penuh.",
    "Pewarisan (inheritance) dan polimorfisme tidak diterapkan karena di luar cakupan UTS ini.",
])

story.append(h2("1.4 Daftar Objek dan Class"))
story.append(P("Objek dunia nyata pada sistem hotel dipetakan menjadi class sebagaimana pada Tabel 1.2."))
story += tabel("1.2", "Pemetaan objek dunia nyata menjadi class", ["No", "Class", "Objek dunia nyata", "Alasan dijadikan class", "Jenis"], [
    ["1", "Kamar", "Kamar fisik yang disewakan", "Punya data (nomor, tipe, tarif, kapasitas, status) dan perilaku (dipesan, dikosongkan, dihitung biayanya)", "Entitas"],
    ["2", "Tamu", "Orang yang memesan dan menginap", "Punya identitas dan riwayat menginap yang menentukan kategori tamu", "Entitas"],
    ["3", "Reservasi", "Transaksi pemesanan kamar", "Menghubungkan Tamu dan Kamar; punya lama menginap, tanggal, status, dan biaya", "Entitas"],
    ["4", "Hotel", "Pengelola hotel", "Memegang seluruh kamar, tamu, reservasi, dan menegakkan aturan bisnis", "Entitas"],
    ["5", "StackRiwayat", "Tumpukan catatan reservasi", "Struktur data LIFO untuk membatalkan reservasi paling akhir", "ADT"],
    ["6", "Main", "Resepsionis / pengguna", "Menangani menu dan input pengguna, bukan aturan bisnis", "Antarmuka"],
    ["7", "FormatUtil", "(alat bantu)", "Memformat rupiah dan tanggal agar tidak ditulis berulang", "Utilitas"],
], [0.8, 2.3, 3.2, 7.4, 1.8], center_cols=(0, 4))

story.append(h2("1.5 Aturan Bisnis"))
story.append(P(
    "Dua aturan pertama pada Tabel 1.3 adalah <i>invariant</i> wajib untuk topik Hotel. Aturan lainnya adalah "
    "validasi tambahan agar data tetap masuk akal. Setiap pelanggaran memunculkan pesan yang jelas tanpa menghentikan program."))
story += tabel("1.3", "Aturan bisnis dan lokasi penerapannya", ["Kode", "Aturan", "Lokasi di kode", "Pesan saat dilanggar"], [
    ["AB-1", "Kamar yang terisi tidak bisa dipesan (WAJIB)", "Kamar.pesan(), Hotel.buatReservasi()", "Kamar 101 sedang terisi dan tidak dapat dipesan."],
    ["AB-2", "Biaya = tarif per malam x jumlah malam (WAJIB)", "Kamar.hitungBiaya(), Reservasi.hitungBiaya()", "-"],
    ["AB-3", "Tarif per malam harus lebih dari 0", "Kamar.setTarifPerMalam()", "Tarif per malam harus lebih dari 0."],
    ["AB-4", "Jumlah malam 1 sampai 30", "Reservasi.setJumlahMalam()", "Jumlah malam harus lebih dari 0."],
    ["AB-5", "Umur tamu 17 sampai 120 tahun", "Tamu.setUmur()", "Umur tamu harus antara 17 sampai 120 tahun."],
    ["AB-6", "Nomor telepon 8-15 digit angka", "Tamu.setNoTelepon()", "Nomor telepon harus berupa angka 8 sampai 15 digit."],
    ["AB-7", "Kapasitas kamar 1 sampai 6 orang", "Kamar.setKapasitas()", "Kapasitas kamar harus antara 1 sampai 6 orang."],
    ["AB-8", "Nomor kamar dan kode tamu tidak boleh kembar", "Hotel.tambahKamar(), Hotel.tambahTamu()", "Nomor kamar X sudah terdaftar."],
    ["AB-9", "Reservasi baru ditolak bila stack riwayat penuh", "Hotel.buatReservasi()", "Riwayat reservasi (stack) penuh, kapasitas 5. ..."],
    ["AB-10", "Hanya reservasi berstatus AKTIF yang bisa dibatalkan / check-out", "Reservasi.batalkan(), checkOut()", "Reservasi RSV-001 berstatus ... sehingga tidak dapat dibatalkan."],
], [1.2, 5.0, 4.6, 4.7], center_cols=(0,))

story.append(h2("1.6 Perbandingan Pendekatan Prosedural dan OOP"))
story.append(P(
    "Pada pendekatan prosedural, data kamar biasanya disimpan sebagai beberapa array terpisah (array paralel) dan "
    "dioperasikan oleh fungsi-fungsi lepas. Aturan \"kamar terisi tidak boleh dipesan\" harus diingat dan ditulis ulang "
    "di setiap fungsi yang menyentuh data tersebut. Cuplikan berikut menunjukkan celahnya."))
story.extend(code(
    "// PROSEDURAL: data tersebar di array paralel\n"
    "String[]  nomorKamar = new String[50];\n"
    "double[]  tarif      = new double[50];\n"
    "boolean[] terisi     = new boolean[50];\n\n"
    "static void pesanKamar(int idx) {\n"
    "    if (terisi[idx]) { System.out.println(\"Kamar terisi\"); return; }\n"
    "    terisi[idx] = true;\n"
    "}\n"
    "// Celah: bagian program lain bebas menulis terisi[3] = true / tarif[3] = -5\n"
    "// tanpa melewati pengecekan apa pun."))
story.append(P(
    "Pada OOP, data dan aturan dibungkus dalam satu objek. Class <b>Kamar</b> menyimpan data kamar sebagai atribut "
    "<i>private</i> dan hanya dapat diubah melalui method yang sudah memeriksa aturan, sehingga aturan tidak mungkin terlewat."))
story.extend(code(
    "// OOP: aturan melekat pada objek\n"
    "Kamar k = new Kamar(\"101\", \"Standard\", 250000, 2);\n"
    "k.pesan();          // berhasil, kamar menjadi terisi\n"
    "k.pesan();          // dilempar IllegalStateException: kamar sudah terisi\n"
    "// k.terisi = true;  // tidak bisa: atribut private, kode tidak mau dikompilasi"))
story += tabel("1.4", "Perbandingan prosedural dan OOP pada kasus hotel", ["Aspek", "Prosedural", "OOP (project ini)"], [
    ["Penyimpanan data", "Array terpisah per atribut; mudah tidak sinkron", "Satu objek per kamar / tamu / reservasi"],
    ["Penjagaan aturan bisnis", "Tersebar di banyak fungsi, mudah terlewat", "Terpusat dalam class (misal Kamar.pesan())"],
    ["Perlindungan data", "Semua data dapat diubah dari mana saja", "Atribut private, akses lewat getter / setter berisi validasi"],
    ["Penambahan fitur", "Mengubah banyak fungsi dan array", "Menambah method / class; bagian lain tidak terganggu"],
    ["Keterbacaan", "Sulit melihat data mana milik entitas mana", "Class mencerminkan objek nyata: Kamar, Tamu, Reservasi"],
    ["Pengujian", "Harus menguji gabungan fungsi dan data global", "Setiap class dapat diuji sendiri"],
], [3.2, 6.0, 6.3])

story.append(h2("1.7 Abstraksi dan Enkapsulasi"))
story.append(h3("Abstraksi"))
story.append(P(
    "Abstraksi berarti menampilkan hal yang penting saja dan menyembunyikan detail. Pemanggil cukup menulis "
    "<font name=\"Courier\">hotel.buatReservasi(kodeTamu, nomorKamar, malam, tanggal)</font> tanpa perlu tahu bahwa di dalamnya terjadi "
    "pencarian tamu dan kamar, pengecekan ketersediaan, pengecekan stack, pembuatan objek Reservasi, penandaan kamar, dan "
    "push ke stack. Class <b>StackRiwayat</b> juga merupakan abstraksi: pengguna hanya mengenal operasi push, pop, peek, "
    "isEmpty, isFull, dan size, tanpa perlu mengetahui array dan indeks <i>top</i> di dalamnya."))
story.append(h3("Enkapsulasi"))
story.append(P(
    "Enkapsulasi berarti membungkus data dan perilaku dalam satu class serta membatasi akses langsung ke data. "
    "Penerapannya pada project ini:"))
story += B([
    "Semua atribut class dideklarasikan <font name=\"Courier\">private</font>.",
    "Akses data lewat getter dan setter; setter memvalidasi nilai (misalnya tarif harus lebih dari 0).",
    "Konstruktor berparameter memanggil setter sehingga objek tidak pernah terbentuk dengan nilai tidak valid.",
    "Hotel mengembalikan daftar kamar, tamu, dan reservasi sebagai <i>unmodifiableList</i> (hanya-baca) agar tidak diubah dari luar.",
    "Isi array di dalam StackRiwayat tersembunyi; hanya dapat diubah melalui push, pop, dan clear.",
])
story.append(h3("Dua prinsip OOP lain"))
story.append(P(
    "<b>Pewarisan (inheritance)</b> memungkinkan sebuah class mewarisi atribut dan method class lain, misalnya "
    "tipe kamar khusus yang diturunkan dari Kamar. <b>Polimorfisme</b> memungkinkan satu pemanggilan method "
    "berperilaku berbeda tergantung jenis objeknya, misalnya perhitungan tarif yang berbeda untuk tiap tipe kamar. "
    "Kedua prinsip ini sengaja belum diterapkan karena tidak termasuk cakupan UTS."))

# ================================================================== BAB 2
story.append(PageBreak())
story.append(h1("2", "PERANCANGAN"))
story.append(h2("2.1 Class Diagram"))
story.append(P(
    "Gambar 2.1 memperlihatkan class diagram final. Notasi yang dipakai: tanda <b>-</b> berarti private, "
    "<b>+</b> berarti public; garis dengan belah ketupat hitam menandakan komposisi, belah ketupat putih menandakan "
    "agregasi, panah terbuka menandakan asosiasi, dan panah putus-putus menandakan dependensi. Angka pada ujung garis "
    "adalah <i>multiplicity</i>."))
story.append(figure("uml_class_diagram.png", W, 15.5 * cm, "TEMPEL CLASS DIAGRAM DI SINI",
                    "Gambar dari draw.io / PlantUML (PNG resolusi tinggi)\nSimpan sebagai laporan/gambar/uml_class_diagram.png\n"
                    "Isi: Kamar, Tamu, Reservasi, Hotel, StackRiwayat, Main"))
story.append(Paragraph("Gambar 2.1 Class diagram Aplikasi Manajemen Hotel Mini", CAP))

story.append(h2("2.2 Penjelasan Setiap Class"))
story.append(P("Bagian ini menjelaskan atribut dan method setiap class. Tanda <b>-</b> adalah private, <b>+</b> adalah public. "
               "Method getter dan setter ditulis ringkas dalam satu baris."))

CLASSES = []

CLASSES.append(("2.2.1 Class Kamar", "Mewakili satu kamar fisik hotel. Class ini menjaga aturan AB-1 (kamar terisi tidak bisa dipesan) dan AB-2 (biaya = tarif x malam).",
    [("-", "nomorKamar", "String", "Nomor unik kamar, maksimal 10 karakter"),
     ("-", "tipe", "String", "Standard, Deluxe, atau Suite"),
     ("-", "tarifPerMalam", "double", "Tarif sewa per malam (rupiah), harus lebih dari 0"),
     ("-", "kapasitas", "int", "Jumlah tamu maksimal, 1 sampai 6"),
     ("-", "terisi", "boolean", "true bila kamar sedang terisi"),
     ("+", "TIPE_VALID", "String[]", "Konstanta (static final): daftar tipe yang diizinkan")],
    [("+", "Kamar()", "Konstruktor default: nomor \"000\", Standard, tarif 100000, kapasitas 1"),
     ("+", "Kamar(String nomorKamar, String tipe, double tarifPerMalam, int kapasitas)", "Konstruktor berparameter; setiap nilai divalidasi lewat setter"),
     ("+", "isTersedia() : boolean", "true bila kamar kosong"),
     ("+", "pesan() : void", "Menandai kamar terisi; melempar IllegalStateException bila sudah terisi"),
     ("+", "kosongkan() : void", "Mengosongkan kamar (check-out / pembatalan)"),
     ("+", "hitungBiaya(int jumlahMalam) : double", "Mengembalikan tarif x jumlah malam"),
     ("+", "getStatusTeks() : String", "\"Tersedia\" atau \"Terisi\""),
     ("+", "header() : String  (static)", "Judul kolom tabel daftar kamar"),
     ("+", "tampilkanInfo() : void", "Mencetak satu baris informasi kamar"),
     ("+", "getXxx() / setXxx()", "Getter dan setter semua atribut; setter memvalidasi")]))

CLASSES.append(("2.2.2 Class Tamu", "Mewakili tamu hotel. Total malam menginap dipakai untuk menentukan kategori tamu: Reguler (0 malam), Silver (1-4 malam), Gold (5 malam atau lebih).",
    [("-", "kodeTamu", "String", "Kode unik tamu, disimpan huruf besar (mis. T001)"),
     ("-", "nama", "String", "Nama lengkap, tidak boleh kosong"),
     ("-", "noTelepon", "String", "Angka saja, 8 sampai 15 digit"),
     ("-", "umur", "int", "17 sampai 120 tahun"),
     ("-", "totalMalamMenginap", "int", "Bertambah setiap check-out"),
     ("+", "BATAS_TAMU_SETIA", "int", "Konstanta (static final) = 5 malam")],
    [("+", "Tamu()", "Konstruktor default"),
     ("+", "Tamu(String kodeTamu, String nama, String noTelepon, int umur)", "Konstruktor berparameter dengan validasi"),
     ("+", "tambahMalamMenginap(int malam) : void", "Menambah total malam menginap"),
     ("+", "isTamuSetia() : boolean", "true bila total malam mencapai batas"),
     ("+", "getKategori() : String", "Reguler / Silver / Gold"),
     ("+", "header() : String  (static)", "Judul kolom tabel daftar tamu"),
     ("+", "tampilkanInfo() : void", "Mencetak satu baris informasi tamu"),
     ("+", "getXxx() / setXxx()", "Getter dan setter semua atribut")]))

CLASSES.append(("2.2.3 Class Reservasi", "Transaksi utama yang menghubungkan satu Tamu dengan satu Kamar. Status berubah dari AKTIF menjadi SELESAI (check-out) atau DIBATALKAN (pop stack).",
    [("-", "kodeReservasi", "String", "Kode otomatis, mis. RSV-001"),
     ("-", "tamu", "Tamu", "Relasi asosiasi ke Tamu pemesan"),
     ("-", "kamar", "Kamar", "Relasi asosiasi ke Kamar yang dipesan"),
     ("-", "jumlahMalam", "int", "Lama menginap, 1 sampai 30"),
     ("-", "tanggalCheckIn", "LocalDate", "Tanggal masuk"),
     ("-", "status", "String", "AKTIF, SELESAI, atau DIBATALKAN"),
     ("+", "STATUS_AKTIF / STATUS_SELESAI / STATUS_DIBATALKAN", "String", "Konstanta status (static final)")],
    [("+", "Reservasi()", "Konstruktor default (tamu dan kamar belum terisi)"),
     ("+", "Reservasi(String kode, Tamu tamu, Kamar kamar, int jumlahMalam, LocalDate tanggalCheckIn)", "Konstruktor berparameter dengan validasi"),
     ("+", "hitungBiaya() : double", "Tarif kamar x jumlah malam"),
     ("+", "getTanggalCheckOut() : LocalDate", "Tanggal check-in ditambah jumlah malam"),
     ("+", "isAktif() : boolean", "true bila status AKTIF"),
     ("+", "batalkan() : void", "Status DIBATALKAN dan kamar dikosongkan"),
     ("+", "checkOut() : void", "Status SELESAI, kamar dikosongkan, total malam tamu bertambah"),
     ("+", "header() : String  (static)", "Judul kolom tabel reservasi"),
     ("+", "tampilkanInfo() : void", "Mencetak satu baris reservasi"),
     ("+", "cetakStruk() : void", "Mencetak rincian reservasi"),
     ("+", "getXxx() / setXxx()", "Getter dan setter semua atribut")]))

CLASSES.append(("2.2.4 Class Hotel", "Pengelola utama. Hotel menyimpan seluruh kamar, tamu, dan reservasi, memegang objek StackRiwayat, serta menegakkan aturan bisnis lintas objek.",
    [("-", "namaHotel", "String", "Nama hotel"),
     ("-", "alamat", "String", "Alamat hotel"),
     ("-", "bintang", "int", "Kelas hotel 1 sampai 5"),
     ("-", "daftarKamar", "ArrayList<Kamar>", "Seluruh kamar (komposisi)"),
     ("-", "daftarTamu", "ArrayList<Tamu>", "Seluruh tamu terdaftar (agregasi)"),
     ("-", "daftarReservasi", "ArrayList<Reservasi>", "Seluruh reservasi (komposisi)"),
     ("-", "riwayat", "StackRiwayat", "ADT Stack riwayat reservasi (komposisi)"),
     ("-", "urutanReservasi", "int", "Penghitung untuk kode RSV-001, RSV-002, ...")],
    [("+", "Hotel()", "Konstruktor default (kapasitas riwayat 5)"),
     ("+", "Hotel(String namaHotel, String alamat, int bintang, int kapasitasRiwayat)", "Konstruktor berparameter"),
     ("+", "tambahKamar(Kamar) : void", "Menambah kamar; menolak nomor kembar"),
     ("+", "tambahTamu(Tamu) : void", "Mendaftarkan tamu; menolak kode kembar"),
     ("+", "cariKamar(String) : Kamar", "Mencari kamar menurut nomor"),
     ("+", "cariTamuByKode(String) : Tamu", "Mencari tamu menurut kode"),
     ("+", "cariTamu(String) : List<Tamu>", "Mencari tamu menurut kode atau sebagian nama"),
     ("+", "cariReservasi(String) : Reservasi", "Mencari reservasi menurut kode"),
     ("+", "buatReservasi(String, String, int, LocalDate) : Reservasi", "Membuat reservasi dan PUSH ke stack"),
     ("+", "batalkanReservasiTerakhir() : Reservasi", "POP stack dan membatalkan reservasi"),
     ("+", "checkOut(String) : Reservasi", "Check-out menurut kode reservasi"),
     ("+", "hitungKamarTersedia() / hitungKamarTerisi() : int", "Menghitung kamar kosong / terisi"),
     ("+", "hitungReservasiByStatus(String) : int", "Menghitung reservasi menurut status"),
     ("+", "hitungTotalPendapatan() : double", "Jumlah biaya reservasi tidak dibatalkan"),
     ("+", "hitungTingkatHunian() : double", "Persentase kamar terisi"),
     ("+", "getXxx() / setXxx()", "Getter dan setter; daftar dikembalikan hanya-baca")]))

CLASSES.append(("2.2.5 Class StackRiwayat (ADT Stack)", "Struktur data LIFO berbasis array. Rincian lengkap spesifikasi dan analisisnya ada pada Bab 4.",
    [("-", "data", "Reservasi[]", "Array penyimpan elemen"),
     ("-", "top", "int", "Indeks elemen teratas; -1 berarti kosong"),
     ("-", "kapasitas", "int", "Jumlah elemen maksimal"),
     ("-", "KAPASITAS_DEFAULT", "int", "Konstanta (static final) = 5")],
    [("+", "StackRiwayat()", "Konstruktor default (kapasitas 5)"),
     ("+", "StackRiwayat(int kapasitas)", "Konstruktor berparameter; kapasitas minimal 1"),
     ("+", "push(Reservasi) : boolean", "Menambah ke puncak; false bila penuh"),
     ("+", "pop() : Reservasi", "Mengambil dan menghapus puncak; null bila kosong"),
     ("+", "peek() : Reservasi", "Melihat puncak tanpa menghapus; null bila kosong"),
     ("+", "isEmpty() / isFull() : boolean", "Memeriksa kosong / penuh"),
     ("+", "size() : int", "Jumlah elemen tersimpan"),
     ("+", "getKapasitas() : int", "Kapasitas maksimal"),
     ("+", "clear() : void", "Mengosongkan stack"),
     ("+", "tampilkan() : void", "Mencetak isi dari TOP ke BOTTOM")]))

CLASSES.append(("2.2.6 Class Main", "Titik masuk program. Hanya mengurus menu dan input; semua aturan bisnis berada di class lain.",
    [("-", "KAPASITAS_RIWAYAT", "int", "Konstanta = 5"),
     ("-", "PILIHAN_MAKSIMAL", "int", "Konstanta = 14 (nomor menu terbesar)"),
     ("-", "SCANNER", "Scanner", "Pembaca input keyboard"),
     ("-", "hotel", "Hotel", "Objek hotel yang dikelola")],
    [("+", "main(String[] args) : void", "Membuat Hotel dan menjalankan perulangan menu"),
     ("-", "tampilkanMenu() : void", "Mencetak daftar menu"),
     ("-", "prosesPilihan(int) : boolean", "Memanggil menu terpilih; menangkap exception aturan bisnis"),
     ("-", "menuXxx() : void  (14 method)", "Satu method per menu (tambah kamar, buat reservasi, pop, dll.)"),
     ("-", "bacaTeks(String) : String", "Membaca satu baris teks"),
     ("-", "bacaInt(String) : int", "Membaca bilangan bulat; diulang sampai valid"),
     ("-", "bacaInt(String, int, int) : int", "Overload: bilangan bulat dengan batas min dan maks"),
     ("-", "bacaDouble(String) : double", "Membaca bilangan desimal; diulang sampai valid"),
     ("-", "bacaTanggal(String) : LocalDate", "Membaca tanggal dd-MM-yyyy; diulang sampai valid")]))

CLASSES.append(("2.2.7 Class FormatUtil", "Kelas utilitas dengan method static untuk memformat rupiah dan tanggal. Konstruktornya private karena tidak perlu dibuat objeknya.",
    [("+", "POLA_TANGGAL", "String", "Konstanta \"dd-MM-yyyy\""),
     ("-", "FORMATTER_TANGGAL", "DateTimeFormatter", "Formatter mode STRICT (tanggal tidak ada ditolak)")],
    [("+", "formatRupiah(double) : String  (static)", "350000 menjadi \"Rp 350.000\""),
     ("+", "formatTanggal(LocalDate) : String  (static)", "LocalDate menjadi teks dd-MM-yyyy"),
     ("+", "parseTanggal(String) : LocalDate  (static)", "Teks dd-MM-yyyy menjadi LocalDate")]))

tno = 4
for title, desc, attrs, meths in CLASSES:
    story.append(h3(title))
    story.append(P(desc))
    story += tabel("2.%d" % (tno - 3), "Atribut " + title.split(" ", 1)[1].replace("Class ", "class "),
                   ["Vis", "Atribut", "Tipe", "Keterangan"],
                   [[a, b, c, d] for a, b, c, d in attrs], [1.0, 4.2, 3.3, 7.0], center_cols=(0,))
    tno += 1
    story += tabel("2.%d" % (tno - 3), "Method " + title.split(" ", 1)[1].replace("Class ", "class "),
                   ["Vis", "Method", "Keterangan"],
                   [[a, b, c] for a, b, c in meths], [1.0, 6.7, 7.8], center_cols=(0,))
    tno += 1
# nomor tabel 2.1 ... dihitung otomatis: tno mulai 4 -> 2.1, 2.2, dst.

story.append(h2("2.3 Relasi Antarclass dan Multiplicity"))
story.append(P("Relasi yang membentuk struktur sistem dirangkum pada Tabel 2.15. Kolom terakhir menunjukkan bukti relasi di dalam kode."))
story += tabel("2.15", "Relasi antarclass", ["Relasi", "Jenis", "Multiplicity", "Alasan", "Bukti di kode"], [
    ["Hotel - Kamar", "Komposisi", "1 ke 0..*", "Kamar tidak bermakna tanpa hotel", "Hotel.daftarKamar"],
    ["Hotel - Reservasi", "Komposisi", "1 ke 0..*", "Reservasi dicatat dan dimiliki hotel", "Hotel.daftarReservasi"],
    ["Hotel - Tamu", "Agregasi", "1 ke 0..*", "Tamu orang mandiri yang hanya didaftarkan", "Hotel.daftarTamu"],
    ["Hotel - StackRiwayat", "Komposisi", "1 ke 1", "Stack dibuat dan hilang bersama hotel", "Hotel.riwayat"],
    ["Reservasi - Tamu", "Asosiasi", "banyak ke 1", "Satu tamu dapat memiliki banyak reservasi", "Reservasi.tamu"],
    ["Reservasi - Kamar", "Asosiasi", "banyak ke 1", "Satu kamar dapat muncul di banyak reservasi pada waktu berbeda", "Reservasi.kamar"],
    ["StackRiwayat - Reservasi", "Agregasi", "1 ke 0..*", "Stack menyimpan referensi reservasi", "StackRiwayat.data"],
    ["Main - Hotel", "Dependensi", "-", "Main memakai Hotel untuk semua operasi", "Main.hotel"],
], [3.2, 2.0, 2.0, 5.2, 3.1])

story.append(h2("2.4 Alur Proses Utama"))
story.append(h3("Alur membuat reservasi (menu 5)"))
story += N([
    "Main membaca kode tamu, nomor kamar, jumlah malam, dan tanggal check-in (angka dan tanggal divalidasi sampai benar).",
    "Hotel.buatReservasi() mencari tamu; bila tidak ada, ditolak dengan pesan.",
    "Hotel mencari kamar; bila tidak ada, ditolak dengan pesan.",
    "Hotel memeriksa kamar.isTersedia(); bila terisi, ditolak (aturan AB-1).",
    "Hotel memeriksa riwayat.isFull(); bila penuh, ditolak (aturan AB-9).",
    "Hotel membuat objek Reservasi; konstruktor memvalidasi jumlah malam dan tanggal.",
    "Semua pengecekan lolos: kamar.pesan(), riwayat.push(reservasi), reservasi disimpan di daftarReservasi.",
    "Main mencetak struk beserta total biaya (tarif x malam).",
])
story.append(P("Seluruh pengecekan dilakukan <b>sebelum</b> data diubah, sehingga bila ada penolakan tidak ada perubahan setengah jadi."))
story.append(h3("Alur membatalkan reservasi terakhir (menu 8)"))
story += N([
    "Hotel memeriksa riwayat.isEmpty(); bila kosong, ditolak dengan pesan.",
    "Hotel melakukan riwayat.pop() sehingga mendapat reservasi paling baru (LIFO).",
    "Bila status reservasi bukan AKTIF (misalnya sudah check-out), ditolak dan item dikeluarkan dari riwayat.",
    "Reservasi.batalkan() mengubah status menjadi DIBATALKAN dan mengosongkan kamar sehingga dapat dipesan lagi.",
])

# ================================================================== BAB 3
story.append(PageBreak())
story.append(h1("3", "IMPLEMENTASI"))
story.append(h2("3.1 Lingkungan dan Struktur Project"))
story.append(P("Aplikasi ditulis dengan bahasa Java (JDK 11 atau lebih baru) dan dijalankan melalui terminal di Visual Studio Code. "
               "Nama project dan repositori: <b>UTS-POO_22515065_TirtaApriliansyah</b>. Seluruh class berada dalam package <font name=\"Courier\">hotel</font>."))
story.extend(code(
    "UTS-POO_22515065_TirtaApriliansyah/\n"
    "|-- src/hotel/\n"
    "|   |-- Main.java\n|   |-- Hotel.java\n|   |-- Kamar.java\n|   |-- Tamu.java\n"
    "|   |-- Reservasi.java\n|   |-- StackRiwayat.java\n|   `-- FormatUtil.java\n"
    "|-- tests/          (input skenario pengujian)\n"
    "|-- .gitignore\n`-- README.md"))
story += tabel("3.1", "Daftar file sumber", ["File", "Isi", "Jumlah baris"], [
    ["Main.java", "Menu console dan pembaca input", str(count_lines("Main.java"))],
    ["Hotel.java", "Pengelola dan aturan bisnis", str(count_lines("Hotel.java"))],
    ["Kamar.java", "Entitas Kamar", str(count_lines("Kamar.java"))],
    ["Tamu.java", "Entitas Tamu", str(count_lines("Tamu.java"))],
    ["Reservasi.java", "Entitas Reservasi", str(count_lines("Reservasi.java"))],
    ["StackRiwayat.java", "ADT Stack berbasis array", str(count_lines("StackRiwayat.java"))],
    ["FormatUtil.java", "Format rupiah dan tanggal", str(count_lines("FormatUtil.java"))],
], [4.0, 8.0, 3.5], center_cols=(2,))
story.append(P("Cara menjalankan dari terminal VS Code pada folder root project:"))
story.extend(code("mkdir out\njavac -d out src/hotel/*.java\njava -cp out hotel.Main"))

story.append(h2("3.2 Konstruktor dan Overloading"))
story.append(P(
    "Setiap class entitas memiliki dua konstruktor: <b>konstruktor default</b> (tanpa parameter) dan "
    "<b>konstruktor berparameter</b>. Dua konstruktor dengan nama sama tetapi daftar parameter berbeda disebut "
    "<i>overloading</i>. Konstruktor default memanggil konstruktor berparameter lewat <font name=\"Courier\">this(...)</font> "
    "dengan nilai bawaan yang valid, sedangkan konstruktor berparameter memanggil setter agar semua nilai tervalidasi. "
    "Contoh pada class Kamar:"))
story.extend(jmeth("Kamar.java", "public Kamar() {", "public Kamar(String nomorKamar"))
story.append(P(
    "Overloading juga dipakai pada method: <font name=\"Courier\">bacaInt(String)</font> membaca bilangan bulat bebas, sedangkan "
    "<font name=\"Courier\">bacaInt(String, int, int)</font> membaca bilangan bulat dalam rentang tertentu (dipakai untuk memilih menu)."))
story.extend(jmeth("Main.java", "private static int bacaInt(String prompt) {", "private static int bacaInt(String prompt, int min, int max)"))

story.append(h2("3.3 Siklus Hidup Objek"))
story.append(P(
    "Siklus hidup sebuah objek di aplikasi ini terdiri dari tiga fase. <b>Pembuatan</b>: operator <font name=\"Courier\">new</font> "
    "mengalokasikan objek di memori heap lalu menjalankan konstruktor, yang memvalidasi nilai lewat setter; bila ada nilai tidak valid, "
    "exception dilempar sehingga objek setengah jadi tidak pernah tersimpan. <b>Penggunaan</b>: objek disimpan di ArrayList milik Hotel "
    "(dan referensinya di StackRiwayat) serta berubah status sesuai transaksi. <b>Akhir hidup</b>: ketika tidak ada lagi variabel yang "
    "merujuk objek, Garbage Collector Java membebaskan memorinya. Pada StackRiwayat, saat pop dilakukan, slot array diisi "
    "<font name=\"Courier\">null</font> agar referensi lama tidak tertahan."))
story.append(P("Tabel 3.2 menelusuri siklus hidup satu reservasi dan kamar yang dipesannya."))
story += tabel("3.2", "Perubahan status objek pada sebuah transaksi", ["Peristiwa", "Status Reservasi", "Status Kamar", "Isi Stack"], [
    ["Kamar 101 dibuat (new Kamar)", "-", "Tersedia", "-"],
    ["Menu 5: buat reservasi RSV-001", "AKTIF (objek baru dibuat)", "Terisi (pesan())", "RSV-001 di-push"],
    ["Alternatif A, menu 12: check-out", "SELESAI", "Tersedia (kosongkan())", "RSV-001 tetap di stack"],
    ["Alternatif B, menu 8: batalkan (pop)", "DIBATALKAN", "Tersedia (kosongkan())", "RSV-001 dikeluarkan"],
    ["Menu 11: clear riwayat", "Tidak berubah", "Tidak berubah", "Semua referensi di stack dilepas"],
], [4.8, 3.8, 3.5, 3.4])

story.append(h2("3.4 Enkapsulasi dan Validasi pada Setter"))
story.append(P("Setter tidak sekadar menyalin nilai, tetapi menolak nilai yang melanggar aturan. Contoh pada class Kamar dan Tamu:"))
story.extend(jmeth("Kamar.java", "public void setTarifPerMalam(double tarifPerMalam) {"))
story.extend(jmeth("Tamu.java", "public void setNoTelepon(String noTelepon) {"))
story.append(P("Class Hotel melindungi daftar internalnya dengan mengembalikan salinan hanya-baca:"))
story.extend(jmeth("Hotel.java", "public List<Kamar> getDaftarKamar() {"))

story.append(h2("3.5 Penerapan Aturan Bisnis Wajib"))
story.append(h3("Aturan 1: kamar terisi tidak bisa dipesan"))
story.extend(jmeth("Kamar.java", "public void pesan() {"))
story.append(h3("Aturan 2: biaya = tarif x malam"))
story.extend(jmeth("Kamar.java", "public double hitungBiaya(int jumlahMalam) {"))
story.append(h3("Method transaksi yang menggabungkan seluruh aturan"))
story.append(P("<font name=\"Courier\">Hotel.buatReservasi()</font> melakukan semua pengecekan lebih dulu, baru kemudian mengubah data:"))
story.extend(jmeth("Hotel.java", "public Reservasi buatReservasi("))
story.append(h3("Pembatalan dan status reservasi"))
story.extend(jmeth("Reservasi.java", "public void batalkan() {"))

story.append(h2("3.6 Menu Console dan Penanganan Kesalahan"))
story += tabel("3.3", "Daftar menu aplikasi", ["No", "Menu", "Method di Main", "Operasi utama"], [
    ["1", "Tambah kamar", "menuTambahKamar()", "new Kamar(...), Hotel.tambahKamar()"],
    ["2", "Tampilkan semua kamar", "menuTampilKamar()", "Kamar.tampilkanInfo()"],
    ["3", "Tambah tamu", "menuTambahTamu()", "new Tamu(...), Hotel.tambahTamu()"],
    ["4", "Tampilkan semua tamu", "menuTampilTamu()", "Tamu.tampilkanInfo()"],
    ["5", "Buat reservasi (PUSH)", "menuBuatReservasi()", "Hotel.buatReservasi() lalu push"],
    ["6", "Tampilkan semua reservasi", "menuTampilReservasi()", "Reservasi.tampilkanInfo()"],
    ["7", "Cari data", "menuCari()", "cariKamar / cariTamu / cariReservasi"],
    ["8", "Batalkan reservasi terakhir (POP)", "menuPop()", "Hotel.batalkanReservasiTerakhir()"],
    ["9", "Lihat reservasi terakhir (PEEK)", "menuPeek()", "StackRiwayat.peek()"],
    ["10", "Tampilkan isi stack", "menuTampilStack()", "StackRiwayat.tampilkan()"],
    ["11", "Kosongkan riwayat (CLEAR)", "menuClear()", "StackRiwayat.clear()"],
    ["12", "Check-out tamu", "menuCheckOut()", "Hotel.checkOut()"],
    ["13", "Laporan ringkasan", "menuLaporan()", "hitungTotalPendapatan(), hitungTingkatHunian(), dll."],
    ["14", "Muat data contoh", "menuDataContoh()", "6 kamar dan 3 tamu demo"],
    ["0", "Keluar", "prosesPilihan() mengembalikan false", "Perulangan menu berhenti"],
], [1.0, 4.8, 4.7, 5.0], center_cols=(0,))
story.append(P("Penanganan kesalahan dibagi menurut jenisnya sehingga program tidak pernah berhenti karena input pengguna:"))
story += tabel("3.4", "Jenis kesalahan input dan penanganannya", ["Jenis kesalahan", "Contoh", "Penanganan"], [
    ["Huruf atau kosong pada kolom angka", "Menu: abc; tarif: abc", "Pesan [ERROR] lalu input diminta ulang (bacaInt / bacaDouble)"],
    ["Angka di luar rentang menu", "Menu: 99", "Pesan [ERROR] lalu input diminta ulang"],
    ["Tanggal salah atau tidak ada", "31-02-2026", "Pesan [ERROR] lalu input diminta ulang (formatter STRICT)"],
    ["Teks kosong / nilai melanggar aturan", "Nama kosong, tarif 0, umur 10", "Setter melempar IllegalArgumentException; Main menampilkan [GAGAL]"],
    ["Pelanggaran aturan transaksi", "Kamar terisi, stack penuh", "Hotel melempar IllegalStateException; Main menampilkan [GAGAL]"],
    ["Input berakhir (Ctrl+D)", "-", "NoSuchElementException ditangkap; program berhenti rapi"],
], [4.5, 4.0, 7.0])
story.append(P("Kerangka penanganan exception pada <font name=\"Courier\">prosesPilihan</font> (disingkat):"))
story.extend(code(
    "private static boolean prosesPilihan(int pilihan) {\n"
    "    try {\n"
    "        switch (pilihan) {\n"
    "            case 1: menuTambahKamar(); break;\n"
    "            case 5: menuBuatReservasi(); break;\n"
    "            case 8: menuPop(); break;\n"
    "            // ... menu lainnya ...\n"
    "            case 0: return false;\n"
    "            default: System.out.println(\"[GAGAL] Menu tidak dikenal.\");\n"
    "        }\n"
    "    } catch (IllegalArgumentException | IllegalStateException e) {\n"
    "        System.out.println(\"[GAGAL] \" + e.getMessage());\n"
    "    }\n"
    "    return true;\n"
    "}"))

story.append(h2("3.7 Catatan Kesesuaian dengan Class Diagram"))
story.append(P(
    "Class diagram pada Gambar 2.1 dibuat mengikuti kode ini. Dibandingkan dengan syarat minimal soal, terdapat dua tambahan: "
    "class <b>FormatUtil</b> (utilitas pemformat) dan method tambahan seperti <font name=\"Courier\">clear()</font> pada StackRiwayat "
    "serta <font name=\"Courier\">checkOut()</font> pada Reservasi dan Hotel. Method <font name=\"Courier\">header()</font> bersifat static "
    "dan dipakai untuk judul tabel. Tidak ada penyimpangan lain antara diagram dan kode. "
    "<font backColor=\"#FFF200\">[ISI: bila diagram Anda berbeda dari kode, tulis alasannya di sini]</font>"))

# ================================================================== BAB 4
story.append(PageBreak())
story.append(h1("4", "ADT STACK"))
story.append(h2("4.1 Definisi dan Alasan Pemilihan Stack"))
story.append(P(
    "<b>Abstract Data Type (ADT)</b> adalah model struktur data yang didefinisikan oleh nilai yang disimpan dan operasi yang diizinkan, "
    "terlepas dari cara penyimpanannya. <b>Stack</b> adalah ADT dengan prinsip <b>LIFO (Last In First Out)</b>: elemen yang dimasukkan "
    "paling akhir adalah yang pertama dikeluarkan."))
story.append(P(
    "Stack dipilih (sesuai hasil perhitungan NIM) untuk menyimpan <b>riwayat reservasi</b>. Kebutuhan \"batalkan reservasi terakhir\" "
    "sesuai dengan sifat LIFO: reservasi yang paling baru dibuat adalah yang pertama dibatalkan. Bila dipakai antrean (queue, FIFO), yang "
    "akan keluar lebih dulu justru reservasi paling lama, sehingga tidak sesuai kebutuhan."))
story.append(h2("4.2 Representasi Internal"))
story.append(P(
    "StackRiwayat diimplementasikan dengan <b>array</b> berkapasitas tetap. Tiga atribut private dipakai: "
    "<font name=\"Courier\">data</font> (array Reservasi), <font name=\"Courier\">top</font> (indeks elemen teratas, bernilai -1 saat kosong), "
    "dan <font name=\"Courier\">kapasitas</font>. Stack kosong bila <font name=\"Courier\">top == -1</font> dan penuh bila "
    "<font name=\"Courier\">top == kapasitas - 1</font>. Atribut ini tidak dapat diakses dari luar; pemakai hanya menggunakan operasi publik."))
story.append(h2("4.3 Spesifikasi Operasi"))
story += tabel("4.1", "Spesifikasi operasi ADT Stack", ["Operasi", "Parameter", "Kembalian", "Prasyarat", "Efek"], [
    ["push", "Reservasi r", "boolean", "r bukan null dan stack tidak penuh", "r menjadi elemen teratas, size + 1; false bila penuh atau null"],
    ["pop", "-", "Reservasi", "Stack tidak kosong", "Elemen teratas dihapus, size - 1; null bila kosong"],
    ["peek", "-", "Reservasi", "Stack tidak kosong", "Tidak ada perubahan; null bila kosong"],
    ["isEmpty", "-", "boolean", "-", "true bila size = 0"],
    ["isFull", "-", "boolean", "-", "true bila size = kapasitas"],
    ["size", "-", "int", "-", "Mengembalikan jumlah elemen"],
    ["clear", "-", "void", "-", "Semua elemen dihapus, size = 0"],
    ["tampilkan", "-", "void", "-", "Mencetak isi dari TOP ke BOTTOM (menangani kosong dengan pesan)"],
], [1.9, 2.0, 2.0, 3.6, 6.0])

story.append(h2("4.4 Penanganan Kondisi Batas"))
story += tabel("4.2", "Penanganan stack penuh, kosong, dan null", ["Kondisi", "Operasi", "Perilaku ADT", "Perilaku aplikasi"], [
    ["Stack penuh", "push", "Mengembalikan false tanpa mengubah isi", "Hotel menolak reservasi baru dengan pesan [GAGAL] sebelum data diubah"],
    ["Stack kosong", "pop", "Mengembalikan null", "Hotel melempar pesan \"Riwayat kosong\"; tampil [GAGAL]"],
    ["Stack kosong", "peek", "Mengembalikan null", "Main menampilkan [INFO] Stack kosong"],
    ["Stack kosong", "tampilkan", "Mencetak \"(Stack kosong ...)\"", "Tidak ada error"],
    ["Elemen null", "push", "Mengembalikan false", "Tidak terjadi karena Hotel selalu mengirim objek valid"],
], [2.5, 2.0, 5.0, 6.0])

story.append(h2("4.5 Ilustrasi Cara Kerja"))
story.append(P("Gambar 4.1 menunjukkan tiga keadaan stack berkapasitas 5, sedangkan Tabel 4.3 menelusuri operasi langkah demi langkah."))
story.append(StackFigure())
story.append(Paragraph("Gambar 4.1 Ilustrasi isi stack riwayat reservasi (indeks 0 = dasar, indeks tertinggi = puncak)", CAP))
story += tabel("4.3", "Jejak operasi stack (kapasitas 5)", ["No", "Operasi", "Hasil", "Isi stack (dasar ke puncak)", "top", "size", "isFull"], [
    ["0", "(awal)", "-", "kosong", "-1", "0", "false"],
    ["1", "push RSV-001", "true", "RSV-001", "0", "1", "false"],
    ["2", "push RSV-002", "true", "RSV-001, RSV-002", "1", "2", "false"],
    ["3", "push RSV-003", "true", "RSV-001, RSV-002, RSV-003", "2", "3", "false"],
    ["4", "peek", "RSV-003", "(tidak berubah)", "2", "3", "false"],
    ["5", "pop", "RSV-003", "RSV-001, RSV-002", "1", "2", "false"],
    ["6", "push RSV-004", "true", "RSV-001, RSV-002, RSV-004", "2", "3", "false"],
    ["7", "push RSV-005", "true", "RSV-001, RSV-002, RSV-004, RSV-005", "3", "4", "false"],
    ["8", "push RSV-006", "true", "RSV-001, RSV-002, RSV-004, RSV-005, RSV-006", "4", "5", "true"],
    ["9", "push RSV-007", "false", "(tidak berubah, stack penuh)", "4", "5", "true"],
], [0.8, 2.4, 1.6, 6.0, 1.0, 1.0, 1.4], center_cols=(0, 4, 5, 6))
story.append(P("Pada langkah 6, kode reservasi yang dipush adalah RSV-004 karena RSV-003 sudah dibatalkan oleh pop (penghitung kode hanya bertambah ketika reservasi berhasil dibuat)."))

story.append(h2("4.6 Potongan Kode Implementasi"))
story.extend(jmeth("StackRiwayat.java", "public boolean push(Reservasi reservasi) {", "public Reservasi pop() {",
                   "public Reservasi peek() {", "public boolean isEmpty() {", "public boolean isFull() {"))

story.append(h2("4.7 Hubungan ADT dengan Sistem"))
story += B([
    "<b>Push</b>: dipanggil oleh <font name=\"Courier\">Hotel.buatReservasi()</font> setiap kali reservasi baru berhasil dibuat.",
    "<b>Pop</b>: dipanggil oleh <font name=\"Courier\">Hotel.batalkanReservasiTerakhir()</font> (menu 8) untuk membatalkan reservasi paling baru.",
    "<b>Peek</b>: dipakai menu 9 untuk melihat reservasi terakhir tanpa membatalkannya.",
    "<b>isEmpty / isFull / size</b>: dipakai Hotel dan menu 10 untuk memeriksa kondisi sebelum operasi dan untuk laporan.",
    "<b>Clear</b>: dipakai menu 11 untuk mengosongkan riwayat; data reservasi tetap ada di Hotel tetapi tidak lagi dapat dibatalkan lewat pop.",
])

story.append(h2("4.8 Analisis Kompleksitas"))
story += tabel("4.4", "Kompleksitas waktu dan ruang ADT Stack", ["Operasi", "Waktu", "Alasan"], [
    ["push", "O(1)", "Satu pengecekan penuh dan satu penugasan pada indeks top + 1"],
    ["pop", "O(1)", "Membaca indeks top, mengisi null, dan mengurangi top"],
    ["peek", "O(1)", "Hanya membaca elemen pada indeks top"],
    ["isEmpty, isFull, size", "O(1)", "Hanya membandingkan atau menghitung dari nilai top"],
    ["clear", "O(n)", "Perulangan mengisi null untuk n elemen yang tersimpan"],
    ["tampilkan", "O(n)", "Mencetak n elemen dari puncak ke dasar"],
    ["Ruang (memori)", "O(k)", "Array tetap berukuran kapasitas k; tidak ada penambahan ukuran dinamis"],
], [3.5, 2.0, 10.0], center_cols=(1,))
story.append(P(
    "Seluruh operasi inti stack berjalan konstan, sehingga fitur pembatalan reservasi tidak menambah beban walaupun jumlah reservasi "
    "bertambah. Pencarian pada Hotel (cariKamar, cariTamuByKode, cariReservasi) menggunakan penelusuran linear O(n) yang memadai "
    "untuk skala hotel kecil di memori."))

# ================================================================== BAB 5
story.append(PageBreak())
story.append(h1("5", "PENGUJIAN"))
story.append(h2("5.1 Lingkungan dan Cara Pengujian"))
story.append(P("Pengujian dilakukan secara manual melalui menu console pada lingkungan berikut: %s. "
               "Setiap skenario dapat diulang dengan mengetik langkahnya di menu, atau memutar berkas masukan di folder "
               "<font name=\"Courier\">tests/</font> (contoh: <font name=\"Courier\">Get-Content tests\\input_B.txt | java -cp out hotel.Main</font> "
               "pada PowerShell). Hasil aktual pada Tabel 5.1 adalah keluaran program yang sebenarnya." % F("lingkungan_uji")))

SC = [
 dict(no=1, kat="Normal", nama="Memuat data contoh",
      langkah="Menu 14, lalu menu 2 dan menu 4",
      harap="6 kamar dan 3 tamu terisi", aktual="[BERHASIL] Data contoh dimuat: 6 kamar dan 3 tamu baru.; tabel kamar dan tamu tampil",
      lihat="Pesan BERHASIL, tabel 6 kamar (101, 102, 103, 201, 202, 301) dan tabel 3 tamu (T001-T003)."),
 dict(no=2, kat="Normal", nama="Membuat reservasi",
      langkah="Menu 14; menu 5: T001, 101, 3, 25-11-2026",
      harap="Struk RSV-001 dengan biaya 3 x 250.000", aktual="Total biaya Rp 750.000; check-out 28-11-2026; status AKTIF",
      lihat="Struk reservasi: tamu Budi Santoso, kamar 101, TOTAL BIAYA Rp 750.000."),
 dict(no=3, kat="Normal", nama="Check-out tamu",
      langkah="Menu 14; menu 5: T001, 101, 6, 25-11-2026; menu 12: RSV-001; menu 4",
      harap="Kamar kembali tersedia; kategori tamu naik", aktual="Total bayar Rp 1.500.000; Kategori tamu: Gold (total 6 malam)",
      lihat="Pesan check-out, total bayar Rp 1.500.000, kategori Gold; menu 4 menampilkan total malam 6."),
 dict(no=4, kat="Normal", nama="Mencari tamu berdasarkan nama",
      langkah="Menu 14; menu 7; pilih 2; kata kunci: budi",
      harap="Tamu Budi Santoso ditemukan", aktual="Baris Budi Santoso tampil; Ditemukan: 1 tamu.",
      lihat="Tabel hasil pencarian berisi Budi Santoso dan teks \"Ditemukan: 1 tamu.\""),
 dict(no=5, kat="Pelanggaran aturan", nama="Memesan kamar yang sudah terisi (AB-1)",
      langkah="Menu 14; menu 5: T001, 101, 3, 25-11-2026; menu 5: T002, 101, 2, 26-11-2026",
      harap="Reservasi kedua ditolak", aktual="[GAGAL] Kamar 101 sedang terisi dan tidak dapat dipesan.",
      lihat="Pesan [GAGAL] pada pemesanan kedua; program kembali ke menu."),
 dict(no=6, kat="Pelanggaran aturan", nama="Tarif kamar 0 (AB-3)",
      langkah="Menu 1: nomor 105, tipe 2, tarif 0, kapasitas 2",
      harap="Kamar tidak dibuat", aktual="[GAGAL] Tarif per malam harus lebih dari 0.",
      lihat="Pesan [GAGAL] tarif harus lebih dari 0."),
 dict(no=7, kat="Pelanggaran aturan", nama="Jumlah malam 0 (AB-4)",
      langkah="Menu 14; menu 5: T001, 101, 0, 25-11-2026",
      harap="Reservasi ditolak", aktual="[GAGAL] Jumlah malam harus lebih dari 0.",
      lihat="Pesan [GAGAL] jumlah malam harus lebih dari 0."),
 dict(no=8, kat="Pelanggaran aturan", nama="Umur tamu di luar rentang (AB-5)",
      langkah="Menu 3: kode T009, nama Dewi, telepon 081234567890, umur 10",
      harap="Tamu tidak ditambahkan", aktual="[GAGAL] Umur tamu harus antara 17 sampai 120 tahun.",
      lihat="Pesan [GAGAL] umur harus antara 17 sampai 120 tahun."),
 dict(no=9, kat="ADT Stack penuh", nama="Reservasi ke-6 saat stack berkapasitas 5 penuh (AB-9)",
      langkah="Menu 14; menu 5 sebanyak 5 kali (T001-101, T001-102, T002-103, T002-201, T003-202; masing-masing 1 malam, 25-11-2026); menu 10; menu 5: T003, 301, 1, 25-11-2026",
      harap="Reservasi ke-6 ditolak; program tetap jalan", aktual="[GAGAL] Riwayat reservasi (stack) penuh, kapasitas 5. Batalkan reservasi terakhir (POP) atau kosongkan riwayat (CLEAR) terlebih dahulu.",
      lihat="Menu 10 menampilkan isFull: true dan 5 elemen; pemesanan ke-6 menampilkan pesan [GAGAL] stack penuh."),
 dict(no=10, kat="ADT Stack kosong", nama="POP saat stack kosong",
      langkah="Jalankan program, langsung menu 8",
      harap="Pesan error, tidak crash", aktual="[GAGAL] Riwayat kosong: tidak ada reservasi yang dapat dibatalkan.",
      lihat="Pesan [GAGAL] riwayat kosong."),
 dict(no=11, kat="ADT Stack kosong", nama="PEEK saat stack kosong",
      langkah="Jalankan program, langsung menu 9 (lalu menu 10 untuk bukti isEmpty)",
      harap="Pesan info, tidak crash", aktual="[INFO] Stack kosong: belum ada reservasi terakhir.",
      lihat="Pesan [INFO] stack kosong; menu 10 menampilkan isEmpty: true."),
 dict(no=12, kat="Input tidak valid", nama="Huruf dan angka di luar rentang pada menu",
      langkah="Di menu utama ketik: abc, lalu 99",
      harap="Input diminta ulang", aktual="[ERROR] Input harus berupa bilangan bulat (angka), bukan huruf/kosong. Coba lagi.; [ERROR] Pilihan harus antara 0 sampai 14. Coba lagi.",
      lihat="Dua pesan [ERROR] berurutan dan prompt menu muncul kembali."),
 dict(no=13, kat="Input tidak valid", nama="Huruf pada kolom tarif",
      langkah="Menu 1: nomor 105, tipe 2, tarif abc, lalu 350000, kapasitas 2",
      harap="Tarif diminta ulang, lalu kamar tersimpan", aktual="[ERROR] Input harus berupa angka, bukan huruf/kosong. Coba lagi.; [BERHASIL] Kamar 105 (Deluxe, Rp 350.000/malam) ditambahkan.",
      lihat="Pesan [ERROR], prompt tarif diulang, lalu pesan BERHASIL."),
 dict(no=14, kat="Input tidak valid", nama="Tanggal yang tidak ada di kalender",
      langkah="Menu 14; menu 5: T001, 101, 1, tanggal 31-02-2026, lalu 25-11-2026",
      harap="Tanggal diminta ulang", aktual="[ERROR] Format tanggal salah atau tanggal tidak ada. Gunakan dd-MM-yyyy, contoh 25-11-2026.; lalu reservasi berhasil",
      lihat="Pesan [ERROR] tanggal, prompt tanggal diulang, lalu struk reservasi."),
 dict(no=15, kat="Input tidak valid", nama="Nama tamu dikosongkan",
      langkah="Menu 3: kode T009, nama (langsung Enter), telepon 081234567890, umur 30",
      harap="Tamu tidak ditambahkan", aktual="[GAGAL] Nama tamu tidak boleh kosong.",
      lihat="Pesan [GAGAL] nama tidak boleh kosong."),
 dict(no=16, kat="Normal (POP)", nama="Membatalkan reservasi terakhir (POP)",
      langkah="Menu 14; menu 5: T001, 101, 3, 25-11-2026; menu 8; menu 2",
      harap="Reservasi dibatalkan; kamar kembali tersedia", aktual="[BERHASIL] Reservasi RSV-001 atas nama Budi Santoso dibatalkan. Kamar 101 kembali tersedia.; Sisa isi stack: 0",
      lihat="Pesan pembatalan, sisa stack 0, dan menu 2 menunjukkan kamar 101 berstatus Tersedia."),
]

story.append(h2("5.2 Tabel Skenario Uji"))
story += tabel("5.1", "Skenario pengujian, hasil diharapkan, dan hasil aktual",
               ["No", "Skenario", "Langkah input", "Diharapkan", "Hasil aktual", "Status"],
               [[str(s["no"]), "%s: %s" % (s["kat"], s["nama"]), s["langkah"], s["harap"], s["aktual"], "Lulus"] for s in SC],
               [0.7, 3.0, 3.5, 2.7, 4.0, 1.6], center_cols=(0, 5))
story += tabel("5.2", "Rekap cakupan skenario", ["Kategori", "Minimal diminta", "Skenario", "Jumlah"], [
    ["Normal", "3", "1, 2, 3, 4, 16", "5"],
    ["Pelanggaran aturan bisnis", "3", "5, 6, 7, 8", "4"],
    ["ADT penuh / kosong", "2", "9, 10, 11", "3"],
    ["Input tidak valid", "2", "12, 13, 14, 15", "4"],
    ["Total", "10", "-", "16"],
], [5.0, 3.0, 5.0, 2.5], center_cols=(1, 3))
story.append(P("Seluruh 16 skenario menghasilkan keluaran sesuai harapan; tidak ada skenario yang menyebabkan program berhenti tiba-tiba (crash)."))

story.append(PageBreak())
story.append(h2("5.3 Tangkapan Layar Setiap Skenario"))
story.append(P("Bagian ini memuat tangkapan layar terminal untuk masing-masing skenario pada Tabel 5.1. "
               "Setiap gambar memuat langkah input dan bagian keluaran yang harus terlihat."))
for s in SC:
    blok = [
        h3("5.3.%d Skenario %d: %s" % (s["no"], s["no"], esc(s["nama"]))),
        P("<b>Langkah:</b> %s.<br/><b>Yang harus tampak pada gambar:</b> %s" % (esc(s["langkah"]), esc(s["lihat"])), BODYL),
        figure("skenario_%02d.png" % s["no"], W, 5.4 * cm,
               "TEMPEL TANGKAPAN LAYAR SKENARIO %d" % s["no"],
               "Simpan sebagai laporan/gambar/skenario_%02d.png" % s["no"]),
        Paragraph("Gambar 5.%d Hasil skenario %d: %s" % (s["no"], s["no"], esc(s["nama"])), CAP),
    ]
    story.append(KeepTogether(blok))

# ================================================================== BAB 6
story.append(PageBreak())
story.append(h1("6", "PENUTUP"))
story.append(P('<font backColor="#FFF200">[CATATAN: bagian kendala dan refleksi adalah draf. Sesuaikan dengan pengalaman pribadi Anda sebelum dikumpulkan.]</font>', NOTE))
story.append(h2("6.1 Kesimpulan"))
story += B([
    "Aplikasi Manajemen Hotel Mini berhasil dibuat dengan 7 class (Kamar, Tamu, Reservasi, Hotel, StackRiwayat, Main, FormatUtil) dan menu console 14 pilihan.",
    "Dua aturan wajib topik Hotel terpenuhi: kamar terisi tidak bisa dipesan, dan biaya dihitung sebagai tarif x jumlah malam.",
    "ADT Stack berbasis array berhasil dipakai untuk fitur pembatalan reservasi terakhir dengan prinsip LIFO; kondisi penuh dan kosong ditangani tanpa crash.",
    "Enkapsulasi lewat atribut private dan setter berisi validasi menjaga data tetap konsisten, dan 16 skenario uji seluruhnya lulus.",
])
story.append(h2("6.2 Kendala yang Dihadapi"))
story += B([
    "Menentukan perilaku ketika stack penuh. Solusi: reservasi baru ditolak agar fitur pembatalan terakhir selalu konsisten dengan urutan reservasi.",
    "Menjaga konsistensi status kamar saat pembatalan atau check-out. Solusi: perubahan status ditempatkan di Reservasi (batalkan dan checkOut) yang sekaligus mengosongkan kamar.",
    "Mencegah program berhenti karena input salah. Solusi: pembaca input diulang sampai valid, dan exception aturan bisnis ditangkap di satu tempat (prosesPilihan).",
    "Memastikan tidak ada perubahan setengah jadi saat transaksi gagal. Solusi: semua pengecekan dilakukan sebelum data diubah pada Hotel.buatReservasi().",
])
story.append(h2("6.3 Refleksi"))
story.append(P(
    "Dari pengerjaan UTS ini saya memahami bahwa OOP membantu menempatkan aturan pada tempat yang tepat: aturan kamar berada di Kamar, "
    "aturan transaksi di Hotel, dan antarmuka di Main. Memisahkan tanggung jawab membuat kesalahan lebih mudah dicari dan diuji. "
    "Saya juga belajar bahwa memilih struktur data harus mengikuti kebutuhan: stack cocok untuk pembatalan karena sifat LIFO-nya. "
    "Untuk pengembangan berikutnya, aplikasi dapat dilengkapi penyimpanan ke berkas atau database, serta penerapan pewarisan dan polimorfisme "
    "untuk tipe kamar yang berbeda."))

# ================================================================== DAFTAR PUSTAKA
story.append(PageBreak())
story.append(h1(None, "DAFTAR PUSTAKA"))
story.append(P('<font backColor="#FFF200">[CATATAN: cantumkan hanya sumber yang benar-benar Anda baca atau gunakan; hapus yang tidak dipakai.]</font>', NOTE))
REF = ParagraphStyle("REF", parent=BODYL, leftIndent=24, firstLineIndent=-24, spaceAfter=8)
for r in [
    "Bloch, J. (2018). <i>Effective Java</i> (3rd ed.). Addison-Wesley.",
    "Cormen, T. H., Leiserson, C. E., Rivest, R. L., &amp; Stein, C. (2022). <i>Introduction to Algorithms</i> (4th ed.). MIT Press.",
    "Deitel, P., &amp; Deitel, H. (2017). <i>Java How to Program, Early Objects</i> (11th ed.). Pearson.",
    "Fowler, M. (2003). <i>UML Distilled: A Brief Guide to the Standard Object Modeling Language</i> (3rd ed.). Addison-Wesley.",
    "Horstmann, C. S. (2019). <i>Core Java, Volume I: Fundamentals</i> (11th ed.). Pearson.",
    "Oracle. (n.d.). <i>The Java Tutorials: Object-Oriented Programming Concepts</i>. https://docs.oracle.com/javase/tutorial/java/concepts/",
    "Oracle. (n.d.). <i>Java Platform, Standard Edition Documentation</i>. https://docs.oracle.com/en/java/javase/",
]:
    story.append(Paragraph(r, REF))

# ================================================================== LAMPIRAN
story.append(PageBreak())
story.append(h1(None, "LAMPIRAN"))
story.append(h2("Lampiran A. Repositori GitHub dan Riwayat Commit"))
story += tabel("A.1", "Informasi repositori", ["Item", "Isi"], [
    ["Nama repositori", "UTS-POO_22515065_TirtaApriliansyah"],
    ["Tautan repositori", Paragraph(F("github_url"), TD)],
    ["Hash commit terakhir", Paragraph(F("commit_hash"), TD)],
], [4.5, 11.0])
story += tabel("A.2", "Riwayat commit (minimal 8 commit)", ["No", "Pesan commit", "Hash"], [
    [str(i + 1), m, Paragraph('<font backColor="#FFF200">[ISI hash]</font>', TD)] for i, m in enumerate([
        "Tambah .gitignore dan README awal",
        "Tambah class diagram",
        "Tambah FormatUtil untuk format rupiah dan tanggal",
        "Tambah class entitas Kamar dan Tamu",
        "Tambah class Reservasi dan relasi ke Tamu dan Kamar",
        "Tambah ADT StackRiwayat berbasis array",
        "Tambah class Hotel dengan aturan bisnis",
        "Tambah menu console di Main",
        "Tambah input skenario pengujian",
    ])], [1.0, 10.5, 4.0], center_cols=(0,))
story.append(P("Hash commit dilihat dengan perintah <font name=\"Courier\">git log --oneline</font>.", NOTE))

story.append(h2("Lampiran B. Video Demo"))
story += tabel("B.1", "Informasi video demo", ["Item", "Isi"], [
    ["Tautan video", Paragraph(F("video_url"), TD)],
    ["Durasi", "Maksimal 5 menit"],
], [4.5, 11.0])
story.append(P("Isi video yang disarankan: (1) menjalankan program, (2) membuat reservasi normal, (3) memesan kamar terisi sehingga ditolak, "
               "(4) menunjukkan PUSH, PEEK, dan isi stack, (5) POP untuk membatalkan reservasi terakhir, (6) stack penuh dan stack kosong, "
               "(7) contoh input tidak valid.", BODYL))

story.append(PageBreak())
story.append(h2("Lampiran C. Pernyataan Orisinalitas"))
story.append(P(
    "Saya yang bertanda tangan di bawah ini:"))
story.append(table(["Item", "Keterangan"], [
    ["Nama", NAMA], ["NIM", NIM], ["Kelas", Paragraph(F("kelas"), TD)],
], [4.5, 11.0], zebra=False))
story.append(Spacer(1, 6))
story.append(P(
    "menyatakan bahwa project UTS Object Oriented Programming berjudul <b>%s</b> ini adalah hasil pekerjaan saya sendiri, "
    "bahwa saya memahami seluruh isi kode dan laporan ini, serta tidak menyalin dari karya mahasiswa lain. Apabila di kemudian hari terbukti "
    "melakukan pelanggaran, saya bersedia menerima sanksi sesuai ketentuan yang berlaku." % esc(JUDUL.title())))
sign = Table([[Paragraph("%s, %s" % (F("kota"), F("tanggal")), BODYL)],
              [Paragraph("Yang menyatakan,", BODYL)],
              [figure("tanda_tangan.png", 5 * cm, 2.4 * cm, "TANDA TANGAN", "gambar/tanda_tangan.png")],
              [Paragraph("<b><u>%s</u></b><br/>NIM %s" % (NAMA, NIM), BODYL)]],
             colWidths=[7 * cm])
sign.hAlign = "RIGHT"
story.append(Spacer(1, 6))
story.append(KeepTogether([sign]))

# ------------------------------------------------------------------ bangun PDF
if __name__ == "__main__":
    doc = build_doc(OUT)
    doc.multiBuild(story)
    print("Selesai:", OUT)
