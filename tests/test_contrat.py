import unittest

from src.contrat import Decision, Evenement


class TestContrat(unittest.TestCase):
    def test_evenement_valeurs_par_defaut(self):
        ev = Evenement(source="paiement", message="timeout")
        self.assertEqual(ev.gravite, 1)
        self.assertEqual(ev.occurrences, 1)

    def test_evenement_champs(self):
        ev = Evenement("build", "echec", gravite=4, occurrences=2)
        self.assertEqual((ev.source, ev.gravite, ev.occurrences), ("build", 4, 2))

    def test_decision_reference_evenement(self):
        ev = Evenement("scanner", "faille")
        d = Decision(ev, "alerter", "gravite elevee")
        self.assertIs(d.evenement, ev)
        self.assertEqual(d.action, "alerter")


if __name__ == "__main__":
    unittest.main()
