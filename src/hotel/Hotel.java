package hotel;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Class entitas Hotel: pusat pengelola seluruh data dan aturan bisnis.
 *
 * Relasi:
 * - Hotel memiliki banyak Kamar        (KOMPOSISI: kamar tidak ada tanpa hotel)
 * - Hotel memiliki banyak Reservasi    (KOMPOSISI)
 * - Hotel mendaftarkan banyak Tamu     (AGREGASI: tamu bisa berdiri sendiri)
 * - Hotel memiliki satu StackRiwayat   (KOMPOSISI)
 *
 * Aturan bisnis yang ditegakkan di class ini:
 * 1. Kamar terisi tidak bisa dipesan.
 * 2. Biaya = tarif x malam (didelegasikan ke Kamar / Reservasi).
 * 3. Reservasi baru ditolak bila stack riwayat penuh, agar fitur "batalkan
 *    reservasi terakhir" selalu konsisten dengan urutan reservasi.
 *
 * @author Tirta Apriliansyah (NIM 22515065)
 */
public class Hotel {

    // ====================== ATRIBUT (semua private) ======================
    private String namaHotel;
    private String alamat;
    private int bintang;                         // 1 - 5
    private ArrayList<Kamar> daftarKamar;
    private ArrayList<Tamu> daftarTamu;
    private ArrayList<Reservasi> daftarReservasi;
    private StackRiwayat riwayat;                // ADT Stack
    private int urutanReservasi;                 // penghitung untuk kode RSV-001, dst.

    // ====================== KONSTRUKTOR ======================

    /** Konstruktor default: hotel contoh dengan kapasitas riwayat 5. */
    public Hotel() {
        this("Hotel Tirta Kendari", "Jl. Contoh No. 1, Kendari", 3, 5);
    }

    /**
     * Konstruktor berparameter.
     *
     * @param namaHotel         nama hotel
     * @param alamat            alamat hotel
     * @param bintang           kelas hotel 1-5
     * @param kapasitasRiwayat  kapasitas stack riwayat reservasi (minimal 1)
     */
    public Hotel(String namaHotel, String alamat, int bintang, int kapasitasRiwayat) {
        setNamaHotel(namaHotel);
        setAlamat(alamat);
        setBintang(bintang);
        this.daftarKamar = new ArrayList<>();
        this.daftarTamu = new ArrayList<>();
        this.daftarReservasi = new ArrayList<>();
        this.riwayat = new StackRiwayat(kapasitasRiwayat);
        this.urutanReservasi = 0;
    }

    // ====================== GETTER ======================
    public String getNamaHotel() {
        return namaHotel;
    }

    public String getAlamat() {
        return alamat;
    }

    public int getBintang() {
        return bintang;
    }

    /** Mengembalikan daftar read-only agar luar class tidak bisa mengubah isinya langsung. */
    public List<Kamar> getDaftarKamar() {
        return Collections.unmodifiableList(daftarKamar);
    }

    public List<Tamu> getDaftarTamu() {
        return Collections.unmodifiableList(daftarTamu);
    }

    public List<Reservasi> getDaftarReservasi() {
        return Collections.unmodifiableList(daftarReservasi);
    }

    public StackRiwayat getRiwayat() {
        return riwayat;
    }

    // ====================== SETTER + VALIDASI ======================

    public void setNamaHotel(String namaHotel) {
        if (namaHotel == null || namaHotel.trim().isEmpty()) {
            throw new IllegalArgumentException("Nama hotel tidak boleh kosong.");
        }
        this.namaHotel = namaHotel.trim();
    }

    public void setAlamat(String alamat) {
        if (alamat == null || alamat.trim().isEmpty()) {
            throw new IllegalArgumentException("Alamat hotel tidak boleh kosong.");
        }
        this.alamat = alamat.trim();
    }

    public void setBintang(int bintang) {
        if (bintang < 1 || bintang > 5) {
            throw new IllegalArgumentException("Bintang hotel harus antara 1 sampai 5.");
        }
        this.bintang = bintang;
    }

    // ====================== PENAMBAHAN DATA ======================

