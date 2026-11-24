package hotel;

import java.time.LocalDate;

/**
 * Class entitas Reservasi: transaksi utama yang menghubungkan satu Tamu
 * dengan satu Kamar selama beberapa malam.
 *
 * Relasi (asosiasi):
 * - Reservasi -> Tamu  (banyak reservasi bisa dimiliki satu tamu)
 * - Reservasi -> Kamar (satu kamar bisa muncul di banyak reservasi pada waktu berbeda)
 *
 * Siklus status: AKTIF -> SELESAI (check-out) atau AKTIF -> DIBATALKAN (undo/pop stack).
 *
 * @author Tirta Apriliansyah (NIM 22515065)
 */
public class Reservasi {

    /** Konstanta status reservasi (UPPER_CASE sesuai konvensi). */
    public static final String STATUS_AKTIF = "AKTIF";
    public static final String STATUS_SELESAI = "SELESAI";
    public static final String STATUS_DIBATALKAN = "DIBATALKAN";

    // ====================== ATRIBUT (semua private) ======================
    private String kodeReservasi;     // misal "RSV-001"
    private Tamu tamu;                // relasi ke Tamu
    private Kamar kamar;             // relasi ke Kamar
    private int jumlahMalam;          // lama menginap
    private LocalDate tanggalCheckIn;
    private String status;            // AKTIF / SELESAI / DIBATALKAN

    // ====================== KONSTRUKTOR ======================

    /** Konstruktor default: reservasi kosong (tamu dan kamar belum diisi). */
    public Reservasi() {
        this.kodeReservasi = "RSV-000";
        this.tamu = null;
        this.kamar = null;
        this.jumlahMalam = 1;
        this.tanggalCheckIn = LocalDate.now();
        this.status = STATUS_AKTIF;
    }

    /**
     * Konstruktor berparameter. Semua nilai divalidasi lewat setter.
     * Bila ada nilai tidak valid, exception dilempar SEBELUM objek terbentuk,
     * sehingga tidak ada reservasi setengah jadi.
     *
     * @param kodeReservasi  kode unik reservasi
     * @param tamu           tamu pemesan (tidak boleh null)
     * @param kamar          kamar yang dipesan (tidak boleh null)
     * @param jumlahMalam    lama menginap (> 0)
     * @param tanggalCheckIn tanggal masuk (tidak boleh null)
     */
    public Reservasi(String kodeReservasi, Tamu tamu, Kamar kamar,
                     int jumlahMalam, LocalDate tanggalCheckIn) {
        setKodeReservasi(kodeReservasi);
        setTamu(tamu);
        setKamar(kamar);
        setJumlahMalam(jumlahMalam);
        setTanggalCheckIn(tanggalCheckIn);
        this.status = STATUS_AKTIF; // reservasi baru selalu aktif
    }

    // ====================== GETTER ======================
    public String getKodeReservasi() {
        return kodeReservasi;
    }

    public Tamu getTamu() {
        return tamu;
    }

    public Kamar getKamar() {
        return kamar;
    }

    public int getJumlahMalam() {
        return jumlahMalam;
    }

    public LocalDate getTanggalCheckIn() {
        return tanggalCheckIn;
    }

    public String getStatus() {
        return status;
    }

    // ====================== SETTER + VALIDASI ======================

    public void setKodeReservasi(String kodeReservasi) {
        if (kodeReservasi == null || kodeReservasi.trim().isEmpty()) {
            throw new IllegalArgumentException("Kode reservasi tidak boleh kosong.");
        }
        this.kodeReservasi = kodeReservasi.trim().toUpperCase();
    }

    public void setTamu(Tamu tamu) {
        if (tamu == null) {
            throw new IllegalArgumentException("Tamu pada reservasi tidak boleh kosong.");
        }
        this.tamu = tamu;
    }

    public void setKamar(Kamar kamar) {
        if (kamar == null) {
            throw new IllegalArgumentException("Kamar pada reservasi tidak boleh kosong.");
        }
        this.kamar = kamar;
    }

    public void setJumlahMalam(int jumlahMalam) {
        if (jumlahMalam <= 0) {
            throw new IllegalArgumentException("Jumlah malam harus lebih dari 0.");
        }
        if (jumlahMalam > 30) {
            throw new IllegalArgumentException("Jumlah malam maksimal 30 malam per reservasi.");
        }
        this.jumlahMalam = jumlahMalam;
    }

    public void setTanggalCheckIn(LocalDate tanggalCheckIn) {
        if (tanggalCheckIn == null) {
            throw new IllegalArgumentException("Tanggal check-in tidak boleh kosong.");
        }
        this.tanggalCheckIn = tanggalCheckIn;
    }

