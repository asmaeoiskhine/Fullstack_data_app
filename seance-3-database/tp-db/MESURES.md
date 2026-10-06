# MESURES — index (table items, 200 004 lignes)

Mesures faites avec `EXPLAIN ANALYZE` après `ANALYZE items;`.
Les temps changent un peu à chaque exécution.

## 1. Recherche exacte sur le titre

`WHERE titre = 'Item de test 123456'`

- Sans index : 30,769 ms (Seq Scan)
- Avec index sur `titre` : 0,197 ms (Index Scan)
- Facteur : 30,769 / 0,197 ≈ **156 fois plus rapide**

Sans index, PostgreSQL lit les 200 004 lignes pour en garder une seule. Avec l'index, il va
directement à la bonne ligne.

## 2. Titre qui se termine par 123456

`WHERE titre LIKE '%123456'`

- Avec l'index sur `titre` : 44,096 ms (Seq Scan, l'index n'est pas utilisé)

L'index est trié par le début du texte. Avec un `%` au début, on ne connaît pas le début, donc
PostgreSQL doit tout lire.

## 3. Filtre sur `disponible`

J'ai mis 200 lignes à `FALSE` (0,1 % de la table) pour pouvoir comparer.

| Requête | Sans index | Avec index | Plan avec index |
|---|---|---|---|
| `disponible = TRUE` (199 804 lignes) | 66,863 ms | 64,165 ms | Seq Scan |
| `disponible = FALSE` (200 lignes) | 15,700 ms | 0,398 ms | Index Scan |

- Pour `FALSE` : 15,700 / 0,398 ≈ **39 fois plus rapide**.
- Pour `TRUE` : pas de gain (66,863 → 64,165 ms, la différence est juste du bruit).

Pour `TRUE`, presque toute la table correspond, donc PostgreSQL préfère la lire en entier plutôt que
passer par l'index. Un index sert seulement quand on cherche peu de lignes.

## Bonus : `LIKE` avec le joker à la fin

`WHERE titre LIKE 'Item de test 12345%'`

- Avec l'index sur `titre` : 36,916 ms (Seq Scan, l'index n'est pas utilisé)

Réponse : non, dans mes mesures l'index sur `titre` ne sert pas pour un `LIKE` avec le joker à la
fin. PostgreSQL lit toute la table, comme pour le joker au début.
