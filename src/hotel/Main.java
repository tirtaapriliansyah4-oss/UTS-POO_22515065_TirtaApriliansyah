package hotel;

import java.time.LocalDate;
import java.time.format.DateTimeParseException;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.Scanner;

/**
 * Class Main: titik masuk program dan pengelola menu console.
 *
 * Tanggung jawab class ini hanya interaksi dengan pengguna (baca input, cetak output).
 * Semua aturan bisnis ada di class entitas dan Hotel, bukan di sini.
 *
 * Dependensi: Main memakai Hotel, Kamar, Tamu, Reservasi, StackRiwayat, FormatUtil.
 *
 * Penanganan kesalahan:
 * - Input angka diulang terus sampai valid (huruf/kosong tidak membuat crash).
 * - Pelanggaran aturan bisnis ditangkap (catch) lalu dicetak sebagai pesan [GAGAL].
 *
 * @author Tirta Apriliansyah (NIM 22515065)
 */
public class Main {

    private static final int KAPASITAS_RIWAYAT = 5;
    private static final int PILIHAN_MAKSIMAL = 14;

    private static final Scanner SCANNER = new Scanner(System.in);
    private static Hotel hotel;

    // ====================== TITIK MASUK PROGRAM ======================

    public static void main(String[] args) {
        hotel = new Hotel("Hotel Tirta Kendari", "Jl. Contoh No. 1, Kendari", 3, KAPASITAS_RIWAYAT);
        System.out.println("==================================================");
        System.out.println(" APLIKASI MANAJEMEN HOTEL MINI");
        System.out.println(" Tirta Apriliansyah - NIM 22515065");
        System.out.println(" Topik: Hotel | ADT: Stack (riwayat reservasi)");
        System.out.println("==================================================");

        boolean berjalan = true;
        try {
            while (berjalan) {
                tampilkanMenu();
                int pilihan = bacaInt("Pilih menu (0-" + PILIHAN_MAKSIMAL + ") : ", 0, PILIHAN_MAKSIMAL);
                berjalan = prosesPilihan(pilihan);
            }
        } catch (NoSuchElementException e) {
            // Terjadi bila input ditutup (misal Ctrl+D): keluar dengan rapi
            System.out.println("\n[INFO] Input berakhir. Program dihentikan.");
        }
        System.out.println("Terima kasih telah menggunakan aplikasi ini.");
    }

    // ====================== MENU ======================

    private static void tampilkanMenu() {
        System.out.println();
        System.out.println("=============== MENU UTAMA ===============");
        System.out.println(" 1. Tambah kamar");
        System.out.println(" 2. Tampilkan semua kamar");
        System.out.println(" 3. Tambah tamu");
        System.out.println(" 4. Tampilkan semua tamu");
        System.out.println(" 5. Buat reservasi (PUSH ke stack)");
        System.out.println(" 6. Tampilkan semua reservasi");
        System.out.println(" 7. Cari data (kamar / tamu / reservasi)");
        System.out.println(" 8. Batalkan reservasi terakhir (POP)");
        System.out.println(" 9. Lihat reservasi terakhir (PEEK)");
        System.out.println("10. Tampilkan isi stack riwayat");
        System.out.println("11. Kosongkan riwayat (CLEAR)");
        System.out.println("12. Check-out tamu");
        System.out.println("13. Laporan ringkasan");
        System.out.println("14. Muat data contoh (demo)");
        System.out.println(" 0. Keluar");
        System.out.println("==========================================");
    }

    /**
     * Menjalankan menu yang dipilih.
     * Semua exception aturan bisnis ditangkap di sini sehingga program tidak berhenti.
     *
     * @return false bila pengguna memilih keluar, true untuk lanjut
     */
    private static boolean prosesPilihan(int pilihan) {
        try {
            switch (pilihan) {
                case 1:
                    menuTambahKamar();
                    break;
                case 2:
                    menuTampilKamar();
                    break;
                case 3:
                    menuTambahTamu();
                    break;
                case 4:
                    menuTampilTamu();
                    break;
                case 5:
                    menuBuatReservasi();
                    break;
                case 6:
                    menuTampilReservasi();
                    break;
                case 7:
                    menuCari();
                    break;
                case 8:
                    menuPop();
                    break;
                case 9:
                    menuPeek();
                    break;
                case 10:
                    menuTampilStack();
                    break;
                case 11:
                    menuClear();
                    break;
                case 12:
                    menuCheckOut();
                    break;
                case 13:
                    menuLaporan();
                    break;
                case 14:
                    menuDataContoh();
                    break;
                case 0:
                    return false;
                default:
                    System.out.println("[GAGAL] Menu tidak dikenal.");
            }
        } catch (IllegalArgumentException | IllegalStateException e) {
            // Pelanggaran validasi / aturan bisnis: tampilkan pesan, kembali ke menu
            System.out.println("[GAGAL] " + e.getMessage());
        }
        return true;
    }

