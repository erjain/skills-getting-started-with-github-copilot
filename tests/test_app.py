from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_root_redirects_to_index():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers.get("location") == "/static/index.html"


def test_get_activities_returns_all():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()

    # Should be a mapping of activity names to details
    assert isinstance(data, dict)
    # Spot-check a few known activities
    for name in [
        "Chess Club",
        "Programming Class",
        "Gym Class",
    ]:
        assert name in data
        assert "description" in data[name]
        assert "schedule" in data[name]
        assert "participants" in data[name]


def test_signup_for_activity_success():
    activity_name = "Art Club"  # initially has empty participants
    email = "newstudent@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert response.status_code == 200
    body = response.json()
    assert "Signed up" in body.get("message", "")
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_not_found():
    response = client.post(
        "/activities/Nonexistent%20Club/signup",
        params={"email": "student@mergington.edu"},
    )
    assert response.status_code == 404


def test_unregister_from_activity_success():
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )
    assert response.status_code == 200
    body = response.json()
    assert "Unregistered" in body.get("message", "")
    assert email not in activities[activity_name]["participants"]


def test_unregister_from_activity_not_registered():
    activity_name = "Programming Class"
    email = "notregistered@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )
    assert response.status_code == 404
