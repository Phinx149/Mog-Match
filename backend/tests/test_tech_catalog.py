from app.seed import DEMO_PROFILE, SEED_PROFILES
from app.services.tech_catalog import ALIASES, ALL_TECHNOLOGIES, TECH_CATALOG, _key, normalize_technology


def test_normalizes_case_spacing_and_aliases():
    assert normalize_technology("react") == "React"
    assert normalize_technology("NODEJS") == "Node.js"
    assert normalize_technology("node js") == "Node.js"
    assert normalize_technology("k8s") == "Kubernetes"
    assert normalize_technology("postgres") == "PostgreSQL"
    assert normalize_technology("c#") == "C#"
    assert normalize_technology("c++") == "C++"
    assert normalize_technology("C") == "C"


def test_rejects_unknown():
    assert normalize_technology("NotARealFramework") is None
    assert normalize_technology("") is None


def test_catalog_has_no_conflicting_entries():
    seen: dict[str, str] = {}
    for tech in (t for techs in TECH_CATALOG.values() for t in techs):
        assert seen.setdefault(_key(tech), tech) == tech, f"{tech!r} collides with {seen[_key(tech)]!r}"
    for alias, canonical in ALIASES.items():
        assert canonical in ALL_TECHNOLOGIES, f"alias {alias!r} points to unknown {canonical!r}"
        assert _key(alias) not in seen or seen[_key(alias)] == canonical, f"alias {alias!r} shadows a catalog entry"


def test_all_seed_technologies_are_known():
    for profile in [DEMO_PROFILE, *SEED_PROFILES]:
        for skill in profile["skills"]:
            assert normalize_technology(skill) == skill, f"{profile['username']} skill: {skill!r}"
        for project in profile["projects"]:
            for tech in project["technologies"]:
                assert normalize_technology(tech) == tech, f"{profile['username']}: {tech!r}"


def test_all_seed_looking_for_values_are_allowed():
    from app.services.profile_service import LOOKING_FOR_OPTIONS

    for profile in [DEMO_PROFILE, *SEED_PROFILES]:
        for item in profile["looking_for"]:
            assert item in LOOKING_FOR_OPTIONS, f"{profile['username']} looking_for: {item!r}"


def test_patch_normalizes_project_technologies(client):
    response = client.patch(
        "/api/profiles/me",
        json={"projects": [{"title": "App", "description": "A web app.", "technologies": ["react", "ts", "TypeScript", "k8s"]}]},
    )
    assert response.status_code == 200, response.get_json()
    assert response.get_json()["projects"][0]["technologies"] == ["React", "TypeScript", "Kubernetes"]


def test_patch_rejects_unknown_project_technology(client):
    response = client.patch(
        "/api/profiles/me",
        json={"projects": [{"title": "App", "description": "A web app.", "technologies": ["React", "Blorptastic"]}]},
    )
    assert response.status_code == 400
    message = response.get_json()["error"]["fields"]["projects[0].technologies"]
    assert "Blorptastic" in message


def test_patch_normalizes_skills(client):
    response = client.patch("/api/profiles/me", json={"skills": ["python", "k8s", "ML", "fullstack", "Python"]})
    assert response.status_code == 200, response.get_json()
    assert response.get_json()["skills"] == ["Python", "Kubernetes", "Machine Learning", "Full-stack"]


def test_patch_rejects_unknown_skill(client):
    response = client.patch("/api/profiles/me", json={"skills": ["React", "Vibes"]})
    assert response.status_code == 400
    assert response.get_json()["error"]["fields"]["skills"].startswith("Unknown skill: Vibes")


def test_specialty_filter_still_works_after_normalized_save(client):
    client.patch("/api/profiles/me", json={"skills": ["frontend"]})
    assert client.get("/api/profiles/me").get_json()["skills"] == ["Frontend"]
