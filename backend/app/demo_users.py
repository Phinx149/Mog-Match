"""Quick-login demo accounts for local testing, spread across every Mog tier.

Created by `flask seed-test-users` (not by `flask seed`, so tests and teammates' databases don't
see them). Every account's password is DEMO_PASSWORD. Each profile is shaped to land in a tier:
Mog points come from esoteric languages used in projects, number of skills, links, projects,
description and bio length, profile completeness and experience (see docs/MOG_SCORE.md).
`tests/test_demo_users.py` checks every account really lands in its intended tier.
"""

DEMO_PASSWORD = "123"


def _avatar(username: str) -> str:
    return f"https://api.dicebear.com/9.x/thumbs/svg?seed={username}"


def _long(text: str, length: int) -> str:
    """Repeat a sentence up to `length` characters (Mog points scale with bio/description length)."""
    out = text
    while len(out) < length:
        out += " " + text
    return out[:length].rstrip()


def _project(title: str, technologies: list[str], about: str, length: int | None = 120, url: bool = True) -> dict:
    """length=None keeps `about` exactly as written (used by the hand-written second batch)."""
    slug = title.lower().replace(" ", "-")
    return {
        "title": title,
        "description": about if length is None else _long(about, length),
        "project_url": f"https://example.com/{slug}" if url else None,
        "technologies": technologies,
    }


def _links(username: str, count: int) -> list[tuple[str, str]]:
    options = [
        ("GitHub", f"https://github.com/{username}"),
        ("Portfolio", f"https://example.com/{username}"),
        ("Blog", f"https://example.com/{username}/blog"),
    ]
    return options[:count]


