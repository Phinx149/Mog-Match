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


def _project(title: str, technologies: list[str], about: str, length: int = 120, url: bool = True) -> dict:
    slug = title.lower().replace(" ", "-")
    return {
        "title": title,
        "description": _long(about, length),
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