    /**
     * Menambah kamar ke hotel.
     *
     * @throws IllegalArgumentException bila kamar null atau nomor kamar sudah ada
     */
    public void tambahKamar(Kamar kamar) {
        if (kamar == null) {
            throw new IllegalArgumentException("Data kamar tidak boleh kosong.");
        }
        if (cariKamar(kamar.getNomorKamar()) != null) {
            throw new IllegalArgumentException(
                    "Nomor kamar " + kamar.getNomorKamar() + " sudah terdaftar.");
        }
        daftarKamar.add(kamar);
    }

    /**
     * Mendaftarkan tamu.
     *
     * @throws IllegalArgumentException bila tamu null atau kode tamu sudah ada
     */
    public void tambahTamu(Tamu tamu) {
        if (tamu == null) {
            throw new IllegalArgumentException("Data tamu tidak boleh kosong.");
        }
        if (cariTamuByKode(tamu.getKodeTamu()) != null) {
            throw new IllegalArgumentException(
                    "Kode tamu " + tamu.getKodeTamu() + " sudah terdaftar.");
        }
        daftarTamu.add(tamu);
    }

    // ====================== PENCARIAN ======================

    /** @return kamar dengan nomor tersebut, atau null bila tidak ditemukan. */
    public Kamar cariKamar(String nomorKamar) {
        if (nomorKamar == null) {
            return null;
        }
        for (Kamar k : daftarKamar) {
            if (k.getNomorKamar().equalsIgnoreCase(nomorKamar.trim())) {
                return k;
            }
        }
        return null;
    }

    /** @return tamu dengan kode tersebut, atau null bila tidak ditemukan. */
    public Tamu cariTamuByKode(String kodeTamu) {
        if (kodeTamu == null) {
            return null;
        }
        for (Tamu t : daftarTamu) {
            if (t.getKodeTamu().equalsIgnoreCase(kodeTamu.trim())) {
                return t;
            }
        }
        return null;
    }

    /**
     * Mencari tamu berdasarkan kode (persis) ATAU sebagian nama (tanpa peduli huruf besar/kecil).
     *
     * @param kunci kata kunci pencarian
     * @return daftar tamu yang cocok (bisa kosong)
     */
    public List<Tamu> cariTamu(String kunci) {
        List<Tamu> hasil = new ArrayList<>();
        if (kunci == null || kunci.trim().isEmpty()) {
            return hasil;
        }
        String kataKunci = kunci.trim().toLowerCase();
        for (Tamu t : daftarTamu) {
            if (t.getKodeTamu().equalsIgnoreCase(kataKunci)
                    || t.getNama().toLowerCase().contains(kataKunci)) {
                hasil.add(t);
            }
        }
        return hasil;
    }

    /** @return reservasi dengan kode tersebut, atau null bila tidak ditemukan. */
    public Reservasi cariReservasi(String kodeReservasi) {
        if (kodeReservasi == null) {
            return null;
        }
        for (Reservasi r : daftarReservasi) {
            if (r.getKodeReservasi().equalsIgnoreCase(kodeReservasi.trim())) {
                return r;
            }
        }
        return null;
    }

    // ====================== TRANSAKSI UTAMA ======================