# tier -> accounts, highest Mog first. "tier" is only used by the test and the README table.
DEMO_USERS: list[dict] = [
    # ---------- 👑 Gigamogger (85–100): rare languages shipped in real projects, everything filled in
    {
        "tier": "Gigamogger", "username": "gigachad", "full_name": "Giga Chad",
        "avatar_url": _avatar("gigachad"), "location": "Zurich, CH", "education": "PhD Programming Languages, ETH Zurich",
        "bio": _long("Compiler engineer who writes Haskell for fun and COBOL for money. Maintains three type checkers and a mainframe emulator.", 320),
        "favorite_ide": "Neovim", "favorite_ai_agents": ["Claude Code", "Cursor"],
        "skills": ["Haskell", "COBOL", "Zig", "OCaml", "Prolog", "Rust", "Systems Programming", "Backend", "C", "Assembly"],
        "interests": ["Compilers", "Type Theory", "Retro Computing"], "experience_level": "Lead",
        "looking_for": ["Open source", "Mentee"], "links": _links("gigachad", 3),
        "projects": [
            _project("Monad Mainframe", ["Haskell", "COBOL"], "A COBOL-to-Haskell transpiler that keeps 1970s banking code running on modern hardware.", 420),
            _project("ZigOS", ["Zig", "Assembly"], "A tiny hobby operating system kernel written in Zig with hand-tuned assembly boot code.", 420),
            _project("Prolog Planner", ["Prolog", "OCaml"], "A logic-programming scheduler that plans hackathon teams from skill constraints.", 420),
        ],
    },
    {
        "tier": "Gigamogger", "username": "lispwizard", "full_name": "Lisa Lambda",
        "avatar_url": _avatar("lispwizard"), "location": "Boston, MA", "education": "B.S. Computer Science, MIT",
        "bio": _long("Parenthesis enthusiast. Builds interpreters, live-coding music tools and the occasional Fortran physics sim.", 310),
        "favorite_ide": "Emacs", "favorite_ai_agents": ["Claude Code"],
        "skills": ["Lisp", "Racket", "Fortran", "Clojure", "Scheme", "Elixir", "Python", "Backend", "Machine Learning", "Julia"],
        "interests": ["Programming Languages", "Music Tech", "Physics"], "experience_level": "Senior",
        "looking_for": ["Side project", "Open source"], "links": _links("lispwizard", 3),
        "projects": [
            _project("Paren Synth", ["Racket", "Lisp"], "A live-coding synthesizer where every sound is an S-expression you can edit while it plays.", 410),
            _project("Fortran Fluids", ["Fortran", "Julia"], "A fluid dynamics simulator that compares a 1977 Fortran solver with a modern Julia port.", 410),
            _project("Elixir Echo", ["Elixir", "Clojure"], "A fault-tolerant chat relay that survives its own bugs, built to learn the BEAM.", 410),
        ],
    },
    {
        "tier": "Gigamogger", "username": "verilogvic", "full_name": "Victor Gates",
        "avatar_url": _avatar("verilogvic"), "location": "Austin, TX", "education": "M.S. Electrical Engineering, UT Austin",
        "bio": _long("Designs CPUs for fun on FPGAs. If it has a clock signal, I have opinions about it.", 300),
        "favorite_ide": "Vim", "favorite_ai_agents": ["Copilot"],
        "skills": ["Verilog", "VHDL", "Ada", "C", "Embedded", "Rust", "Assembly", "Robotics", "Python", "C++"],
        "interests": ["Hardware", "FPGAs", "Robotics"], "experience_level": "Lead",
        "looking_for": ["Hackathon team", "Mentee"], "links": _links("verilogvic", 3),
        "projects": [
            _project("RISC-Me", ["Verilog", "Assembly"], "A five-stage RISC-V CPU on a cheap FPGA board, with a tiny assembler to program it.", 400),
            _project("Ada Autopilot", ["Ada", "C"], "Safety-first drone autopilot firmware written in Ada with formally checked control loops.", 400),
            _project("VHDL Pong", ["VHDL"], "Pong rendered straight from logic gates to a VGA monitor. No CPU involved.", 400),
        ],
    },
    {
        "tier": "Gigamogger", "username": "rustacean", "full_name": "Rusty Crab",
        "avatar_url": _avatar("rustacean"), "location": "Berlin, DE", "education": "B.Sc. Informatics, TU Berlin",
        "bio": _long("Memory-safe and proud. Ships Rust and Zig in production and writes Elm on the frontend so nothing ever crashes.", 300),
        "favorite_ide": "RustRover", "favorite_ai_agents": ["Claude Code", "Copilot"],
        "skills": ["Rust", "Zig", "Elm", "Nim", "WebAssembly", "Systems Programming", "Backend", "Frontend", "Go", "TypeScript"],
        "interests": ["Performance", "WebAssembly", "Open Source"], "experience_level": "Senior",
        "looking_for": ["Open source", "Side project"], "links": _links("rustacean", 3),
        "projects": [
            _project("Ferris DB", ["Rust", "Zig"], "An embedded key-value store with a Rust core and Zig bindings, benchmarked against SQLite.", 400),
            _project("Elm Board", ["Elm", "WebAssembly"], "A collaborative whiteboard with an Elm UI and a WebAssembly drawing engine.", 400),
            _project("Nim Notes", ["Nim"], "A note-taking CLI that compiles to a 200 KB binary and starts in a millisecond.", 400),
        ],
    },
    {
        "tier": "Gigamogger", "username": "fsharpfiona", "full_name": "Fiona Sharp",
        "avatar_url": _avatar("fsharpfiona"), "location": "Dublin, IE", "education": "M.Sc. Data Science, Trinity College Dublin",
        "bio": _long("Functional data scientist. Uses F# and OCaml for models, Julia for numbers, and Erlang when things must never go down.", 300),
        "favorite_ide": "JetBrains Rider", "favorite_ai_agents": ["Claude Code"],
        "skills": ["F#", "OCaml", "Julia", "Erlang", "Data Science", "Machine Learning", "Python", "SQL", "R", "Haskell"],
        "interests": ["Functional Programming", "Statistics", "Finance"], "experience_level": "Senior",
        "looking_for": ["Cofounder", "Hackathon team"], "links": _links("fsharpfiona", 1),
        "projects": [
            _project("Typed Trader", ["F#", "OCaml"], "A backtesting engine for trading strategies where units and currencies are checked by the type system.", 400),
            _project("Julia Forecast", ["Julia", "R"], "Probabilistic weather forecasts for cyclists, with uncertainty bands that actually mean something.", 400),
            _project("Never Down", ["Erlang"], "A supervision-tree demo that keeps a chat server alive while you randomly kill its processes.", 400),
        ],
    },
    # ---------- 🔥 Senior Mogger (65–84): strong profiles, a few gaps
    {
        "tier": "Senior Mogger", "username": "seniorsam", "full_name": "Sam Senior",
        "avatar_url": _avatar("seniorsam"), "location": "Toronto, CA", "education": "B.Eng. Software, University of Waterloo",
        "bio": _long("Backend lead who loves boring, reliable systems. Go services, Postgres, and well-written runbooks.", 250),
        "favorite_ide": "GoLand", "favorite_ai_agents": ["Copilot"],
        "skills": ["Go", "Rust", "Backend", "PostgreSQL", "Kubernetes", "Docker", "Python", "Cloud"],
        "interests": ["Distributed Systems", "Reliability"], "experience_level": "Lead",
        "looking_for": ["Mentee"], "links": _links("seniorsam", 2),
        "projects": [
            _project("Queue Keeper", ["Go", "Rust"], "A job queue that survives restarts and tells you exactly why a job failed.", 300),
            _project("Pager Pal", ["Go"], "Turns noisy alerts into one calm summary message for whoever is on call.", 250),
        ],
    },
    {
        "tier": "Senior Mogger", "username": "elixirella", "full_name": "Ella Elixir",
        "avatar_url": _avatar("elixirella"), "location": "Lisbon, PT", "education": "B.Sc. Computer Engineering, IST Lisbon",
        "bio": _long("Real-time everything. Phoenix LiveView fan, building multiplayer apps without writing much JavaScript.", 240),
        "favorite_ide": "VS Code", "favorite_ai_agents": ["Cursor"],
        "skills": ["Elixir", "Phoenix", "Backend", "PostgreSQL", "JavaScript", "Full-stack", "Erlang"],
        "interests": ["Real-time Apps", "Multiplayer"], "experience_level": "Senior",
        "looking_for": ["Side project"], "links": _links("elixirella", 2),
        "projects": [
            _project("Live Quiz", ["Elixir", "Phoenix"], "A pub-quiz app where hundreds of phones answer at once and the scoreboard updates live.", 280),
            _project("Beam Chat", ["Erlang"], "A tiny chat server to learn OTP supervisors.", 150),
        ],
    },
    {
        "tier": "Senior Mogger", "username": "kotlinkai", "full_name": "Kai Kotlin",
        "avatar_url": _avatar("kotlinkai"), "location": "Seoul, KR", "education": "B.S. Computer Science, KAIST",
        "bio": _long("Android and Kotlin Multiplatform developer. Ships apps people actually keep installed.", 230),
        "favorite_ide": "Android Studio", "favorite_ai_agents": ["Gemini"],
        "skills": ["Kotlin", "Swift", "Mobile", "Dart", "Flutter", "Java", "Scala"],
        "interests": ["Mobile UX", "Fitness"], "experience_level": "Senior",
        "looking_for": ["Hackathon team"], "links": _links("kotlinkai", 2),
        "projects": [
            _project("Step Streak", ["Kotlin", "Swift"], "A cross-platform step counter that turns daily walks into a streak game with friends.", 260),
            _project("Dart Darts", ["Dart"], "A Flutter scorekeeper for pub darts nights.", 120),
        ],
    },
    {
        "tier": "Senior Mogger", "username": "clojureclara", "full_name": "Clara Clojure",
        "avatar_url": _avatar("clojureclara"), "location": "Stockholm, SE", "education": "M.Sc. Computer Science, KTH",
        "bio": _long("Data pipelines in Clojure, dashboards in ClojureScript. Immutable by default.", 200),
        "favorite_ide": "IntelliJ IDEA", "favorite_ai_agents": ["Claude Code"],
        "skills": ["Clojure", "Data Engineering", "Kafka", "SQL", "Python", "Scala"],
        "interests": ["Data", "Open Data"], "experience_level": "Mid-level",
        "looking_for": ["Open source"], "links": _links("clojureclara", 2),
        "projects": [
            _project("Transit Tap", ["Clojure", "Scala"], "Streams live bus positions into a map so you know if running is worth it.", 260),
            _project("Open Budget", ["Clojure"], "Turns city budget spreadsheets into something humans can read.", 200),
        ],
    },
    {
        "tier": "Senior Mogger", "username": "swiftsofia", "full_name": "Sofia Swift",
        "avatar_url": _avatar("swiftsofia"), "location": "Mexico City, MX", "education": "B.S. Computer Science, UNAM",
        "bio": _long("iOS developer and accessibility advocate. VoiceOver testing is part of every feature.", 220),
        "favorite_ide": "Xcode", "favorite_ai_agents": ["Copilot"],
        "skills": ["Swift", "Mobile", "Objective-C", "Ruby", "Frontend", "UI/UX Design"],
        "interests": ["Accessibility", "Design"], "experience_level": "Senior",
        "looking_for": ["Mentee", "Side project"], "links": _links("swiftsofia", 2),
        "projects": [
            _project("See For Me", ["Swift"], "Describes what's in front of the camera for blind and low-vision users.", 250),
            _project("Legacy Lift", ["Objective-C", "Swift"], "A step-by-step migration of an old Objective-C app to SwiftUI.", 200),
        ],
    },
    # ---------- 🧑‍💻 Mid Mogger (45–64): decent profiles, mainstream languages
    {
        "tier": "Mid Mogger", "username": "midmike", "full_name": "Mike Middle",
        "avatar_url": _avatar("midmike"), "location": "Chicago, IL", "education": "B.S. Information Systems, UIC",
        "bio": _long("Full-stack dev at an agency. React on the front, Node on the back, coffee in between.", 160),
        "favorite_ide": "VS Code", "favorite_ai_agents": ["Copilot"],
        "skills": ["JavaScript", "TypeScript", "React", "Node.js", "Full-stack", "Go"],
        "interests": ["Web Dev", "Coffee"], "experience_level": "Mid-level",
        "looking_for": ["Side project"], "links": _links("midmike", 1),
        "projects": [_project("Bean Tracker", ["TypeScript", "React", "Go"], "Logs every coffee you drink and judges you gently.", 150)],
    },
    {
        "tier": "Mid Mogger", "username": "pythonpat", "full_name": "Pat Python",
        "avatar_url": _avatar("pythonpat"), "location": "Manchester, UK", "education": "B.Sc. Mathematics, University of Manchester",
        "bio": _long("Data analyst turned Python developer. Automates spreadsheets so nobody has to.", 150),
        "favorite_ide": "PyCharm", "favorite_ai_agents": ["Claude Code"],
        "skills": ["Python", "SQL", "Data Science", "Pandas", "Ruby"],
        "interests": ["Automation", "Football"], "experience_level": "Junior",
        "looking_for": ["Mentor", "Side project"], "links": _links("pythonpat", 1),
        "projects": [_project("Sheet Slayer", ["Python", "Ruby"], "Merges fifty messy spreadsheets into one clean report every Monday.", 160)],
    },
    {
        "tier": "Mid Mogger", "username": "javajade", "full_name": "Jade Java",
        "avatar_url": None, "location": "Pune, IN", "education": "B.Tech. Computer Science, COEP",
        "bio": _long("Spring Boot developer building banking APIs. Learning Kotlin on weekends.", 140),
        "favorite_ide": "IntelliJ IDEA", "favorite_ai_agents": ["Copilot"],
        "skills": ["Java", "Spring Boot", "Kotlin", "Backend", "SQL"],
        "interests": ["Fintech", "Cricket"], "experience_level": "Mid-level",
        "looking_for": ["Hackathon team"], "links": _links("javajade", 1),
        "projects": [_project("Split Smart", ["Java", "Kotlin"], "Splits group bills fairly, even when someone only had a salad.", 140)],
    },
    {
        "tier": "Mid Mogger", "username": "phpphil", "full_name": "Phil PHP",
        "avatar_url": _avatar("phpphil"), "location": "Warsaw, PL", "education": None,
        "bio": _long("Laravel developer. Still believes PHP is fine, actually.", 120),
        "favorite_ide": "PhpStorm", "favorite_ai_agents": ["Cursor"],
        "skills": ["PHP", "Laravel", "JavaScript", "MySQL", "Backend", "Lua"],
        "interests": ["Web Dev", "Gaming"], "experience_level": "Mid-level",
        "looking_for": ["Just vibes"], "links": [],
        "projects": [_project("Guild Board", ["PHP", "Lua"], "A raid planner for my gaming guild with a Lua addon that syncs sign-ups.", 140)],
    },
    {
        "tier": "Mid Mogger", "username": "csharpchris", "full_name": "Chris Sharp",
        "avatar_url": _avatar("csharpchris"), "location": "Melbourne, AU", "education": "B.IT, RMIT",
        "bio": _long("Unity game developer making cozy games about plants.", 120),
        "favorite_ide": "Visual Studio", "favorite_ai_agents": ["Copilot"],
        "skills": ["C#", "Unity", "Game Dev", "C++"],
        "interests": ["Cozy Games", "Gardening"], "experience_level": "Junior",
        "looking_for": ["Hackathon team"], "links": _links("csharpchris", 1),
        "projects": [_project("Sprout", ["C#", "C++"], "A tiny game where you keep a houseplant alive by actually remembering to water it.", 130)],
    },
    # ---------- 🐣 Junior Mogger (25–44): starting out, a project or two
    {
        "tier": "Junior Mogger", "username": "juniorjo", "full_name": "Jo Junior",
        "avatar_url": None, "location": "Nairobi, KE", "education": "Bootcamp graduate",
        "bio": _long("Just finished a web bootcamp. Building my portfolio one project at a time.", 80),
        "favorite_ide": "VS Code", "favorite_ai_agents": ["ChatGPT"],
        "skills": ["HTML", "CSS", "JavaScript"],
        "interests": ["Web Dev", "Music"], "experience_level": "Junior",
        "looking_for": ["Mentor"], "links": [],
        "projects": [_project("My Portfolio", ["HTML", "CSS"], "My first website.", 40, url=False)],
    },
    {
        "tier": "Junior Mogger", "username": "studentstu", "full_name": "Stu Dent",
        "avatar_url": None, "location": "Lagos, NG", "education": "B.Sc. Computer Science (2nd year), UNILAG",
        "bio": _long("CS student learning Python and C.", 40),
        "favorite_ide": "VS Code", "favorite_ai_agents": [],
        "skills": ["Python", "C", "Java"],
        "interests": ["Learning", "Chess"], "experience_level": "Student",
        "looking_for": ["Mentor", "Hackathon team"], "links": [],
        "projects": [_project("Chess Clock", ["Python"], "A chess clock in the terminal.", 30, url=False)],
    },
    {
        "tier": "Junior Mogger", "username": "learnerlee", "full_name": "Lee Learner",
        "avatar_url": None, "location": None, "education": None,
        "bio": _long("Career changer from teaching. Learning React.", 45),
        "favorite_ide": "VS Code", "favorite_ai_agents": ["ChatGPT"],
        "skills": ["JavaScript", "React"],
        "interests": ["Education"], "experience_level": "Junior",
        "looking_for": ["Mentor"], "links": _links("learnerlee", 1),
        "projects": [_project("Flashcards", ["JavaScript"], "Flashcards for my old students.", 40, url=False)],
    },
    {
        "tier": "Junior Mogger", "username": "copypasta", "full_name": "Cody Pasta",
        "avatar_url": None, "location": "Phoenix, AZ", "education": None,
        "bio": "Stack Overflow is my IDE.",
        "favorite_ide": "Notepad++", "favorite_ai_agents": ["ChatGPT"],
        "skills": ["JavaScript", "jQuery"],
        "interests": ["Memes"], "experience_level": "Junior",
        "looking_for": ["Just vibes"], "links": [],
        "projects": [_project("Todo App", ["JavaScript"], "Another todo app.", 20, url=False)],
    },
    {
        "tier": "Junior Mogger", "username": "bootcampbea", "full_name": "Bea Camp",
        "avatar_url": _avatar("bootcampbea"), "location": "Madrid, ES", "education": "Ironhack Web Dev",
        "bio": _long("Week 8 of bootcamp. Send coffee.", 60),
        "favorite_ide": "VS Code", "favorite_ai_agents": [],
        "skills": ["HTML", "CSS"],
        "interests": ["Design", "Travel"], "experience_level": "Student",
        "looking_for": ["Mentor"], "links": [],
        "projects": [_project("Landing Page", ["HTML", "CSS"], "A landing page for my mum's bakery.", 50, url=False)],
    },
    # ---------- 🥚 Hello World (0–24): nearly empty profiles
    {
        "tier": "Hello World", "username": "newbie", "full_name": "Nova Newbie",
        "avatar_url": None, "location": None, "education": None,
        "bio": "Hello world!", "favorite_ide": "Notepad", "favorite_ai_agents": [],
        "skills": ["HTML"], "interests": [], "experience_level": "Student",
        "looking_for": ["Mentor"], "links": [], "projects": [],
    },
    {
        "tier": "Hello World", "username": "lurker", "full_name": "Larry Lurker",
        "avatar_url": None, "location": None, "education": None,
        "bio": "Just looking.", "favorite_ide": "VS Code", "favorite_ai_agents": [],
        "skills": [], "interests": [], "experience_level": None,
        "looking_for": [], "links": [], "projects": [],
    },
    {
        "tier": "Hello World", "username": "printhello", "full_name": "Priya Print",
        "avatar_url": None, "location": "Delhi, IN", "education": None,
        "bio": "print('hello')", "favorite_ide": "IDLE", "favorite_ai_agents": [],
        "skills": ["Python"], "interests": ["Learning"], "experience_level": "Student",
        "looking_for": [], "links": [], "projects": [],
    },
    {
        "tier": "Hello World", "username": "ghostdev", "full_name": "Ghost Dev",
        "avatar_url": None, "location": None, "education": None,
        "bio": "...", "favorite_ide": "Vim", "favorite_ai_agents": [],
        "skills": [], "interests": [], "experience_level": None,
        "looking_for": ["Just vibes"], "links": [], "projects": [],
    },
    {
        "tier": "Hello World", "username": "firststep", "full_name": "Finn First",
        "avatar_url": None, "location": "Oslo, NO", "education": None,
        "bio": "Day one of coding.", "favorite_ide": "VS Code", "favorite_ai_agents": ["ChatGPT"],
        "skills": ["HTML", "CSS"], "interests": [], "experience_level": "Student",
        "looking_for": ["Mentor"], "links": [], "projects": [],
    },
]


