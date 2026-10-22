"""Clone local do legalize-pt: commit atual e ficheiros a importar."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from leis_portugal.errors import MetadataError


# Pasta do legalize-pt -> região autónoma (pt-20 Açores, pt-30 Madeira).
LEGALIZE_DIRECTORIES = {"pt": None, "pt-20": "acores", "pt-30": "madeira"}


def territory_hint(relative: Path) -> str | None:
    return LEGALIZE_DIRECTORIES.get(relative.parts[0])


@dataclass(frozen=True)
class LegalizeSnapshot:
    """Versão do clone local do legalize-pt usada na importação."""

    path: Path
    commit: str
    committed_at: str

    @classmethod
    def from_path(cls, path: str | Path) -> LegalizeSnapshot:
        repo = Path(path).resolve()
        if not (repo / "pt").is_dir():
            raise MetadataError(f"{repo} não parece um clone do legalize-pt (falta a pasta pt/).")
        try:
            output = subprocess.run(
                ["git", "-C", str(repo), "log", "-1", "--format=%H %cI"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.split()
        except (OSError, subprocess.CalledProcessError) as exc:
            raise MetadataError(f"Não foi possível ler o commit atual de {repo}: {exc}") from exc
        commit, committed_at = output[0], output[1]
        # Normaliza para UTC em forma Z, como o resto do acervo.
        committed_at = committed_at.replace("+00:00", "Z")
        return cls(path=repo, commit=commit, committed_at=committed_at)

    def files(self) -> list[Path]:
        paths: list[Path] = []
        for directory in LEGALIZE_DIRECTORIES:
            base = self.path / directory
            if base.is_dir():
                paths.extend(base.rglob("*.md"))
        return sorted(paths)
