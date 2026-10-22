import unittest

from src.contrat import Diagnostic, FICHES, Message, NIVEAUX, Signal


class TestContrat(unittest.TestCase):
    def test_etat_par_defaut(self):
        s = Signal("SH-0001", "2026-11-27T17:00:00Z", "PAIEMENT", "paiement",
                   "production", "JOURNAL", "MINEUR", "demarrage")
        self.assertEqual(s.etat, "RECU")
        self.assertEqual(s.ref, "SH-0001")
        self.assertEqual(s.texte, "demarrage")

    def test_niveaux_ordonnes(self):
        self.assertEqual(NIVEAUX, ["MINEUR", "MODERE", "MAJEUR", "BLOQUANT"])

    def test_base_fiches(self):
        self.assertEqual(list(FICHES), ["timeout", "build", "faille"])
        self.assertTrue(all(FICHES.values()))

    def test_diagnostic_et_message_referencent_le_signal(self):
        diagnostic = Diagnostic("SH-0001", "MINEUR", "Cause inconnue", "Observer",
                                False, ["PAIEMENT"])
        message = Message(diagnostic.signal_ref, "TABLEAU", "astreinte-shop", "Service demarre")
        self.assertEqual(message.signal_ref, diagnostic.signal_ref)
        self.assertFalse(diagnostic.critique)

    def test_demo_et_workflow_importables(self):
        # Les imports detectent une divergence entre les interfaces des agents.
        import main
        from src import workflow

        self.assertTrue(callable(main.main))
        self.assertTrue(callable(workflow.traiter_journal))
        self.assertTrue(callable(workflow.traiter_scan))
        self.assertTrue(callable(workflow.traiter_build))


if __name__ == "__main__":
    unittest.main()
