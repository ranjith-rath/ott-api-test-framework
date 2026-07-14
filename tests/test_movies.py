"""Tests covering movie details and popular movie listings."""

import pytest

from src.endpoints import Endpoints
from utils.schema_validator import validate_schema


@pytest.mark.smoke
def test_popular_movies_returns_200(api_client):
    response = api_client.get(Endpoints.POPULAR_MOVIES)
    assert response.status_code == 200


@pytest.mark.smoke
def test_popular_movies_returns_results(api_client):
    response = api_client.get(Endpoints.POPULAR_MOVIES)
    body = response.json()

    assert "results" in body
    assert len(body["results"]) > 0


@pytest.mark.regression
def test_popular_movies_pagination(api_client):
    page_1 = api_client.get(Endpoints.POPULAR_MOVIES, params={"page": 1}).json()
    page_2 = api_client.get(Endpoints.POPULAR_MOVIES, params={"page": 2}).json()

    page_1_ids = {m["id"] for m in page_1["results"]}
    page_2_ids = {m["id"] for m in page_2["results"]}

    assert page_1["page"] == 1
    assert page_2["page"] == 2
    assert page_1_ids.isdisjoint(page_2_ids), "Pages should not return duplicate movies"


@pytest.mark.regression
def test_popular_movie_schema_contract(api_client):
    """Validate that each movie in the popular list matches the expected contract.

    This catches breaking API changes (renamed/removed fields, type changes)
    that individual field assertions would miss.
    """
    response = api_client.get(Endpoints.POPULAR_MOVIES)
    results = response.json()["results"]

    for movie in results[:5]:
        validate_schema(movie, "movie_schema.json")


@pytest.mark.regression
def test_movie_details_matches_requested_id(api_client):
    popular = api_client.get(Endpoints.POPULAR_MOVIES).json()
    sample_id = popular["results"][0]["id"]

    response = api_client.get(Endpoints.movie_details(sample_id))
    body = response.json()

    assert response.status_code == 200
    assert body["id"] == sample_id
    assert "runtime" in body
    assert "genres" in body


@pytest.mark.smoke
def test_movie_details_average_vote_within_valid_range(api_client):
    popular = api_client.get(Endpoints.POPULAR_MOVIES).json()
    sample_id = popular["results"][0]["id"]

    body = api_client.get(Endpoints.movie_details(sample_id)).json()

    assert 0 <= body["vote_average"] <= 10
