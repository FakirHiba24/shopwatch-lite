
import unittest

from src.contrat import Diagnostic, Signal
from src.notification import (
    choisir_canal,
    composer,
    diffuser,
    approuver,
    consigner,
)


def exemple(critique=True, niveau="BLOQUANT"):
    s = Signal(
        "SH-0125",
        "2026-11-27T17:02:11Z",
        "PAIEMENT",
        "paiement",
        "production",
        "JOURNAL",
        "MAJEUR",
        "timeout passerelle apres 30s",
    )

    d = Diagnostic(
        "SH-0125",
        niveau,
        "Passerelle lente",
        "Isoler le service paiement",
        critique,
        ["PAIEMENT"],
    )

    return s, d


class TestNotification(unittest.TestCase):

    def test_canal_inconnu_refuse(self):
        for niveau in ("INCONNU", "", "majeur"):
            with self.subTest(niveau=niveau), self.assertRaises(ValueError):
                choisir_canal(niveau)

    def test_canaux(self):
        self.assertEqual(choisir_canal("BLOQUANT"), "SLACK")
        self.assertEqual(choisir_canal("MAJEUR"), "TEAMS")
        self.assertEqual(choisir_canal("MODERE"), "EMAIL")
        self.assertEqual(choisir_canal("MINEUR"), "TABLEAU")

    def test_composer(self):
        s, d = exemple()
        contenu = composer(s, d)

        attendu = (
            "*** BLOQUANT *** Service : paiement\n"
            "Constat : timeout passerelle apres 30s\n"
            "Cause : Passerelle lente\n"
            "A faire : Isoler le service paiement\n"
            "Origines : PAIEMENT"
        )

        self.assertEqual(contenu, attendu)

    def test_plusieurs_origines_sur_cinq_lignes(self):
        s, d = exemple()
        d.origines = ["PAIEMENT", "SCANNER", "BUILD"]
        lignes = composer(s, d).splitlines()
        self.assertEqual(len(lignes), 5)
        self.assertEqual(lignes[-1], "Origines : PAIEMENT + SCANNER + BUILD")

    def test_diffuser(self):
        s, d = exemple()
        registre = []

        msg = diffuser(s, d, registre)

        self.assertEqual(msg.canal, "SLACK")
        self.assertEqual(msg.destinataire, "astreinte-shop")
        self.assertEqual(msg.signal_ref, "SH-0125")
        self.assertEqual(msg.contenu, composer(s, d))
        self.assertEqual(len(registre), 1)
        self.assertIs(registre[0], msg)
        self.assertEqual(s.etat, "DIFFUSE")

    def test_niveau_invalide_ne_modifie_pas_le_registre(self):
        s, d = exemple(niveau="INCONNU")
        registre = []
        with self.assertRaises(ValueError):
            diffuser(s, d, registre)
        self.assertEqual(registre, [])
        self.assertEqual(s.etat, "RECU")

    def test_approbation(self):
        _, d = exemple()

        self.assertTrue(approuver(d, " OUI "))
        self.assertTrue(approuver(d, "o"))
        self.assertTrue(approuver(d, "ok"))
        self.assertTrue(approuver(d, "YES"))
        self.assertFalse(approuver(d, "n"))

    def test_action_critique_refusee_sans_accord_explicite(self):
        _, d = exemple()
        for reponse in ("", "  ", "non", "no", "peut-etre", "oui puis non", "1"):
            with self.subTest(reponse=reponse):
                self.assertFalse(approuver(d, reponse))

    def test_action_non_critique_ne_necessite_pas_d_accord(self):
        _, d = exemple(critique=False, niveau="MINEUR")
        d.action = "Observer"
        for reponse in ("", "n", "non", "oui"):
            with self.subTest(reponse=reponse):
                self.assertTrue(approuver(d, reponse))

    def test_consigner(self):
        _, d = exemple()
        carnet = []

        entree = consigner(
            d,
            True,
            "astreinte-shop",
            carnet,
            "2026-11-27T17:10:00Z",
        )

        self.assertEqual(entree["ref"], "SH-0125")
        self.assertEqual(entree["accord"], True)
        self.assertEqual(
            entree["action"],
            "Isoler le service paiement"
        )
        self.assertEqual(
            entree["responsable"],
            "astreinte-shop"
        )
        self.assertEqual(
            entree["instant"],
            "2026-11-27T17:10:00Z"
        )
        self.assertEqual(carnet, [entree])

    def test_refus_consigne_et_historique_conserve(self):
        _, d = exemple()
        carnet = [{"ref": "SH-0000"}]
        entree = consigner(d, False, "astreinte-shop", carnet, "2026-11-27T17:11:00Z")
        self.assertEqual(entree, {
            "ref": "SH-0125", "action": "Isoler le service paiement", "accord": False,
            "responsable": "astreinte-shop", "instant": "2026-11-27T17:11:00Z",
        })
        self.assertIs(carnet[-1], entree)
        self.assertEqual(carnet[0], {"ref": "SH-0000"})
