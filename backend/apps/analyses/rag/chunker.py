def split_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[str]:
    """
    Metni belirli uzunlukta ve birbiriyle örtüşen parçalara ayırır.
    """

    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size sıfırdan büyük olmalıdır.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap negatif olamaz.")

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap, chunk_size değerinden küçük olmalıdır."
        )

    clean_text = " ".join(text.split())

    chunks = []
    start = 0
    step = chunk_size - chunk_overlap

    while start < len(clean_text):
        end = start + chunk_size
        chunk = clean_text[start:end].strip()

        if not chunk:
            break

        # Çok kısa son chunk oluşmasını engelle
        if len(chunk) < chunk_size * 0.3 and chunks:
            chunks[-1] += " " + chunk
            break

        chunks.append(chunk)

        start += step

    return chunks