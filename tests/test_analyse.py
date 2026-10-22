import unittest
from dataclasses import replace

from src.analyse import chercher_fiches, compter_incidents, diagnostiquer, est_repete, evaluer
from src.contrat import Signal


def exemple(**changements):
    champs = dict(ref="SH-0001", date="2026-11-27T17:02:11Z", origine="PAIEMENT",
                  service="paiement", env="production", categorie="JOURNAL", gravite="MAJEUR",
                  texte="timeout passerelle")
    champs.update(changements)
    return Signal(**champs)



class TestRepetition(unittest.TestCase):
    def test_premier_signal_puis_copie(self):
        vus = set()
        sig = exemple()
        self.assertFalse(est_repete(sig, vus))
        self.assertTrue(est_repete(replace(sig, ref="SH-0002"), vus))
        self.assertEqual(len(vus), 1)

    def test_erreurs_a_des_secondes_differentes(self):
        vus = set()
        self.assertFalse(est_repete(exemple(), vus))
        self.assertFalse(est_repete(exemple(date="2026-11-27T17:02:12Z"), vus))
        self.assertEqual(len(vus), 2)

    def test_chaque_composante_de_la_cle(self):
        for champ, valeur in {"origine": "API", "service": "panier", "categorie": "FAILLE",
                              "texte": "autre incident"}.items():
            with self.subTest(champ=champ):
                vus = set()
                est_repete(exemple(), vus)
                self.assertFalse(est_repete(exemple(**{champ: valeur}), vus))

    def test_gravite_et_reference_ne_distinguent_pas_un_doublon(self):
        vus = set()
        est_repete(exemple(), vus)
        self.assertTrue(est_repete(exemple(ref="SH-9999", gravite="BLOQUANT"), vus))