    // ====================== MENU: KAMAR ======================

    private static void menuTambahKamar() {
        System.out.println("\n--- Tambah Kamar ---");
        String nomor = bacaTeks("Nomor kamar              : ");
        System.out.println("Tipe kamar: 1. Standard  2. Deluxe  3. Suite");
        int pilihTipe = bacaInt("Pilih tipe (1-3)          : ", 1, 3);
        String tipe = Kamar.TIPE_VALID[pilihTipe - 1];
        double tarif = bacaDouble("Tarif per malam (Rp)     : ");
        int kapasitas = bacaInt("Kapasitas (orang)        : ");

        // Validasi nilai dilakukan di dalam konstruktor/setter Kamar
        Kamar kamar = new Kamar(nomor, tipe, tarif, kapasitas);
        hotel.tambahKamar(kamar);
        System.out.println("[BERHASIL] Kamar " + kamar.getNomorKamar() + " (" + kamar.getTipe()
                + ", " + FormatUtil.formatRupiah(kamar.getTarifPerMalam()) + "/malam) ditambahkan.");
    }

    private static void menuTampilKamar() {
        System.out.println("\n--- Daftar Kamar ---");
        List<Kamar> daftar = hotel.getDaftarKamar();
        if (daftar.isEmpty()) {
            System.out.println("(Belum ada data kamar)");
            return;
        }
        System.out.println(Kamar.header());
        for (Kamar k : daftar) {
            k.tampilkanInfo();
        }
        System.out.println("Total kamar: " + daftar.size());
    }

    // ====================== MENU: TAMU ======================

    private static void menuTambahTamu() {
        System.out.println("\n--- Tambah Tamu ---");
        String kode = bacaTeks("Kode tamu (mis. T001) : ");
        String nama = bacaTeks("Nama lengkap          : ");
        String telepon = bacaTeks("No. telepon (angka)   : ");
        int umur = bacaInt("Umur                  : ");

        Tamu tamu = new Tamu(kode, nama, telepon, umur);
        hotel.tambahTamu(tamu);
        System.out.println("[BERHASIL] Tamu " + tamu.getNama() + " (" + tamu.getKodeTamu() + ") ditambahkan.");
    }

    private static void menuTampilTamu() {
        System.out.println("\n--- Daftar Tamu ---");
        List<Tamu> daftar = hotel.getDaftarTamu();
        if (daftar.isEmpty()) {
            System.out.println("(Belum ada data tamu)");
            return;
        }
        System.out.println(Tamu.header());
        for (Tamu t : daftar) {
            t.tampilkanInfo();
        }
        System.out.println("Total tamu: " + daftar.size());
    }

    // ====================== MENU: RESERVASI ======================

    private static void menuBuatReservasi() {
        System.out.println("\n--- Buat Reservasi ---");
        if (hotel.getDaftarTamu().isEmpty() || hotel.getDaftarKamar().isEmpty()) {
            System.out.println("[GAGAL] Data tamu dan data kamar harus diisi terlebih dahulu.");
            return;
        }
        String kodeTamu = bacaTeks("Kode tamu                     : ");
        String nomorKamar = bacaTeks("Nomor kamar                   : ");
        int malam = bacaInt("Jumlah malam                  : ");
        LocalDate tanggal = bacaTanggal("Tanggal check-in (" + FormatUtil.POLA_TANGGAL + ") : ");

        Reservasi reservasi = hotel.buatReservasi(kodeTamu, nomorKamar, malam, tanggal);
        System.out.println("[BERHASIL] Reservasi dibuat dan di-PUSH ke stack riwayat.");
        reservasi.cetakStruk();
    }

    private static void menuTampilReservasi() {
        System.out.println("\n--- Daftar Reservasi ---");
        List<Reservasi> daftar = hotel.getDaftarReservasi();
        if (daftar.isEmpty()) {
            System.out.println("(Belum ada reservasi)");
            return;
        }
        System.out.println(Reservasi.header());
        for (Reservasi r : daftar) {
            r.tampilkanInfo();
        }
        System.out.println("Total reservasi: " + daftar.size());
    }

