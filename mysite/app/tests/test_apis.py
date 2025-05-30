import logging
import random
from datetime import date

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from ninja.testing import TestClient
from ninja_jwt.routers.obtain import obtain_pair_router

from app.api import router as jobs_router
from app.models import Job

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def client():
    return TestClient(jobs_router)


@pytest.fixture
def today():
    return date.today()


@pytest.fixture
@pytest.mark.django_db
def existing_job(today):
    return Job.objects.get(pk=random.randint(1, 200))


@pytest.fixture
def django_db_setup(django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "app_job.json")


@pytest.fixture
def token(create_user):
    """Fixture to create a JWT token for testing."""
    client = TestClient(obtain_pair_router)
    payload = {
        "username": create_user.username,
        "password": "testpassword",
    }
    response = client.post("/pair", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access" in data
    return data["access"]


@pytest.fixture
def create_user(django_db_setup):
    """Fixture to create a user for testing."""
    return User.objects.create_user(
        username="testuser",
        email="testuser@mail.com",
        password="testpassword",
        is_superuser=True,
        is_staff=True,
    )


@pytest.mark.django_db
class TestJWTAuthentication:
    """Test cases for JWT authentication."""

    def test_jwt_authentication(self, create_user):
        """Test JWT authentication with a valid user."""
        # Create a user and get the token
        user = create_user
        client = TestClient(obtain_pair_router)
        payload = {"username": user.username, "password": "testpassword"}
        response = client.post("/pair", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "access" in data


# --- Test Cases ---
@pytest.mark.django_db
class TestJobPostingAPI:
    # --- POST /jobs ---
    def test_create_job_success(self, client: TestClient, token: str):
        """Test the successful creation of a job posting.

        Args:
            client: TestClient
        assert:
            - The response status code is 201.
            - The response contains the created job's ID and title.
        """
        payload = {
            "title": "Test Job",
            "desc": "This is a test job description.",
            "location": "Remote",
            "salary_range": "50000~70000",
            "company_name": "Test Company",
            "posting_date": "2025-01-01",
            "expiration_date": "2025-04-01",
            "required_skills": "Python, Django",
        }
        response = client.post(
            "/jobs", headers={"Authorization": f"Bearer {token}"}, json=payload
        )
        assert response.status_code == 201
        data = response.json()
        logger.info(f"Response data: {data}")
        assert data["id"] is not None
        assert data["title"] == payload["title"]

    def test_create_job_with_negotiable_salary(self, client: TestClient, token: str):
        """Test creating a job with a negotiable salary.

        Args:
            client: TestClient
        assert:
            - The response status code is 201.
            - The response contains the created job's ID and title.
        """
        payload = {
            "title": "Negotiable Salary Job",
            "desc": "This job has a negotiable salary.",
            "location": "Remote",
            "salary_range": "面議",
            "company_name": "Negotiable Company",
            "posting_date": "2025-01-01",
            "expiration_date": "2025-04-01",
            "required_skills": "Python, Django",
        }
        response = client.post(
            "/jobs", headers={"Authorization": f"Bearer {token}"}, json=payload
        )
        assert response.status_code == 201
        data = response.json()
        logger.info(f"Response data: {data}")
        assert data["id"] is not None
        assert data["title"] == payload["title"]

    def test_creat_jobs_fail(self, client: TestClient, token: str):
        """Test the failure of job creation due to missing required fields.

        Args:
            client: TestClient
        assert:
            - The response status code is 422.
            - The response contains validation errors.
        """
        payload = {
            "title": "Incomplete Job",
            "location": "Remote",
            # Missing salary_range, company_name, posting_date, expiration_date, required_skills
        }
        response = client.post(
            "/jobs", headers={"Authorization": f"Bearer {token}"}, json=payload
        )
        assert response.status_code == 422
        data = response.json()
        logger.info(f"Response data: {data}")
        assert "detail" in data

    # --- GET /jobs ---
    def test_get_jobs_default_data_200(self, client: TestClient):
        """Test the default data returned by the GET /jobs endpoint.

        Args:
            client: TestClient
        assert:
            - The response status code is 200.
            - The response contains 10 job items.
            - The response matches the expected structure and data.
        """
        response = client.get("/jobs")
        print(repr(response.json()))
        assert response.status_code == 200
        assert len(response.json()["items"]) == 10

    def test_list_jobs_filter_and_order_by_200(self, client: TestClient):
        """Test the GET /jobs endpoint with specific filters and ordering.

        Args:
            client: TestClient
        assert:
            - The response status code is 200.
        """
        skill = "Project"
        order_by = "posting_date"

        response = client.get(
            f"/jobs?required_skills={skill}&order_by={order_by}&page=1"
        )
        assert response.status_code == 200
        data = response.json()
        logger.info(f"Response data: {data}")
        assert data["count"] == 41

        salary_gte = "30000"
        salary_lte = "50000"

        response = client.get(
            f"/jobs?salary_gte={salary_gte}&salary_lte={salary_lte}&order_by={order_by}&page=1"
        )
        assert response.status_code == 200
        data = response.json()
        logger.info(f"Response data: {data}")
        assert data["count"] == 20
        assert data["items"][0]["id"] == 51

    def test_list_jobs_with_search_params(self, client: TestClient):
        """Test the GET /jobs endpoint with search parameters.

        Args:
            client: TestClient
        assert:
            - The response status code is 200.
            - The response contains the expected job items.
        """
        # Search by title
        response = client.get("/jobs?search=Software Engineer")
        assert response.status_code == 200
        data = response.json()
        logger.info(f"Response data: {data}")
        assert len(data["items"]) > 0
        assert all("Software Engineer" in job["title"] for job in data["items"])

        # Search by company name
        response = client.get("/jobs?search=Travel and Leisure Co.")
        assert response.status_code == 200
        data = response.json()
        logger.info(f"Response data: {data}")
        assert len(data["items"]) > 0
        assert all(
            "Travel and Leisure Co." in job["company_name"] for job in data["items"]
        )

    def test_list_jobs_with_job_status(self, client: TestClient):
        """Test the GET /jobs endpoint with job status filtering.

        Args:
            client: TestClient
        assert:
            - The response status code is 200.
            - The response contains the expected job items.
        """
        # Filter by active jobs
        response = client.get("/jobs?status=active")
        assert response.status_code == 200
        data = response.json()
        logger.info(f"Response data: {data}")
        assert len(data["items"]) > 0
        assert all(job["status"] == "active" for job in data["items"])

        # Filter by expired jobs
        response = client.get("/jobs?status=expired")
        assert response.status_code == 200
        data = response.json()
        logger.info(f"Response data: {data}")
        assert len(data["items"]) > 0
        assert all(job["status"] == "expired" for job in data["items"])

    def test_list_jobs_invalid_params(self, client: TestClient):
        """Test the GET /jobs endpoint with a non-existent page.

        Arg:
            client: TestClient
        assert:
            - The response status code is 404.
        """

        # no title or company_name in JobListFilters,
        # return page 1 with 10 items
        response = client.get("/jobs?title=1+2&company_name=TechCorp")
        assert response.status_code == 200
        assert len(response.json()["items"]) == 10

        # Test with a non-existent page
        # return empty items
        response = client.get("/jobs?page=99999")  # Non-existent page
        assert response.status_code == 200
        assert len(response.json()["items"]) == 0

        # Test with a non-existent location and company_name
        # return empty items
        response = client.get("/jobs?location=1+2&company_name=TechCorp")
        assert response.status_code == 200
        data = response.json()
        assert data == {"count": 0, "items": []}

    def test_list_jobs_invalid_order_by(self, client: TestClient):
        """Test the GET /jobs endpoint with an invalid order_by parameter.

        Args:
            client: TestClient
        assert:
            - The response status code is 422.
        """
        response = client.get("/jobs?order_by=invalid_field")
        assert response.status_code == 422
        data = response.json()
        logger.info(f"Response data: {data}")
        assert "detail" in data
        assert data["detail"] == [
            {
                "type": "enum",
                "loc": ["query", "order_by"],
                "msg": "Input should be 'posting_date', '-posting_date', 'expiration_date' or '-expiration_date'",
                "ctx": {
                    "expected": "'posting_date', '-posting_date', 'expiration_date' or '-expiration_date'"
                },
            }
        ]

    # --- GET /jobs/{id} ---
    def test_get_job_by_id_success(self, client: TestClient, existing_job: Job):
        """Test the GET /jobs/{id} endpoint for an existing job.

        Args:
            client: TestClient instance for making requests.
            existing_job: A job instance created in the database.
        assert:
            - The response status code is 200.
            - The response contains the correct job ID and title.
        """
        response = client.get(f"/jobs/{existing_job.id}")
        assert response.status_code == 200
        data = response.json()
        logger.info(f"Response data: {data}")
        assert data["id"] == existing_job.id
        assert data["title"] == existing_job.title

    def test_get_job_by_id_not_found(self, client: TestClient):
        """Test the GET /jobs/{id} endpoint for a non-existent job ID.

        Args:
            client: TestClient instance for making requests.
        assert:
            - The response status code is 404.
        """
        response = client.get("/jobs/99999")  # Non-existent ID
        assert response.status_code == 404

    # --- PUT /jobs/{id} ---
    def test_update_job_by_title_success(
        self, client: TestClient, existing_job: Job, token: str
    ):
        """Test the PUT /jobs/{id} endpoint to update a job's title."""
        new_title = "Updated Job Title"
        payload = {"title": new_title}
        response = client.put(
            f"/jobs/{existing_job.id}",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
        )
        assert response.status_code == 200
        data = response.json()
        logger.info(f"Response data: {data}")
        assert data["id"] == existing_job.id
        assert data["title"] == new_title

    # --- DELETE /jobs/{id} ---
    def test_delete_job_by_id_success(
        self, client: TestClient, existing_job: Job, token: str
    ):
        """Test the DELETE /jobs/{id} endpoint to delete a job."""
        response = client.delete(
            f"/jobs/{existing_job.id}", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204

        # Verify the job is deleted
        response = client.get(f"/jobs/{existing_job.id}")
        assert response.status_code == 404
