# PyInstaller: a aplicação Leis de Portugal para macOS (.app) e Windows (pasta com o .exe).
#
#   pip install -e '.[rag,app]'
#   pyinstaller app/leis-portugal.spec --noconfirm
#
# Sai em dist/Leis de Portugal.app (macOS) ou dist/Leis de Portugal/Leis de Portugal.exe (Windows).
# Os dados (o índice, ~4 GB) não vão dentro: a aplicação descarrega-os da primeira vez (rag.dados).
import importlib.util
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, copy_metadata

RAIZ = Path(SPECPATH).parent
NOME = "Leis de Portugal"

datas = [
    (str(RAIZ / "rag" / "pagina"), "rag/pagina"),
    (str(RAIZ / "rag" / "REESCRITA.md"), "rag"),
    (str(RAIZ / "avaliacao" / "comum.py"), "avaliacao"),
    (str(RAIZ / "data" / "jurisprudencia" / "tribunal-constitucional" / "normas-julgadas.jsonl"), "data/jurisprudencia/tribunal-constitucional"),
]
binaries = []
hiddenimports = [
    "rag.dados", "rag.definicoes", "rag.jurisprudencia", "rag.modelos", "rag.pesquisa", "rag.perguntar",
    "rag.provedores", "rag.reescrita", "rag.resposta", "rag.texto", "rag.web",
    "py_rust_stemmers", "keyring.backends.macOS", "keyring.backends.Windows",
]
for pacote in ("fastembed", "onnxruntime", "tokenizers", "py_rust_stemmers", "anthropic", "openai", "google.genai", "keyring", "webview"):
    if importlib.util.find_spec(pacote.split(".")[0]) is None:
        print(f"AVISO: {pacote} não está instalado; a aplicação fica sem ele")
        continue
    d, b, h = collect_all(pacote)
    datas += d
    binaries += b
    hiddenimports += h
for pacote in ("fastembed", "anthropic", "openai", "google-genai", "keyring", "requests", "huggingface-hub"):
    try:
        datas += copy_metadata(pacote)
    except Exception:
        pass

a = Analysis(
    [str(RAIZ / "app" / "leis_portugal_app.py")],
    pathex=[str(RAIZ), str(RAIZ / "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["tkinter", "matplotlib", "pytest"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=NOME,
    console=False,
    icon=str(RAIZ / "app" / ("icone.icns" if sys.platform == "darwin" else "icone.ico")),
)
coll = COLLECT(exe, a.binaries, a.datas, name=NOME)
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name=f"{NOME}.app",
        icon=str(RAIZ / "app" / "icone.icns"),
        bundle_identifier="pt.leis-portugal.app",
        info_plist={"CFBundleShortVersionString": "0.1.1", "NSHighResolutionCapable": True, "LSApplicationCategoryType": "public.app-category.reference"},
    )
