package hotel;

/**
 * ADT (Abstract Data Type) STACK untuk menyimpan riwayat reservasi terakhir.
 *
 * Prinsip LIFO (Last In First Out): reservasi yang dibuat paling akhir berada di
 * puncak (top) dan menjadi yang pertama dibatalkan (fitur "batalkan reservasi terakhir").
 *
 * Implementasi memakai ARRAY berkapasitas tetap. Atribut internal bersifat private,
 * dunia luar hanya boleh memakai operasi publik: push, pop, peek, isEmpty, isFull, size.
 *
 * Kondisi batas ditangani tanpa crash:
 * - push saat penuh  -> mengembalikan false
 * - pop/peek saat kosong -> mengembalikan null
 *
 * Kompleksitas waktu semua operasi inti (push, pop, peek, isEmpty, isFull, size): O(1).
 *
 * @author Tirta Apriliansyah (NIM 22515065)
 */
public class StackRiwayat {

    /** Kapasitas bawaan bila konstruktor default dipakai. */
    private static final int KAPASITAS_DEFAULT = 5;

    // ====================== ATRIBUT INTERNAL (private) ======================
    private Reservasi[] data;   // tempat penyimpanan elemen
    private int top;            // indeks elemen teratas; -1 berarti stack kosong
    private int kapasitas;      // jumlah maksimal elemen

    // ====================== KONSTRUKTOR ======================

    /** Konstruktor default: kapasitas 5. */
    public StackRiwayat() {
        this(KAPASITAS_DEFAULT);
    }

    /**
     * Konstruktor berparameter.
     *
     * @param kapasitas jumlah maksimal elemen (minimal 1)
     * @throws IllegalArgumentException bila kapasitas kurang dari 1
     */
    public StackRiwayat(int kapasitas) {
        if (kapasitas < 1) {
            throw new IllegalArgumentException("Kapasitas stack minimal 1.");
        }
        this.kapasitas = kapasitas;
        this.data = new Reservasi[kapasitas];
        this.top = -1; // -1 = kosong
    }

    // ====================== OPERASI ADT ======================

    /**
     * PUSH: menambahkan reservasi ke puncak stack.
     * Prasyarat : stack tidak penuh dan reservasi tidak null.
     * Efek      : size bertambah 1, reservasi menjadi elemen teratas.
     *
     * @param reservasi reservasi yang disimpan
     * @return true bila berhasil, false bila stack penuh atau reservasi null
     */
    public boolean push(Reservasi reservasi) {
        if (reservasi == null || isFull()) {
            return false;
        }
        top++;
        data[top] = reservasi;
        return true;
    }

    /**
     * POP: mengambil dan menghapus elemen teratas.
     * Prasyarat : stack tidak kosong.
     * Efek      : size berkurang 1.
     *
     * @return reservasi teratas, atau null bila stack kosong
     */
    public Reservasi pop() {
        if (isEmpty()) {
            return null;
        }
        Reservasi hasil = data[top];
        data[top] = null; // lepaskan referensi agar tidak tertahan di memori
        top--;
        return hasil;
    }

    /**
     * PEEK: melihat elemen teratas TANPA menghapusnya.
     *
     * @return reservasi teratas, atau null bila stack kosong
     */
    public Reservasi peek() {
        if (isEmpty()) {
            return null;
        }
        return data[top];
    }

    /** @return true bila stack tidak berisi elemen. */
    public boolean isEmpty() {
        return top == -1;
    }

    /** @return true bila jumlah elemen sudah sama dengan kapasitas. */
    public boolean isFull() {
        return top == kapasitas - 1;
    }

    /** @return jumlah elemen yang sedang tersimpan. */
    public int size() {
        return top + 1;
    }

    /** @return kapasitas maksimal stack. */
    public int getKapasitas() {
        return kapasitas;
    }

    /** CLEAR: mengosongkan seluruh isi stack. Kompleksitas O(n). */
    public void clear() {
        for (int i = 0; i <= top; i++) {
            data[i] = null;
        }
        top = -1;
    }

    /**
     * Menampilkan isi stack dari puncak (terbaru) ke dasar (terlama).
     * Menangani kondisi kosong dengan pesan, bukan error.
     */
    public void tampilkan() {
        System.out.println("Kapasitas: " + kapasitas + " | Terisi: " + size()
                + " | isEmpty: " + isEmpty() + " | isFull: " + isFull());
        if (isEmpty()) {
            System.out.println("(Stack kosong - belum ada riwayat reservasi)");
            return;
        }
        System.out.println("      " + Reservasi.header());
        for (int i = top; i >= 0; i--) {
            String penanda = (i == top) ? "TOP->" : "     ";
            System.out.print(penanda + " ");
            data[i].tampilkanInfo();
        }
        System.out.println("(BOTTOM = reservasi tertua, TOP = reservasi terbaru)");
    }
}
