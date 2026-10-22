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



class TestJournal(unittest.TestCase):
    def test_normalisation_et_masquage(self):
        sig = lire_journal("2026-11-27 17:02:11 paiement ERROR timeout card=123 suite", 42)
        self.assertEqual((sig.ref, sig.date, sig.origine, sig.service, sig.env, sig.categorie,
                          sig.gravite, sig.texte, sig.etat),
                         ("SH-0042", "2026-11-27T17:02:11Z", "PAIEMENT", "paiement",
                          "production", "JOURNAL", "MAJEUR", "timeout card=[MASQUE] suite", "RECU"))

    def test_tous_les_niveaux_et_casse(self):
        for niveau, attendu in {"fatal": "BLOQUANT", "CrItIcAl": "BLOQUANT",
                                "error": "MAJEUR", "warn": "MODERE", "WARNING": "MODERE",
                                "INFO": "MINEUR", "inconnu": "MINEUR"}.items():
            with self.subTest(niveau=niveau):
                sig = lire_journal(f"2026-11-27 17:00:00 panier {niveau} message", 1)
                self.assertEqual(sig.gravite, attendu)

    def test_origine_env_et_grand_numero(self):
        sig = lire_journal("2026-11-27 17:00:00 api INFO ok", 12345, "API", "test")
        self.assertEqual((sig.ref, sig.origine, sig.env), ("SH-12345", "API", "test"))

    def test_ligne_incomplete(self):
        for ligne in ("", "2026-11-27", "2026-11-27 17:00:00 paiement ERROR"):
            with self.subTest(ligne=ligne), self.assertRaises(ValueError):
                lire_journal(ligne, 1)
