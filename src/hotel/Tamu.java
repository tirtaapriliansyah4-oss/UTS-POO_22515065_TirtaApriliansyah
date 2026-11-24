package hotel;

/**
 * Class entitas Tamu: mewakili orang yang memesan dan menginap di hotel.
 *
 * Selain data diri, Tamu menyimpan total malam menginap yang dipakai untuk
 * menentukan kategori tamu (Reguler, Silver, Gold).
 *
 * @author Tirta Apriliansyah (NIM 22515065)
 */
public class Tamu {

    /** Batas total malam menginap agar tamu dianggap tamu setia (Gold). */
    public static final int BATAS_TAMU_SETIA = 5;

    // ====================== ATRIBUT (semua private) ======================
    private String kodeTamu;          // kunci unik, misal "T001"
    private String nama;
    private String noTelepon;         // hanya angka, 8-15 digit
    private int umur;                 // 17 - 120
    private int totalMalamMenginap;   // bertambah setiap check-out

    // ====================== KONSTRUKTOR ======================

    /** Konstruktor default: tamu kosong dengan nilai awal yang valid. */
    public Tamu() {
        this("T000", "Tamu Baru", "00000000", 17);
    }

    /**
     * Konstruktor berparameter.
     *
     * @param kodeTamu  kode unik tamu
     * @param nama      nama lengkap
     * @param noTelepon nomor telepon (angka saja, 8-15 digit)
     * @param umur      umur dalam tahun (17-120)
     */
    public Tamu(String kodeTamu, String nama, String noTelepon, int umur) {
        setKodeTamu(kodeTamu);
        setNama(nama);
        setNoTelepon(noTelepon);
        setUmur(umur);
        this.totalMalamMenginap = 0; // tamu baru belum pernah menginap
    }

    // ====================== GETTER ======================
    public String getKodeTamu() {
        return kodeTamu;
    }

    public String getNama() {
        return nama;
    }

    public String getNoTelepon() {
        return noTelepon;
    }

    public int getUmur() {
        return umur;
    }

    public int getTotalMalamMenginap() {
        return totalMalamMenginap;
    }

    // ====================== SETTER + VALIDASI ======================

    public void setKodeTamu(String kodeTamu) {
        if (kodeTamu == null || kodeTamu.trim().isEmpty()) {
            throw new IllegalArgumentException("Kode tamu tidak boleh kosong.");
        }
        this.kodeTamu = kodeTamu.trim().toUpperCase();
    }

    public void setNama(String nama) {
        if (nama == null || nama.trim().isEmpty()) {
            throw new IllegalArgumentException("Nama tamu tidak boleh kosong.");
        }
        this.nama = nama.trim();
    }

    public void setNoTelepon(String noTelepon) {
        // regex \\d{8,15} = hanya digit, panjang 8 sampai 15
        if (noTelepon == null || !noTelepon.trim().matches("\\d{8,15}")) {
            throw new IllegalArgumentException("Nomor telepon harus berupa angka 8 sampai 15 digit.");
        }
        this.noTelepon = noTelepon.trim();
    }

    public void setUmur(int umur) {
        if (umur < 17 || umur > 120) {
            throw new IllegalArgumentException("Umur tamu harus antara 17 sampai 120 tahun.");
        }
        this.umur = umur;
    }

    public void setTotalMalamMenginap(int totalMalamMenginap) {
        if (totalMalamMenginap < 0) {
            throw new IllegalArgumentException("Total malam menginap tidak boleh negatif.");
        }
        this.totalMalamMenginap = totalMalamMenginap;
    }

    // ====================== METHOD PERILAKU ======================

    /**
     * Menambah total malam menginap (dipanggil saat check-out).
     *
     * @param malam jumlah malam yang baru selesai (harus > 0)
     */
    public void tambahMalamMenginap(int malam) {
        if (malam <= 0) {
            throw new IllegalArgumentException("Tambahan malam harus lebih dari 0.");
        }
        this.totalMalamMenginap += malam;
    }

    /** @return true bila total malam menginap sudah mencapai batas tamu setia. */
    public boolean isTamuSetia() {
        return totalMalamMenginap >= BATAS_TAMU_SETIA;
    }

    /** @return kategori tamu: Reguler (0 malam), Silver (1-4), Gold (5 atau lebih). */
    public String getKategori() {
        if (totalMalamMenginap == 0) {
            return "Reguler";
        }
        return isTamuSetia() ? "Gold" : "Silver";
    }

    /** @return judul kolom untuk tabel daftar tamu. */
    public static String header() {
        return String.format("%-8s %-22s %-16s %-6s %-12s %-10s",
                "Kode", "Nama", "No. Telepon", "Umur", "Total Malam", "Kategori");
    }

    /** Mencetak satu baris informasi tamu (cocok dengan header()). */
    public void tampilkanInfo() {
        System.out.printf("%-8s %-22s %-16s %-6d %-12d %-10s%n",
                kodeTamu, nama, noTelepon, umur, totalMalamMenginap, getKategori());
    }
}
