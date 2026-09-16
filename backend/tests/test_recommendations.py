from app.models.elective import Elective
from app.recommendation.scoring_engine import SCORE_WEIGHTS, score_elective


def _score(**overrides):
    base = dict(
        interest_tags=[],
        career_tags=[],
        skills=[],
        completed_courses=[],
        elective_slot=None,
        elective_interest_tags=[],
        elective_career_tags=[],
        elective_topics=[],
        elective_title="Sample Course",
        elective_description="",
        elective_syllabus_outline=[],
        elective_prerequisites="",
        elective_category="Elective I",
    )
    base.update(overrides)
    return score_elective(**base)


def test_score_weights_sum_to_100():
    assert sum(SCORE_WEIGHTS.values()) == 100


def test_custom_interest_term_with_no_canonical_match_still_scores():
    # Regression test: a student's typed interest that doesn't match any of
    # the ~25 preset canonical tags used to be silently dropped before it
    # ever reached score_elective — the chip would render in the UI but have
    # zero effect on the match percentage, which is exactly the kind of
    # silent-nothing behavior that misleads a student trusting the number.
    no_custom_term = _score(interest_tags=[])
    with_matching_custom_term = _score(
        interest_tags=[],
        custom_interest_terms=["sustainable computing"],
        elective_description="This course covers sustainable computing practices in depth.",
    )
    interest_without = next(c for c in no_custom_term.components if c.key == "interest").earned
    interest_with = next(c for c in with_matching_custom_term.components if c.key == "interest").earned
    assert interest_with > interest_without
    assert "sustainable computing" in with_matching_custom_term.matched_interests


def test_skill_matching_respects_word_boundaries():
    # Regression test: skill/custom-interest matching used to be a raw
    # substring check with no word boundary, so a short skill like "go"
    # (the Go language) falsely matched any course description containing
    # "algorithm" or "categorical" — pure coincidental substrings, not real
    # evidence the course covers Go. That's exactly the kind of false
    # positive that misleads a student trusting the match.
    result = _score(
        skills=["go"],
        elective_description="This course covers general algorithms and categorical data structures.",
    )
    assert "go" not in result.matched_skills

    real_match = _score(
        skills=["go"],
        elective_description="This course teaches concurrent programming in Go.",
    )
    assert "go" in real_match.matched_skills


def test_custom_interest_term_with_no_text_match_earns_nothing_fabricated():
    # A custom term that genuinely doesn't appear anywhere in the course's
    # text must not be credited — no invented relevance.
    result = _score(
        interest_tags=[],
        custom_interest_terms=["underwater basket weaving"],
        elective_description="This course covers cloud infrastructure.",
    )
    assert "underwater basket weaving" not in result.matched_interests


def test_career_alignment_is_proportional_not_all_or_nothing():
    # A course matching only 1 of the student's 2 career tags should score
    # half the career weight, not the full weight — previously any single
    # match earned full credit regardless of how many tags the student had.
    one_of_two = _score(
        career_tags=["AI/ML Engineer", "Robotics Engineer"],
        elective_career_tags=["AI/ML Engineer"],
    )
    two_of_two = _score(
        career_tags=["AI/ML Engineer", "Robotics Engineer"],
        elective_career_tags=["AI/ML Engineer", "Robotics Engineer"],
    )
    career_one = next(c for c in one_of_two.components if c.key == "career").earned
    career_two = next(c for c in two_of_two.components if c.key == "career").earned
    # Engine rounds half-up (see scoring_engine._earn), not Python's
    # banker's-rounding round() — 12.5 -> 13, not 12.
    assert career_one == int(SCORE_WEIGHTS["career"] * 0.5 + 0.5)
    assert career_two == SCORE_WEIGHTS["career"]
    assert career_one < career_two


def test_syllabus_alignment_floor_when_tag_relevant_but_no_real_text_evidence():
    # A course's real EFB unit headers can legitimately never spell out a
    # broader theme it's obviously about (e.g. a UI/UX course whose units
    # are named after specific technologies like "JavaScript"). Rather
    # than scoring 0, a tag-relevant course with no textual line evidence
    # gets a flat floor.
    scored = _score(
        interest_tags=["Natural Language Processing"],
        elective_interest_tags=["Natural Language Processing"],
        elective_topics=["Natural Language Processing"],
        elective_syllabus_outline=["Robot Manipulation", "Inverse Kinematics", "Gripping and Task Learning"],
    )
    syllabus_component = next(c for c in scored.components if c.key == "syllabus")
    assert scored.matched_syllabus_lines == []
    assert syllabus_component.earned == int(SCORE_WEIGHTS["syllabus"] * 0.35 + 0.5)


