"""Repeatable demo data. Run with `flask seed` (add `--reset` to restore seeded profiles)."""

import click
from flask import Flask, current_app

from .extensions import db
from .models import Profile, ProfileLink, Project, User

SEED_EMAIL_DOMAIN = "seed.mogmatch.dev"

DEMO_PROFILE = {
    "full_name": "Jordan Avery",
    "username": "jordan-dev",
    "location": "Austin, TX",
    "education": "B.S. Computer Science, UT Austin (2027)",
    "bio": "CS student and hackathon regular. I like shipping full-stack prototypes fast and "
    "I'm looking for teammates who are stronger on ML or design than I am.",
    "favorite_ide": "VS Code",
    "favorite_ai_agents": ["Claude Code", "GitHub Copilot"],
    "skills": ["Full-stack", "TypeScript", "React", "Python", "Flask", "PostgreSQL"],
    "interests": ["Hackathons", "Startups", "Developer Tools"],
    "experience_level": "Student",
    "looking_for": ["Hackathon team", "Side project"],
    "links": [
        ("GitHub", "https://github.com/jordan-dev"),
        ("Portfolio", "https://example.com/jordan-dev"),
    ],
    "projects": [
        {
            "title": "StudyBuddy",
            "description": "Flashcard app that turns lecture notes into spaced-repetition decks.",
            "project_url": "https://example.com/jordan-dev/studybuddy",
            "technologies": ["React", "Flask", "SQLite"],
        }
    ],
}

