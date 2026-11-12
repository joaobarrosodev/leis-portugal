"""Imagem de partilha do repositório (GitHub → Settings → Social preview).

    python .github/social-preview.py

Grava .github/social-preview.png (1280×640). Precisa do Pillow e do numpy e das
fontes Baskerville e Avenir Next do macOS. Os números vêm do README; confirmar
antes de gerar outra vez.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2  # desenha a 2× e reduz no fim, para os contornos ficarem suaves
L, A = 1280, 640

VERDE = (15, 61, 46)
VERDE_ESCURO = (10, 44, 33)
BRILHO = (22, 85, 64)
PAPEL = (247, 242, 231)
TINTA = (29, 42, 36)
CINZA = (201, 193, 176)
ROSA = (216, 183, 176)
VERMELHO = (200, 16, 46)
OURO = (217, 164, 65)
VERDE_FLAG = (4, 106, 56)
VERDE_SELO = (46, 139, 87)
VERDE_CLARO = (159, 203, 176)

BASK = "/System/Library/Fonts/Supplemental/Baskerville.ttc"
AVENIR = "/System/Library/Fonts/Avenir Next.ttc"


def fonte(caminho, tamanho, indice):
    return ImageFont.truetype(caminho, int(tamanho * S), index=indice)


serif = lambda t: fonte(BASK, t, 0)
serif_it = lambda t: fonte(BASK, t, 2)
sans = lambda t: fonte(AVENIR, t, 7)
sans_medio = lambda t: fonte(AVENIR, t, 5)
sans_demi = lambda t: fonte(AVENIR, t, 2)


def s(v):
    return int(round(v * S))


def espacado(d, xy, texto, f, cor, espaco):
    """Texto com espaçamento entre letras (o Pillow não o tem)."""
    x, y = xy
    for c in texto:
        d.text((x, y), c, font=f, fill=cor)
        x += d.textlength(c, font=f) + espaco * S
    return x


def fundo():
    w, h = s(L), s(A)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = (xx / w + yy / h) / 2  # diagonal, como um linear-gradient de 135°
    base = np.array(VERDE)[None, None] * (1 - t[..., None]) + np.array(VERDE_ESCURO)[None, None] * t[..., None]
    # brilho suave à direita, atrás da pilha de folhas
    dx, dy = (xx - 0.85 * w) / (0.7 * w), (yy - 0.4 * h) / (0.95 * h)
    g = np.clip(1 - np.sqrt(dx**2 + dy**2), 0, 1)[..., None] ** 1.6
    img = base * (1 - g) + np.array(BRILHO)[None, None] * g
    # linhas finas, como papel pautado
    linhas = (yy.astype(int) % s(32)) < S
    img[linhas] = img[linhas] * 0.975 + 255 * 0.025
    return Image.fromarray(img.clip(0, 255).astype(np.uint8), "RGB").convert("RGBA")


def folha(largura, altura, cor_papel, desenhar):
    """Uma folha com sombra, numa camada própria para se poder rodar."""
    m = s(60)
    w, h = s(largura) + 2 * m, s(altura) + 2 * m
    sombra = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rounded_rectangle(
        (m, m + s(22), m + s(largura), m + s(altura) + s(22)), s(6), fill=(0, 0, 0, 110)
    )
    sombra = sombra.filter(ImageFilter.GaussianBlur(s(22)))
    camada = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    camada.alpha_composite(sombra)
    d = ImageDraw.Draw(camada)
    d.rounded_rectangle((m, m, m + s(largura), m + s(altura)), s(6), fill=cor_papel + (255,))
    desenhar(d, m, m)
    return camada


def colocar(base, camada, centro, angulo):
    rodada = camada.rotate(-angulo, resample=Image.BICUBIC, expand=True)
    cx, cy = s(centro[0]), s(centro[1])
    base.alpha_composite(rodada, (cx - rodada.width // 2, cy - rodada.height // 2))


def linha(d, x, y, largura, cor, riscada=False):
    d.rounded_rectangle((x, y, x + s(largura), y + s(8)), s(4), fill=cor)
    if riscada:
        d.rectangle((x - s(4), y + s(3), x + s(largura) + s(4), y + s(5)), fill=VERMELHO + (210,))
    return y + s(19)


INTERIOR = 270  # largura útil de uma folha (330 menos 30 de cada lado)


def folha_atras(cor):
    """Folha de trás: só se vê a borda esquerda, por isso leva só linhas."""

    def desenhar(d, x0, y0):
        x, y = x0 + s(30), y0 + s(110)
        for p in (0.92, 0.80, 0.86, 0.6, 0.9, 0.84, 0.7, 0.88, 0.8):
            y = linha(d, x, y, INTERIOR * p, cor) + s(6)

    return desenhar


def folha_vigor(d, x0, y0):
    x, y = x0 + s(30), y0 + s(30)
    # selo "Em vigor"
    f = sans_demi(12)
    larg = espacado(ImageDraw.Draw(Image.new("RGBA", (1, 1))), (0, 0), "EM VIGOR", f, (0, 0, 0), 1.4)
    sx1 = x0 + s(330) - s(22)
    sx0 = sx1 - larg - s(24)
    d.rounded_rectangle((sx0, y0 + s(22), sx1, y0 + s(50)), s(14), fill=VERDE_SELO)
    espacado(d, (sx0 + s(12), y0 + s(27)), "EM VIGOR", f, (255, 255, 255), 1.4)

    espacado(d, (x, y), "DECRETO-LEI", sans_demi(13), (107, 101, 86), 2.3)
    d.text((x, y + s(22)), "Texto em vigor,", font=serif(29), fill=TINTA)
    d.text((x, y + s(56)), "artigo a artigo", font=serif(29), fill=TINTA)
    y += s(110)
    d.text((x, y), "Artigo 1.º", font=serif_it(19), fill=(58, 70, 63))
    y += s(32)
    y = linha(d, x, y, INTERIOR * 0.96, CINZA)
    y = linha(d, x, y, INTERIOR * 0.88, CINZA)
    y = linha(d, x, y, INTERIOR * 0.70, ROSA, riscada=True)
    y = linha(d, x, y, INTERIOR * 0.62, VERDE_CLARO)
    y += s(8)
    d.text((x, y), "Artigo 2.º", font=serif_it(19), fill=(58, 70, 63))
    y += s(32)
    for p in (0.94, 0.82, 0.90):
        y = linha(d, x, y, INTERIOR * p, CINZA)
    f = sans(13)
    d.text((x, y0 + s(420) - s(40)), "1833–2026", font=f, fill=(122, 116, 100))
    t = "v. 12"
    d.text((x0 + s(300) - d.textlength(t, font=f), y0 + s(420) - s(40)), t, font=f, fill=(122, 116, 100))


def main():
    img = fundo()
    d = ImageDraw.Draw(img)

    # texto à esquerda
    x = s(76)
    espacado(d, (x, s(74)), "OPEN SOURCE · DADOS ABERTOS", sans_demi(17), OURO, 3.7)
    d.text((x, s(102)), "Leis de", font=serif(104), fill=PAPEL)
    d.text((x, s(204)), "Portugal", font=serif_it(104), fill=OURO)
    y = s(348)
    d.rectangle((x, y, x + s(48), y + s(3)), fill=VERDE_SELO)
    d.rectangle((x + s(48), y, x + s(120), y + s(3)), fill=VERMELHO)
    f = sans(25)
    cor_sub = tuple(int(c * 0.86 + v * 0.14) for c, v in zip(PAPEL, VERDE))
    for i, t in enumerate(["A legislação portuguesa em formato aberto,", "ligada às fontes oficiais e atualizada todos os dias."]):
        d.text((x, s(374 + i * 35)), t, font=f, fill=cor_sub)

    # números
    cor_peq = tuple(int(c * 0.62 + v * 0.38) for c, v in zip(PAPEL, VERDE))
    nx = x
    for grande, pequeno in [
        ("360 mil", "diplomas e atos"),
        ("1833", "até hoje"),
        ("29 mil", "acórdãos do TC"),
        ("54 mil", "atos da UE"),
    ]:
        d.text((nx, s(512)), grande, font=serif(44), fill=PAPEL)
        d.text((nx, s(560)), pequeno, font=sans_medio(15), fill=cor_peq)
        larg = max(d.textlength(grande, font=serif(44)), d.textlength(pequeno, font=sans_medio(15)))
        nx += larg + s(46)

    # pilha de folhas à direita
    colocar(img, folha(330, 420, (226, 217, 198), folha_atras(ROSA)), (948, 336), -13)
    colocar(img, folha(330, 420, (238, 231, 215), folha_atras(CINZA)), (992, 318), -5)
    colocar(img, folha(330, 420, PAPEL, folha_vigor), (1039, 302), 4)

    # faixa com as cores da bandeira
    d = ImageDraw.Draw(img)
    d.rectangle((0, s(A - 10), s(L * 0.4), s(A)), fill=VERDE_FLAG)
    d.rectangle((s(L * 0.4), s(A - 10), s(L), s(A)), fill=VERMELHO)

    saida = Path(__file__).with_name("social-preview.png")
    img.convert("RGB").resize((L, A), Image.LANCZOS).save(saida, optimize=True)
    print(saida, saida.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