def test_syllabus_alignment_strong_real_evidence_exceeds_the_floor():
    scored = _score(
        interest_tags=["Natural Language Processing"],
        elective_interest_tags=["Natural Language Processing"],
        elective_topics=["Natural Language Processing"],
        elective_syllabus_outline=[
            "Introduction to Natural Language Processing",
            "Advanced Natural Language Processing",
            "Robot Manipulation",
            "Reinforcement Learning",
        ],
    )
    syllabus_component = next(c for c in scored.components if c.key == "syllabus")
    # 2 of 4 outline lines genuinely match -> 0.5, clearing the 0.35 floor.
    assert syllabus_component.earned == int(SCORE_WEIGHTS["syllabus"] * 0.5 + 0.5)
    assert syllabus_component.earned > int(SCORE_WEIGHTS["syllabus"] * 0.35 + 0.5)


def test_syllabus_alignment_weak_real_evidence_never_scores_below_the_floor():
    # Only 1 of 5 outline lines matches (0.2), weaker than the 0.35 floor
    # — finding *some* real evidence must never score worse than finding
    # none at all.
    scored = _score(
        interest_tags=["Natural Language Processing"],
        elective_interest_tags=["Natural Language Processing"],
        elective_topics=["Natural Language Processing"],
        elective_syllabus_outline=[
            "Introduction to Natural Language Processing",
            "Robot Manipulation",
            "Reinforcement Learning",
            "Perception",
            "Task Learning",
        ],
    )
    syllabus_component = next(c for c in scored.components if c.key == "syllabus")
    assert syllabus_component.earned == int(SCORE_WEIGHTS["syllabus"] * 0.35 + 0.5)


def test_syllabus_alignment_has_no_denominator_bias_for_richly_tagged_courses():
    # Regression: an earlier design divided by *this course's own* topic
    # count, so a narrowly-tagged course (1 topic total) hit a "perfect"
    # ratio trivially while a richly-tagged course covering MORE genuine
    # ground (matching the student's interest plus other real topics)
    # scored *lower* for the identical match — rewarding thin tagging
    # over substantive relevance. Two courses with the same matched tag
    # but different total tag counts must now score identically.
    narrowly_tagged = _score(
        interest_tags=["Autonomous Systems"],
        elective_interest_tags=["Autonomous Systems"],
        elective_topics=["Autonomous Systems"],
    )
    richly_tagged = _score(
        interest_tags=["Autonomous Systems"],
        elective_interest_tags=["Autonomous Systems", "Computer Vision", "Artificial Intelligence"],
        elective_topics=["Autonomous Systems", "Computer Vision", "Artificial Intelligence"],
    )
    narrow_syllabus = next(c for c in narrowly_tagged.components if c.key == "syllabus")
    rich_syllabus = next(c for c in richly_tagged.components if c.key == "syllabus")
    assert narrow_syllabus.earned == rich_syllabus.earned


def test_full_interest_and_career_match_scores_higher_than_no_match():
    strong = _score(
        interest_tags=["Machine Learning", "Artificial Intelligence"],
        career_tags=["AI/ML Engineer"],
        elective_interest_tags=["Machine Learning", "Artificial Intelligence"],
        elective_career_tags=["AI/ML Engineer"],
        elective_topics=["Machine Learning", "Artificial Intelligence"],
    )
    weak = _score(
        interest_tags=["Machine Learning", "Artificial Intelligence"],
        career_tags=["AI/ML Engineer"],
        elective_interest_tags=["Finance"],
        elective_career_tags=["Finance/FinTech"],
        elective_topics=["Finance"],
    )
    assert strong.match_percentage > weak.match_percentage
    assert strong.matched_interests == ["Artificial Intelligence", "Machine Learning"]
    # The sum of components must equal the reported percentage exactly —
    # this is what makes the score auditable rather than a black box.
    assert sum(c.earned for c in strong.components) == strong.match_percentage


