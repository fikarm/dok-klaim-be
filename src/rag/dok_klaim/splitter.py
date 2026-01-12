import re
import pymupdf
from src.rag.dok_klaim.segmentation import ocr, get_scanned_image


def norm_tgl(tgl: str):
    nama_bulan = [
        "Januari",
        "Februari",
        "Maret",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Agustus",
        "September",
        "Oktober",
        "November",
        "Desember",
    ]

    # d/m/Y
    for match in re.finditer(r"(\d{2})/(\d{2})/(\d{4})", tgl):
        tgl = tgl.replace(
            match.group(),
            "%s %s %s"
            % (
                match.group(1),
                nama_bulan[int(match.group(2)) - 1],
                match.group(3),
            ),
            1,
        )

    # Y-m-d
    for match in re.finditer(r"(\d{4})-(\d{2})-(\d{2})", tgl):
        tgl = tgl.replace(
            match.group(),
            "%s %s %s"
            % (
                match.group(3),
                nama_bulan[int(match.group(2)) - 1],
                match.group(1),
            ),
            1,
        )

    # d-m-Y
    for match in re.finditer(r"(\d{2})-(\d{2})-(\d{4})", tgl):
        tgl = tgl.replace(
            match.group(),
            "%s %s %s"
            % (
                match.group(1),
                nama_bulan[int(match.group(2)) - 1],
                match.group(3),
            ),
            1,
        )

    return tgl


def norm(text: str):
    # sejajarkan tanda titik dua (:) dengan line sebelumnya
    text = re.sub(r"[\s\n]+:", ":", text)

    # sejajarkan tanda titik dua (:) dengan line berikutnya (selain list item)
    text = re.sub(r":[\s\n]+([^-])", ": \\1", text)
    text = re.sub(r":[\s\n]+-\n", ": -\n", text)
    text = re.sub(r":[\s\n]+-$", ": -", text)

    # sejajarkan tanda strip
    text = re.sub(r"-[\s\n]+-", "- -", text)

    # sejajarkan Rp
    text = re.sub(r"Rp[\s\n]+", "Rp ", text)

    # strip leading & trailing space setiap line
    text = re.sub(r"^\s+", "", text)
    text = re.sub(r"\s+$", "", text)

    # normalisasi tgl
    text = norm_tgl(text)

    return text


def block_height(block: tuple):
    """
    @param tuple block: return value of `pymupdf.get_text_blocks()`
    """
    return block[3] - block[1]


def block_distance(block1: tuple, block2: tuple):
    """
    @param tuple block1: return value of `pymupdf.get_text_blocks()`
    @param tuple block2: return value of `pymupdf.get_text_blocks()`
    """
    return block2[1] - block1[3]


def group_by_block_distance(blocks: list[tuple]) -> list[list[tuple]]:
    """
    line dengan tinggi yg sama dan jarak yg berdekatan akan menjadi satu group
    """
    i = 0
    groups: list[list[tuple]] = [[]]
    prev = blocks[0]
    for block in blocks:
        # jika jarak antara line sekarang dengan line sebelumnya
        sama_tinggi = block_height(block) == block_height(prev)
        berdekatan = block_distance(prev, block) <= block_height(prev)

        if sama_tinggi and berdekatan:
            # satu group
            groups[i].append(block)
        else:
            # beda group
            groups.append([block])
            i += 1

        prev = block

    return groups


def merge_single_lines(chunks: list[str]) -> list[str]:
    """
    Menggabungkan chunk yang hanya satu baris menjadi satu chunk.
    """
    g = 0
    groups = [""]
    prev: str = ""
    for chunk in chunks:
        if len(prev.splitlines()) == 1:
            # pass
            groups[g] += "\n" + chunk
        else:
            # if len(chunk.splitlines()) == 1:
            #     groups[g] += "\n" + chunk
            # else:
            #     groups.append(chunk)
            groups.append(chunk)
            g += 1
        prev = chunk

    # hapus chunk pertama jika kosong
    groups = groups[1:] if groups[0] == "" else groups

    return groups


def merge_by_colon(chunks: list[str]) -> list[str]:
    """
    menggabungkan line berdasarkan dangling colon (:).
    1. jika chunk diawali tanda (:), maka gabungkan dengan chunk sebelumnya
    2. jika chunk diakhiri tanda (:), maka gabungkan dengan chunk setelahnya
    3. jika chunk ada tanda (:), maka gabungkan dengan chunk sebelumnya
    4. selain itu beda jadikan chunk terpisah
    """
    groups = [""]
    g = 0
    for chunk in chunks:
        # Handle dangling colon (:)
        # jika chunk sebelumnya diakhiri tanda (:)
        if re.findall(r":[\s\n]*$", groups[g]):
            # maka gabungkan dg baris sebelumnya
            groups[g] += "\n" + chunk
        # jika chunk saat ini diawali tanda (:)
        elif re.findall(r"^[\s\n]*:", chunk):
            # maka gabungkan dg baris sebelumnya
            groups[g] += "\n" + chunk
        elif ":" in chunk:
            groups[g] += "\n" + chunk
        else:
            groups.append(chunk)
            g += 1

    # hapus chunk pertama jika kosong
    groups = groups[1:] if groups[0] == "" else groups

    return groups


def chunking(pages: list[pymupdf.Page]) -> list[str]:
    combined_chunks: list[str] = []
    for page in pages:
        blocks = page.get_text_blocks()
        if not blocks:
            continue

        groups = group_by_block_distance(blocks)

        chunks = []
        for g in groups:
            content = "\n".join([b[4] for b in g])
            # content = norm(content)
            chunks.append(content.strip())

        chunks = merge_by_colon(chunks)

        chunks = [norm(c) for c in chunks]

        chunks = merge_single_lines(chunks)

        combined_chunks += chunks

    # untuk scanned images yang tidak ada text blocks,
    # maka chunk adalah hasil OCR per page.
    if not combined_chunks:
        for page in pages:
            scanned = get_scanned_image(page)

            if not scanned:
                break

            combined_chunks.append(ocr(scanned))

    return combined_chunks
