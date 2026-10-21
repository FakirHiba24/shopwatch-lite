"""Contrat d'echange commun aux trois agents."""
from dataclasses import dataclass


@dataclass
class Signal:
    source: str           # ex: "paiement", "build", "scanner"
    message: str          # texte (deja masque par l'agent Extraction)
    gravite: int = 1      # 1 (info) a 5 (critique)
    occurrences: int = 1  # nombre de repetitions du signal


@dataclass
class Diagnostic:
    signal: Signal
    action: str           # "ignorer", "alerter" ou "escalader"
    raison: str
