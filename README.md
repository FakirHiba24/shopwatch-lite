# ShopWatch-Lite

Supervision miniature d'une boutique en ligne : trois agents (Extraction, Analyse, Notification) qui partagent un contrat d'echange commun.

## Lancer les tests

    python -m unittest -v

## Etat du projet

Le socle reprend le contrat du tutoriel fourni : `Signal`, `Diagnostic`,
`Message`, `NIVEAUX` et `FICHES`. Les anciennes interfaces ne correspondent
pas a ce document.

Cette correction fournit les interfaces des trois agents, l'orchestration et
la demonstration officielles. Les agents contiennent encore les squelettes
`NotImplementedError` : leurs implementations arrivent dans les branches
`feature/extraction`, `feature/analyse` et `feature/notification`.
Les tests du socle verifient le contrat et les imports ; ils ne certifient pas
encore le fonctionnement de bout en bout. `python main.py` sera utilisable
apres integration des trois agents.

Les dates du 27 novembre et la reference CVE dans `main.py` sont des donnees
fictives reprises de l'enonce pour la demonstration.