    private static void menuCheckOut() {
        System.out.println("\n--- Check-out Tamu ---");
        String kode = bacaTeks("Kode reservasi (mis. RSV-001) : ");
        Reservasi r = hotel.checkOut(kode);
        System.out.println("[BERHASIL] Check-out " + r.getKodeReservasi() + " atas nama "
                + r.getTamu().getNama() + ". Kamar " + r.getKamar().getNomorKamar()
                + " kini tersedia. Total bayar: " + FormatUtil.formatRupiah(r.hitungBiaya()));
        System.out.println("Kategori tamu sekarang: " + r.getTamu().getKategori()
                + " (total " + r.getTamu().getTotalMalamMenginap() + " malam)");
    }

    // ====================== MENU: PENCARIAN ======================

    private static void menuCari() {
        System.out.println("\n--- Cari Data ---");
        System.out.println("1. Cari kamar (nomor kamar)");
        System.out.println("2. Cari tamu (kode atau nama)");
        System.out.println("3. Cari reservasi (kode reservasi)");
        int jenis = bacaInt("Pilih (1-3) : ", 1, 3);
        String kunci = bacaTeks("Kata kunci  : ");

        if (jenis == 1) {
            Kamar k = hotel.cariKamar(kunci);
            if (k == null) {
                System.out.println("[TIDAK DITEMUKAN] Kamar '" + kunci + "' tidak ada.");
            } else {
                System.out.println(Kamar.header());
                k.tampilkanInfo();
            }
        } else if (jenis == 2) {
            List<Tamu> hasil = hotel.cariTamu(kunci);
            if (hasil.isEmpty()) {
                System.out.println("[TIDAK DITEMUKAN] Tamu '" + kunci + "' tidak ada.");
            } else {
                System.out.println(Tamu.header());
                for (Tamu t : hasil) {
                    t.tampilkanInfo();
                }
                System.out.println("Ditemukan: " + hasil.size() + " tamu.");
            }
        } else {
            Reservasi r = hotel.cariReservasi(kunci);
            if (r == null) {
                System.out.println("[TIDAK DITEMUKAN] Reservasi '" + kunci + "' tidak ada.");
            } else {
                System.out.println(Reservasi.header());
                r.tampilkanInfo();
            }
        }
    }

    // ====================== MENU: OPERASI ADT STACK ======================

    private static void menuPop() {
        System.out.println("\n--- Batalkan Reservasi Terakhir (POP) ---");
        Reservasi r = hotel.batalkanReservasiTerakhir();
        System.out.println("[BERHASIL] Reservasi " + r.getKodeReservasi() + " atas nama "
                + r.getTamu().getNama() + " dibatalkan. Kamar " + r.getKamar().getNomorKamar()
                + " kembali tersedia.");
        System.out.println("Sisa isi stack: " + hotel.getRiwayat().size());
    }

    private static void menuPeek() {
        System.out.println("\n--- Reservasi Terakhir (PEEK) ---");
        Reservasi r = hotel.getRiwayat().peek();
        if (r == null) {
            System.out.println("[INFO] Stack kosong: belum ada reservasi terakhir.");
            return;
        }
        System.out.println(Reservasi.header());
        r.tampilkanInfo();
        System.out.println("(PEEK hanya melihat, reservasi tidak dihapus dari stack)");
    }

    private static void menuTampilStack() {
        System.out.println("\n--- Isi Stack Riwayat Reservasi ---");
        hotel.getRiwayat().tampilkan();
    }

    private static void menuClear() {
        System.out.println("\n--- Kosongkan Riwayat (CLEAR) ---");
        int jumlah = hotel.getRiwayat().size();
        if (jumlah == 0) {
            System.out.println("[INFO] Stack sudah kosong.");
            return;
        }
        hotel.getRiwayat().clear();
        System.out.println("[BERHASIL] " + jumlah + " riwayat dihapus. Data reservasi tetap tersimpan, "
                + "namun tidak bisa dibatalkan lewat POP.");
    }

    // ====================== MENU: LAPORAN ======================

    private static void menuLaporan() {
        System.out.println("\n========== LAPORAN RINGKASAN ==========");
        System.out.println("Hotel                : " + hotel.getNamaHotel()
                + " (" + hotel.getBintang() + " bintang)");
        System.out.println("Alamat               : " + hotel.getAlamat());
        System.out.println("Jumlah kamar         : " + hotel.getDaftarKamar().size());
        System.out.println("  - Tersedia         : " + hotel.hitungKamarTersedia());
        System.out.println("  - Terisi           : " + hotel.hitungKamarTerisi());
        System.out.printf("Tingkat hunian       : %.1f%%%n", hotel.hitungTingkatHunian());
        System.out.println("Jumlah tamu          : " + hotel.getDaftarTamu().size());
        System.out.println("Jumlah reservasi     : " + hotel.getDaftarReservasi().size());
        System.out.println("  - Aktif            : " + hotel.hitungReservasiByStatus(Reservasi.STATUS_AKTIF));
        System.out.println("  - Selesai          : " + hotel.hitungReservasiByStatus(Reservasi.STATUS_SELESAI));
        System.out.println("  - Dibatalkan       : " + hotel.hitungReservasiByStatus(Reservasi.STATUS_DIBATALKAN));
        System.out.println("Total pendapatan     : " + FormatUtil.formatRupiah(hotel.hitungTotalPendapatan())
                + " (aktif + selesai)");
        System.out.println("Stack riwayat        : " + hotel.getRiwayat().size() + " / "
                + hotel.getRiwayat().getKapasitas());
        System.out.println("=======================================");
    }