def _theme(background: str, effect: str | None = None, **options) -> dict:
    """A profile theme: a dark card background plus an optional animated effect and its settings."""
    theme: dict = {"background": background}
    if effect:
        theme["effect"] = effect
    if options:
        theme["effect_options"] = options
    return theme


# username -> a unique look for every test account (background colors never repeat).
# Effects and their options: THEME_EFFECTS / EFFECT_OPTION_RANGES in app/services/profile_service.py.
DEMO_THEMES: dict[str, dict] = {
    # 👑 Gigamogger
    "gigachad": _theme("#1a0b2e", "matrix", rain_color="#b388ff", rain_symbols="katakana", glow=True, brightness=60),
    "verilogvic": _theme("#001a0f", "matrix", rain_color="#22ff66", rain_symbols="binary", speed=7),
    "lispwizard": _theme("#0f1a2e", "emoji", emojis=["🧙", "🔮", "✨", "📜"], emoji_path="wave", emoji_count=18),
    "rustacean": _theme("#2a0f05", "emoji", emojis=["🦀", "⚙️", "🔧"], emoji_path="bounce", emoji_spin=-3),
    "fsharpfiona": _theme("#04201c", "market", chart_mood="bull", chart_palette="neon", chart_ticker="FSHARP", chart_volatility=4),
    # 🔥 Senior Mogger
    "elixirella": _theme("#1e0526", "emoji", emojis=["🧪", "💜", "⚗️"], emoji_path="wave", emoji_angle=270),
    "kotlinkai": _theme("#0b1530", "dvd", count=3, color_change=True, speed=5),
    "seniorsam": _theme("#101418", "slogans", slogans=["SHIP IT", "NO FRIDAY DEPLOYS", "IT WORKS ON PROD"],
                        slogan_color="#38bdf8", slogan_style="outline", slogan_tilt=-12),
    "clojureclara": _theme("#06231a", "snow", snow_kind="crystals", snow_count=60, snow_wind=-2),
    "swiftsofia": _theme("#2b0d0d", "emoji", emojis=["🐦", "📱", "♿"], emoji_path="bounce", emoji_count=10),
    # 🧑‍💻 Mid Mogger
    "midmike": _theme("#1c1208", "emoji", emojis=["☕", "🍩"], emoji_path="straight", emoji_angle=90, emoji_count=12),
    "pythonpat": _theme("#0a1a24", "matrix", rain_color="#ffd43b", rain_symbols="code", brightness=35),
    "javajade": _theme("#1f0f00", "slogans", slogans=["WRITE ONCE", "RUN ANYWHERE", "SPRING BOOT GANG"],
                       slogan_color="#f89820", slogan_style="solid", slogan_tilt=6),
    "phpphil": _theme("#120a24", "dvd", count=2, color_change=False, color="#8892bf"),
    "csharpchris": _theme("#0a2010", "emoji", emojis=["🌱", "🪴", "🌿"], emoji_path="wave", emoji_spin=0),
    # 🐣 Junior Mogger
    "juniorjo": _theme("#11111f", "snow", snow_kind="dots", snow_count=120, snow_wind=3),
    "studentstu": _theme("#1a1410", "emoji", emojis=["📚", "♟️", "☕"], emoji_count=8, speed=2),
    "bootcampbea": _theme("#200a18", "money", money_kind="bills", money_count=15, money_wind=2),
    "learnerlee": _theme("#0e1a12", "slogans", slogans=["STILL LEARNING", "HELLO REACT", "CTRL+Z"],
                         slogan_color="#a3e635", slogan_style="mixed", slogan_tilt=-20),
    "copypasta": _theme("#1a1a1a", "matrix", rain_symbols="chaos", rain_rainbow=True, speed=9),
    # 🥚 Hello World
    "firststep": _theme("#0d1b2a", "snow", snow_kind="mixed", snow_count=40, snow_wind=-5),
    "newbie": _theme("#141008", "emoji", emojis=["🥚", "🐣"], emoji_count=6, speed=1),
    "printhello": _theme("#0a0f1f", "matrix", rain_color="#60a5fa", rain_symbols="binary", brightness=25, speed=2),
    "lurker": _theme("#0c0c0c", "dvd", count=1, color_change=False, color="#888888", speed=2),
    "ghostdev": _theme("#050505", "emoji", emojis=["👻"], emoji_count=5, emoji_path="wave", brightness=20),
    # user1 / user2 (TEST_USERS in seed.py)
    "user1": _theme("#1b1035", "market", chart_mood="choppy", chart_palette="classic", chart_ticker="USER1"),
    "user2": _theme("#052e2b", "money", money_kind="coins", money_count=40, money_weight=8),
}