    /**
     * Membuat reservasi baru yang menghubungkan Tamu dan Kamar, lalu PUSH ke stack riwayat.
     *
     * Urutan pengecekan (semua dilakukan SEBELUM ada perubahan data):
     * 1. tamu harus ada
     * 2. kamar harus ada
     * 3. kamar harus tersedia            (aturan bisnis: kamar terisi tidak bisa dipesan)
     * 4. stack riwayat tidak boleh penuh
     * 5. objek Reservasi dibuat -> memvalidasi jumlah malam dan tanggal
     * Baru setelah semua lolos, kamar ditandai terisi dan reservasi disimpan.
     *
     * @return reservasi yang berhasil dibuat
     * @throws IllegalArgumentException bila tamu/kamar tidak ditemukan atau input tidak valid
     * @throws IllegalStateException    bila kamar terisi atau stack riwayat penuh
     */
    public Reservasi buatReservasi(String kodeTamu, String nomorKamar,
                                   int jumlahMalam, LocalDate tanggalCheckIn) {
        Tamu tamu = cariTamuByKode(kodeTamu);
        if (tamu == null) {
            throw new IllegalArgumentException("Tamu dengan kode '" + kodeTamu + "' tidak ditemukan.");
        }
        Kamar kamar = cariKamar(nomorKamar);
        if (kamar == null) {
            throw new IllegalArgumentException("Kamar dengan nomor '" + nomorKamar + "' tidak ditemukan.");
        }
        if (!kamar.isTersedia()) {
            throw new IllegalStateException(
                    "Kamar " + kamar.getNomorKamar() + " sedang terisi dan tidak dapat dipesan.");
        }
        if (riwayat.isFull()) {
            throw new IllegalStateException("Riwayat reservasi (stack) penuh, kapasitas "
                    + riwayat.getKapasitas() + ". Batalkan reservasi terakhir (POP) atau "
                    + "kosongkan riwayat (CLEAR) terlebih dahulu.");
        }

        String kode = String.format("RSV-%03d", urutanReservasi + 1);
        Reservasi reservasi = new Reservasi(kode, tamu, kamar, jumlahMalam, tanggalCheckIn);

        // Semua validasi lolos: sekarang aman mengubah data
        kamar.pesan();
        riwayat.push(reservasi);
        daftarReservasi.add(reservasi);
        urutanReservasi++;
        return reservasi;
    }

    /**
     * Membatalkan reservasi paling akhir (POP dari stack).
     *
     * @return reservasi yang dibatalkan
     * @throws IllegalStateException bila riwayat kosong, atau reservasi teratas
     *                               sudah tidak aktif (misalnya sudah check-out)
     */
    public Reservasi batalkanReservasiTerakhir() {
        if (riwayat.isEmpty()) {
            throw new IllegalStateException("Riwayat kosong: tidak ada reservasi yang dapat dibatalkan.");
        }
        Reservasi terakhir = riwayat.pop();
        if (!terakhir.isAktif()) {
            throw new IllegalStateException("Reservasi terakhir (" + terakhir.getKodeReservasi()
                    + ") berstatus " + terakhir.getStatus()
                    + " sehingga tidak dapat dibatalkan. Item dikeluarkan dari riwayat.");
        }
        terakhir.batalkan();
        return terakhir;
    }

    /**
     * Check-out tamu berdasarkan kode reservasi.
     *
     * @throws IllegalArgumentException bila reservasi tidak ditemukan
     * @throws IllegalStateException    bila reservasi sudah tidak aktif
     */
    public Reservasi checkOut(String kodeReservasi) {
        Reservasi reservasi = cariReservasi(kodeReservasi);
        if (reservasi == null) {
            throw new IllegalArgumentException(
                    "Reservasi dengan kode '" + kodeReservasi + "' tidak ditemukan.");
        }
        reservasi.checkOut();
        return reservasi;
    }

    // ====================== LAPORAN ======================

    public int hitungKamarTersedia() {
        int jumlah = 0;
        for (Kamar k : daftarKamar) {
            if (k.isTersedia()) {
                jumlah++;
            }
        }
        return jumlah;
    }

    public int hitungKamarTerisi() {
        return daftarKamar.size() - hitungKamarTersedia();
    }

    /** @return jumlah reservasi dengan status tertentu (gunakan konstanta Reservasi.STATUS_...). */
    public int hitungReservasiByStatus(String status) {
        int jumlah = 0;
        for (Reservasi r : daftarReservasi) {
            if (r.getStatus().equals(status)) {
                jumlah++;
            }
        }
        return jumlah;
    }

    /** @return total biaya semua reservasi yang tidak dibatalkan (AKTIF + SELESAI). */
    public double hitungTotalPendapatan() {
        double total = 0;
        for (Reservasi r : daftarReservasi) {
            if (!Reservasi.STATUS_DIBATALKAN.equals(r.getStatus())) {
                total += r.hitungBiaya();
            }
        }
        return total;
    }

    /** @return persentase kamar terisi (0-100); 0 bila belum ada kamar. */
    public double hitungTingkatHunian() {
        if (daftarKamar.isEmpty()) {
            return 0;
        }
        return hitungKamarTerisi() * 100.0 / daftarKamar.size();
    }
}
