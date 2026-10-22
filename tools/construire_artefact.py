"""Construire une archive executable avec la bibliotheque standard uniquement."""
import argparse
from pathlib import Path
import re
from zipfile import ZIP_DEFLATED, ZipFile


def construire(tag: str, racine: Path | None = None) -> Path:
    if not re.fullmatch(r"v[0-9]+\.[0-9]+(?:\.[0-9]+)?", tag):
        raise ValueError("Tag attendu : vX.Y ou vX.Y.Z")
    racine = Path(racine) if racine is not None else Path(__file__).resolve().parents[1]
    fichiers = [racine / nom for nom in ("main.py", "VERSION", "README.md")]
    for fichier in fichiers:
        if not fichier.is_file():
            raise FileNotFoundError(f"Fichier requis absent : {fichier.name}")
    if not (racine / "VERSION").read_text(encoding="utf-8").strip():
        raise ValueError("VERSION ne peut pas etre vide")
    modules = sorted(p for p in (racine / "src").rglob("*.py")
                     if p.is_file() and "__pycache__" not in p.relative_to(racine).parts)
    if not modules:
        raise ValueError("Aucun module Python dans src")
    fichiers += modules
    if (racine / "CHANGELOG.md").is_file():
        fichiers.append(racine / "CHANGELOG.md")
    destination = racine / "dist" / f"shopwatch-lite-{tag}.zip"
    destination.parent.mkdir(exist_ok=True)
    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as archive:
        for fichier in fichiers:
            archive.write(fichier, arcname=fichier.relative_to(racine).as_posix())
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    print(construire(parser.parse_args().tag))