    // ====================== DATA CONTOH ======================

    /** Mengisi 6 kamar dan 3 tamu sekaligus supaya pengujian lebih cepat. */
    private static void menuDataContoh() {
        System.out.println("\n--- Muat Data Contoh ---");
        Kamar[] kamarContoh = {
                new Kamar("101", "Standard", 250000, 2),
                new Kamar("102", "Standard", 250000, 2),
                new Kamar("103", "Standard", 275000, 3),
                new Kamar("201", "Deluxe", 400000, 3),
                new Kamar("202", "Deluxe", 425000, 4),
                new Kamar("301", "Suite", 750000, 4)
        };
        Tamu[] tamuContoh = {
                new Tamu("T001", "Budi Santoso", "081234567890", 30),
                new Tamu("T002", "Siti Aisyah", "082345678901", 25),
                new Tamu("T003", "Andi Pratama", "083456789012", 41)
        };
        int kamarBaru = 0;
        int tamuBaru = 0;
        for (Kamar k : kamarContoh) {
            if (hotel.cariKamar(k.getNomorKamar()) == null) {
                hotel.tambahKamar(k);
                kamarBaru++;
            }
        }
        for (Tamu t : tamuContoh) {
            if (hotel.cariTamuByKode(t.getKodeTamu()) == null) {
                hotel.tambahTamu(t);
                tamuBaru++;
            }
        }
        System.out.println("[BERHASIL] Data contoh dimuat: " + kamarBaru + " kamar dan "
                + tamuBaru + " tamu baru.");
    }

    // ====================== PEMBACA INPUT (VALIDASI TIPE DATA) ======================

    /**
     * Membaca satu baris teks. Nilai kosong TIDAK ditolak di sini; penolakan dilakukan
     * oleh setter/konstruktor class entitas, sehingga pesan error datang dari aturan bisnis.
     */
    private static String bacaTeks(String prompt) {
        System.out.print(prompt);
        return SCANNER.nextLine().trim();
    }

    /** Membaca bilangan bulat tanpa batas; diulang sampai pengguna memasukkan angka. */
    private static int bacaInt(String prompt) {
        while (true) {
            System.out.print(prompt);
            String baris = SCANNER.nextLine().trim();
            try {
                return Integer.parseInt(baris);
            } catch (NumberFormatException e) {
                System.out.println("[ERROR] Input harus berupa bilangan bulat (angka), bukan huruf/kosong. Coba lagi.");
            }
        }
    }

    /** Membaca bilangan bulat dalam rentang [min, max]; diulang sampai valid. */
    private static int bacaInt(String prompt, int min, int max) {
        while (true) {
            int nilai = bacaInt(prompt);
            if (nilai >= min && nilai <= max) {
                return nilai;
            }
            System.out.println("[ERROR] Pilihan harus antara " + min + " sampai " + max + ". Coba lagi.");
        }
    }

    /** Membaca bilangan desimal; diulang sampai pengguna memasukkan angka. */
    private static double bacaDouble(String prompt) {
        while (true) {
            System.out.print(prompt);
            String baris = SCANNER.nextLine().trim();
            try {
                double nilai = Double.parseDouble(baris);
                if (Double.isNaN(nilai) || Double.isInfinite(nilai)) {
                    throw new NumberFormatException("bukan angka biasa");
                }
                return nilai;
            } catch (NumberFormatException e) {
                System.out.println("[ERROR] Input harus berupa angka, bukan huruf/kosong. Coba lagi.");
            }
        }
    }

    /** Membaca tanggal format dd-MM-yyyy; diulang sampai format dan tanggalnya valid. */
    private static LocalDate bacaTanggal(String prompt) {
        while (true) {
            System.out.print(prompt);
            String baris = SCANNER.nextLine().trim();
            try {
                return FormatUtil.parseTanggal(baris);
            } catch (DateTimeParseException e) {
                System.out.println("[ERROR] Format tanggal salah atau tanggal tidak ada. "
                        + "Gunakan " + FormatUtil.POLA_TANGGAL + ", contoh 25-11-2026.");
            }
        }
    }
}