# ---------------------------------------------------------------------------------------------
# Second batch: 25 more accounts with hand-written stories (no repeated filler), 5 per tier.
# ---------------------------------------------------------------------------------------------
def _p(title: str, technologies: list[str], about: str, url: bool = True) -> dict:
    return _project(title, technologies, about, length=None, url=url)


DEMO_USERS += [
    # ---------- 👑 Gigamogger
    {
        "tier": "Gigamogger", "username": "assemblyamy", "full_name": "Amy Register",
        "avatar_url": _avatar("assemblyamy"), "location": "Houston, TX", "education": "B.S. Aerospace Engineering, Rice University",
        "bio": "Spent twenty years writing flight software where a single bit flip could end a mission. Now retired from the space program "
               "and restoring the guidance code of old satellites for fun. I still count cycles by hand, and I still think 4 KB of RAM is plenty "
               "if you respect it.",
        "favorite_ide": "Vim", "favorite_ai_agents": ["Claude Code"],
        "skills": ["Assembly", "Fortran", "Ada", "C", "Embedded", "Systems Programming", "Python", "MATLAB", "Robotics", "Pascal"],
        "interests": ["Space", "Retro Computing", "Electronics"], "experience_level": "Lead",
        "looking_for": ["Mentee", "Open source"], "links": _links("assemblyamy", 3),
        "projects": [
            _p("Apollo Replay", ["Assembly", "Fortran"], "A cycle-accurate emulator of a 1960s guidance computer that runs the original landing program. "
               "It replays the famous 1202 alarms in real time and explains, line by line, why the computer kept going instead of crashing. "
               "Used by two museums for their interactive exhibits."),
            _p("SafeLoop", ["Ada", "C"], "A small control-loop library for hobby rockets, written in Ada with every timing guarantee written down and checked. "
               "It refuses to compile if a loop could overrun its deadline. Includes a C wrapper so Arduino projects can use it too."),
            _p("Pascal Pilot", ["Pascal"], "A flight-simulator autopilot written in Turbo Pascal, because I wanted to prove that 1990s tools can still "
               "fly a modern plane. Talks to the simulator over a serial cable and holds altitude to within ten feet."),
        ],
    },
    {
        "tier": "Gigamogger", "username": "prologpete", "full_name": "Pete Horn",
        "avatar_url": _avatar("prologpete"), "location": "Edinburgh, UK", "education": "PhD Artificial Intelligence, University of Edinburgh",
        "bio": "Old-school AI researcher. Before neural networks were cool, I taught computers to reason with logic, and I still think the best "
               "explanation is one a program can prove. These days I mix symbolic reasoning with language models so the answers come with receipts.",
        "favorite_ide": "Emacs", "favorite_ai_agents": ["Claude Code", "Cursor"],
        "skills": ["Prolog", "Lisp", "Haskell", "Python", "AI", "Machine Learning", "Scheme", "Racket", "Backend", "Erlang"],
        "interests": ["Logic", "AI Safety", "Board Games"], "experience_level": "Lead",
        "looking_for": ["Cofounder", "Mentee"], "links": _links("prologpete", 3),
        "projects": [
            _p("Proof Buddy", ["Prolog", "Python"], "A homework helper that checks logic proofs step by step and tells students exactly which rule they broke. "
               "The language model writes friendly hints; the Prolog engine decides whether the proof is actually right, so it can't be sweet-talked."),
            _p("Lisp Machine Lite", ["Lisp", "Scheme"], "A tiny Lisp interpreter that runs in the browser, with a time-travel debugger that lets you step "
               "backwards through any evaluation. Built to teach recursion to first-year students who think it's magic."),
            _p("Rulebook", ["Haskell", "Erlang"], "Turns the rules of a board game into a checker that spots impossible moves and loopholes. "
               "It found two infinite-combo bugs in a published card game before the expansion shipped."),
        ],
    },
    {
        "tier": "Gigamogger", "username": "soliditysara", "full_name": "Sara Ledger",
        "avatar_url": _avatar("soliditysara"), "location": "Singapore", "education": "B.Comp. Computer Science, NUS",
        "bio": "Smart-contract auditor. I read other people's code for a living and break it before attackers do. Found my first critical bug at "
               "nineteen and have been paranoid ever since. Outside work I teach security workshops and write very long threads about integer overflows.",
        "favorite_ide": "VS Code", "favorite_ai_agents": ["Claude Code"],
        "skills": ["Solidity", "Haskell", "Rust", "OCaml", "Blockchain", "Security", "TypeScript", "Go", "Reverse Engineering", "Python"],
        "interests": ["Security", "Cryptography", "Teaching"], "experience_level": "Senior",
        "looking_for": ["Hackathon team", "Open source"], "links": _links("soliditysara", 3),
        "projects": [
            _p("Overflow Hunter", ["Solidity", "Haskell"], "A static analyzer that reads Solidity contracts and flags arithmetic that can wrap around. "
               "The core is written in Haskell so the analysis itself can't have the bug it looks for. Caught issues in three audits last year."),
            _p("Vault Game", ["Solidity", "TypeScript"], "A capture-the-flag game made of deliberately broken contracts. Each level teaches one real attack "
               "that has cost someone money, with a write-up of the original incident after you solve it."),
            _p("Rusty Signer", ["Rust", "OCaml"], "A hardware-wallet companion app that explains, in plain words, what a transaction will actually do "
               "before you sign it. The parser is fuzzed for days with every malformed input we could think of."),
        ],
    },
    {
        "tier": "Gigamogger", "username": "shadershiro", "full_name": "Shiro Pixel",
        "avatar_url": _avatar("shadershiro"), "location": "Osaka, JP", "education": "B.A. Media Arts, Kyoto Seika University",
        "bio": "Graphics programmer and demoscener. I make real-time visuals for concerts and squeeze whole worlds into 4 KB executables for "
               "demo parties. My favourite bug turned into an art piece that toured three galleries, so I no longer fix bugs I find beautiful.",
        "favorite_ide": "Visual Studio", "favorite_ai_agents": ["Cursor"],
        "skills": ["GLSL", "HLSL", "WebAssembly", "C++", "Game Dev", "Rust", "Zig", "AR/VR", "TypeScript", "Lua"],
        "interests": ["Generative Art", "Music", "Demoscene"], "experience_level": "Senior",
        "looking_for": ["Side project", "Hackathon team"], "links": _links("shadershiro", 3),
        "projects": [
            _p("Neon Tide", ["GLSL", "WebAssembly"], "Concert visuals that react to the band's audio in real time: an ocean of light that swells with the bass. "
               "Runs in a browser tab on the venue's laptop, with every shader hand-tuned to stay at 60 frames per second on old GPUs."),
            _p("Four Kilobytes", ["HLSL", "Zig"], "A 4 KB demo with a full city fly-through, synthesized music and a sunset, all generated from math at "
               "start-up. Placed second at a European demo party, losing only to a team that has been doing this since 1997."),
            _p("Glitch Garden", ["GLSL", "Rust"], "An interactive installation where visitors grow digital plants by walking around. The plants were "
               "born from a rendering bug I decided to keep. It has been shown in Osaka, Seoul and Berlin."),
        ],
    },
    {
        "tier": "Gigamogger", "username": "cobolcarl", "full_name": "Carl Batch",
        "avatar_url": _avatar("cobolcarl"), "location": "Frankfurt, DE", "education": "Diplom Informatik, TU Darmstadt",
        "bio": "Mainframe whisperer. Banks call me when the code that moves billions overnight was written before their CTO was born. I translate "
               "between 1980s COBOL and modern teams without judging either of them, and I am the only person I know with a favourite JCL card.",
        "favorite_ide": "IntelliJ IDEA", "favorite_ai_agents": ["Copilot", "Claude Code"],
        "skills": ["COBOL", "Pascal", "Ada", "Java", "Backend", "SQL", "Kotlin", "Clojure", "Cloud", "Security"],
        "interests": ["Banking", "History of Computing", "Chess"], "experience_level": "Lead",
        "looking_for": ["Mentee", "Cofounder"], "links": _links("cobolcarl", 3),
        "projects": [
            _p("Batch to Cloud", ["COBOL", "Java"], "A step-by-step migration kit that moves overnight COBOL batch jobs onto cloud schedulers without "
               "changing a single result. Every run is compared to the mainframe's output to the last cent before anything is switched over."),
            _p("Copybook Viewer", ["COBOL", "Kotlin"], "Turns COBOL copybooks, the data layouts nobody can read anymore, into searchable diagrams. "
               "New developers at two banks now use it on their first day instead of asking the one person who remembers."),
            _p("Pascal Ledger", ["Pascal", "Ada"], "A double-entry bookkeeping engine written in Pascal and Ada for a charity, designed to run "
               "untouched for the next thirty years. It already survived two operating-system upgrades without a recompile."),
        ],
    },
    # ---------- 🔥 Senior Mogger
    {
        "tier": "Senior Mogger", "username": "gophergwen", "full_name": "Gwen Gopher",
        "avatar_url": _avatar("gophergwen"), "location": "Amsterdam, NL", "education": "B.Sc. Computer Science, VU Amsterdam",
        "bio": "Platform engineer at a bike-sharing startup. Our bikes report in every five seconds, so I care a lot about queues, "
               "back-pressure and what happens when half the city rides home at once.",
        "favorite_ide": "GoLand", "favorite_ai_agents": ["Claude Code"],
        "skills": ["Go", "Rust", "Backend", "DevOps", "Cloud", "Kafka", "PostgreSQL"],
        "interests": ["Cycling", "Cities"], "experience_level": "Senior",
        "looking_for": ["Side project"], "links": _links("gophergwen", 2),
        "projects": [
            _p("Rush Hour", ["Go", "Rust"], "A load simulator that replays a rainy Friday rush hour against our bike API so we find the slow parts before riders do."),
            _p("Dock Map", ["Go"], "A live map of empty and full docks that rebalancing vans use to decide where to drive next."),
        ],
    },
    {
        "tier": "Senior Mogger", "username": "dartdana", "full_name": "Dana Flutter",
        "avatar_url": _avatar("dartdana"), "location": "Cape Town, ZA", "education": "B.Sc. Computer Science, University of Cape Town",
        "bio": "Runs a two-person app studio. We build Flutter apps for local clinics and schools, usually for phones that are "
               "five years old with a cracked screen and a slow connection, so offline-first is a way of life.",
        "favorite_ide": "Android Studio", "favorite_ai_agents": ["Gemini"],
        "skills": ["Dart", "Flutter", "Kotlin", "Mobile", "Firebase", "Swift"],
        "interests": ["Health Tech", "Education"], "experience_level": "Senior",
        "looking_for": ["Hackathon team"], "links": _links("dartdana", 2),
        "projects": [
            _p("Clinic Queue", ["Dart", "Kotlin"], "Lets patients take a number by SMS and wait at home instead of outside the clinic all morning."),
            _p("Offline Classroom", ["Dart", "Swift"], "Homework that syncs over Bluetooth between phones when there's no internet in the village."),
        ],
    },
    {
        "tier": "Senior Mogger", "username": "scalasteve", "full_name": "Steve Spark",
        "avatar_url": _avatar("scalasteve"), "location": "Dublin, IE", "education": "M.Sc. Data Analytics, UCD",
        "bio": "Data engineer at a music-streaming company. I build the pipelines that decide what plays next, and "
               "I take it personally when the shuffle button isn't random enough.",
        "favorite_ide": "IntelliJ IDEA", "favorite_ai_agents": ["Copilot"],
        "skills": ["Scala", "Spark", "Data Engineering", "Python", "SQL", "Kotlin", "Kafka"],
        "interests": ["Music", "Data"], "experience_level": "Senior",
        "looking_for": ["Open source"], "links": _links("scalasteve", 2),
        "projects": [
            _p("Fair Shuffle", ["Scala", "Kotlin"], "A shuffle that feels random to humans: no artist twice in a row, no three sad songs in a row."),
            _p("Skip Radar", ["Scala", "Python"], "Spots songs people skip in the first five seconds so playlists stop recommending them."),
        ],
    },
    {
        "tier": "Senior Mogger", "username": "lualuna", "full_name": "Luna Moddy",
        "avatar_url": _avatar("lualuna"), "location": "Montreal, CA", "education": "B.Sc. Software Engineering, Concordia",
        "bio": "Game modder turned tools programmer. My first mod got two million downloads; now I build the "
               "scripting systems that let players make mods for the games I work on.",
        "favorite_ide": "VS Code", "favorite_ai_agents": ["Cursor"],
        "skills": ["Lua", "C++", "Game Dev", "C#", "Python", "Ruby"],
        "interests": ["Modding", "Indie Games"], "experience_level": "Mid-level",
        "looking_for": ["Side project", "Mentee"], "links": _links("lualuna", 2),
        "projects": [
            _p("Mod Forge", ["Lua", "C++"], "A sandboxed Lua scripting layer for a game engine, so player mods can't crash the game or read your files."),
            _p("Quest Writer", ["Lua", "Ruby"], "A small language for writing branching quests that compiles to Lua tables."),
        ],
    },
    {
        "tier": "Senior Mogger", "username": "rubyruth", "full_name": "Ruth Rails",
        "avatar_url": _avatar("rubyruth"), "location": "Portland, OR", "education": "B.A. English, Reed College",
        "bio": "English major who fell into Rails in 2009 and never left. Founded a tiny bookshop-inventory SaaS "
               "that pays the bills, and I mentor career changers who think they are too late to start.",
        "favorite_ide": "RubyMine", "favorite_ai_agents": ["Claude Code"],
        "skills": ["Ruby", "Rails", "PostgreSQL", "Elixir", "Full-stack", "JavaScript"],
        "interests": ["Books", "Small Business"], "experience_level": "Lead",
        "looking_for": ["Mentee"], "links": _links("rubyruth", 2),
        "projects": [
            _p("Shelf Life", ["Ruby", "Elixir"], "Inventory software for independent bookshops, with a barcode scanner that works on any phone."),
            _p("First Commit", ["Ruby"], "A mentoring tracker that pairs career changers with volunteers for a first open-source pull request."),
        ],
    },
    # ---------- 🧑‍💻 Mid Mogger
    {
        "tier": "Mid Mogger", "username": "reactrita", "full_name": "Rita Hooks",
        "avatar_url": _avatar("reactrita"), "location": "São Paulo, BR", "education": "B.Sc. Information Systems, USP",
        "bio": "Frontend dev at a fintech. I turn Figma files into React components and argue about loading spinners.",
        "favorite_ide": "VS Code", "favorite_ai_agents": ["Copilot"],
        "skills": ["React", "TypeScript", "Frontend", "Tailwind CSS", "Go"],
        "interests": ["Design Systems", "Samba"], "experience_level": "Mid-level",
        "looking_for": ["Side project"], "links": _links("reactrita", 1),
        "projects": [_p("Spinner Zoo", ["TypeScript", "Go"], "A gallery of loading states with a vote on which one feels fastest to users.")],
    },
    {
        "tier": "Mid Mogger", "username": "nodenate", "full_name": "Nate Express",
        "avatar_url": _avatar("nodenate"), "location": "Atlanta, GA", "education": "B.S. Computer Science, Georgia State",
        "bio": "Backend dev for a food-delivery app. Node.js all day, mostly making sure your fries arrive warm.",
        "favorite_ide": "WebStorm", "favorite_ai_agents": ["Cursor"],
        "skills": ["Node.js", "JavaScript", "Backend", "MongoDB", "Ruby"],
        "interests": ["Food", "Basketball"], "experience_level": "Mid-level",
        "looking_for": ["Hackathon team"], "links": _links("nodenate", 1),
        "projects": [_p("Warm Fries", ["JavaScript", "Ruby"], "Predicts when a courier should leave so food spends less time waiting on the counter.")],
    },
    {
        "tier": "Mid Mogger", "username": "djangodeb", "full_name": "Deb Models",
        "avatar_url": None, "location": "Accra, GH", "education": "B.Sc. Computer Science, University of Ghana",
        "bio": "Django developer building tools for farmers' cooperatives. Python and spreadsheets, mostly.",
        "favorite_ide": "PyCharm", "favorite_ai_agents": ["Claude Code"],
        "skills": ["Python", "Django", "Backend", "PostgreSQL", "Go"],
        "interests": ["Agriculture", "Open Data"], "experience_level": "Mid-level",
        "looking_for": ["Open source"], "links": _links("djangodeb", 1),
        "projects": [_p("Harvest Ledger", ["Python", "Go"], "Tracks how much each farmer delivered so cooperative payouts are fair and on time.")],
    },
    {
        "tier": "Mid Mogger", "username": "angularal", "full_name": "Al Directive",
        "avatar_url": _avatar("angularal"), "location": "Madrid, ES", "education": "Grado en Ingeniería Informática, UPM",
        "bio": "Angular developer at an airline. Builds the screens gate agents use when your flight is delayed.",
        "favorite_ide": "WebStorm", "favorite_ai_agents": ["Copilot"],
        "skills": ["Angular", "TypeScript", "Frontend", "Java", "Swift"],
        "interests": ["Aviation", "Travel"], "experience_level": "Junior",
        "looking_for": ["Mentor"], "links": _links("angularal", 1),
        "projects": [_p("Gate Calm", ["TypeScript", "Swift"], "A rebooking screen that offers the three best options first instead of a list of forty.")],
    },
    {
        "tier": "Mid Mogger", "username": "vuevera", "full_name": "Vera View",
        "avatar_url": _avatar("vuevera"), "location": "Kyiv, UA", "education": "B.Sc. Applied Mathematics, KPI",
        "bio": "Vue developer and part-time illustrator. Makes dashboards that are actually nice to look at.",
        "favorite_ide": "VS Code", "favorite_ai_agents": ["Claude Code"],
        "skills": ["Vue", "JavaScript", "Frontend", "Figma", "Kotlin"],
        "interests": ["Illustration", "Data Viz"], "experience_level": "Mid-level",
        "looking_for": ["Side project"], "links": [],
        "projects": [_p("Pretty Metrics", ["JavaScript", "Kotlin"], "A dashboard kit where every chart is hand-drawn style but still readable at a glance.")],
    },
    # ---------- 🐣 Junior Mogger
    {
        "tier": "Junior Mogger", "username": "hackhannah", "full_name": "Hannah Hack",
        "avatar_url": None, "location": "Leeds, UK", "education": "B.Sc. Biology (final year), University of Leeds",
        "bio": "Biology student at my first hackathon. Learning Python to analyse lab data.",
        "favorite_ide": "VS Code", "favorite_ai_agents": ["ChatGPT"],
        "skills": ["Python", "Data Science", "R"],
        "interests": ["Biology", "Hackathons"], "experience_level": "Student",
        "looking_for": ["Hackathon team", "Mentor"], "links": [],
        "projects": [_p("Petri Counter", ["Python"], "Counts bacteria colonies in a photo.", url=False)],
    },
    {
        "tier": "Junior Mogger", "username": "datadan", "full_name": "Dan Sheets",
        "avatar_url": None, "location": "Denver, CO", "education": None,
        "bio": "Accountant moving from Excel macros to Python. Pandas is my new best friend.",
        "favorite_ide": "Jupyter", "favorite_ai_agents": ["ChatGPT"],
        "skills": ["Python", "SQL"],
        "interests": ["Finance", "Hiking"], "experience_level": "Junior",
        "looking_for": ["Mentor"], "links": [],
        "projects": [_p("Expense Sorter", ["Python"], "Sorts my bank export into categories.", url=False)],
    },
    {
        "tier": "Junior Mogger", "username": "designdina", "full_name": "Dina Kern",
        "avatar_url": _avatar("designdina"), "location": "Paris, FR", "education": "Master Design Graphique, ENSAD",
        "bio": "Graphic designer learning to code my own portfolio. CSS grid made me cry, then made me happy.",
        "favorite_ide": "VS Code", "favorite_ai_agents": [],
        "skills": ["HTML", "CSS", "UI/UX Design"],
        "interests": ["Typography", "Design"], "experience_level": "Junior",
        "looking_for": ["Side project"], "links": [],
        "projects": [_p("Folio", ["HTML", "CSS"], "My portfolio site, coded by hand.", url=False)],
    },
    {
        "tier": "Junior Mogger", "username": "ittomas", "full_name": "Tomás Helpdesk",
        "avatar_url": None, "location": "Buenos Aires, AR", "education": None,
        "bio": "IT support tech automating the boring parts of my job with PowerShell.",
        "favorite_ide": "VS Code", "favorite_ai_agents": ["Copilot"],
        "skills": ["PowerShell", "Bash"],
        "interests": ["Automation"], "experience_level": "Junior",
        "looking_for": ["Mentor"], "links": [],
        "projects": [_p("Reset Bot", ["PowerShell"], "Resets passwords without a ticket.", url=False)],
    },
    {
        "tier": "Junior Mogger", "username": "gamergus", "full_name": "Gus Level",
        "avatar_url": None, "location": None, "education": "High school senior",
        "bio": "Making my first platformer. The jump feels wrong and I can't stop tweaking it.",
        "favorite_ide": "Godot Editor", "favorite_ai_agents": [],
        "skills": ["GDScript", "Game Dev"],
        "interests": ["Games", "Pixel Art"], "experience_level": "Student",
        "looking_for": ["Mentor", "Hackathon team"], "links": [],
        "projects": [_p("Jump Test", ["GDScript"], "A one-level platformer from my first game jam.", url=False)],
    },
    # ---------- 🥚 Hello World
    {
        "tier": "Hello World", "username": "justjoined", "full_name": "June Joiner",
        "avatar_url": None, "location": None, "education": None,
        "bio": "Signed up five minutes ago.", "favorite_ide": "VS Code", "favorite_ai_agents": [],
        "skills": [], "interests": [], "experience_level": None,
        "looking_for": ["Just vibes"], "links": [], "projects": [],
    },
    {
        "tier": "Hello World", "username": "codecurious", "full_name": "Cora Curious",
        "avatar_url": None, "location": "Vienna, AT", "education": None,
        "bio": "What is a terminal?", "favorite_ide": "Notepad", "favorite_ai_agents": ["ChatGPT"],
        "skills": ["HTML"], "interests": ["Learning"], "experience_level": "Student",
        "looking_for": ["Mentor"], "links": [], "projects": [],
    },
    {
        "tier": "Hello World", "username": "nullnick", "full_name": "Nick Null",
        "avatar_url": None, "location": None, "education": None,
        "bio": "null", "favorite_ide": "Vim", "favorite_ai_agents": [],
        "skills": [], "interests": [], "experience_level": None,
        "looking_for": [], "links": [], "projects": [],
    },
    {
        "tier": "Hello World", "username": "helloharper", "full_name": "Harper Hello",
        "avatar_url": None, "location": "Auckland, NZ", "education": None,
        "bio": "Learning to code with my kid.", "favorite_ide": "Scratch", "favorite_ai_agents": [],
        "skills": ["JavaScript"], "interests": ["Family"], "experience_level": "Student",
        "looking_for": ["Just vibes"], "links": [], "projects": [],
    },
    {
        "tier": "Hello World", "username": "zeroxp", "full_name": "Zed Zero",
        "avatar_url": None, "location": None, "education": None,
        "bio": "0 XP. Level 1.", "favorite_ide": "VS Code", "favorite_ai_agents": [],
        "skills": ["CSS"], "interests": [], "experience_level": "Student",
        "looking_for": [], "links": [], "projects": [],
    },
]

