import streamlit as st
import os
import re

# =========================================================
# JUDUL APLIKASI
# =========================================================

st.set_page_config(
    page_title="AI Tutor Bahasa Indonesia",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Tutor Bahasa Indonesia")
st.write(
    "Tutor Bahasa Indonesia berbasis database materi pembelajaran."
)

# =========================================================
# LOKASI DATABASE
# =========================================================

DATABASE_FOLDER = os.path.join(
    os.path.dirname(__file__),
    "..",
    "DATA BASE"
)

# =========================================================
# MEMBACA SEMUA FILE DATABASE
# =========================================================

def baca_database():
    semua_materi = {}

    if not os.path.exists(DATABASE_FOLDER):
        return semua_materi

    for nama_file in os.listdir(DATABASE_FOLDER):

        lokasi_file = os.path.join(
            DATABASE_FOLDER,
            nama_file
        )

        # Hanya membaca file, bukan folder
        if os.path.isfile(lokasi_file):

            try:
                with open(
                    lokasi_file,
                    "r",
                    encoding="utf-8"
                ) as file:

                    isi = file.read().strip()

                if isi:
                    semua_materi[nama_file] = isi

            except UnicodeDecodeError:

                try:
                    with open(
                        lokasi_file,
                        "r",
                        encoding="latin-1"
                    ) as file:

                        isi = file.read().strip()

                    if isi:
                        semua_materi[nama_file] = isi

                except:
                    pass

    return semua_materi


database = baca_database()

# =========================================================
# CEK DATABASE
# =========================================================

if database:

    st.success(
        f"✅ Database berhasil terhubung! "
        f"{len(database)} materi ditemukan."
    )

else:

    st.error(
        "❌ Database tidak ditemukan."
    )

# =========================================================
# DAFTAR MATERI
# =========================================================

st.sidebar.header("📖 Materi Tersedia")

if database:

    for nama_file in database.keys():

        nama_materi = os.path.splitext(
            nama_file
        )[0]

        st.sidebar.write(
            "📘 " + nama_materi
        )

# =========================================================
# FUNGSI MEMBERSIHKAN TEKS
# =========================================================

def bersihkan_teks(teks):

    teks = teks.lower()

    teks = re.sub(
        r"[^a-zA-ZÀ-ÿ0-9\s]",
        " ",
        teks
    )

    teks = re.sub(
        r"\s+",
        " ",
        teks
    )

    return teks.strip()


# =========================================================
# FUNGSI MENCARI JAWABAN
# =========================================================

def cari_jawaban(pertanyaan):

    if not database:
        return None, None

    pertanyaan_bersih = bersihkan_teks(
        pertanyaan
    )

    kata_pertanyaan = set(
        pertanyaan_bersih.split()
    )

    hasil = []

    for nama_file, isi in database.items():

        teks_bersih = bersihkan_teks(isi)

        kata_teks = set(
            teks_bersih.split()
        )

        # Menghitung kata yang sama
        kecocokan = kata_pertanyaan.intersection(
            kata_teks
        )

        skor = len(kecocokan)

        if skor > 0:

            hasil.append(
                (
                    skor,
                    nama_file,
                    isi
                )
            )

    # Tidak ditemukan
    if not hasil:
        return None, None

    # Mengurutkan berdasarkan kecocokan
    hasil.sort(
        key=lambda x: x[0],
        reverse=True
    )

    skor_tertinggi = hasil[0][0]
    nama_file = hasil[0][1]
    isi = hasil[0][2]

    # =====================================================
    # MENCARI BAGIAN MATERI YANG RELEVAN
    # =====================================================

    paragraf = re.split(
        r"\n\s*\n",
        isi
    )

    paragraf_cocok = []

    for p in paragraf:

        p_bersih = bersihkan_teks(p)

        kata_p = set(
            p_bersih.split()
        )

        kecocokan = kata_pertanyaan.intersection(
            kata_p
        )

        if len(kecocokan) > 0:

            paragraf_cocok.append(
                (
                    len(kecocokan),
                    p.strip()
                )
            )

    if paragraf_cocok:

        paragraf_cocok.sort(
            key=lambda x: x[0],
            reverse=True
        )

        jawaban = "\n\n".join(
            [
                p[1]
                for p in paragraf_cocok[:3]
            ]
        )

    else:

        # Jika tidak menemukan paragraf khusus,
        # tampilkan bagian awal materi
        jawaban = isi[:3000]

    return nama_file, jawaban


# =========================================================
# BAGIAN TANYA AI
# =========================================================

st.subheader("🤖 Tanya AI Tutor")

st.write(
    "Silakan ajukan pertanyaan berdasarkan materi "
    "Bahasa Indonesia yang tersedia."
)

pertanyaan = st.chat_input(
    "Contoh: Apa yang dimaksud semantik?"
)

# =========================================================
# PROSES PERTANYAAN
# =========================================================

if pertanyaan:

    # Menampilkan pertanyaan siswa
    with st.chat_message("user"):

        st.write(pertanyaan)

    # Mencari jawaban
    nama_file, jawaban = cari_jawaban(
        pertanyaan
    )

    # Menampilkan jawaban
    with st.chat_message("assistant"):

        if jawaban:

            st.write("📚 **Jawaban berdasarkan database:**")

            st.write(jawaban)

            st.caption(
                "📖 Sumber materi: "
                + os.path.splitext(nama_file)[0]
            )

        else:

            st.write(
                "Maaf, pertanyaan tersebut belum "
                "ditemukan dalam database materi."
            )

            st.write(
                "Coba gunakan kata kunci yang sesuai "
                "dengan materi yang tersedia."
            )


# =========================================================
# INFORMASI DATABASE
# =========================================================

with st.expander("🔎 Lihat informasi database"):

    st.write(
        "Lokasi database:"
    )

    st.code(
        os.path.abspath(DATABASE_FOLDER)
    )

    st.write(
        f"Jumlah materi: **{len(database)}**"
    )