from src.workflow import executer

SIGNAUX = [
    ("paiement", "Timeout paiement password=abc123"),
    ("paiement", "Timeout paiement password=abc123"),
    ("build", "Echec du build de deploiement"),
    ("scanner", "Faille dans la bibliotheque du panier"),
]

if __name__ == "__main__":
    for ligne in executer(SIGNAUX):
        print(ligne)
