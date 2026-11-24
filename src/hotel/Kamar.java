package hotel;

/**
 * Class entitas Kamar: mewakili satu kamar fisik di hotel.
 *
 * Aturan bisnis yang dijaga class ini:
 * 1. Kamar yang sedang terisi TIDAK boleh dipesan lagi (method pesan()).
 * 2. Biaya menginap = tarif per malam x jumlah malam (method hitungBiaya()).
 * 3. Tarif harus lebih dari 0 (validasi di setTarifPerMalam()).
 *
 * @author Tirta Apriliansyah (NIM 22515065)
 */
public class Kamar {

    /** Tipe kamar yang diizinkan. Konstanta ditulis UPPER_CASE sesuai konvensi Java. */
    public static final String[] TIPE_VALID = {"Standard", "Deluxe", "Suite"};

    // ====================== ATRIBUT (semua private) ======================
    private String nomorKamar;     // kunci unik kamar, misal "101"
    private String tipe;           // Standard / Deluxe / Suite
    private double tarifPerMalam;  // dalam rupiah
    private int kapasitas;         // jumlah orang maksimal
    private boolean terisi;        // true = sedang ditempati/dipesan

    // ====================== KONSTRUKTOR ======================

    /** Konstruktor default: membuat kamar standar dengan nilai awal yang valid. */
    public Kamar() {
        // "this(...)" memanggil konstruktor berparameter di bawah dengan nilai default
        this("000", "Standard", 100000, 1);
    }

    /**
     * Konstruktor berparameter. Setiap nilai lewat setter agar divalidasi.
     *
     * @param nomorKamar    nomor kamar (tidak boleh kosong)
     * @param tipe          Standard / Deluxe / Suite
     * @param tarifPerMalam tarif per malam, harus lebih dari 0
     * @param kapasitas     kapasitas orang, 1 sampai 6
     */
    public Kamar(String nomorKamar, String tipe, double tarifPerMalam, int kapasitas) {
        setNomorKamar(nomorKamar);
        setTipe(tipe);
        setTarifPerMalam(tarifPerMalam);
        setKapasitas(kapasitas);
        this.terisi = false; // kamar baru selalu kosong
    }

    // ====================== GETTER ======================
    public String getNomorKamar() {
        return nomorKamar;
    }

    public String getTipe() {
        return tipe;
    }

    public double getTarifPerMalam() {
        return tarifPerMalam;
    }

    public int getKapasitas() {
        return kapasitas;
    }

    public boolean isTerisi() {
        return terisi;
    }

    // ====================== SETTER + VALIDASI ======================

    public void setNomorKamar(String nomorKamar) {
        if (nomorKamar == null || nomorKamar.trim().isEmpty()) {
            throw new IllegalArgumentException("Nomor kamar tidak boleh kosong.");
        }
        if (nomorKamar.trim().length() > 10) {
            throw new IllegalArgumentException("Nomor kamar maksimal 10 karakter.");
        }
        this.nomorKamar = nomorKamar.trim();
    }

    public void setTipe(String tipe) {
        if (tipe == null || tipe.trim().isEmpty()) {
            throw new IllegalArgumentException("Tipe kamar tidak boleh kosong.");
        }
        // Cocokkan tanpa peduli huruf besar/kecil, lalu simpan versi baku
        for (String valid : TIPE_VALID) {
            if (valid.equalsIgnoreCase(tipe.trim())) {
                this.tipe = valid;
                return;
            }
        }
        throw new IllegalArgumentException("Tipe kamar harus Standard, Deluxe, atau Suite.");
    }

    public void setTarifPerMalam(double tarifPerMalam) {
        // ATURAN BISNIS: tarif harus > 0 (NaN juga ditolak)
        if (Double.isNaN(tarifPerMalam) || tarifPerMalam <= 0) {
            throw new IllegalArgumentException("Tarif per malam harus lebih dari 0.");
        }
        this.tarifPerMalam = tarifPerMalam;
    }

    public void setKapasitas(int kapasitas) {
        if (kapasitas < 1 || kapasitas > 6) {
            throw new IllegalArgumentException("Kapasitas kamar harus antara 1 sampai 6 orang.");
        }
        this.kapasitas = kapasitas;
    }

    public void setTerisi(boolean terisi) {
        this.terisi = terisi;
    }

    // ====================== METHOD PERILAKU ======================

    /** @return true bila kamar masih kosong dan boleh dipesan. */
    public boolean isTersedia() {
        return !terisi;
    }

    /**
     * Menandai kamar sebagai terisi.
     * ATURAN BISNIS: kamar yang sudah terisi tidak bisa dipesan lagi.
     *
     * @throws IllegalStateException bila kamar sudah terisi
     */
    public void pesan() {
        if (terisi) {
            throw new IllegalStateException(
                    "Kamar " + nomorKamar + " sedang terisi dan tidak dapat dipesan.");
        }
        this.terisi = true;
    }

    /** Mengosongkan kamar (dipakai saat check-out atau pembatalan). */
    public void kosongkan() {
        this.terisi = false;
    }

    /**
     * Menghitung biaya menginap.
     * ATURAN BISNIS: biaya = tarif per malam x jumlah malam.
     *
     * @param jumlahMalam lama menginap (harus > 0)
     * @return total biaya dalam rupiah
     */
    public double hitungBiaya(int jumlahMalam) {
        if (jumlahMalam <= 0) {
            throw new IllegalArgumentException("Jumlah malam harus lebih dari 0.");
        }
        return tarifPerMalam * jumlahMalam;
    }

    /** @return teks status: "Tersedia" atau "Terisi". */
    public String getStatusTeks() {
        return terisi ? "Terisi" : "Tersedia";
    }

    /** @return judul kolom untuk tabel daftar kamar. */
    public static String header() {
        return String.format("%-8s %-10s %-14s %-10s %-10s",
                "Nomor", "Tipe", "Tarif/Malam", "Kapasitas", "Status");
    }

    /** Mencetak satu baris informasi kamar (cocok dengan header()). */
    public void tampilkanInfo() {
        System.out.printf("%-8s %-10s %-14s %-10s %-10s%n",
                nomorKamar, tipe, FormatUtil.formatRupiah(tarifPerMalam),
                kapasitas + " orang", getStatusTeks());
    }
}
