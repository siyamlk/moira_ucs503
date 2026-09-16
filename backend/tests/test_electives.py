from app.models.elective import Elective
from app.services.recommendation_service import (
    normalize_career_goal,
    normalize_interests,
    score_elective,
)


def test_normalize_interests_extracts_tags_from_free_text():
    tags = normalize_interests(
        "I enjoy AI, data analysis, and programming, and I want to work in "
        "healthcare predictive systems and autonomous systems.",
        selected_interests=[],
    )
    assert "Artificial Intelligence" in tags
    assert "Data Science" in tags
    assert "Predictive Healthcare" in tags
    assert "Autonomous Systems" in tags
    assert "Software Engineering" in tags


def test_normalize_interests_merges_selected_chips_and_free_text():
    tags = normalize_interests("I like cloud computing", selected_interests=["Cybersecurity"])
    assert "Cybersecurity" in tags
    assert "Cloud Computing" in tags


def test_normalize_career_goal_extracts_canonical_tag():
    tags = normalize_career_goal("", "Applied AI Researcher / ML Engineer")
    assert "AI/ML Engineer" in tags


def test_score_elective_is_higher_for_stronger_overlap():
    strong_score, matched, interest_match, career_match, breakdown = score_elective(
        interest_tags=["Machine Learning", "Artificial Intelligence"],
        career_tags=["AI/ML Engineer"],
        elective_interest_tags=["Machine Learning", "Artificial Intelligence", "Data Science"],
        elective_career_tags=["AI/ML Engineer", "Data Scientist"],
        elective_topics=["Machine Learning", "Predictive Analytics"],
    )
    weak_score, _, _, _, _ = score_elective(
        interest_tags=["Machine Learning", "Artificial Intelligence"],
        career_tags=["AI/ML Engineer"],
        elective_interest_tags=["Finance"],
        elective_career_tags=["Finance/FinTech"],
        elective_topics=["Finance"],
    )
    assert strong_score > weak_score
    assert interest_match is True
    assert career_match is True
    assert "Machine Learning" in matched
    # The breakdown's components must sum to the displayed score — this is
    # what makes the percentage auditable rather than a hardcoded number.
    assert round(
        breakdown["interest_points"]
        + breakdown["career_points"]
        + breakdown["topic_points"]
        + breakdown["bonus_points"]
    ) == strong_score
    assert breakdown["interest_matched"] == 2
    assert breakdown["interest_total"] == 2


def test_score_elective_zero_overlap_scores_zero():
    score, matched, interest_match, career_match, breakdown = score_elective(
        interest_tags=["Cybersecurity"],
        career_tags=["Software Engineer"],
        elective_interest_tags=["Finance"],
        elective_career_tags=["Finance/FinTech"],
        elective_topics=["Finance"],
    )
    assert score == 0
    assert matched == []
    assert interest_match is False
    assert career_match is False
    assert breakdown["interest_matched"] == 0
    assert breakdown["bonus_points"] == 0


def test_recommend_endpoint_ranks_best_match_first(client, auth_headers, db_session):
    ml_elective = Elective(
        code="CS-402",
        title="Machine Learning & Predictive Analytics",
        credits=4.0,
        topics=["Machine Learning", "Predictive Analytics"],
        interest_tags=["Machine Learning", "Artificial Intelligence"],
        career_tags=["AI/ML Engineer"],
    )
    finance_elective = Elective(
        code="FIN-301",
        title="Financial Analytics",
        credits=3.0,
        topics=["Finance"],
        interest_tags=["Finance"],
        career_tags=["Finance/FinTech"],
    )
    db_session.add_all([ml_elective, finance_elective])
    db_session.commit()

    response = client.post(
        "/api/electives/recommend",
        json={
            "free_text": "I love AI and machine learning",
            "interests": [],
            "career_goal": "AI/ML Engineer",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["top_recommendation"]["elective"]["code"] == "CS-402"
    assert body["top_recommendation"]["match_percent"] > 0


def test_list_electives_is_public(client, db_session):
    db_session.add(Elective(code="CS-380", title="Cloud Computing", credits=4.0))
    db_session.commit()
    response = client.get("/api/electives")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_electives_filters_by_department(client, db_session):
    db_session.add_all(
        [
            Elective(code="UCS531", title="Cloud Computing", credits=3.0, department="Computer Science and Engineering"),
            Elective(code="UCS531", title="Cloud Computing", credits=3.0, department="Computer Engineering"),
        ]
    )
    db_session.commit()
    response = client.get("/api/electives", params={"department": "Computer Engineering"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["department"] == "Computer Engineering"


def test_recommend_only_shows_students_own_branch_plus_open_electives(
    client, auth_headers, db_session
):
    from app.models.user import User

    db_session.add_all(
        [
            Elective(
                code="UCS531",
                title="Cloud Computing",
                credits=3.0,
                department="Computer Science and Engineering",
                topics=["Cloud Computing"],
                interest_tags=["Cloud Computing"],
            ),
            Elective(
                code="UCS531",
                title="Cloud Computing",
                credits=3.0,
                department="Computer Engineering",
                topics=["Cloud Computing"],
                interest_tags=["Cloud Computing"],
            ),
            Elective(
                code="UHU051",
                title="Creative Writing",
                credits=2.0,
                department="Open Elective (All Branches)",
                topics=["Cloud Computing"],  # tagged for test purposes only
                interest_tags=["Cloud Computing"],
            ),
        ]
    )
    user = db_session.query(User).filter(User.email == "test.student@thapar.edu").first()
    user.profile.branch = "Computer Science and Engineering"
    db_session.commit()

    response = client.post(
        "/api/electives/recommend",
        json={"free_text": "cloud computing", "interests": [], "career_goal": ""},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    codes_and_departments = {
        (r["elective"]["code"], r["elective"]["department"])
        for r in [body["top_recommendation"], *body["alternatives"]]
        if r
    }
    # The CSE section and the open elective are visible; the COE-only section is not.
    assert ("UCS531", "Computer Science and Engineering") in codes_and_departments
    assert ("UHU051", "Open Elective (All Branches)") in codes_and_departments
    assert ("UCS531", "Computer Engineering") not in codes_and_departments
