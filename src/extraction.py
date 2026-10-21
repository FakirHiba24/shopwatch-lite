"""Agent 1 : Extraction (A)."""
from src.contrat import Signal


def masquer_donnees(texte):
    """Masque les donnees sensibles (mots de passe, cles...)."""
    raise NotImplementedError


def extraire(texte_brut, source):
    """Transforme un texte brut en Signal (donnees masquees)."""
    raise NotImplementedError


def est_repete(signal, deja_vus):
    """True si le signal a deja ete vu ; l'ajoute sinon a deja_vus (set)."""
    raise NotImplementedError
