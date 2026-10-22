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
    champs = ligne.split(maxsplit=4)
    if len(champs) < 5:
        raise ValueError("Journal incomplet : date, heure, service, niveau et message requis")
    date, heure, service, niveau, texte = champs
    gravites = {"FATAL": "BLOQUANT", "CRITICAL": "BLOQUANT", "ERROR": "MAJEUR",
                "WARN": "MODERE", "WARNING": "MODERE"}
    return Signal(ref=f"SH-{numero:04d}", date=f"{date}T{heure}Z", origine=origine,
                  service=service, env=env, categorie="JOURNAL",
                  gravite=gravites.get(niveau.upper(), "MINEUR"),
                  texte=masquer_donnees(texte))


def lire_scan(rapport: dict, numero: int, env: str = "production") -> Signal:
    requises = {"id_faille", "paquet", "risque", "date"}
    if not requises.issubset(rapport):
        raise ValueError("Rapport de scan incomplet : " + ", ".join(sorted(requises - rapport.keys())))
    gravites = {"critique": "BLOQUANT", "haut": "MAJEUR", "moyen": "MODERE"}
    return Signal(ref=f"SH-{numero:04d}", date=rapport["date"], origine="SCANNER",
                  service=rapport["paquet"], env=env, categorie="FAILLE",
                  gravite=gravites.get(rapport["risque"].lower(), "MINEUR"),
                  texte=f"Faille {rapport['id_faille']} dans {rapport['paquet']}")


def lire_build(rapport: dict, numero: int, env: str = "production") -> Signal:
    requises = {"etape", "resultat", "date"}
    if not requises.issubset(rapport):
        raise ValueError("Rapport de build incomplet : " + ", ".join(sorted(requises - rapport.keys())))
    echec = rapport["resultat"].lower() == "echec"
    return Signal(ref=f"SH-{numero:04d}", date=rapport["date"], origine="BUILD",
                  service=rapport["etape"], env=env,
                  categorie="BUILD_ECHEC" if echec else "BUILD_OK",
                  gravite="MAJEUR" if echec else "MINEUR",
                  texte=f"Build {rapport['etape']} : {rapport['resultat']}")
