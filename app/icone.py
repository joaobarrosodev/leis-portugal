"""O ícone da aplicação (app/icone.png, .icns e .ico), no estilo da imagem do projeto.

    python app/icone.py

Fundo verde-escuro e uma folha de papel com as linhas de um artigo: uma riscada a vermelho e a
redação nova a verde, como na imagem de partilha (`.github/social-preview.png`).
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


PASTA = Path(__file__).resolve().parent
L = 1024
VERDE, VERDE_ESCURO = (15, 61, 46), (10, 44, 33)
PAPEL, CINZA, ROSA = (247, 242, 231), (201, 193, 176), (216, 183, 176)
VERMELHO, VERDE_NOVO, OURO = (200, 16, 46), (120, 190, 150), (217, 164, 65)


def desenhar() -> Image.Image:
    img = Image.new("RGBA", (L, L), (0, 0, 0, 0))
    fundo = Image.new("RGBA", (L, L), VERDE + (255,))
    d = ImageDraw.Draw(fundo)
    for y in range(L):  # degradê suave de cima para baixo
        t = y / L
        d.line([(0, y), (L, y)], fill=tuple(int(a * (1 - t) + b * t) for a, b in zip(VERDE, VERDE_ESCURO, strict=False)) + (255,))
    mascara = Image.new("L", (L, L), 0)
    ImageDraw.Draw(mascara).rounded_rectangle((40, 40, L - 40, L - 40), 220, fill=255)
    img.paste(fundo, (0, 0), mascara)

    folha = Image.new("RGBA", (L, L), (0, 0, 0, 0))
    f = ImageDraw.Draw(folha)
    x0, y0, x1, y1 = 262, 190, 762, 834
    sombra = Image.new("RGBA", (L, L), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rounded_rectangle((x0, y0 + 30, x1, y1 + 30), 26, fill=(0, 0, 0, 120))
    folha.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(28)))
    f.rounded_rectangle((x0, y0, x1, y1), 26, fill=PAPEL + (255,))
    f.rounded_rectangle((x0 + 60, y0 + 70, x0 + 230, y0 + 100), 15, fill=OURO + (255,))
    y = y0 + 170
    for largura, cor in ((380, CINZA), (330, CINZA), (300, ROSA), (250, VERDE_NOVO), (360, CINZA), (310, CINZA)):
        f.rounded_rectangle((x0 + 60, y, x0 + 60 + largura, y + 34), 17, fill=cor + (255,))
        if cor == ROSA:
            f.rectangle((x0 + 48, y + 13, x0 + 72 + largura, y + 21), fill=VERMELHO + (255,))
        y += 84
    folha = folha.rotate(-6, resample=Image.BICUBIC, center=(L // 2, L // 2))
    img.alpha_composite(folha)
    return img


def main() -> None:
    img = desenhar()
    img.save(PASTA / "icone.png")
    img.save(PASTA / "icone.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    img.save(PASTA / "icone.icns")
    print("app/icone.png, icone.ico e icone.icns")


if __name__ == "__main__":
    main()