    public void setStatus(String status) {
        if (!STATUS_AKTIF.equals(status) && !STATUS_SELESAI.equals(status)
                && !STATUS_DIBATALKAN.equals(status)) {
            throw new IllegalArgumentException("Status reservasi tidak dikenal: " + status);
        }
        this.status = status;
    }

    // ====================== METHOD PERILAKU ======================

    /** @return true bila reservasi masih aktif (belum check-out / dibatalkan). */
    public boolean isAktif() {
        return STATUS_AKTIF.equals(status);
    }

    /**
     * Menghitung biaya reservasi.
     * ATURAN BISNIS: biaya = tarif kamar x jumlah malam.
     *
     * @return total biaya dalam rupiah (0 bila kamar belum diisi)
     */
    public double hitungBiaya() {
        if (kamar == null) {
            return 0;
        }
        return kamar.hitungBiaya(jumlahMalam);
    }

    /** @return tanggal check-out = tanggal check-in + jumlah malam. */
    public LocalDate getTanggalCheckOut() {
        return tanggalCheckIn.plusDays(jumlahMalam);
    }

    /**
     * Membatalkan reservasi aktif dan mengosongkan kamarnya.
     * Dipanggil ketika operasi POP (undo) pada stack riwayat dijalankan.
     *
     * @throws IllegalStateException bila reservasi tidak lagi aktif
     */
    public void batalkan() {
        if (!isAktif()) {
            throw new IllegalStateException("Reservasi " + kodeReservasi + " berstatus "
                    + status + " sehingga tidak dapat dibatalkan.");
        }
        this.status = STATUS_DIBATALKAN;
        if (kamar != null) {
            kamar.kosongkan(); // kamar bisa dipesan lagi
        }
    }

    /**
     * Menyelesaikan reservasi (tamu check-out): kamar dikosongkan dan
     * total malam menginap tamu bertambah.
     *
     * @throws IllegalStateException bila reservasi tidak lagi aktif
     */
    public void checkOut() {
        if (!isAktif()) {
            throw new IllegalStateException("Reservasi " + kodeReservasi + " berstatus "
                    + status + " sehingga tidak dapat di-check-out.");
        }
        this.status = STATUS_SELESAI;
        if (kamar != null) {
            kamar.kosongkan();
        }
        if (tamu != null) {
            tamu.tambahMalamMenginap(jumlahMalam);
        }
    }

    /** @return judul kolom untuk tabel daftar reservasi. */
    public static String header() {
        return String.format("%-9s %-18s %-7s %-11s %-11s %-6s %-14s %-11s",
                "Kode", "Tamu", "Kamar", "Check-in", "Check-out", "Malam", "Biaya", "Status");
    }

    /** Mencetak satu baris informasi reservasi (cocok dengan header()). */
    public void tampilkanInfo() {
        String namaTamu = (tamu == null) ? "-" : tamu.getNama();
        String noKamar = (kamar == null) ? "-" : kamar.getNomorKamar();
        System.out.printf("%-9s %-18s %-7s %-11s %-11s %-6d %-14s %-11s%n",
                kodeReservasi, namaTamu, noKamar,
                FormatUtil.formatTanggal(tanggalCheckIn),
                FormatUtil.formatTanggal(getTanggalCheckOut()),
                jumlahMalam, FormatUtil.formatRupiah(hitungBiaya()), status);
    }

    /** Mencetak struk rincian satu reservasi (dipakai setelah reservasi berhasil dibuat). */
    public void cetakStruk() {
        System.out.println("----------- STRUK RESERVASI -----------");
        System.out.println("Kode Reservasi : " + kodeReservasi);
        System.out.println("Tamu           : " + (tamu == null ? "-" : tamu.getNama()
                + " (" + tamu.getKodeTamu() + ")"));
        System.out.println("Kamar          : " + (kamar == null ? "-" : kamar.getNomorKamar()
                + " - " + kamar.getTipe()));
        System.out.println("Tarif/Malam    : " + FormatUtil.formatRupiah(
                kamar == null ? 0 : kamar.getTarifPerMalam()));
        System.out.println("Check-in       : " + FormatUtil.formatTanggal(tanggalCheckIn));
        System.out.println("Check-out      : " + FormatUtil.formatTanggal(getTanggalCheckOut()));
        System.out.println("Jumlah Malam   : " + jumlahMalam);
        System.out.println("TOTAL BIAYA    : " + FormatUtil.formatRupiah(hitungBiaya()));
        System.out.println("Status         : " + status);
        System.out.println("---------------------------------------");
    }
}
