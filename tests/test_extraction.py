import unittest

from src.extraction import lire_build, lire_journal, lire_scan, masquer_donnees



class TestMasquage(unittest.TestCase):
    def test_six_parametres_et_casse(self):
        for nom in ("password", "pwd", "token", "secret", "card", "iban"):
            for cle in (nom, nom.upper(), nom.capitalize()):
                with self.subTest(cle=cle):
                    self.assertEqual(masquer_donnees(f"client=bob {cle}=abc123"),
                                     f"client=bob {cle}=[MASQUE]")

    def test_deux_points_et_separateurs_preserves(self):
        for fin in (" client=bob", "&client=bob", ",client=bob", ";client=bob", "\tfin"):
            with self.subTest(fin=fin):
                self.assertEqual(masquer_donnees("PWD: abc123" + fin), "PWD: [MASQUE]" + fin)

    def test_plusieurs_secrets(self):
        self.assertEqual(masquer_donnees("pwd=a&token=b,secret=c;card=d iban=e"),
                         "pwd=[MASQUE]&token=[MASQUE],secret=[MASQUE];card=[MASQUE] iban=[MASQUE]")

    def test_texte_ordinaire_et_nom_plus_long(self):
        texte = "client=bob motpassword=public access_token=public"
        self.assertEqual(masquer_donnees(texte), texte)
        self.assertEqual(masquer_donnees(""), "")

    def test_masquage_idempotent(self):
        masque = masquer_donnees("token=abc&pwd=def")
        self.assertEqual(masquer_donnees(masque), masque)
