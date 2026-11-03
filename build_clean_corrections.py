import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

# Curated clean, accurate Indonesian translations for all flagged words
corrections = {
    # 1. User mentioned & formula error words
    "centre": {
        "n.": "pusat, tengah",
        "v.": "memusatkan, menitikberatkan"
    },
    "defence": {
        "n.": "pertahanan, pembelaan"
    },
    "downwards": {
        "adv.": "ke bawah, mengarah ke bawah, menurun"
    },
    "upwards": {
        "adv.": "ke atas, mengarah ke atas, naik"
    },
    "upon": {
        "prep.": "di atas, saat, segera setelah"
    },
    "disc": {
        "n.": "cakram, piringan, piringan hitam"
    },
    "enquiry": {
        "n.": "pertanyaan, penyelidikan, permintaan keterangan"
    },
    "judgement": {
        "n.": "penilaian, pertimbangan, keputusan"
    },
    
    # 2. Homonyms & Sense Mismatches
    "lead": {
        "v.": "memimpin, memandu, mengarahkan",
        "n.": "pemimpin, keunggulan, petunjuk"
    },
    "leading": {
        "adj.": "terkemuka, terdepan, utama"
    },
    "bear": {
        "n.": "beruang",
        "v.": "menahan, menanggung, memikul"
    },
    "cross": {
        "v., n.": "menyeberang, menyilang, salib"
    },
    "fair": {
        "adj.": "adil, wajar, cukup baik"
    },
    "fall": {
        "v.": "jatuh, runtuh, turun",
        "n.": "musim gugur, kejatuhan, penurunan"
    },
    "board": {
        "n.": "papan, dewan, pengurus",
        "v.": "menaiki (pesawat/kapal/kereta), menumpang"
    },
    "book": {
        "v.": "memesan (tiket/tempat), membukukan"
    },
    "can": {
        "n.": "kaleng"
    },
    "close": {
        "adj.": "dekat, akrab, rapat",
        "adv.": "dekat, berdekatan",
        "n.": "penutupan, akhir"
    },
    "fly": {
        "n.": "lalat",
        "v.": "terbang, menerbangkan"
    },
    "last": {
        "v.": "bertahan, berlangsung",
        "adv., n.": "terakhir, paling akhir",
        "det.": "terakhir, yang lalu"
    },
    "light": {
        "v.": "menyalakan, menerangi",
        "adj.": "ringan, terang, muda (warna)"
    },
    "may": {
        "modal v.": "boleh, mungkin, dapat"
    },
    "present": {
        "v.": "menyajikan, mempersembahkan, memperkenalkan"
    },
    "record": {
        "n., v.": "catatan, rekor, merekam, mencatat"
    },
    "recording": {
        "n.": "rekaman, proses merekam"
    },
    "rest": {
        "n. (remaining part)": "sisa, bagian yang tersisa",
        "n., v. (sleep/relax)": "beristirahat, istirahat, bersantai"
    },
    "ring": {
        "n. (cincin/arena)": "cincin, arena, gelanggang",
        "v. (berdering)": "berdering, menelepon, membunyikan"
    },
    "rock": {
        "n. (stone)": "batu, batu karang",
        "n. (music)": "musik rok"
    },
    "second": {
        "adv.": "kedua, di tempat kedua"
    },
    "spring": {
        "v.": "melompat, memantul, muncul tiba-tiba"
    },
    "star": {
        "v.": "membintangi, menjadi bintang utama"
    },
    "stick": {
        "v.": "menempelkan, melekat, menusukkan",
        "n.": "tongkat, batang, ranting"
    },
    "tear": {
        "v., n. (merobek)": "merobek, menyobek, sobekan",
        "n. (air mata)": "air mata"
    },
    "train": {
        "v.": "melatih, berlatih"
    },
    "trip": {
        "v.": "tersandung, menjegal"
    },
    "wave": {
        "v.": "melambai, mengibarkan",
        "n.": "gelombang, ombak, lambaian"
    },
    "will": {
        "n.": "kemauan, tekad, surat wasiat"
    },
    "wind": {
        "v.": "memutar, melilit, berliku-liku",
        "n.": "angin"
    },
    "object": {
        "v.": "keberatan, menolak"
    },
    "kind": {
        "adj. (caring)": "baik hati, ramah, murah hati",
        "n. (type)": "jenis, macam, tipe"
    },
    "bank": {
        "n. (river)": "tepi sungai, bantaran sungai"
    },
    
    # 3. Untranslated words & British variants
    "according to": "menurut, sesuai dengan, berdasarkan",
    "active": "aktif, giat, bertenaga",
    "all right": "baiklah, baik-baik saja, tidak apa-apa",
    "any more": "lagi, tidak lagi",
    "app": "aplikasi (perangkat lunak)",
    "badly": "dengan buruk, parah, sangat",
    "based": "berdasarkan, berbasis",
    "behaviour": "perilaku, tingkah laku, budi pekerti",
    "brilliant": "cemerlang, luar biasa, sangat cerdas",
    "broken": "rusak, patah, hancur, pecah",
    "camp": "berkemah, perkemahan, kamp",
    "camping": "berkemah, kamping",
    "closed": "tutup, tertutup",
    "coach": {
        "n.": "pelatih, bus wisata, gerbong",
        "v.": "melatih, membina"
    },
    "cycle": "bersepeda, mengayuh sepeda, siklus",
    "divorced": "bercerai, bercerai hidup",
    "download": "mengunduh, berkas unduhan",
    "driving": "mengemudi, berkendara",
    "electronic": "elektronik, secara elektronik",
    "gift": "hadiah, kado, bakat, pemberian",
    "hockey": "hoki (cabang olahraga)",
    "included": "termasuk, tercakup, sudah dihitung",
    "individual": "individu, perseorangan, pribadi",
    "involve": "melibatkan, mengikutsertakan",
    "jewellery": "perhiasan, perhiasan emas/permata",
    "journalist": "wartawan, jurnalis",
    "knock": {
        "v.": "mengetuk, memukul, membentur",
        "n.": "ketukan, pukulan, bunyi ketukan"
    },
    "lifestyle": "gaya hidup, pola hidup",
    "lorry": "truk, truk pengangkut",
    "petrol": "bensin, bahan bakar minyak",
    "pleased": "senang, gembira, puas",
    "pub": "kedai minum, pub",
    "role": "peran, fungsi, lakon",
    "running": "lari, berlari, olahraga lari",
    "secretary": "sekretaris",
    "smartphone": "ponsel pintar, telepon pintar",
    "teenage": "remaja, usia belasan",
    "themselves": "diri mereka sendiri",
    "towards": "menuju, ke arah, terhadap",
    "traveller": "pelancong, pelancong wisata, musafir",
    "used to": "dulu biasa, terbiasa, pernah",
    "wedding": "pernikahan, pesta pernikahan",
    "achievement": "prestasi, pencapaian, keberhasilan",
    "analyse": "menganalisis, mengkaji, menelaah",
    "annoying": "menjengkelkan, menyebalkan, mengganggu",
    "backwards": "ke belakang, mundur, terbalik",
    "campaign": "kampanye, mengadakan kampanye",
    "coloured": "berwarna, memiliki warna",
    "confused": "bingung, rancu, keliru",
    "determined": "bertekad bulat, gigih, teguh",
    "educated": "berpendidikan, terpelajar, berilmu",
    "engaged": "bertunangan, sibuk, terpakai",
    "experienced": "berpengalaman, berjam terbang",
    "fascinating": "mempesona, mengagumkan, sangat menarik",
    "favour": {
        "n.": "kebaikan, bantuan, dukungan, kemurahan hati",
        "v.": "mendukung, menyukai, mengutamakan"
    },
    "gather": "mengumpulkan, berkumpul, menghimpun",
    "goods": "barang, barang dagangan, komoditas",
    "incredibly": "luar biasa, sangat, tak disangka",
    "indoors": "di dalam ruangan, ke dalam rumah",
    "injured": "terluka, cedera",
    "involved": "terlibat, turut serta, rumit",
    "latest": {
        "adj.": "terbaru, paling mutakhir, terkini",
        "n.": "kabar terbaru, hal terkini"
    },
    "living": "hidup, kehidupan, biaya hidup, nafkah",
    "located": "terletak, berlokasi, berada",
    "mall": "pusat perbelanjaan, mal",
    "necessarily": "pasti, selalu, niscaya, harus",
    "organized": "teratur, terorganisir, rapi",
    "ought to": "seharusnya, semestinya, patutnya",
    "planning": "perencanaan, rencana kerja",
    "possibly": "mungkin, barangkali, bisa jadi",
    "prepared": "siap, bersiap, bersedia",
    "racing": "balapan, perlombaan balap",
    "related": "terkait, berhubungan, bertalian, bersanak",
    "retired": "pensiun, purnatugas",
    "rugby": "rugbi (olahraga bola lonjong)",
    "specifically": "secara khusus, spesifik, persisnya",
    "spoken": "lisan, terucap, diucapkan",
    "tyre": "ban roda, ban mobil/motor",
    "wonder": "bertanya-tanya, kagum, heran, keajaiban",
    "worldwide": "seluruh dunia, mendunia",
    "arms": "senjata, persenjataan (militer)",
    "associated": "terkait, terhubung, berhubungan",
    "basically": "pada dasarnya, pokoknya, intinya",
    "complicated": "rumit, kompleks, berbelit-belit",
    "confusing": "membingungkan, memusingkan",
    "convinced": "yakin, merasa percaya, mantap",
    "curved": "melengkung, berlekuk",
    "fully": "sepenuhnya, secara penuh, tuntas",
    "hesitate": "ragu-ragu, bimbang, segan",
    "honour": "kehormatan, memuliakan, menghormati",
    "housing": "perumahan, pemukiman, hunian",
    "humour": "humor, kelucuan, rasa jenaka",
    "increasingly": "semakin, kian, bertambah-tambah",
    "install": "memasang, menginstal, melantik",
    "labour": "tenaga kerja, kaum buruh, persalinan",
    "licence": "izin, lisensi, surat izin mengemudi",
    "long-term": "jangka panjang",
    "minimum": "minimum, paling sedikit, batas terendah",
    "offence": "pelanggaran, tindak pidana, serangan",
    "opposed": "menentang, berlawanan, berseberangan",
    "rescue": "menyelamatkan, penyelamatan, pertolongan",
    "saving": "penghematan, tabungan, simpanan",
    
    # 4. Dictionary artifacts cleanup
    "along": "di sepanjang, terus, bersama",
    "bean": "buncis, kacang polong, tauge",
    "bone": "tulang, duri (ikan)",
    "brain": "otak, pikiran, akal budi",
    "finger": "jari tangan, jari",
    "fix": {
        "v.": "memperbaiki, memasang, menentukan",
        "n.": "perbaikan, jalan keluar, kesulitan"
    },
    "fixed": "tetap, baku, sudah diperbaiki",
    "fold": {
        "v.": "melipat, merangkul, membungkus",
        "n.": "lipatan, lekukan"
    },
    "folding": "dapat dilipat, lipat",
    "grass": "rumput, padang rumput",
    "guy": "pria, orang, teman",
    "instrument": "alat musik, instrumen, peralatan instrumen",
    "jazz": "aliran musik jaz, jaz",
    "lemon": "jeruk lemon, buah sitrun",
    "score": "skor, angka nilai, mencetak skor",
    "speed": {
        "n.": "kecepatan, laju",
        "v.": "melaju cepat, melesat, mempercepat"
    },
    "square": "persegi, kuadrat, bujur sangkar",
    "straight": "lurus, langsung, jujur",
    "wow": "wah! (ungkapan kagum), memukau",
    "bomb": "bom, meledakkan bom, membom",
    "cotton": "kapas, katun, kain katun",
    "dirt": "kotoran, debu, noda",
    "percentage": "persentase, kadar persen",
    "sharp": "tajam, runcing, cerdas, tajam pikiran",
    "broad": "luas, lebar, lapang",
    "bush": "semak-semak, belukar",
    "drag": "menyeret, menarik dengan susah payah",
    "grab": "meraih, menyambar, merebut, mengambil cepat",
    "grand": "megah, agung, luar biasa",
    "organ": "organ tubuh, alat musik organ",
    "scream": "menjerit, memekik, teriakan",
    "stiff": "kaku, keras, tegang"
}

with open('clean_corrections_map.json', 'w', encoding='utf-8') as f:
    json.dump(corrections, f, ensure_ascii=False, indent=2)

print(f"Curated dictionary created with {len(corrections)} entries!")
