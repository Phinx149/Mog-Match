"""Deterministic Team Mog Score, 0–1000. A team benefits from overlap AND different strengths."""

from .mog_score import compute_mog_score
from .tech_catalog import TECH_CATALOG, normalize_technology

EXPERIENCE = ["Student", "Junior", "Mid-level", "Senior", "Lead"]
SPECIALTIES = {value.lower() for value in TECH_CATALOG["specialties"]}


def _values(items):
    result = {}
    for value in items:
        clean = value.strip()
        if clean:
            canonical = normalize_technology(clean) or clean
            result.setdefault(canonical.lower(), canonical)
    return result


def compute_team_mog(first, second):
    profiles = sorted([first, second], key=lambda p: str(p["id"]))
    a, b = profiles
    scores = [compute_mog_score(profile)["score"] for profile in profiles]
    skills_a, skills_b = _values(a["skills"]), _values(b["skills"])
    shared = sorted(set(skills_a) & set(skills_b))
    union = set(skills_a) | set(skills_b)
    specialties = sorted(union & SPECIALTIES)
    display = {**skills_a, **skills_b}
    strength = round(sum(scores) / 2 * 4)  # individual scores are 0–100, team strength is 0–400
    coverage = min(len(specialties), 5) * 50
    distance = 1 - len(shared) / len(union) if union else 0
    complementarity = round(200 * max(0, 1 - abs(distance - 0.65) / 0.65)) if skills_a and skills_b else 0
    goals_a = {value.strip().lower() for value in a["looking_for"] if value.strip()}
    goals_b = {value.strip().lower() for value in b["looking_for"] if value.strip()}
    mentorship = ("mentor" in goals_a and "mentee" in goals_b) or ("mentee" in goals_a and "mentor" in goals_b)
    aligned = bool(goals_a & goals_b) or mentorship
    ground = (60 if shared else 0) + (40 if aligned else 0)
    experience_a, experience_b = a.get("experience_level"), b.get("experience_level")
    if experience_a in EXPERIENCE and experience_b in EXPERIENCE:
        gap = abs(EXPERIENCE.index(experience_a) - EXPERIENCE.index(experience_b))
        balance = 50 if mentorship else [50, 50, 35, 20, 0][gap]
        experience_reason = ("Your Mentor/Mentee goals support a learning partnership." if mentorship else
                             f"{experience_a} + {experience_b}: " + (
                                 "closely matched experience." if gap <= 1 else "room to bridge an experience gap."))
    else:
        balance = 0
        experience_reason = "Both profiles need an experience level to earn balance points."
    rows = [
        {"key": "strength", "label": "Combined strength", "points": strength, "max": 400,
         "reason": f"Individual Mog Scores of {scores[0]} and {scores[1]}; their average contributes up to 400 points."},
        {"key": "coverage", "label": "Specialty coverage", "points": coverage, "max": 250,
         "reason": (f"Together you cover {', '.join(display[key] for key in specialties)}. Each distinct specialty earns 50 points, up to five."
                    if specialties else "List specialty skills, such as Frontend or Backend, to show your team's coverage.")},
        {"key": "complementarity", "label": "Complementary skills", "points": complementarity, "max": 200,
         "reason": (f"Your combined stack has {len(union)} distinct skills and {len(shared)} shared. Different strengths with some overlap score best."
                    if skills_a and skills_b else "Both profiles need skills before complementary strengths can be measured.")},
        {"key": "ground", "label": "Shared ground", "points": ground, "max": 100,
         "reason": ((f"Shared skills: {', '.join(display[key] for key in shared[:5])}" if shared else "No shared skills listed yet")
                    + (". Your collaboration goals also align." if aligned else ". Your collaboration goals don't overlap yet."))},
        {"key": "balance", "label": "Experience balance", "points": balance, "max": 50, "reason": experience_reason},
    ]
    score = sum(row["points"] for row in rows)
    tier = next(label for floor, label in [(800, "Inferno alliance"), (600, "Power duo"), (400, "Rising duo"), (0, "Fresh spark")] if score >= floor)
    return {"score": score, "max_score": 1000, "tier": tier, "breakdown": rows,
            "members": [{"id": profile["id"], "full_name": profile["full_name"], "username": profile["username"],
                         "avatar_url": profile.get("avatar_url"), "mog_score": member_score}
                        for profile, member_score in zip(profiles, scores)]}
