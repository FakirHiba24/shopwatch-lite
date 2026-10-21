import unittest

from src.contrat import Diagnostic, Signal


class TestContrat(unittest.TestCase):
    def test_signal_valeurs_par_defaut(self):
        s = Signal(source="paiement", message="timeout")
        self.assertEqual(s.gravite, 1)
        self.assertEqual(s.occurrences, 1)

    def test_signal_champs(self):
        s = Signal("build", "echec", gravite=4, occurrences=2)
        self.assertEqual((s.source, s.gravite, s.occurrences), ("build", 4, 2))

    def test_diagnostic_reference_signal(self):
        s = Signal("scanner", "faille")
        d = Diagnostic(s, "alerter", "gravite elevee")
        self.assertIs(d.signal, s)
        self.assertEqual(d.action, "alerter")


if __name__ == "__main__":
    unittest.main()