def test_score_is_deterministic_for_identical_inputs():
    kwargs = dict(
        interest_tags=["Cybersecurity"],
        career_tags=["Cybersecurity Analyst"],
        elective_interest_tags=["Cybersecurity", "Digital Forensics"],
        elective_career_tags=["Cybersecurity Analyst"],
        elective_topics=["Cybersecurity"],
        skills=["nmap", "wireshark"],
        elective_title="Network Defence",
        elective_description="Covers ethical hacking and wireshark traffic analysis.",
    )
    first = _score(**kwargs)
    second = _score(**kwargs)
    assert first.match_percentage == second.match_percentage
    assert first.components == second.components


def test_skill_alignment_only_credits_skills_actually_in_course_text():
    scored = _score(
        skills=["docker", "photoshop"],
        elective_title="Cloud & DevOps",
        elective_description="Covers Docker and Kubernetes container orchestration.",
    )
    assert scored.matched_skills == ["docker"]
    skill_component = next(c for c in scored.components if c.key == "skill")
    # 1 of 2 skills matched -> half the skill weight, rounded.
    assert skill_component.earned == round(SCORE_WEIGHTS["skill"] * 0.5)


def test_prerequisite_compatibility_reflects_completed_courses():
    met = _score(
        completed_courses=["Finance, Accounting and Valuation"],
        elective_prerequisites="Finance, Accounting and Valuation",
    )
    unmet = _score(
        completed_courses=["Data Structures"],
        elective_prerequisites="Finance, Accounting and Valuation",
    )
    met_prereq = next(c for c in met.components if c.key == "prerequisite")
    unmet_prereq = next(c for c in unmet.components if c.key == "prerequisite")
    assert met_prereq.earned == SCORE_WEIGHTS["prerequisite"]
    assert unmet_prereq.earned == 0
    assert met.prerequisite_checks[0].satisfied is True
    assert unmet.prerequisite_checks[0].satisfied is False


def test_no_prerequisite_listed_is_fully_compatible():
    scored = _score(completed_courses=[], elective_prerequisites="")
    prereq_component = next(c for c in scored.components if c.key == "prerequisite")
    assert prereq_component.earned == SCORE_WEIGHTS["prerequisite"]


def test_elective_slot_mismatch_lowers_academic_fit():
    matching_slot = _score(elective_slot="Elective II", elective_category="Elective II")
    wrong_slot = _score(elective_slot="Elective II", elective_category="Elective IV")
    matching_academic = next(c for c in matching_slot.components if c.key == "academic")
    wrong_academic = next(c for c in wrong_slot.components if c.key == "academic")
    assert matching_academic.earned > wrong_academic.earned
    assert matching_slot.slot_matched is True
    assert wrong_slot.slot_matched is False


def _seed_two_electives(db_session):
    ml_course = Elective(
        code="UCS761",
        title="Deep Learning",
        department="Computer Science and Engineering",
        credits=3.0,
        category="Elective III",
        basket="Data Science",
        description="Covers convolutional neural networks, transformers and generative adversarial networks for computer vision.",
        prerequisites="",
        topics=["Machine Learning", "Artificial Intelligence", "Computer Vision"],
        interest_tags=["Machine Learning", "Artificial Intelligence", "Computer Vision"],
        career_tags=["AI/ML Engineer"],
        syllabus_outline=["Convolutional Neural Networks", "Recurrent Neural Networks", "Autoencoders and GANs"],
    )
    devops_course = Elective(
        code="UCS745",
        title="Cloud & DevOps",
        department="Computer Science and Engineering",
        credits=3.0,
        category="Elective IV",
        basket="DevOps and Continuous Delivery",
        description="Covers DevOps principles, CI/CD, Docker and Kubernetes container orchestration.",
        prerequisites="",
        topics=["DevOps", "Cloud Computing"],
        interest_tags=["DevOps", "Cloud Computing"],
        career_tags=["DevOps Engineer"],
        syllabus_outline=["Introduction to DevOps", "Application Containerization", "Green Cloud Computing"],
    )
    db_session.add_all([ml_course, devops_course])
    db_session.commit()
    return ml_course, devops_course


