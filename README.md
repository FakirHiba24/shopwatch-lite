# ShopWatch-Lite

Mini-plateforme Python de supervision d'une boutique en ligne : extraction,
analyse deterministe et notification via un contrat commun. Le projet
fonctionne avec Python 3.10 ou plus, sans dependance externe.

## Equipe et repartition prevue par le TP

| Role | Etudiant | Agent | Fichiers |
| --- | --- | --- | --- |
| A | Hiba FAKIR | Extraction | `src/extraction.py`, `tests/test_extraction.py` |
| B | Amina ZEKRI | Analyse | `src/analyse.py`, `tests/test_analyse.py` |
| C | Abderrahmane EL GARTI | Notification | `src/notification.py`, `tests/test_notification.py` |

Cette repartition de roles ne remplace pas l'historique Git et les revues
GitHub pour identifier les contributions effectivement realisees.

## Executer le projet

Depuis la racine du depot :

    python -m unittest -v
    python main.py

Repondre `o` puis `n` aux deux demandes de validation. Le scenario fourni
produit neuf signaux, un doublon ignore, huit messages et deux decisions
consignees. Les canaux SLACK, TEAMS, EMAIL et TABLEAU sont des destinations
simulees : aucun message n'est envoye a un service externe et aucune action
sur un serveur n'est executee.

## Traitement et garde-fous

1. Extraction normalise journaux, rapports de scan et rapports de build en
   `Signal`, en masquant les parametres sensibles du contrat et les jetons Bearer.
2. Analyse ignore les signaux deja recus, compte les incidents par service,
   recherche les fiches et construit un `Diagnostic`. Le quatrieme incident
   eleve le niveau a BLOQUANT ; les actions FAILLE et BUILD_ECHEC ont priorite.
3. Notification choisit un canal, compose un `Message` en cinq lignes et
   conserve les messages dans le registre. Les actions d'isolation exigent un
   accord explicite ; accords et refus sont consignes dans un carnet d'audit.

Le contrat `src/contrat.py` definit `Signal`, `Diagnostic`, `Message`, `NIVEAUX`
et `FICHES`. L'etat du signal evolue de RECU a EVALUE puis DIFFUSE.
Les registres et carnets sont des listes en memoire pour cette demonstration.

Les dates du 27 novembre et la reference CVE dans `main.py` sont des donnees
fictives reprises de l'enonce pour la demonstration.

## Tests et Git Flow

La suite comporte 55 tests : contrat, Extraction, Analyse, Notification et
construction de l'artefact. Elle couvre notamment les seuils 3/4/5, les
priorites du diagnostic, les refus de validation, le masquage Bearer et le contenu du ZIP.

`main` correspond aux versions stables et `develop` a l'integration. Les
changements passent par une branche et une PR avec une approbation et le
check `test` vert. Une release part de `develop` ; un hotfix part de `main`.
Les deux types de branches sont ensuite reintegres dans les deux branches
permanentes. Les historiques publies ne sont pas reecrits par push force.

## Livraison continue et utilisation de l'archive

Les PR et les branches declenchent le job `test`. Un tag `vX.Y` ou `vX.Y.Z`
declenche ensuite `build`, qui depend de la reussite des tests, puis `deploy`.
Le deploiement est simule : le dernier job affiche un message sans contacter
de serveur. L'artefact telechargeable contient une archive ZIP avec `src/`,
`main.py`, `VERSION`, `README.md` et `CHANGELOG.md`, sans caches Python.

La version est conservee dans `VERSION`. Construction locale :

    python tools/construire_artefact.py v1.0

Extraire le ZIP, puis lancer `python main.py` depuis son dossier. Les choix
`o` puis `n` illustrent l'autorisation et le refus des deux actions critiques.
