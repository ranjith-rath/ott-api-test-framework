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
def test_pagination_returns_distinct_pages(api_client):
    """Verify pagination returns different items per page.

    Uses /movie/top_rated instead of /movie/popular: the popular list
    re-sorts continuously by live popularity score, so an item can drift
    across the page boundary between two calls and appear on both pages —
    a false failure. Top-rated ordering is stable.
    """
    resp_1 = api_client.get(Endpoints.TOP_RATED, params={"page": 1})
    resp_2 = api_client.get(Endpoints.TOP_RATED, params={"page": 2})

    # Assert status BEFORE .json() — a 5xx error body isn't JSON,
    # and calling .json() on it raises a misleading decode error.
    assert resp_1.status_code == 200
    assert resp_2.status_code == 200

    page_1 = resp_1.json()
    page_2 = resp_2.json()

    # The API should echo back the page we requested
    assert page_1["page"] == 1
    assert page_2["page"] == 2

    # Both pages should actually contain results (guard against
    # vacuously passing on empty lists)
    assert page_1["results"], "Page 1 returned no results"
    assert page_2["results"], "Page 2 returned no results"

    page_1_ids = {m["id"] for m in page_1["results"]}
    page_2_ids = {m["id"] for m in page_2["results"]}

    overlap = page_1_ids & page_2_ids
    assert not overlap, f"Pages returned duplicate movies: {overlap}"


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
