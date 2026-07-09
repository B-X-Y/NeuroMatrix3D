import matrix_app


def test_livez_returns_200_and_ok():
    response = matrix_app.app.test_client().get("/livez")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
