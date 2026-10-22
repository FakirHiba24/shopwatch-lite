from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from tools.construire_artefact import construire


class TestArtefact(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.racine = Path(self.temp.name)
        for nom, texte in {"main.py": 'print("demo")\n', "VERSION": "1.0.0\n",
                           "README.md": "ShopWatch-Lite\n", "CHANGELOG.md": "Release\n",
                           "src/__init__.py": "", "src/contrat.py": "# contrat\n",
                           "src/__pycache__/contrat.cpython-312.pyc": "cache"}.items():
            fichier = self.racine / nom
            fichier.parent.mkdir(parents=True, exist_ok=True)
            fichier.write_text(texte, encoding="utf-8")

    def test_archive_autonome_sans_cache(self):
        chemin = construire("v1.0", self.racine)
        self.assertEqual(chemin.name, "shopwatch-lite-v1.0.zip")
        with ZipFile(chemin) as archive:
            self.assertEqual(set(archive.namelist()), {"main.py", "VERSION", "README.md", "CHANGELOG.md",
                                                      "src/__init__.py", "src/contrat.py"})
            self.assertEqual(archive.read("VERSION"), (self.racine / "VERSION").read_bytes())
            self.assertIsNone(archive.testzip())

    def test_hotfix_et_fichier_requis_absent(self):
        self.assertEqual(construire("v1.0.1", self.racine).name, "shopwatch-lite-v1.0.1.zip")
        (self.racine / "VERSION").unlink()
        with self.assertRaisesRegex(FileNotFoundError, "VERSION"):
            construire("v1.0", self.racine)

    def test_version_vide_refusee(self):
        (self.racine / "VERSION").write_text("\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "VERSION"):
            construire("v1.0", self.racine)

    def test_nom_de_tag_invalide_refuse(self):
        for tag in ("main", "v1.0/../../autre", "v1.0;commande"):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                construire(tag, self.racine)
