
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

    def test_approbation(self):
        _, d = exemple()

        self.assertTrue(approuver(d, " OUI "))
        self.assertTrue(approuver(d, "o"))
        self.assertTrue(approuver(d, "ok"))
        self.assertTrue(approuver(d, "YES"))
        self.assertFalse(approuver(d, "n"))

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