def test_recommend_endpoint_ranks_differently_for_different_profiles(client, auth_headers, db_session):
    _seed_two_electives(db_session)

    ml_response = client.post(
        "/api/recommendations",
        json={
            "student_profile": {
                "interests": ["Machine Learning", "Computer Vision"],
                "career_goals": ["AI/ML Engineer"],
                "skills": ["pytorch"],
            }
        },
        headers=auth_headers,
    )
    devops_response = client.post(
        "/api/recommendations",
        json={
            "student_profile": {
                "interests": ["DevOps", "Cloud Computing"],
                "career_goals": ["DevOps Engineer"],
                "skills": ["docker"],
            }
        },
        headers=auth_headers,
    )

    assert ml_response.status_code == 200
    assert devops_response.status_code == 200

    ml_top = ml_response.json()["primary_recommendation"]
    devops_top = devops_response.json()["primary_recommendation"]

    assert ml_top["course_code"] == "UCS761"
    assert devops_top["course_code"] == "UCS745"
    # Different profiles against the same course catalogue must produce
    # different top picks and different percentages — proves this isn't a
    # fixed/hardcoded per-course number.
    assert ml_top["match_percentage"] != devops_top["match_percentage"] or ml_top["course_code"] != devops_top["course_code"]

    # The explanation must cite real syllabus text, not a generic template.
    assert any(
        "Convolutional Neural Networks" in line or "Autoencoders" in line
        for line in ml_top["matched_syllabus_topics"]
    )

    # Every response's all_eligible_courses must include both courses —
    # lower-scoring eligible electives are never hidden.
    all_codes = {c["course_code"] for c in ml_response.json()["all_eligible_courses"]}
    assert all_codes == {"UCS761", "UCS745"}