SEED_PROFILES = [
    {
        "full_name": "Maya Chen",
        "username": "mayacodes",
        "location": "San Francisco, CA",
        "education": "B.A. Cognitive Science, UC Berkeley",
        "bio": "Frontend engineer obsessed with accessible, buttery-smooth interfaces. "
        "Design systems by day, creative coding by night.",
        "favorite_ide": "VS Code",
        "favorite_ai_agents": ["Cursor", "Claude Code"],
        "skills": ["Frontend", "TypeScript", "React", "Next.js", "Tailwind CSS", "Figma"],
        "interests": ["Design Systems", "Accessibility", "Generative Art"],
        "experience_level": "Senior",
        "looking_for": ["Side project", "Mentee"],
        "links": [("GitHub", "https://github.com/mayacodes"), ("Portfolio", "https://example.com/maya")],
        "projects": [
            {
                "title": "Prism UI",
                "description": "Open-source React component library with WCAG AA defaults.",
                "project_url": "https://example.com/maya/prism",
                "technologies": ["React", "TypeScript", "Storybook"],
            },
            {
                "title": "Flowfield",
                "description": "Generative art playground running in the browser with WebGL shaders.",
                "project_url": None,
                "technologies": ["WebGL", "GLSL", "TypeScript"],
            },
        ],
    },
    {
        "full_name": "Diego Ramirez",
        "username": "diego-rs",
        "location": "Mexico City, MX",
        "education": "B.Eng. Software Engineering, UNAM",
        "bio": "Backend and systems engineer. I write Rust services that handle millions of "
        "requests and I like making slow things fast.",
        "favorite_ide": "Neovim",
        "favorite_ai_agents": ["Claude Code"],
        "skills": ["Backend", "Rust", "Go", "PostgreSQL", "gRPC", "Kubernetes"],
        "interests": ["Distributed Systems", "Open Source", "Performance"],
        "experience_level": "Senior",
        "looking_for": ["Side project", "Hackathon team", "Open source"],
        "links": [("GitHub", "https://github.com/diego-rs"), ("Blog", "https://example.com/diego/blog")],
        "projects": [
            {
                "title": "ferrocache",
                "description": "Redis-compatible in-memory cache written in Rust with async I/O.",
                "project_url": "https://example.com/diego/ferrocache",
                "technologies": ["Rust", "Tokio"],
            }
        ],
    },
    {
        "full_name": "Priya Natarajan",
        "username": "priya-ml",
        "location": "Bengaluru, IN",
        "education": "M.S. Machine Learning, IISc",
        "bio": "ML engineer working on retrieval and LLM evaluation. I want to pair with "
        "frontend folks to turn research demos into real products.",
        "favorite_ide": "PyCharm",
        "favorite_ai_agents": ["Claude Code", "Codex"],
        "skills": ["Machine Learning", "Python", "PyTorch", "LLMs", "FastAPI", "SQL"],
        "interests": ["AI", "Research", "Education"],
        "experience_level": "Mid-level",
        "looking_for": ["Hackathon team", "Side project"],
        "links": [("GitHub", "https://github.com/priya-ml"), ("LinkedIn", "https://www.linkedin.com/in/priya-ml")],
        "projects": [
            {
                "title": "EvalKit",
                "description": "Lightweight harness for comparing LLM outputs with rubric-based grading.",
                "project_url": "https://example.com/priya/evalkit",
                "technologies": ["Python", "LLMs", "Pandas"],
            }
        ],
    },
    {
        "full_name": "Sam Okafor",
        "username": "samfullstack",
        "location": "Lagos, NG",
        "education": "Self-taught, freeCodeCamp",
        "bio": "Full-stack dev who ships MVPs for early-stage startups. Happy in any layer "
        "of the stack as long as there are users waiting.",
        "favorite_ide": "WebStorm",
        "favorite_ai_agents": ["GitHub Copilot", "Claude Code"],
        "skills": ["Full-stack", "JavaScript", "Node.js", "React", "MongoDB", "AWS"],
        "interests": ["Startups", "Fintech", "Mentoring"],
        "experience_level": "Mid-level",
        "looking_for": ["Side project", "Mentor", "Cofounder"],
        "links": [("GitHub", "https://github.com/samfullstack"), ("Website", "https://example.com/sam")],
        "projects": [
            {
                "title": "PayLink",
                "description": "Shareable payment links for small vendors with WhatsApp notifications.",
                "project_url": None,
                "technologies": ["Node.js", "React", "MongoDB"],
            }
        ],
    },
    {
        "full_name": "Lena Fischer",
        "username": "lena-gamedev",
        "location": "Berlin, DE",
        "education": "B.Sc. Games Engineering, TU Munich",
        "bio": "Gameplay programmer and jam addict (30+ game jams). I love tight game feel, "
        "procedural generation and weird physics.",
        "favorite_ide": "JetBrains Rider",
        "favorite_ai_agents": ["GitHub Copilot"],
        "skills": ["Game Dev", "C#", "Unity", "C++", "Godot", "Blender"],
        "interests": ["Gaming", "Procedural Generation", "Pixel Art"],
        "experience_level": "Mid-level",
        "looking_for": ["Hackathon team", "Just vibes"],
        "links": [("itch.io", "https://example.com/lena/itch"), ("GitHub", "https://github.com/lena-gamedev")],
        "projects": [
            {
                "title": "Tidal Drift",
                "description": "Physics-based sailing roguelike made in 48 hours, top 10 at a global jam.",
                "project_url": "https://example.com/lena/tidal-drift",
                "technologies": ["Unity", "C#"],
            },
            {
                "title": "Dungeon Weaver",
                "description": "Wave-function-collapse dungeon generator for Godot.",
                "project_url": None,
                "technologies": ["Godot", "GDScript"],
            },
        ],
    },
    {
        "full_name": "Marcus Johnson",
        "username": "m-sec",
        "location": "Washington, DC",
        "education": "B.S. Cybersecurity, University of Maryland",
        "bio": "Security engineer and CTF player. I break things responsibly and help teams "
        "build them back stronger.",
        "favorite_ide": "Vim",
        "favorite_ai_agents": ["Claude Code"],
        "skills": ["Security", "Python", "C", "Linux", "Reverse Engineering", "Rust"],
        "interests": ["CTFs", "Privacy", "Open Source"],
        "experience_level": "Senior",
        "looking_for": ["Hackathon team", "Mentee"],
        "links": [("GitHub", "https://github.com/m-sec"), ("Blog", "https://example.com/marcus/writeups")],
        "projects": [
            {
                "title": "sniffle",
                "description": "Network traffic anomaly detector for home labs.",
                "project_url": "https://example.com/marcus/sniffle",
                "technologies": ["Rust", "eBPF"],
            }
        ],
    },
    {
        "full_name": "Aisha Rahman",
        "username": "aisha-data",
        "location": "Toronto, CA",
        "education": "B.Math Statistics, University of Waterloo",
        "bio": "Data engineer building pipelines that don't wake anyone up at 3am. "
        "Big fan of boring, reliable infrastructure.",
        "favorite_ide": "DataGrip",
        "favorite_ai_agents": ["Codex", "Claude Code"],
        "skills": ["Data Engineering", "Python", "SQL", "Apache Spark", "Airflow", "dbt"],
        "interests": ["Climate Tech", "Data Visualization", "Open Data"],
        "experience_level": "Mid-level",
        "looking_for": ["Side project", "Cofounder"],
        "links": [("GitHub", "https://github.com/aisha-data"), ("LinkedIn", "https://www.linkedin.com/in/aisha-data")],
        "projects": [
            {
                "title": "CarbonLake",
                "description": "Open pipeline that aggregates public emissions data into a queryable warehouse.",
                "project_url": "https://example.com/aisha/carbonlake",
                "technologies": ["Airflow", "dbt", "DuckDB"],
            }
        ],
    },
    {
        "full_name": "Kenji Watanabe",
        "username": "kenji-mobile",
        "location": "Tokyo, JP",
        "education": "B.Eng. Information Science, Keio University",
        "bio": "Mobile developer who cares about 60fps and offline-first. Shipped apps "
        "with over a million downloads.",
        "favorite_ide": "Android Studio",
        "favorite_ai_agents": ["GitHub Copilot", "Gemini Code Assist"],
        "skills": ["Mobile", "Kotlin", "Swift", "Flutter", "Firebase", "Frontend"],
        "interests": ["Travel", "Photography", "Health Tech"],
        "experience_level": "Senior",
        "looking_for": ["Side project", "Just vibes"],
        "links": [("GitHub", "https://github.com/kenji-mobile")],
        "projects": [
            {
                "title": "Trailmark",
                "description": "Offline hiking map app with community-reported trail conditions.",
                "project_url": "https://example.com/kenji/trailmark",
                "technologies": ["Flutter", "Firebase"],
            }
        ],
    },
    {
        "full_name": "Olivia Brooks",
        "username": "liv-devops",
        "location": "Seattle, WA",
        "education": "B.S. Information Systems, University of Washington",
        "bio": "Platform engineer. Terraform, CI/CD and making deploys boring. I can get your "
        "hackathon project live in 10 minutes.",
        "favorite_ide": "VS Code",
        "favorite_ai_agents": ["Claude Code", "Amazon Q Developer"],
        "skills": ["DevOps", "Terraform", "Docker", "Go", "AWS", "Backend"],
        "interests": ["Cloud", "Automation", "Board Games"],
        "experience_level": "Lead",
        "looking_for": ["Mentee", "Hackathon team", "Open source"],
        "links": [("GitHub", "https://github.com/liv-devops"), ("Website", "https://example.com/olivia")],
        "projects": [
            {
                "title": "shipit-templates",
                "description": "One-command deploy templates for common hackathon stacks.",
                "project_url": "https://example.com/olivia/shipit",
                "technologies": ["Terraform", "GitHub Actions"],
            }
        ],
    },
    {
        "full_name": "Noah Kim",
        "username": "noah-learns",
        "location": "Seoul, KR",
        "education": "High school senior, self-taught",
        "bio": "Just started coding last year and I'm hooked. Learning Rust and web dev, "
        "looking for a patient mentor and my first hackathon team.",
        "favorite_ide": "Zed",
        "favorite_ai_agents": ["Claude Code"],
        "skills": ["Frontend", "HTML", "CSS", "JavaScript", "Rust"],
        "interests": ["Gaming", "AI", "Music"],
        "experience_level": "Student",
        "looking_for": ["Mentor", "Hackathon team"],
        "links": [("GitHub", "https://github.com/noah-learns")],
        "projects": [
            {
                "title": "Lo-fi Timer",
                "description": "Pomodoro timer with procedurally generated lo-fi beats.",
                "project_url": None,
                "technologies": ["JavaScript", "Web Audio API"],
            }
        ],
    },
]


