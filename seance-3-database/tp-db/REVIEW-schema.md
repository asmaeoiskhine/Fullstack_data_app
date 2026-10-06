# REVIEW — schéma v2 (avis et tags)

## Grille de review

| Point de contrôle | OK / KO | Ce que j'ai corrigé |
|---|---|---|
| Chaque table a une clé primaire | OK | Lu dans le DDL : les 6 tables en ont une. Testé : `pk_item_tags` refuse un doublon. Rien à corriger. |
| Les clés étrangères sont déclarées avec `REFERENCES` | OK | Testé : `fk_items_owner`, `fk_reservations_borrower` et `fk_avis_reservation` refusent une référence qui n'existe pas. Rien à corriger. |
| Les `ON DELETE` sont explicites et cohérents avec le métier | OK | Lu : `CASCADE` sur les items, les avis et les tags. Pour `borrower_id`, aucun comportement (c'est demandé par le TP), donc la base refuse la suppression. Rien à corriger. |
| Un seul avis par réservation (`UNIQUE`) | OK | Testé : un 2e avis sur la même réservation est refusé par `uq_avis_reservation`. |
| Note bornée par un `CHECK` entre 1 et 5 | OK | Testé : la note 6 est refusée par `ck_avis_note`. |
| Table de liaison item/tag avec clé primaire composite | OK | Lu : `PRIMARY KEY (item_id, tag_id)`. Testé : le même tag deux fois sur un objet est refusé par `pk_item_tags`. |
| Le libellé de tag est `UNIQUE` | OK, après correction | Au début, j'avais seulement un index sur `lower(label)`, donc `Sport` était accepté alors qu'il faut des minuscules. J'ai mis `UNIQUE (label)` et `CHECK (label = lower(label))`. Testé : `sport` en double est refusé par `uq_tags_label`, et `Sport` par `ck_tags_label_minuscules`. |
| Les contraintes sont nommées | OK | Lu : toutes ont un nom (`pk_`, `fk_`, `uq_`, `ck_`, `ex_`). On voit ces noms dans les messages d'erreur. |
| Index sur les clés étrangères | OK | J'ai ajouté 4 index. Pour `avis.reservation_id` et `item_tags.item_id`, l'index existe déjà grâce au `UNIQUE` et à la clé primaire. Vérifié avec `\d reservations` pour cette table, lu dans le DDL pour les autres. |
| Le non-chevauchement est garanti | OK | Contrainte `ex_reservations_no_overlap` (`EXCLUDE`). Testé : une réservation du 11 au 13 sept. sur la Tente est refusée à cause de celle du 10 au 12. Pas testé : deux réservations qui se touchent (elles devraient être acceptées). |
| Pas de flottant pour un montant, pas de `TIMESTAMP` sans fuseau | OK | Lu : `NUMERIC(8,2)` pour le tarif et `TIMESTAMPTZ` pour les dates. |

## Ce que la base ne garantit pas

Règle : un avis ne peut être laissé qu'après une réservation `terminee`, et par l'emprunteur.
Un `CHECK` ne peut pas regarder une autre table, donc la base ne peut pas le vérifier seule.
C'est l'API (séance 4) qui devra le vérifier : statut `terminee` et utilisateur connecté = emprunteur.

## Étape 2 : suppression d'un utilisateur

Les 5 tentatives qui échouent :

| Tentative | Contrainte violée |
|---|---|
| email `alice@esiee.fr` en double | `uq_users_email` |
| item avec `owner_id = 999` | `fk_items_owner` |
| tarif négatif | `ck_items_tarif_positif` |
| réservation qui finit avant de commencer | `ck_reservations_dates` |
| statut `en_attente_peut_etre` | `ck_reservations_statut` |

Quand je supprime Bob, la base refuse : `fk_reservations_borrower` le bloque, car Bob est encore
emprunteur de la réservation 1. Rien n'est supprimé.

Quand je mets `ON DELETE CASCADE` sur `borrower_id`, Bob et ses 2 items disparaissent, et la table
`reservations` devient vide :

| Réservation perdue | Qui la perd | Par quelle clé étrangère |
|---|---|---|
| 1 (Vélo de ville, emprunté par Bob) | Alice | `fk_reservations_borrower` |
| 2 (Tente de Bob, empruntée par Alice) | Alice | `fk_items_owner` puis `fk_reservations_item` |
| 3 (Appareil photo de Bob, emprunté par Chloé) | Chloé | `fk_items_owner` puis `fk_reservations_item` |

**Ma décision :** on refuse la suppression d'un compte qui a des réservations. Supprimer Bob ne doit
pas effacer les prêts d'Alice et de Chloé, qui ne sont pas à Bob. Donc `borrower_id` reste sans
`ON DELETE`.

**Limite :** `items.owner_id` est en `CASCADE` (imposé par le TP). Un compte qui a seulement prêté du
matériel, sans jamais emprunter, serait supprimé avec ses objets et leurs réservations. L'API devra
donc refuser la suppression d'un compte qui a des réservations, comme emprunteur ou comme propriétaire.
