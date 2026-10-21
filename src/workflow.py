"""Orchestration : extraction -> analyse -> notification."""
from src.analyse import evaluer
from src.extraction import est_repete, extraire
from src.notification import consigner, demander_validation


def executer(signaux, demander=demander_validation):
    """signaux : liste de (source, texte_brut). Retourne le journal."""
    journal = []
    deja_vus = set()
    for source, texte in signaux:
        evenement = extraire(texte, source)
        if est_repete(evenement, deja_vus):
            journal.append(f"IGNORE (repete) : {evenement.message}")
            continue
        decision = evaluer(evenement)
        validee = False
        if decision.action != "ignorer":
            validee = demander(decision)
        consigner(decision, validee, journal)
    return journal
