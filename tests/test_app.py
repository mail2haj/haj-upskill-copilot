import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


# Base activity fixture used to reset the in-memory database between tests.
# We copy the original activity data defined in src/app.py.
INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["alex@mergington.edu", "lucas@mergington.edu"],
    },
    "Basketball Club": {
        "description": "Practice basketball skills and play friendly games",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["mia@mergington.edu", "noah@mergington.edu"],
    },
    "Drama Club": {
        "description": "Act, direct, and participate in school plays",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["ava@mergington.edu", "liam@mergington.edu"],
    },
    "Art Workshop": {
        "description": "Explore painting, drawing, and other visual arts",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["isabella@mergington.edu", "elijah@mergington.edu"],
    },
    "Math Club": {
        "description": "Solve challenging math problems and prepare for competitions",
        "schedule": "Fridays, 4:00 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["charlotte@mergington.edu", "benjamin@mergington.edu"],
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["amelia@mergington.edu", "jack@mergington.edu"],
    },
}


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities data before each test."""
    activities.clear()
    activities.update({k: {**v, "participants": list(v["participants"])} for k, v in INITIAL_ACTIVITIES.items()})


@pytest.fixture
def client():
    return TestClient(app)


def test_root_redirect(client):
    response = client.get("/")
    assert response.status_code in (301, 302, 307)
    assert response.headers["location"].endswith("/static/index.html")


def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["max_participants"] == 12
    assert "participants" in data["Chess Club"]


def test_signup_success(client):
    response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]

    activities_resp = client.get("/activities")
    assert "test@mergington.edu" in activities_resp.json()["Chess Club"]["participants"]


def test_signup_duplicate(client):
    client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")
    response = client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_invalid_activity(client):
    response = client.post("/activities/NotAClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_delete_participant_success(client):
    client.post("/activities/Chess%20Club/signup?email=to_delete@mergington.edu")
    response = client.delete("/activities/Chess%20Club/participants/to_delete@mergington.edu")
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]

    activities_resp = client.get("/activities")
    assert "to_delete@mergington.edu" not in activities_resp.json()["Chess Club"]["participants"]


def test_delete_participant_not_found(client):
    response = client.delete("/activities/Chess%20Club/participants/doesnotexist@mergington.edu")
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]


def test_delete_invalid_activity(client):
    response = client.delete("/activities/NotAClub/participants/test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
