"""Orchestration : extraction -> analyse -> notification."""
from src.analyse import evaluer
from src.extraction import est_repete, extraire
from src.notification import consigner, demander_validation


def executer(signaux, demander=demander_validation):
    """signaux : liste de (source, texte_brut). Retourne le journal."""
    journal = []
    deja_vus = set()
    for source, texte in signaux:
        signal = extraire(texte, source)
        if est_repete(signal, deja_vus):
            journal.append(f"IGNORE (repete) : {signal.message}")
            continue
        diagnostic = evaluer(signal)
        validee = False
        if diagnostic.action != "ignorer":
            validee = demander(diagnostic)
        consigner(diagnostic, validee, journal)
    return journal
