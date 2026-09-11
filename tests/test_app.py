"""
Test suite for Mergington High School Activities API using AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_returns_all_activities_with_status_200(self, client):
        """
        Arrange: TestClient provided by fixture with preset activities
        Act: GET /activities
        Assert: Response status is 200 and all activities are returned
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # 9 total activities in fixture
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_returns_correct_participant_counts(self, client):
        """
        Arrange: TestClient with known participant counts
        Act: GET /activities
        Assert: Each activity has correct participant count
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        data = response.json()
        assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]
        assert len(data["Chess Club"]["participants"]) == 2
        assert len(data["Basketball Team"]["participants"]) == 1
        assert data["Basketball Team"]["max_participants"] == 15
    
    def test_response_contains_activity_metadata(self, client):
        """
        Arrange: TestClient
        Act: GET /activities
        Assert: Each activity has required fields (description, schedule, max_participants, participants)
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful_adds_participant(self, client):
        """
        Arrange: Activity name and new email address
        Act: POST signup with valid activity and email
        Assert: Response status 200, success message returned, participant added to list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
    
    def test_signup_to_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Nonexistent activity name
        Act: POST signup with bad activity name
        Assert: Response status 404 with "Activity not found" message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_email_returns_400(self, client):
        """
        Arrange: Email already signed up for activity
        Act: POST signup with duplicate email
        Assert: Response status 400 with "already signed up" message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_multiple_students_to_same_activity(self, client):
        """
        Arrange: Two different emails
        Act: Sign up both emails to same activity
        Assert: Both are added to participants list
        """
        # Arrange
        activity_name = "Tennis Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email1 in activities_data[activity_name]["participants"]
        assert email2 in activities_data[activity_name]["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_removes_participant(self, client):
        """
        Arrange: Participant already signed up for activity
        Act: DELETE unregister with valid activity and email
        Assert: Response status 200, participant removed from list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Verify participant exists before deletion
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]
        original_count = len(activities_data[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]
        assert len(activities_data[activity_name]["participants"]) == original_count - 1
    
    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Nonexistent activity name
        Act: DELETE unregister from bad activity
        Assert: Response status 404 with "Activity not found" message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_student_not_signed_up_returns_400(self, client):
        """
        Arrange: Student not signed up for activity
        Act: DELETE unregister with email not in participants
        Assert: Response status 400 with "not signed up" message
        """
        # Arrange
        activity_name = "Drama Club"
        email = "notstudent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_doesnt_affect_other_participants(self, client):
        """
        Arrange: Activity with multiple participants
        Act: Unregister one participant
        Assert: Other participants remain in list
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        email_to_keep = "daniel@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )
        
        # Assert
        assert response.status_code == 200
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email_to_remove not in activities_data[activity_name]["participants"]
        assert email_to_keep in activities_data[activity_name]["participants"]


class TestWorkflows:
    """Integration tests for multi-step workflows"""
    
    def test_signup_flow_fetch_verify(self, client):
        """
        Arrange: Activity and new email
        Act: 1) Fetch activities 2) Sign up 3) Fetch to verify
        Assert: Participant count increases after signup
        """
        # Arrange
        activity_name = "Art Club"
        email = "newartist@mergington.edu"
        
        # Act - Get initial count
        response1 = client.get("/activities")
        initial_count = len(response1.json()[activity_name]["participants"])
        
        # Act - Sign up
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act - Get updated list
        response3 = client.get("/activities")
        
        # Assert
        assert response2.status_code == 200
        assert len(response3.json()[activity_name]["participants"]) == initial_count + 1
        assert email in response3.json()[activity_name]["participants"]
    
    def test_full_participant_lifecycle(self, client):
        """
        Arrange: Activity and email
        Act: 1) Sign up 2) Fetch 3) Unregister 4) Fetch again
        Assert: Participant added then removed correctly
        """
        # Arrange
        activity_name = "Science Club"
        email = "newscientist@mergington.edu"
        
        # Act & Assert - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Act & Assert - Verify added
        fetch1_response = client.get("/activities")
        assert email in fetch1_response.json()[activity_name]["participants"]
        
        # Act & Assert - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Act & Assert - Verify removed
        fetch2_response = client.get("/activities")
        assert email not in fetch2_response.json()[activity_name]["participants"]