def _build_profile(user: User, data: dict) -> Profile:
    fields = {k: v for k, v in data.items() if k not in ("links", "projects")}
    profile = Profile(user=user, **fields)
    profile.links = [
        ProfileLink(label=label, url=url, position=index)
        for index, (label, url) in enumerate(data["links"])
    ]
    profile.projects = [
        Project(position=index, **project) for index, project in enumerate(data["projects"])
    ]
    return profile


def _seed_one(email: str, data: dict, reset: bool) -> str:
    """Create one seeded user+profile. Returns 'created', 'reset' or 'skipped'."""
    user = User.query.filter_by(email=email).one_or_none()
    existing = Profile.query.filter_by(username=data["username"]).one_or_none()
    outcome = "created"

    if reset:
        if user is not None:
            db.session.delete(user)  # cascades to profile, links and projects
            outcome = "reset"
        if existing is not None and existing.user is not user:
            db.session.delete(existing.user)  # someone else holds the seeded username
        db.session.flush()
        user = None
    elif (user is not None and user.profile is not None) or existing is not None:
        return "skipped"  # never overwrite data someone may have edited

    user = user or User(email=email)
    db.session.add(user)
    db.session.add(_build_profile(user, data))
    return outcome


def seed_database(reset: bool = False) -> dict[str, int]:
    counts = {"created": 0, "reset": 0, "skipped": 0}
    demo_email = current_app.config["DEMO_USER_EMAIL"]
    counts[_seed_one(demo_email, DEMO_PROFILE, reset)] += 1
    for data in SEED_PROFILES:
        email = f"{data['username']}@{SEED_EMAIL_DOMAIN}"
        counts[_seed_one(email, data, reset)] += 1
    db.session.commit()
    return counts


def register_commands(app: Flask) -> None:
    @app.cli.command("seed")
    @click.option("--reset", is_flag=True, help="Restore seeded profiles to their defaults.")
    def seed_command(reset: bool) -> None:
        """Insert the demo user and sample developer profiles."""
        counts = seed_database(reset=reset)
        click.echo(
            f"Seed complete: {counts['created']} created, {counts['reset']} reset, "
            f"{counts['skipped']} skipped (already present)."
        )
