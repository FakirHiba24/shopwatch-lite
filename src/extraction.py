"""Agent 1 : interfaces du tutoriel, implementation sur feature/extraction."""
from src.contrat import Signal


def masquer_donnees(texte: str) -> str:
    raise NotImplementedError


def lire_journal(ligne: str, numero: int, origine: str = "PAIEMENT",
                 env: str = "production") -> Signal:
    raise NotImplementedError


def lire_scan(rapport: dict, numero: int, env: str = "production") -> Signal:
    raise NotImplementedError


def lire_build(rapport: dict, numero: int, env: str = "production") -> Signal:
    raise NotImplementedError
