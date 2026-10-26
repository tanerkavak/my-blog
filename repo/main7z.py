import py7zr

klasor = "klasör_adi"
arsiv = "klasör_adi.7z"

filters = [
    {
        "id": py7zr.FILTER_LZMA2,
        "preset": 9,
    }
]

with py7zr.SevenZipFile(arsiv, "w", filters=filters) as archive:
    archive.writeall(klasor, arcname=klasor)

print(f"Oluşturuldu: {arsiv}")
