from typing import Any

import pytest
from fastapi.testclient import TestClient

from tests.conftest import Storage

ITEM_VALIDE = {"titre": "Vélo de ville", "description": "Trois vitesses", "tarif_jour": 8.5}


def test_creer_un_item_renvoie_201_et_l_item(client: TestClient) -> None:
    response = client.post("/items", json=ITEM_VALIDE)

    assert response.status_code == 201
    assert response.json() == {"id": 1, **ITEM_VALIDE, "disponible": True}


def test_un_item_cree_est_relisible_par_get(client: TestClient, item_velo: dict[str, Any]) -> None:
    response = client.get(f"/items/{item_velo['id']}")

    assert response.status_code == 200
    assert response.json() == item_velo


def test_lire_un_item_inconnu_renvoie_404(client: TestClient) -> None:
    response = client.get("/items/999")

    assert response.status_code == 404


@pytest.mark.parametrize("item_id", ["abc", "0", "-1"])
def test_identifiant_invalide_renvoie_422(client: TestClient, item_id: str) -> None:
    response = client.get(f"/items/{item_id}")

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("payload", "champ_en_erreur"),
    [
        ({"titre": "ab", "tarif_jour": 8.5}, "titre"),
        ({"titre": "Vélo de ville", "tarif_jour": 0}, "tarif_jour"),
        ({"titre": "Vélo de ville", "tarif_jour": -3}, "tarif_jour"),
        ({"titre": "Vélo de ville"}, "tarif_jour"),
        ({"titre": "Vélo de ville", "tarif_jour": 8.5, "couleur": "rouge"}, "couleur"),
    ],
)
def test_creation_item_invalide_renvoie_422(
    client: TestClient, payload: dict[str, Any], champ_en_erreur: str
) -> None:
    response = client.post("/items", json=payload)

    assert response.status_code == 422
    champs = [erreur["loc"][-1] for erreur in response.json()["detail"]]
    assert champ_en_erreur in champs


def test_lister_une_api_vide_renvoie_une_liste_vide(client: TestClient) -> None:
    response = client.get("/items")

    assert response.status_code == 200
    assert response.json() == []


def test_lister_retourne_les_items_crees(client: TestClient, item_velo: dict[str, Any]) -> None:
    response = client.get("/items")

    assert [item["id"] for item in response.json()] == [item_velo["id"]]


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 500}, {"skip": -1}])
def test_lister_avec_parametres_hors_bornes_renvoie_422(
    client: TestClient, params: dict[str, int]
) -> None:
    response = client.get("/items", params=params)

    assert response.status_code == 422


def test_lister_avec_skip_saute_les_premiers(client: TestClient, storage: Storage) -> None:
    # Given : cinquante items, insérés sans passer par cinquante requêtes HTTP.
    for i in range(1, 51):
        storage.items[i] = {"id": i, "titre": f"Item {i}", "description": None,
                            "tarif_jour": 5.0, "disponible": True}

    response = client.get("/items", params={"skip": 40, "limit": 20})

    assert [item["id"] for item in response.json()] == list(range(41, 51))


def test_lister_filtre_par_titre_sans_tenir_compte_de_la_casse(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    client.post("/items", json={"titre": "Perceuse", "tarif_jour": 5})

    response = client.get("/items", params={"q": "VILLE"})

    assert [item["titre"] for item in response.json()] == ["Vélo de ville"]


def test_lister_filtre_par_disponibilite(client: TestClient, item_velo: dict[str, Any]) -> None:
    client.post("/items", json={"titre": "Perceuse", "tarif_jour": 5, "disponible": False})

    response = client.get("/items", params={"disponible": False})

    assert [item["titre"] for item in response.json()] == ["Perceuse"]


def test_put_remplace_tous_les_champs(client: TestClient, item_velo: dict[str, Any]) -> None:
    response = client.put(f"/items/{item_velo['id']}", json={"titre": "Vélo pliant", "tarif_jour": 6.0})

    assert response.status_code == 200
    assert response.json() == {
        "id": item_velo["id"], "titre": "Vélo pliant", "description": None,
        "tarif_jour": 6.0, "disponible": True,
    }


def test_put_sans_champ_obligatoire_renvoie_422(client: TestClient, item_velo: dict[str, Any]) -> None:
    response = client.put(f"/items/{item_velo['id']}", json={"titre": "Vélo pliant"})

    assert response.status_code == 422


def test_put_item_inconnu_renvoie_404(client: TestClient) -> None:
    response = client.put("/items/999", json=ITEM_VALIDE)

    assert response.status_code == 404


def test_patch_ne_modifie_que_les_champs_envoyes(client: TestClient, item_velo: dict[str, Any]) -> None:
    response = client.patch(f"/items/{item_velo['id']}", json={"titre": "Vélo pliant"})

    corps = response.json()
    assert response.status_code == 200
    assert corps["titre"] == "Vélo pliant"
    assert corps["description"] == item_velo["description"]
    assert corps["tarif_jour"] == item_velo["tarif_jour"]


def test_patch_item_inconnu_renvoie_404(client: TestClient) -> None:
    response = client.patch("/items/999", json={"titre": "Vélo pliant"})

    assert response.status_code == 404


def test_supprimer_un_item_renvoie_204_puis_404_a_la_lecture(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    suppression = client.delete(f"/items/{item_velo['id']}")

    assert suppression.status_code == 204
    assert client.get(f"/items/{item_velo['id']}").status_code == 404


def test_supprimer_un_item_inconnu_renvoie_404(client: TestClient) -> None:
    response = client.delete("/items/999")

    assert response.status_code == 404