def test_recommend_endpoint_respects_elective_slot_filter(client, auth_headers, db_session):
    _seed_two_electives(db_session)

    response = client.post(
        "/api/recommendations",
        json={
            "student_profile": {"interests": ["Machine Learning"], "career_goals": ["AI/ML Engineer"]},
            "elective_slot": "Elective IV",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    codes = {c["course_code"] for c in body["all_eligible_courses"]}
    # Deep Learning is "Elective III" — must be excluded when the student
    # is choosing from the Elective IV slot, even though it scores higher.
    assert codes == {"UCS745"}


def test_recommend_endpoint_respects_basket_lock(client, auth_headers, db_session):
    _seed_two_electives(db_session)
    another_data_science_course = Elective(
        code="UCS548",
        title="Foundation of Data Science",
        department="Computer Science and Engineering",
        credits=3.0,
        category="Elective I",
        basket="Data Science",
        interest_tags=["Data Science"],
        career_tags=[],
        topics=["Data Science"],
    )
    db_session.add(another_data_science_course)
    db_session.commit()

    # A student who has already committed to the "Data Science" basket
    # must only see Data Science-basket courses — Cloud & DevOps belongs
    # to a different basket and is not a real option for them, even though
    # it might otherwise score well.
    response = client.post(
        "/api/recommendations",
        json={
            "student_profile": {
                "interests": ["Machine Learning", "DevOps"],
                "current_basket": "Data Science",
            }
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    codes = {c["course_code"] for c in body["all_eligible_courses"]}
    assert codes == {"UCS761", "UCS548"}
    assert "UCS745" not in codes
    assert body["current_basket"] == "Data Science"
    assert set(body["available_baskets"]) >= {"Data Science", "DevOps and Continuous Delivery"}


def test_recommend_endpoint_aggregates_basket_level_recommendations(client, auth_headers, db_session):
    ml_course, devops_course = _seed_two_electives(db_session)
    second_ds_course = Elective(
        code="UCS548",
        title="Foundation of Data Science",
        department="Computer Science and Engineering",
        credits=3.0,
        category="Elective I",
        basket="Data Science",
        interest_tags=["Data Science"],
        career_tags=[],
        topics=["Data Science"],
    )
    db_session.add(second_ds_course)
    db_session.commit()

    response = client.post(
        "/api/recommendations",
        json={"student_profile": {"interests": ["Machine Learning", "Data Science"], "career_goals": ["AI/ML Engineer"]}},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()

    # The primary recommendation unit is a whole basket, not a single course.
    assert body["primary_basket"]["basket_name"] == "Data Science"
    basket_course_codes = {e["course_code"] for e in body["primary_basket"]["electives"]}
    assert basket_course_codes == {"UCS761", "UCS548"}

    # The basket's match_percentage is the actual average of its member
    # courses' own scores — not an independently fabricated number.
    member_scores = [e["match_percentage"] for e in body["primary_basket"]["electives"]]
    assert body["primary_basket"]["match_percentage"] == round(sum(member_scores) / len(member_scores))

    # The DevOps course's own basket ("DevOps and Continuous Delivery")
    # must appear as an alternative basket, not be silently dropped.
    alt_basket_names = {b["basket_name"] for b in body["alternative_baskets"]}
    assert "DevOps and Continuous Delivery" in alt_basket_names
    assert body["primary_basket"]["basket_name"] not in alt_basket_names


def test_committed_basket_shows_own_basket_as_primary_with_no_alternatives(client, auth_headers, db_session):
    _seed_two_electives(db_session)
    response = client.post(
        "/api/recommendations",
        json={
            "student_profile": {
                "interests": ["DevOps"],
                "current_basket": "DevOps and Continuous Delivery",
            }
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    # Already committed — nothing left to recommend an alternative basket
    # for, so the "primary" is just their own committed basket's status.
    assert body["primary_basket"]["basket_name"] == "DevOps and Continuous Delivery"
    assert body["alternative_baskets"] == []


def test_recommend_endpoint_is_deterministic_across_repeated_calls(client, auth_headers, db_session):
    _seed_two_electives(db_session)
    payload = {
        "student_profile": {"interests": ["Machine Learning"], "career_goals": ["AI/ML Engineer"], "skills": ["pytorch"]}
    }
    first = client.post("/api/recommendations", json=payload, headers=auth_headers).json()
    second = client.post("/api/recommendations", json=payload, headers=auth_headers).json()
    assert first["primary_recommendation"]["match_percentage"] == second["primary_recommendation"]["match_percentage"]
    assert first["primary_recommendation"]["score_breakdown"] == second["primary_recommendation"]["score_breakdown"]


def test_recommend_endpoint_persists_profile_for_next_call(client, auth_headers, db_session):
    _seed_two_electives(db_session)
    client.post(
        "/api/recommendations",
        json={"student_profile": {"interests": ["DevOps"], "career_goals": ["DevOps Engineer"], "skills": ["docker"]}},
        headers=auth_headers,
    )
    # Second call supplies nothing new — should reuse what was just persisted.
    second = client.post("/api/recommendations", json={}, headers=auth_headers)
    assert second.status_code == 200
    assert second.json()["primary_recommendation"]["course_code"] == "UCS745"


def test_recommend_endpoint_respects_explicitly_cleared_selections(client, auth_headers, db_session):
    # Regression test: a student picks a career goal once, then on a later
    # visit deliberately deselects it (submits career_goals: []) without
    # picking a new one. That must be honored — not silently replaced with
    # the stale value from the first call. Previously _merge() treated an
    # empty list the same as "field omitted" and fell back to whatever was
    # last saved, so a cleared chip could never actually go away.
    _seed_two_electives(db_session)
    first = client.post(
        "/api/recommendations",
        json={"student_profile": {"interests": ["Machine Learning"], "career_goals": ["AI/ML Engineer"]}},
        headers=auth_headers,
    )
    assert first.status_code == 200
    assert "AI/ML Engineer" in first.json()["interpreted_career_goals"]

    # Explicitly submits an empty career_goals list this time.
    second = client.post(
        "/api/recommendations",
        json={"student_profile": {"interests": ["Machine Learning"], "career_goals": []}},
        headers=auth_headers,
    )
    assert second.status_code == 200
    assert second.json()["interpreted_career_goals"] == []

    # And the clearing must have actually persisted, not just applied to
    # this one response — a bare {} call afterwards must not resurrect it.
    third = client.post("/api/recommendations", json={}, headers=auth_headers)
    assert third.status_code == 200
    assert third.json()["interpreted_career_goals"] == []


def test_branch_warning_present_when_branch_unset(client, auth_headers, db_session):
    # A fresh signup has no branch set, so the department filter never runs
    # — results blend every department's catalogue together. The student
    # must be told this explicitly rather than shown a confident single
    # recommendation from a department their real program might not offer.
    _seed_two_electives(db_session)
    response = client.post(
        "/api/recommendations",
        json={"student_profile": {"interests": ["Machine Learning"]}},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["branch_warning"] is not None


def test_no_branch_warning_once_branch_is_set(client, auth_headers, db_session):
    from app.database.connection import get_db
    from app.main import app
    from app.models.user import User

    _seed_two_electives(db_session)
    db = next(app.dependency_overrides[get_db]())
    user = db.query(User).filter(User.email == "test.student@thapar.edu").first()
    user.profile.branch = "Computer Science and Engineering"
    db.commit()

    response = client.post(
        "/api/recommendations",
        json={"student_profile": {"interests": ["Machine Learning"]}},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["branch_warning"] is None
