package hotel;

import java.text.NumberFormat;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.ResolverStyle;
import java.util.Locale;

/**
 * Kelas utilitas kecil untuk memformat dan membaca data.
 * Dipisahkan dari class entitas agar kode format tidak ditulis berulang-ulang.
 *
 * Semua method bersifat static sehingga tidak perlu membuat objek FormatUtil.
 *
 * @author Tirta Apriliansyah (NIM 22515065)
 */
public final class FormatUtil {

    /** Format tanggal yang dipakai aplikasi: hari-bulan-tahun, contoh 25-11-2026. */
    public static final String POLA_TANGGAL = "dd-MM-yyyy";

    /**
     * Formatter STRICT: tanggal yang tidak ada di kalender (misal 31-02-2026)
     * akan ditolak, bukan dibulatkan otomatis.
     * Pola "uuuu" dipakai (bukan "yyyy") karena wajib untuk mode STRICT.
     */
    private static final DateTimeFormatter FORMATTER_TANGGAL =
            DateTimeFormatter.ofPattern("dd-MM-uuuu").withResolverStyle(ResolverStyle.STRICT);

    /** Konstruktor private: class utilitas tidak boleh dibuat objeknya. */
    private FormatUtil() {
    }

    /**
     * Mengubah angka menjadi teks rupiah, contoh 350000 menjadi "Rp 350.000".
     *
     * @param nilai nominal uang
     * @return teks rupiah dengan pemisah ribuan titik
     */
    public static String formatRupiah(double nilai) {
        NumberFormat nf = NumberFormat.getNumberInstance(Locale.forLanguageTag("id-ID"));
        nf.setMaximumFractionDigits(0);
        return "Rp " + nf.format(nilai);
    }

    /**
     * Mengubah LocalDate menjadi teks dd-MM-yyyy.
     *
     * @param tanggal tanggal yang akan diformat (boleh null)
     * @return teks tanggal, atau "-" bila null
     */
    public static String formatTanggal(LocalDate tanggal) {
        if (tanggal == null) {
            return "-";
        }
        return tanggal.format(FORMATTER_TANGGAL);
    }

    /**
     * Membaca teks tanggal dd-MM-yyyy menjadi LocalDate.
     *
     * @param teks teks tanggal, contoh "25-11-2026"
     * @return objek LocalDate
     * @throws java.time.format.DateTimeParseException bila format salah / tanggal tidak ada
     */
    public static LocalDate parseTanggal(String teks) {
        return LocalDate.parse(teks.trim(), FORMATTER_TANGGAL);
    }
}
