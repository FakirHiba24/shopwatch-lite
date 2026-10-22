"""Agent 1 : collecte, normalisation et masquage des donnees sensibles."""
import re

from src.contrat import Signal


def masquer_donnees(texte: str) -> str:
    """Masquer les six parametres du contrat avant toute diffusion."""
    motif = r"\b(password|pwd|token|secret|card|iban)(\s*[=:]\s*)[^\s&,;]+"
    return re.sub(motif, lambda m: m.group(1) + m.group(2) + "[MASQUE]",
                  texte, flags=re.IGNORECASE)


def lire_journal(ligne: str, numero: int, origine: str = "PAIEMENT",
                 env: str = "production") -> Signal:
    raise NotImplementedError


def lire_scan(rapport: dict, numero: int, env: str = "production") -> Signal:
    raise NotImplementedError


def lire_build(rapport: dict, numero: int, env: str = "production") -> Signal:
    raise NotImplementedError
