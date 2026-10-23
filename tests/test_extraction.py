import unittest

from src.extraction import lire_build, lire_journal, lire_scan, masquer_donnees



class TestMasquage(unittest.TestCase):
    def test_bearer(self):
        self.assertEqual(masquer_donnees("Authorization: Bearer eyJ.abc-1"),
                         "Authorization: Bearer [MASQUE]")

    def test_bearer_casse_separateurs_et_idempotence(self):
        cas = [
            ("authorization: bearer eyJ.abc-1_~+/==&client=bob",
             "authorization: bearer [MASQUE]&client=bob"),
            ("Authorization: BEARER abc,client=bob",
             "Authorization: BEARER [MASQUE],client=bob"),
            ("Bearer \t abc;pwd=xyz", "Bearer \t [MASQUE];pwd=[MASQUE]"),
        ]
        for texte, attendu in cas:
            with self.subTest(texte=texte):
                self.assertEqual(masquer_donnees(texte), attendu)
                self.assertEqual(masquer_donnees(attendu), attendu)

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
    def test_bearer_masque_avant_creation_signal(self):
        sig = lire_journal("2026-11-27 17:02:11 paiement ERROR Authorization: Bearer eyJ.abc-1", 42)
        self.assertEqual(sig.texte, "Authorization: Bearer [MASQUE]")
        self.assertNotIn("eyJ.abc-1", sig.texte)

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



class TestScan(unittest.TestCase):
    def setUp(self):
        self.rapport = {"id_faille": "CVE-DEMO", "paquet": "lib-panier", "risque": "critique",
                        "date": "2026-11-27T17:09:00Z"}

    def test_signal_scan_complet(self):
        sig = lire_scan(self.rapport, 8, env="test")
        self.assertEqual((sig.ref, sig.date, sig.origine, sig.service, sig.env, sig.categorie,
                          sig.gravite, sig.texte, sig.etat),
                         ("SH-0008", self.rapport["date"], "SCANNER", "lib-panier", "test",
                          "FAILLE", "BLOQUANT", "Faille CVE-DEMO dans lib-panier", "RECU"))

    def test_risques_et_casse(self):
        for risque, attendu in {"CRITIQUE": "BLOQUANT", "Haut": "MAJEUR", "moyen": "MODERE",
                                "bas": "MINEUR", "inconnu": "MINEUR"}.items():
            with self.subTest(risque=risque):
                sig = lire_scan(dict(self.rapport, risque=risque), 1)
                self.assertEqual(sig.gravite, attendu)
                self.assertEqual(sig.env, "production")

    def test_chaque_cle_est_obligatoire(self):
        for cle in self.rapport:
            with self.subTest(cle=cle), self.assertRaises(ValueError):
                lire_scan({k: v for k, v in self.rapport.items() if k != cle}, 1)



class TestBuild(unittest.TestCase):
    def setUp(self):
        self.rapport = {"etape": "deploiement", "resultat": "echec", "date": "2026-11-27T17:08:00Z"}

    def test_signal_build_en_echec(self):
        sig = lire_build(self.rapport, 9, env="dev")
        self.assertEqual((sig.ref, sig.date, sig.origine, sig.service, sig.env, sig.categorie,
                          sig.gravite, sig.texte),
                         ("SH-0009", self.rapport["date"], "BUILD", "deploiement", "dev",
                          "BUILD_ECHEC", "MAJEUR", "Build deploiement : echec"))

    def test_resultats_et_casse(self):
        for resultat in ("ECHEC", "Echec", "succes", "ok", "autre"):
            with self.subTest(resultat=resultat):
                sig = lire_build(dict(self.rapport, resultat=resultat), 1)
                self.assertEqual(sig.categorie, "BUILD_ECHEC" if resultat.lower() == "echec" else "BUILD_OK")
                self.assertEqual(sig.gravite, "MAJEUR" if resultat.lower() == "echec" else "MINEUR")
                self.assertEqual(sig.env, "production")

    def test_chaque_cle_est_obligatoire(self):
        for cle in self.rapport:
            with self.subTest(cle=cle), self.assertRaises(ValueError):
                lire_build({k: v for k, v in self.rapport.items() if k != cle}, 1)
