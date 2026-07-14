"""Data-driven search scenarios using pytest parametrization."""

import pytest

from src.endpoints import Endpoints


@pytest.mark.smoke
@pytest.mark.parametrize(
    "query, expected_min_results",
    [
        ("Inception", 1),
        ("The Matrix", 1),
        ("Interstellar", 1),
    ],
)
def test_search_returns_expected_movie(api_client, query, expected_min_results):
    response = api_client.get(Endpoints.SEARCH_MOVIES, params={"query": query})
    body = response.json()

    assert response.status_code == 200
    assert len(body["results"]) >= expected_min_results
    titles = [m["title"].lower() for m in body["results"]]
    assert any(query.lower() in title for title in titles)


@pytest.mark.regression
@pytest.mark.parametrize("year", [2010, 2015, 2020])
def test_search_with_year_filter_returns_correct_year(api_client, year):
    response = api_client.get(
        Endpoints.SEARCH_MOVIES, params={"query": "the", "primary_release_year": year}
    )
    body = response.json()

    assert response.status_code == 200
    for movie in body["results"][:5]:
        if movie.get("release_date"):
            assert movie["release_date"].startswith(str(year))


@pytest.mark.regression
def test_search_results_have_valid_popularity_scores(api_client):
    response = api_client.get(Endpoints.SEARCH_MOVIES, params={"query": "star"})
    body = response.json()

    scores = [m["popularity"] for m in body["results"]]
    assert all(isinstance(s, (int, float)) for s in scores)