DEMO_THEMES.update({
    # 👑 Gigamogger
    "assemblyamy": _theme("#030b1a", "snow", snow_kind="dots", snow_count=200, snow_wind=0, brightness=70),  # a starfield
    "prologpete": _theme("#1a1405", "matrix", rain_color="#e6c86e", rain_symbols="code", speed=3, glow=True),
    "soliditysara": _theme("#0c0a24", "market", chart_mood="choppy", chart_palette="neon", chart_ticker="AUDIT", chart_volatility=9),
    "shadershiro": _theme("#14001f", "matrix", rain_rainbow=True, rain_symbols="katakana", glow=True, speed=6),
    "cobolcarl": _theme("#00140a", "matrix", rain_color="#33ff99", rain_symbols="binary", brightness=30, speed=1),
    # 🔥 Senior Mogger
    "gophergwen": _theme("#07202a", "emoji", emojis=["🚲", "🌧️", "🐹"], emoji_path="straight", emoji_angle=0, emoji_count=10),
    "dartdana": _theme("#0a1f33", "emoji", emojis=["🎯", "💙", "📱"], emoji_path="bounce", emoji_count=12),
    "scalasteve": _theme("#1f0a14", "emoji", emojis=["🎵", "🎧", "🔀"], emoji_path="wave", emoji_count=16),
    "lualuna": _theme("#0e0b26", "emoji", emojis=["🌙", "🎮", "🧩"], emoji_path="wave", emoji_spin=4),
    "rubyruth": _theme("#2a0508", "slogans", slogans=["READ MORE BOOKS", "RAILS IS FINE", "NEVER TOO LATE"],
                       slogan_color="#e11d48", slogan_style="solid", slogan_tilt=-6),
    # 🧑‍💻 Mid Mogger
    "reactrita": _theme("#04161f", "dvd", count=2, color_change=True, color="#61dafb"),
    "nodenate": _theme("#0f1a05", "emoji", emojis=["🍟", "🛵", "🍔"], emoji_path="straight", emoji_angle=180, emoji_count=10),
    "djangodeb": _theme("#062012", "emoji", emojis=["🌽", "🌾", "🥭"], emoji_path="straight", emoji_angle=90, speed=2),
    "angularal": _theme("#240a0a", "emoji", emojis=["✈️", "☁️"], emoji_path="straight", emoji_angle=0, emoji_count=8),
    "vuevera": _theme("#041a14", "slogans", slogans=["MAKE IT PRETTY", "DATA IS ART"], slogan_color="#42b883",
                      slogan_style="outline", slogan_tilt=10),
    # 🐣 Junior Mogger
    "hackhannah": _theme("#0a1424", "emoji", emojis=["🧫", "🔬", "🧬"], emoji_path="wave", emoji_count=9),
    "datadan": _theme("#101a0a", "money", money_kind="coins", money_count=20, money_wind=1, money_weight=3),
    "designdina": _theme("#1f0d1a", "slogans", slogans=["KERNING MATTERS", "CSS GRID FOREVER"], slogan_color="#f472b6",
                         slogan_style="mixed", slogan_tilt=-30),
    "ittomas": _theme("#0a0e14", "matrix", rain_color="#5391fe", rain_symbols="code", brightness=20, speed=3),
    "gamergus": _theme("#16082a", "emoji", emojis=["🕹️", "👾", "⭐"], emoji_path="bounce", emoji_count=14),
    # 🥚 Hello World
    "justjoined": _theme("#0f0f14", "dvd", count=1, color_change=True, speed=1),
    "codecurious": _theme("#0a141a", "emoji", emojis=["❓", "🤔"], emoji_count=5, speed=1),
    "nullnick": _theme("#000000"),  # null: no effect at all
    "helloharper": _theme("#1a0f05", "emoji", emojis=["🧒", "🧑", "💻"], emoji_count=6, emoji_path="wave"),
    "zeroxp": _theme("#08080c", "snow", snow_kind="dots", snow_count=20, snow_wind=1, brightness=15),
})
