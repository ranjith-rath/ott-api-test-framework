"""
Centralized API endpoint definitions.

Keeping endpoints here instead of scattered across test files means a single
change (e.g., an API version bump) only needs to happen in one place.
"""


class Endpoints:
    POPULAR_MOVIES = "/movie/popular"
    MOVIE_DETAILS = "/movie/{movie_id}"
    SEARCH_MOVIES = "/search/movie"
    GENRES = "/genre/movie/list"
    TOP_RATED = "/movie/top_rated"

    @staticmethod
    def movie_details(movie_id: int) -> str:
        return Endpoints.MOVIE_DETAILS.format(movie_id=movie_id)
