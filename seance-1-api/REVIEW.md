# REVIEW de la ressource `reservations` générée par Copilot

| Point de contrôle | OK / KO | Remarques et ce que j'ai corrigé |
|---|---|---|
| Les codes de statut correspondent à la spec (201, 404, 409) | OK | Testé dans `/docs` : `POST /reservations` renvoie 201 avec `statut: "active"`, `GET /reservations/999` renvoie 404, `POST /reservations/1/annuler` renvoie 200 puis 409 à la 2e tentative. Rien à corriger. |
| `response_model` présent sur les 4 routes | OK | Testé dans `/docs` : une liste apparaît dans « Responses » des 4 routes, cela a aussi été confirmé dans le code. Rien à corriger. |
| La validation `date_fin > date_debut` est bien dans le schéma Pydantic | OK | Testé : avec `date_fin` avant `date_debut`, on obtient 422 avec `"loc": ["body"]` et `"type": "value_error"`. Rien à corriger. |
| Le router n'accède pas au stockage de `items` | OK | Testé : `POST /reservations` avec `item_id: 999` renvoie 201 alors qu'aucun item 999 n'existe. Dans le code aucun import de `items` dans `reservations.py`. Rien à corriger. |
| Pas d'`async def` sans `await` | OK | Dans le code aucun `async` dans `reservations.py`, toutes les fonctions sont des `def`. Rien à corriger. |
| Aucune dépendance ajoutée dans `requirements.txt` | OK | Vérifié directement dans le fichier qui contient seulement `fastapi` et `uvicorn`. Rien à corriger. |
| Les routes littérales sont déclarées avant les routes paramétrées | - | Les chemins sont `""`, `"/{reservation_id}"` et `"/{reservation_id}/annuler"`, il n'y a aucune route littérale qu'une route paramétrée pourrait masquer. |
| Le code renvoie une réponse cohérente pour `POST /reservations/999/annuler` | OK | Testé : 404 avec `"Reservation 999 introuvable"`. Rien à corriger. |
