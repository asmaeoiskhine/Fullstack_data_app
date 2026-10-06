from typing import Any

import pytest
from fastapi.testclient import TestClient

RESERVATION_VALIDE = {"item_id": 1, "date_debut": "2026-09-01", "date_fin": "2026-09-05"}


def test_creer_une_reservation_renvoie_201_et_statut_active(client: TestClient) -> None:
    response = client.post("/reservations", json=RESERVATION_VALIDE)

    assert response.status_code == 201
    assert response.json() == {"id": 1, **RESERVATION_VALIDE, "statut": "active"}


def test_une_reservation_creee_est_relisible_par_get(
    client: TestClient, reservation_active: dict[str, Any]
) -> None:
    response = client.get(f"/reservations/{reservation_active['id']}")

    assert response.status_code == 200
    assert response.json() == reservation_active


def test_lire_une_reservation_inconnue_renvoie_404(client: TestClient) -> None:
    response = client.get("/reservations/999")

    assert response.status_code == 404


@pytest.mark.parametrize("reservation_id", ["abc", "0"])
def test_identifiant_de_reservation_invalide_renvoie_422(
    client: TestClient, reservation_id: str
) -> None:
    response = client.get(f"/reservations/{reservation_id}")

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("payload", "champ_en_erreur"),
    [
        ({"item_id": 1, "date_debut": "2026-09-05", "date_fin": "2026-09-01"}, "body"),
        ({"item_id": 1, "date_debut": "2026-09-01", "date_fin": "2026-09-01"}, "body"),
        ({"item_id": 0, "date_debut": "2026-09-01", "date_fin": "2026-09-05"}, "item_id"),
        ({"item_id": 1, "date_debut": "2026-09-01"}, "date_fin"),
        ({**RESERVATION_VALIDE, "couleur": "rouge"}, "couleur"),
    ],
)
def test_creation_reservation_invalide_renvoie_422(
    client: TestClient, payload: dict[str, Any], champ_en_erreur: str
) -> None:
    response = client.post("/reservations", json=payload)

    assert response.status_code == 422
    champs = [erreur["loc"][-1] for erreur in response.json()["detail"]]
    assert champ_en_erreur in champs


def test_lister_sans_reservation_renvoie_une_liste_vide(client: TestClient) -> None:
    response = client.get("/reservations")

    assert response.status_code == 200
    assert response.json() == []


def test_lister_filtre_par_item(
    client: TestClient, item_velo: dict[str, Any], reservation_active: dict[str, Any]
) -> None:
    autre_item = client.post("/items", json={"titre": "Perceuse", "tarif_jour": 5}).json()
    client.post("/reservations", json={
        "item_id": autre_item["id"], "date_debut": "2026-10-01", "date_fin": "2026-10-03",
    })

    response = client.get("/reservations", params={"item_id": item_velo["id"]})

    assert [r["id"] for r in response.json()] == [reservation_active["id"]]


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 500}, {"item_id": 0}])
def test_lister_avec_parametres_hors_bornes_renvoie_422(
    client: TestClient, params: dict[str, int]
) -> None:
    response = client.get("/reservations", params=params)

    assert response.status_code == 422


def test_annuler_une_reservation_renvoie_200_et_statut_annulee(
    client: TestClient, reservation_active: dict[str, Any]
) -> None:
    response = client.post(f"/reservations/{reservation_active['id']}/annuler")

    assert response.status_code == 200
    assert response.json()["statut"] == "annulee"


def test_annuler_une_reservation_deja_annulee_renvoie_409(
    client: TestClient, reservation_active: dict[str, Any]
) -> None:
    # Given : la réservation a déjà été annulée une fois.
    client.post(f"/reservations/{reservation_active['id']}/annuler")

    # When : on demande une seconde annulation.
    response = client.post(f"/reservations/{reservation_active['id']}/annuler")

    # Then : l'API refuse avec un conflit, et la réservation reste annulée.
    assert response.status_code == 409
    assert client.get(f"/reservations/{reservation_active['id']}").json()["statut"] == "annulee"


def test_annuler_une_reservation_inconnue_renvoie_404(client: TestClient) -> None:
    response = client.post("/reservations/999/annuler")

    assert response.status_code == 404
