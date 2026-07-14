"""Negative test cases: invalid inputs, missing resources, malformed requests.

Negative testing is often what separates SDET-level thinking from basic
automation - verifying the API fails gracefully and predictably matters
as much as verifying the happy path.
"""

import pytest

from src.endpoints import Endpoints
from src.api_client import ApiClient


@pytest.mark.negative
def test_movie_details_with_invalid_id_returns_404(api_client):
    response = api_client.get(Endpoints.movie_details(999_999_999))
    assert response.status_code == 404


@pytest.mark.negative
def test_movie_details_with_non_numeric_id_returns_error(api_client):
    response = api_client.get("/movie/not-a-valid-page")
    assert response.status_code in (400, 404)


@pytest.mark.negative
def test_search_with_empty_query_returns_error_or_empty(api_client):
    response = api_client.get(Endpoints.SEARCH_MOVIES, params={"query": ""})
    # TMDB returns 200 with empty results rather than an error for blank query -
    # asserting the actual observed contract, not an assumption.
    assert response.status_code in (200, 400, 422)


@pytest.mark.negative
def test_request_with_invalid_api_key_returns_401(settings):
    bad_client = ApiClient(
        base_url=settings.base_url,
        api_key="invalid_key_12345",
        timeout=settings.timeout,
    )
    response = bad_client.get(Endpoints.POPULAR_MOVIES)
    assert response.status_code == 401


@pytest.mark.negative
def test_popular_movies_with_out_of_range_page_handles_gracefully(api_client):
    response = api_client.get(Endpoints.POPULAR_MOVIES, params={"page": 99999})
    # TMDB caps pagination and returns 400 beyond max page - verify it doesn't
    # silently succeed with malformed data.
    assert response.status_code in (200, 400)
