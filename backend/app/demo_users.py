"""Quick-login demo accounts for local testing, spread across every Mog tier.

Created by `flask seed-test-users` (not by `flask seed`, so tests and teammates' databases don't
see them). Every account's password is DEMO_PASSWORD. Each profile is shaped to land in a tier:
Mog points come from esoteric languages used in projects, number of skills, links, projects,
description and bio length, profile completeness and experience (see docs/MOG_SCORE.md).
`tests/test_demo_users.py` checks every account really lands in its intended tier.

Profile pictures: accounts with an `avatar_url` use that DiceBear link. Accounts with `None` get the
cartoon in app/seed_avatars/<username>.png when seeded (drawn by scripts/make_seed_avatars.py).
"""

DEMO_PASSWORD = "123"


def _avatar(username: str) -> str:
    return f"https://api.dicebear.com/9.x/thumbs/svg?seed={username}"


def _project(title: str, technologies: list[str], about: str, url: bool = True) -> dict:
    slug = title.lower().replace(" ", "-")
    return {
        "title": title,
        "description": about,
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
        "bio": "Compiler engineer who writes Haskell for fun and COBOL for money. I maintain three type checkers, a mainframe emulator nobody asked for, and a blog where I rank error messages by how rude they are. Ask me about monads and I will draw you a diagram on a napkin, then frame the napkin.",
        "favorite_ide": "Neovim", "favorite_ai_agents": ["Claude Code", "Cursor"],
        "skills": ["Haskell", "COBOL", "Zig", "OCaml", "Prolog", "Rust", "Systems Programming", "Backend", "C", "Assembly"],
        "interests": ["Compilers", "Type Theory", "Retro Computing"], "experience_level": "Lead",
        "looking_for": ["Open source", "Mentee"], "links": _links("gigachad", 3),
        "projects": [
            _project("Monad Mainframe", ["Haskell", "COBOL"], "A COBOL-to-Haskell transpiler that keeps 1970s banking code running on modern hardware. It reads the original programs, builds a typed model of every record layout, and produces Haskell that gives byte-for-byte identical results. A regional bank used it to retire a mainframe without changing a single customer statement."),
            _project("ZigOS", ["Zig", "Assembly"], "A tiny hobby operating-system kernel written in Zig, with hand-tuned assembly boot code that fits in 512 bytes. It boots in under a second on real hardware, has a preemptive scheduler and a filesystem, and runs a text adventure as its first user program. Used in two university operating-systems courses."),
            _project("Prolog Planner", ["Prolog", "OCaml"], "A logic-programming scheduler that plans hackathon teams from skill constraints: everyone gets a team with the skills it is missing, nobody is stuck with an ex, and every team has at least one person who can deploy. The solver is Prolog, the web front end is OCaml, and it has organised six hackathons so far."),
        ],
    },
    {
        "tier": "Gigamogger", "username": "lispwizard", "full_name": "Lisa Lambda",
        "avatar_url": _avatar("lispwizard"), "location": "Boston, MA", "education": "B.S. Computer Science, MIT",
        "bio": "Parenthesis enthusiast. I build interpreters, live-coding music tools and the occasional Fortran physics simulation, usually all on the same weekend. I play synth in a band where every song is a running program, and the encore is whatever crashes least. Recursion is my love language.",
        "favorite_ide": "Emacs", "favorite_ai_agents": ["Claude Code"],
        "skills": ["Lisp", "Racket", "Fortran", "Clojure", "Scheme", "Elixir", "Python", "Backend", "Machine Learning", "Julia"],
        "interests": ["Programming Languages", "Music Tech", "Physics"], "experience_level": "Senior",
        "looking_for": ["Side project", "Open source"], "links": _links("lispwizard", 3),
        "projects": [
            _project("Paren Synth", ["Racket", "Lisp"], "A live-coding synthesizer where every sound is an S-expression you can edit while it plays. Change a number and the music changes on the next beat without a glitch. I have performed with it at eleven shows, and the audience sees the code on a projector as it is written, mistakes and all."),
            _project("Fortran Fluids", ["Fortran", "Julia"], "A fluid-dynamics simulator that runs a 1977 Fortran solver side by side with my modern Julia port and plots where their answers drift apart. The Fortran is still faster on one benchmark, which I find hilarious. A physics department uses it to teach numerical stability with real historical code."),
            _project("Elixir Echo", ["Elixir", "Clojure"], "A fault-tolerant chat relay that survives its own bugs, built to learn how the BEAM really works. Every room is its own process, so one broken room never takes down another. I deliberately inject crashes during demos and nobody in the chat notices. The Clojure client is a bonus experiment."),
        ],
    },
    {
        "tier": "Gigamogger", "username": "verilogvic", "full_name": "Victor Gates",
        "avatar_url": _avatar("verilogvic"), "location": "Austin, TX", "education": "M.S. Electrical Engineering, UT Austin",
        "bio": "I design CPUs for fun on cheap FPGA boards. If it has a clock signal, I have opinions about it. By day I write firmware for industrial robots; by night I build processors out of logic gates and teach them to play Pong. My desk is mostly oscilloscope at this point.",
        "favorite_ide": "Vim", "favorite_ai_agents": ["Copilot"],
        "skills": ["Verilog", "VHDL", "Ada", "C", "Embedded", "Rust", "Assembly", "Robotics", "Python", "C++"],
        "interests": ["Hardware", "FPGAs", "Robotics"], "experience_level": "Lead",
        "looking_for": ["Hackathon team", "Mentee"], "links": _links("verilogvic", 3),
        "projects": [
            _project("RISC-Me", ["Verilog", "Assembly"], "A five-stage RISC-V CPU on a cheap FPGA board, with a tiny assembler to program it. It runs at 50 MHz, has a working cache, and passes the official compliance tests. I wrote a step-by-step guide so students can build one over a semester, and three universities now use it in their labs."),
            _project("Ada Autopilot", ["Ada", "C"], "Safety-first drone autopilot firmware written in Ada, with control loops whose timing and ranges are formally checked before anything flies. If a sensor lies, the drone lands itself gently instead of guessing. It has logged two hundred hours of flight without a crash, which my insurance company appreciates."),
            _project("VHDL Pong", ["VHDL"], "Pong rendered straight from logic gates to a VGA monitor, with no CPU involved at all. The ball, paddles and score are all plain digital circuits written in VHDL, and the game runs at a perfect 60 frames per second because it physically cannot do anything else. Kids at the science fair loved it more than the robots."),
        ],
    },
    {
        "tier": "Gigamogger", "username": "rustacean", "full_name": "Rusty Crab",
        "avatar_url": _avatar("rustacean"), "location": "Berlin, DE", "education": "B.Sc. Informatics, TU Berlin",
        "bio": "Memory-safe and proud. I ship Rust and Zig in production and write Elm on the frontend so nothing ever crashes, which makes on-call very boring and I like it that way. I maintain a popular crate, give talks on fearless concurrency, and own more crab plushies than is reasonable.",
        "favorite_ide": "RustRover", "favorite_ai_agents": ["Claude Code", "Copilot"],
        "skills": ["Rust", "Zig", "Elm", "Nim", "WebAssembly", "Systems Programming", "Backend", "Frontend", "Go", "TypeScript"],
        "interests": ["Performance", "WebAssembly", "Open Source"], "experience_level": "Senior",
        "looking_for": ["Open source", "Side project"], "links": _links("rustacean", 3),
        "projects": [
            _project("Ferris DB", ["Rust", "Zig"], "An embedded key-value store with a Rust core and Zig bindings, benchmarked honestly against SQLite. It wins on write-heavy workloads and loses on everything else, and the README says so in the first paragraph. It survives power cuts mid-write, which I tested by pulling the plug a thousand times."),
            _project("Elm Board", ["Elm", "WebAssembly"], "A collaborative whiteboard with an Elm interface and a WebAssembly drawing engine. Twenty people can sketch at once without lag, and because the UI is Elm, it has never thrown a runtime error in production. Teachers use it for remote lessons and kids use it mostly to draw cats."),
            _project("Nim Notes", ["Nim"], "A note-taking command-line tool written in Nim that compiles to a 200 KB binary and starts in a millisecond. Notes are plain text files with tags, full-text search is instant, and it syncs with git. Built because every other notes app took longer to open than my thought took to disappear."),
        ],
    },
    {
        "tier": "Gigamogger", "username": "fsharpfiona", "full_name": "Fiona Sharp",
        "avatar_url": _avatar("fsharpfiona"), "location": "Dublin, IE", "education": "M.Sc. Data Science, Trinity College Dublin",
        "bio": "Functional data scientist at a fintech. F# and OCaml for models, Julia for the heavy numbers, and Erlang for anything that must never go down. I believe a type error at compile time beats a wrong forecast in production, and I have the incident reports to prove it.",
        "favorite_ide": "JetBrains Rider", "favorite_ai_agents": ["Claude Code"],
        "skills": ["F#", "OCaml", "Julia", "Erlang", "Data Science", "Machine Learning", "Python", "SQL", "R", "Haskell"],
        "interests": ["Functional Programming", "Statistics", "Finance"], "experience_level": "Senior",
        "looking_for": ["Cofounder", "Hackathon team"], "links": _links("fsharpfiona", 1),
        "projects": [
            _project("Typed Trader", ["F#", "OCaml"], "A backtesting engine for trading strategies where units and currencies are checked by the type system, so adding dollars to euros is a compile error. Strategies are written in F#, the order-book simulation is OCaml, and every run produces a report a risk team can actually read."),
            _project("Julia Forecast", ["Julia", "R"], "Probabilistic weather forecasts for cyclists, with uncertainty bands that actually mean something: when it says a 70 percent chance of rain on your route, it rains seven times out of ten. Written in Julia with an R notebook that checks its calibration every single week."),
            _project("Never Down", ["Erlang"], "A supervision-tree demo that keeps a chat server alive while you randomly kill its processes from a big red button on the page. Each crash is shown live, along with how fast the supervisor restarted it. It is the most popular talk I have given."),
        ],
    },
    # ---------- 🔥 Senior Mogger (65–84): strong profiles, a few gaps
    {
        "tier": "Senior Mogger", "username": "seniorsam", "full_name": "Sam Senior",
        "avatar_url": _avatar("seniorsam"), "location": "Toronto, CA", "education": "B.Eng. Software, University of Waterloo",
        "bio": "Backend lead who loves boring, reliable systems. Go services, Postgres and well-written runbooks. I have been paged at 3 a.m. enough times to make everything boring on purpose. I mentor juniors on reading logs calmly.",
        "favorite_ide": "GoLand", "favorite_ai_agents": ["Copilot"],
        "skills": ["Go", "Rust", "Backend", "PostgreSQL", "Kubernetes", "Docker", "Python", "Cloud"],
        "interests": ["Distributed Systems", "Reliability"], "experience_level": "Lead",
        "looking_for": ["Mentee"], "links": _links("seniorsam", 2),
        "projects": [
            _project("Queue Keeper", ["Go", "Rust"], "A job queue that survives restarts and tells you exactly why a job failed, in plain words, with the input that broke it. Retries back off politely, poisoned jobs are set aside instead of blocking everything, and the dashboard shows what is stuck."),
            _project("Pager Pal", ["Go"], "Turns a storm of noisy alerts into one calm summary message for whoever is on call: what broke, since when, and which dashboard to open first. Cut our pages per week in half."),
        ],
    },
    {
        "tier": "Senior Mogger", "username": "elixirella", "full_name": "Ella Elixir",
        "avatar_url": _avatar("elixirella"), "location": "Lisbon, PT", "education": "B.Sc. Computer Engineering, IST Lisbon",
        "bio": "Real-time everything. Phoenix LiveView fan building multiplayer apps without writing much JavaScript. I run a pub quiz on Thursdays using an app I wrote, and the scoreboard has never once fallen over.",
        "favorite_ide": "VS Code", "favorite_ai_agents": ["Cursor"],
        "skills": ["Elixir", "Phoenix", "Backend", "PostgreSQL", "JavaScript", "Full-stack", "Erlang"],
        "interests": ["Real-time Apps", "Multiplayer"], "experience_level": "Senior",
        "looking_for": ["Side project"], "links": _links("elixirella", 2),
        "projects": [
            _project("Live Quiz", ["Elixir", "Phoenix"], "A pub-quiz app where hundreds of phones answer at once and the scoreboard updates live on the big screen. No app install, just a QR code on the table. It has run every Thursday for two years."),
            _project("Beam Chat", ["Erlang"], "A tiny chat server I wrote to finally understand OTP supervisors and restarts."),
        ],
    },
    {
        "tier": "Senior Mogger", "username": "kotlinkai", "full_name": "Kai Kotlin",
        "avatar_url": _avatar("kotlinkai"), "location": "Seoul, KR", "education": "B.S. Computer Science, KAIST",
        "bio": "Android and Kotlin Multiplatform developer. I ship apps people actually keep installed, which means fast start-up, small downloads and no surprise notifications. Weekend marathon runner and step-count obsessive.",
        "favorite_ide": "Android Studio", "favorite_ai_agents": ["Gemini"],
        "skills": ["Kotlin", "Swift", "Mobile", "Dart", "Flutter", "Java", "Scala"],
        "interests": ["Mobile UX", "Fitness"], "experience_level": "Senior",
        "looking_for": ["Hackathon team"], "links": _links("kotlinkai", 2),
        "projects": [
            _project("Step Streak", ["Kotlin", "Swift"], "A cross-platform step counter that turns daily walks into a streak game with friends. Shared Kotlin logic, native Swift and Android screens, and a battery cost you will not notice."),
            _project("Dart Darts", ["Dart"], "A Flutter scorekeeper for pub darts nights, with big buttons for tipsy thumbs."),
        ],
    },
    {
        "tier": "Senior Mogger", "username": "clojureclara", "full_name": "Clara Clojure",
        "avatar_url": _avatar("clojureclara"), "location": "Stockholm, SE", "education": "M.Sc. Computer Science, KTH",
        "bio": "Data pipelines in Clojure, dashboards in ClojureScript, immutable by default. I turn messy public transport feeds into maps commuters actually trust.",
        "favorite_ide": "IntelliJ IDEA", "favorite_ai_agents": ["Claude Code"],
        "skills": ["Clojure", "Data Engineering", "Kafka", "SQL", "Python", "Scala"],
        "interests": ["Data", "Open Data"], "experience_level": "Mid-level",
        "looking_for": ["Open source"], "links": _links("clojureclara", 2),
        "projects": [
            _project("Transit Tap", ["Clojure", "Scala"], "Streams live bus positions into a map so you know if running for the bus is worth it. Built on open city data, used by about four thousand commuters."),
            _project("Open Budget", ["Clojure"], "Turns enormous city budget spreadsheets into simple charts that normal humans can read and question."),
        ],
    },
    {
        "tier": "Senior Mogger", "username": "swiftsofia", "full_name": "Sofia Swift",
        "avatar_url": _avatar("swiftsofia"), "location": "Mexico City, MX", "education": "B.S. Computer Science, UNAM",
        "bio": "iOS developer and accessibility advocate. Every feature I ship gets tested with VoiceOver and huge text before it merges. I speak at meetups about apps everyone can use.",
        "favorite_ide": "Xcode", "favorite_ai_agents": ["Copilot"],
        "skills": ["Swift", "Mobile", "Objective-C", "Ruby", "Frontend", "UI/UX Design"],
        "interests": ["Accessibility", "Design"], "experience_level": "Senior",
        "looking_for": ["Mentee", "Side project"], "links": _links("swiftsofia", 2),
        "projects": [
            _project("See For Me", ["Swift"], "Describes what is in front of the camera for blind and low-vision users, reading signs and menus aloud. Built with feedback from a local accessibility group."),
            _project("Legacy Lift", ["Objective-C", "Swift"], "A careful, screen-by-screen migration of a ten-year-old Objective-C app to SwiftUI."),
        ],
    },
    # ---------- 🧑‍💻 Mid Mogger (45–64): decent profiles, mainstream languages
    {
        "tier": "Mid Mogger", "username": "midmike", "full_name": "Mike Middle",
        "avatar_url": _avatar("midmike"), "location": "Chicago, IL", "education": "B.S. Information Systems, UIC",
        "bio": "Full-stack dev at an agency. React on the front, Node on the back, coffee in between. Twelve client sites a year and counting.",
        "favorite_ide": "VS Code", "favorite_ai_agents": ["Copilot"],
        "skills": ["JavaScript", "TypeScript", "React", "Node.js", "Full-stack", "Go"],
        "interests": ["Web Dev", "Coffee"], "experience_level": "Mid-level",
        "looking_for": ["Side project"], "links": _links("midmike", 1),
        "projects": [_project("Bean Tracker", ["TypeScript", "React", "Go"], "Logs every coffee you drink, charts your caffeine curve, and judges you gently.")],
    },
    {
        "tier": "Mid Mogger", "username": "pythonpat", "full_name": "Pat Python",
        "avatar_url": _avatar("pythonpat"), "location": "Manchester, UK", "education": "B.Sc. Mathematics, University of Manchester",
        "bio": "Data analyst turned Python developer. I automate the spreadsheets so nobody on my team has to copy and paste on Mondays anymore.",
        "favorite_ide": "PyCharm", "favorite_ai_agents": ["Claude Code"],
        "skills": ["Python", "SQL", "Data Science", "Pandas", "Ruby"],
        "interests": ["Automation", "Football"], "experience_level": "Junior",
        "looking_for": ["Mentor", "Side project"], "links": _links("pythonpat", 1),
        "projects": [_project("Sheet Slayer", ["Python", "Ruby"], "Merges fifty messy spreadsheets into one clean report every Monday morning, automatically.")],
    },
    {
        "tier": "Mid Mogger", "username": "javajade", "full_name": "Jade Java",
        "avatar_url": None, "location": "Pune, IN", "education": "B.Tech. Computer Science, COEP",
        "bio": "Spring Boot developer building banking APIs that move real money. Learning Kotlin on weekends and loving the null safety.",
        "favorite_ide": "IntelliJ IDEA", "favorite_ai_agents": ["Copilot"],
        "skills": ["Java", "Spring Boot", "Kotlin", "Backend", "SQL"],
        "interests": ["Fintech", "Cricket"], "experience_level": "Mid-level",
        "looking_for": ["Hackathon team"], "links": _links("javajade", 1),
        "projects": [_project("Split Smart", ["Java", "Kotlin"], "Splits group bills fairly, even when someone only had a salad.")],
    },
    {
        "tier": "Mid Mogger", "username": "phpphil", "full_name": "Phil PHP",
        "avatar_url": _avatar("phpphil"), "location": "Warsaw, PL", "education": "B.Sc. Information Technology, Warsaw University of Technology",
        "bio": "Laravel developer for ten years. Still believes PHP is fine, actually, and has the happy clients to prove it.",
        "favorite_ide": "PhpStorm", "favorite_ai_agents": ["Cursor"],
        "skills": ["PHP", "Laravel", "JavaScript", "MySQL", "Backend", "Lua"],
        "interests": ["Web Dev", "Gaming"], "experience_level": "Mid-level",
        "looking_for": ["Just vibes"], "links": _links("phpphil", 1),
        "projects": [_project("Guild Board", ["PHP", "Lua"], "A raid planner for my gaming guild with a Lua addon that syncs sign-ups.")],
    },
    {
        "tier": "Mid Mogger", "username": "csharpchris", "full_name": "Chris Sharp",
        "avatar_url": _avatar("csharpchris"), "location": "Melbourne, AU", "education": "B.IT, RMIT",
        "bio": "Unity game developer making cozy games about plants, rain and slow afternoons. No combat, ever.",
        "favorite_ide": "Visual Studio", "favorite_ai_agents": ["Copilot"],
        "skills": ["C#", "Unity", "Game Dev", "C++"],
        "interests": ["Cozy Games", "Gardening"], "experience_level": "Junior",
        "looking_for": ["Hackathon team"], "links": _links("csharpchris", 1),
        "projects": [_project("Sprout", ["C#", "C++"], "A tiny game where you keep a houseplant alive by remembering to water it.")],
    },
    # ---------- 🐣 Junior Mogger (25–44): starting out, a project or two
    {
        "tier": "Junior Mogger", "username": "juniorjo", "full_name": "Jo Junior",
        "avatar_url": None, "location": "Nairobi, KE", "education": "Bootcamp graduate",
        "bio": "Just finished a web bootcamp. Building my portfolio one project at a time.",
        "favorite_ide": "VS Code", "favorite_ai_agents": ["ChatGPT"],
        "skills": ["HTML", "CSS", "JavaScript"],
        "interests": ["Web Dev", "Music"], "experience_level": "Junior",
        "looking_for": ["Mentor"], "links": [],
        "projects": [_project("My Portfolio", ["HTML", "CSS"], "My first website, built during week two.", url=False)],
    },
    {
        "tier": "Junior Mogger", "username": "studentstu", "full_name": "Stu Dent",
        "avatar_url": None, "location": "Lagos, NG", "education": "B.Sc. Computer Science (2nd year), UNILAG",
        "bio": "CS student learning Python and C. Chess club on Fridays, and always up for a study group.",
        "favorite_ide": "VS Code", "favorite_ai_agents": [],
        "skills": ["Python", "C", "Java"],
        "interests": ["Learning", "Chess"], "experience_level": "Student",
        "looking_for": ["Mentor", "Hackathon team"], "links": _links("studentstu", 1),
        "projects": [_project("Chess Clock", ["Python"], "A chess clock that runs in the terminal.", url=False)],
    },
    {
        "tier": "Junior Mogger", "username": "learnerlee", "full_name": "Lee Learner",
        "avatar_url": None, "location": "Cork, IE", "education": "B.Ed. Primary Education, University College Cork",
        "bio": "Former teacher, now learning React at night. Building tools I wish I had in the classroom.",
        "favorite_ide": "VS Code", "favorite_ai_agents": ["ChatGPT"],
        "skills": ["JavaScript", "React"],
        "interests": ["Education", "Teaching"], "experience_level": "Junior",
        "looking_for": ["Mentor"], "links": _links("learnerlee", 1),
        "projects": [_project("Flashcards", ["JavaScript"], "Flashcards I made for my old students.", url=False)],
    },
    {
        "tier": "Junior Mogger", "username": "copypasta", "full_name": "Cody Pasta",
        "avatar_url": None, "location": "Phoenix, AZ", "education": "Self-taught, mostly from forum threads",
        "bio": "Stack Overflow is my IDE. Ctrl+C, Ctrl+V, ship it.",
        "favorite_ide": "Notepad++", "favorite_ai_agents": ["ChatGPT"],
        "skills": ["JavaScript", "jQuery"],
        "interests": ["Memes", "Coffee"], "experience_level": "Junior",
        "looking_for": ["Just vibes"], "links": [],
        "projects": [_project("Todo App", ["JavaScript"], "Yet another todo app.", url=False)],
    },
    {
        "tier": "Junior Mogger", "username": "bootcampbea", "full_name": "Bea Camp",
        "avatar_url": _avatar("bootcampbea"), "location": "Madrid, ES", "education": "Ironhack Web Dev",
        "bio": "Week 8 of bootcamp. Send coffee and patience.",
        "favorite_ide": "VS Code", "favorite_ai_agents": [],
        "skills": ["HTML", "CSS"],
        "interests": ["Design", "Travel"], "experience_level": "Student",
        "looking_for": ["Mentor"], "links": _links("bootcampbea", 1),
        "projects": [_project("Landing Page", ["HTML", "CSS"], "A landing page for my mum's bakery in Madrid.", url=False)],
    },
    # ---------- 🥚 Hello World (0–24): nearly empty profiles
    {
        "tier": "Hello World", "username": "newbie", "full_name": "Nova Newbie",
        "avatar_url": None, "location": "Portland, OR", "education": "Intro to web development, community college",
        "bio": "Hello world! Just bought my first laptop and I'm ready to learn.", "favorite_ide": "Notepad", "favorite_ai_agents": [],
        "skills": ["HTML"], "interests": ["Learning", "Cats"], "experience_level": "Student",
        "looking_for": ["Mentor"], "links": [], "projects": [],
    },
    {
        "tier": "Hello World", "username": "lurker", "full_name": "Larry Lurker",
        "avatar_url": None, "location": "Chicago, IL", "education": None,
        "bio": "Just looking. Might say hi later.", "favorite_ide": "VS Code", "favorite_ai_agents": [],
        "skills": [], "interests": ["Reading", "Podcasts"], "experience_level": None,
        "looking_for": [], "links": [], "projects": [],
    },
    {
        "tier": "Hello World", "username": "printhello", "full_name": "Priya Print",
        "avatar_url": None, "location": "Delhi, IN", "education": "Intro to Python, online course",
        "bio": "print('hello')", "favorite_ide": "IDLE", "favorite_ai_agents": [],
        "skills": ["Python"], "interests": ["Learning", "Cooking"], "experience_level": "Student",
        "looking_for": [], "links": [], "projects": [],
    },
    {
        "tier": "Hello World", "username": "ghostdev", "full_name": "Ghost Dev",
        "avatar_url": None, "location": "Somewhere in the cloud", "education": None,
        "bio": "... boo.", "favorite_ide": "Vim", "favorite_ai_agents": [],
        "skills": [], "interests": ["Haunting", "Night owls"], "experience_level": None,
        "looking_for": ["Just vibes"], "links": [], "projects": [],
    },
    {
        "tier": "Hello World", "username": "firststep", "full_name": "Finn First",
        "avatar_url": None, "location": "Oslo, NO", "education": "Self-taught, one tutorial at a time",
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
_p = _project  # shorter name for the second batch


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
        "looking_for": ["Hackathon team", "Mentor"], "links": _links("hackhannah", 1),
        "projects": [_p("Petri Counter", ["Python"], "Counts bacteria colonies in a photo.", url=False)],
    },
    {
        "tier": "Junior Mogger", "username": "datadan", "full_name": "Dan Sheets",
        "avatar_url": None, "location": "Denver, CO", "education": "B.S. Accounting, Metropolitan State University of Denver",
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
        "avatar_url": None, "location": "Buenos Aires, AR", "education": "Technical diploma in IT support, Escuela ORT",
        "bio": "IT support tech automating the boring parts of my job with PowerShell.",
        "favorite_ide": "VS Code", "favorite_ai_agents": ["Copilot"],
        "skills": ["PowerShell", "Bash"],
        "interests": ["Automation"], "experience_level": "Junior",
        "looking_for": ["Mentor"], "links": _links("ittomas", 1),
        "projects": [_p("Reset Bot", ["PowerShell"], "Resets passwords without a ticket.", url=False)],
    },
    {
        "tier": "Junior Mogger", "username": "gamergus", "full_name": "Gus Level",
        "avatar_url": None, "location": "Montréal, CA", "education": "High school senior",
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
        "avatar_url": None, "location": "Wellington, NZ", "education": None,
        "bio": "Signed up five minutes ago.", "favorite_ide": "VS Code", "favorite_ai_agents": [],
        "skills": [], "interests": ["Learning", "Music"], "experience_level": None,
        "looking_for": ["Just vibes"], "links": [], "projects": [],
    },
    {
        "tier": "Hello World", "username": "codecurious", "full_name": "Cora Curious",
        "avatar_url": None, "location": "Vienna, AT", "education": "Curious about everything, degree pending",
        "bio": "What is a terminal? Asking for a friend (the friend is me).", "favorite_ide": "Notepad", "favorite_ai_agents": ["ChatGPT"],
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
        "avatar_url": None, "location": "Auckland, NZ", "education": "Learning alongside my 8-year-old",
        "bio": "Learning to code with my kid.", "favorite_ide": "Scratch", "favorite_ai_agents": [],
        "skills": ["JavaScript"], "interests": ["Family", "Scratch"], "experience_level": "Student",
        "looking_for": ["Just vibes"], "links": [], "projects": [],
    },
    {
        "tier": "Hello World", "username": "zeroxp", "full_name": "Zed Zero",
        "avatar_url": None, "location": "Spawn point", "education": None,
        "bio": "0 XP. Level 1. Grinding.", "favorite_ide": "VS Code", "favorite_ai_agents": [],
        "skills": ["CSS"], "interests": ["Games", "Anime"], "experience_level": "Student",
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


# The look of the accounts made by `flask seed` (the demo user and the sample developers), so they
# aren't plain default cards next to the test accounts. Same shape and rules as DEMO_THEMES, kept
# separate because `flask seed` is what every teammate and production runs.
SEED_THEMES: dict[str, dict] = {
    "jordan-dev": _theme("#0b1a33", "emoji", emojis=["🦊", "🚀", "🏆"], emoji_path="bounce", emoji_count=12),
    "mayacodes": _theme("#2b1020", "emoji", emojis=["🌸", "🎨", "✨"], emoji_path="wave", emoji_count=16, emoji_spin=2),
    "diego-rs": _theme("#1c0f06", "matrix", rain_color="#ff8a4c", rain_symbols="code", glow=True, speed=5),
    "priya-ml": _theme("#140f2e", "matrix", rain_color="#c4b5fd", rain_symbols="binary", brightness=45, speed=3),
    "samfullstack": _theme("#1c1a06", "market", chart_mood="bull", chart_palette="classic", chart_ticker="MVP", chart_volatility=5),
    "lena-gamedev": _theme("#08201a", "emoji", emojis=["🍄", "🎮", "👾"], emoji_path="bounce", emoji_count=14),
    "m-sec": _theme("#0a0f16", "slogans", slogans=["TRY HARDER", "ROOT OR BUST", "PATCH YOUR STUFF"],
                    slogan_color="#39ff88", slogan_style="outline", slogan_tilt=-12),
    "aisha-data": _theme("#06232b", "snow", snow_kind="dots", snow_count=90, snow_wind=-2),
    "kenji-mobile": _theme("#1f0c18", "emoji", emojis=["🗻", "🚄", "📱"], emoji_path="straight", emoji_angle=0, emoji_count=10),
    "liv-devops": _theme("#041b30", "emoji", emojis=["🐳", "☁️", "📦"], emoji_path="straight", emoji_angle=90, emoji_count=12),
    "noah-learns": _theme("#17112f", "emoji", emojis=["🐣", "🎧", "🦀"], emoji_path="wave", emoji_count=10),
}


# ---------------------------------------------------------------------------------------------
# Third batch: 10 accounts that show off the lightning, tron and shapes effects (existing accounts keep their looks).
# ---------------------------------------------------------------------------------------------
DEMO_USERS += [
    # ---------- 🔥 Senior Mogger
    {
        "tier": "Senior Mogger", "username": "stormsophie", "full_name": "Sophie Storm",
        "avatar_url": _avatar("stormsophie"), "location": "Wellington, NZ", "education": "B.Sc. Computer Science, Victoria University",
        "bio": "Reliability engineer who breaks things on purpose so customers never find out how. I run game days where a thunderstorm of "
               "failures hits staging all at once, and I only relax when the pager stays silent.",
        "favorite_ide": "GoLand", "favorite_ai_agents": ["Claude Code"],
        "skills": ["Go", "Rust", "Backend", "DevOps", "Cloud", "Kafka", "PostgreSQL"],
        "interests": ["Chaos Engineering", "Weather"], "experience_level": "Senior",
        "looking_for": ["Side project"], "links": _links("stormsophie", 2),
        "projects": [
            _p("Thunderclap", ["Go", "Rust"], "A chaos tool that strikes random services with realistic failures, slow disks, dropped packets and clock jumps, then writes a plain report of what survived."),
            _p("Lightning Rod", ["Go"], "Catches the first error in a cascade and points at it, so on-call engineers read one line instead of four hundred."),
        ],
    },
    {
        "tier": "Senior Mogger", "username": "gridgrace", "full_name": "Grace Grid",
        "avatar_url": _avatar("gridgrace"), "location": "Montréal, CA", "education": "B.Sc. Computer Science, McGill University",
        "bio": "Graphics engineer at a game studio. I make the neon look cheap and the frame time cheaper. After hours I write tiny "
               "light-cycle games and argue that every good arcade cabinet is a grid with opinions.",
        "favorite_ide": "CLion", "favorite_ai_agents": ["Cursor"],
        "skills": ["Rust", "C++", "GLSL", "WebGL", "Three.js", "Systems Programming", "C"],
        "interests": ["Game Engines", "Arcade Games"], "experience_level": "Senior",
        "looking_for": ["Hackathon team"], "links": _links("gridgrace", 2),
        "projects": [
            _p("Light Cycle Arena", ["Rust", "GLSL"], "A two-player light-cycle game that runs in the browser. Netcode, glowing trails and a replay mode that draws the whole match as one picture."),
            _p("Grid Shader Pack", ["GLSL"], "A pack of neon grid shaders that other studios drop into their own engines, with a live preview and presets named after eighties movies."),
        ],
    },
    # ---------- 🧑‍💻 Mid Mogger
    {
        "tier": "Mid Mogger", "username": "cubecarla", "full_name": "Carla Cube",
        "avatar_url": _avatar("cubecarla"), "location": "Barcelona, ES", "education": "B.Sc. Multimedia Engineering, UPF",
        "bio": "Frontend dev at a furniture company. I make 3D product viewers that spin smoothly on a six-year-old phone.",
        "favorite_ide": "VS Code", "favorite_ai_agents": ["Copilot"],
        "skills": ["TypeScript", "Three.js", "React", "Frontend", "WebGL", "Go"],
        "interests": ["3D", "Furniture"], "experience_level": "Mid-level",
        "looking_for": ["Side project"], "links": _links("cubecarla", 1),
        "projects": [_p("Cube Configurator", ["TypeScript", "Go"], "Lets shoppers rotate a bookshelf, swap its wood and see it in their room before they buy.")],
    },
    {
        "tier": "Mid Mogger", "username": "torustom", "full_name": "Tom Torus",
        "avatar_url": _avatar("torustom"), "location": "Portland, OR", "education": "B.S. Information Systems, Portland State",
        "bio": "Backend dev for a donut chain with forty shops. I keep the till, the fryer timers and the glaze inventory in sync.",
        "favorite_ide": "PyCharm", "favorite_ai_agents": ["ChatGPT"],
        "skills": ["Python", "SQL", "Backend", "PostgreSQL", "Go"],
        "interests": ["Donuts", "Inventory"], "experience_level": "Mid-level",
        "looking_for": ["Mentor", "Side project"], "links": _links("torustom", 1),
        "projects": [_p("Glaze Ledger", ["Python", "Go"], "Counts every donut sold per shop and predicts tomorrow's dough, so nobody sells out of the maple bar by nine.")],
    },
    {
        "tier": "Mid Mogger", "username": "tronteo", "full_name": "Teo Trace",
        "avatar_url": _avatar("tronteo"), "location": "Buenos Aires, AR", "education": "B.Sc. Systems Engineering, UTN",
        "bio": "Network engineer who thinks in packets and wishes every cable trace glowed. I automate the boring parts of running a data center.",
        "favorite_ide": "Vim", "favorite_ai_agents": ["Claude Code"],
        "skills": ["Go", "Bash", "Linux", "DevOps", "Docker", "Ruby"],
        "interests": ["Networks", "Retro Sci-Fi"], "experience_level": "Mid-level",
        "looking_for": ["Open source"], "links": _links("tronteo", 1),
        "projects": [_p("Packet Trails", ["Go", "Ruby"], "Draws the route a packet takes through our racks as a glowing trail, so a failing link is easy to spot.")],
    },
    # ---------- 🐣 Junior Mogger
    {
        "tier": "Junior Mogger", "username": "flashfin", "full_name": "Fin Flash",
        "avatar_url": _avatar("flashfin"), "location": "Reykjavík, IS", "education": "Web development diploma",
        "bio": "Junior web dev. Rare thunderstorms in Iceland, so I made my own.",
        "favorite_ide": "VS Code", "favorite_ai_agents": ["ChatGPT"],
        "skills": ["HTML", "CSS", "JavaScript"],
        "interests": ["Web Dev", "Weather"], "experience_level": "Junior",
        "looking_for": ["Mentor"], "links": [],
        "projects": [_p("Storm Page", ["HTML", "CSS"], "A weather page where the sky flashes when lightning is forecast.", url=False)],
    },
    {
        "tier": "Junior Mogger", "username": "cyclecallie", "full_name": "Callie Cycle",
        "avatar_url": _avatar("cyclecallie"), "location": "Copenhagen, DK", "education": "B.Sc. Computer Science (1st year), DTU",
        "bio": "CS student who commutes by bike and codes the rest. Learning Python with a route planner.",
        "favorite_ide": "VS Code", "favorite_ai_agents": [],
        "skills": ["Python", "C", "Java"],
        "interests": ["Cycling", "Maps"], "experience_level": "Student",
        "looking_for": ["Mentor", "Hackathon team"], "links": _links("cyclecallie", 1),
        "projects": [_p("Bike Lane Finder", ["Python"], "Finds the route with the most bike lanes between two addresses.", url=False)],
    },
    {
        "tier": "Junior Mogger", "username": "orbitorla", "full_name": "Orla Orbit",
        "avatar_url": _avatar("orbitorla"), "location": "Galway, IE", "education": "B.Sc. Physics (final year), University of Galway",
        "bio": "Physics student learning to code planets. Everything I write ends up orbiting something.",
        "favorite_ide": "VS Code", "favorite_ai_agents": ["ChatGPT"],
        "skills": ["Python", "Data Science", "R"],
        "interests": ["Space", "Physics"], "experience_level": "Student",
        "looking_for": ["Mentor"], "links": _links("orbitorla", 1),
        "projects": [_p("Tiny Solar System", ["Python"], "Simulates six planets orbiting a star.", url=False)],
    },
    # ---------- 🥚 Hello World
    {
        "tier": "Hello World", "username": "sparkysid", "full_name": "Sid Spark",
        "avatar_url": _avatar("sparkysid"), "location": "Mumbai, IN", "education": None,
        "bio": "First week of learning to code.", "favorite_ide": "VS Code", "favorite_ai_agents": [],
        "skills": ["HTML"], "interests": ["Learning"], "experience_level": "Student",
        "looking_for": ["Mentor"], "links": [], "projects": [],
    },
    {
        "tier": "Hello World", "username": "wireframewes", "full_name": "Wes Wireframe",
        "avatar_url": _avatar("wireframewes"), "location": "Denver, CO", "education": "Self-taught",
        "bio": "Drawing boxes. Soon, coding them.", "favorite_ide": "Notepad", "favorite_ai_agents": [],
        "skills": ["CSS"], "interests": ["Design"], "experience_level": "Student",
        "looking_for": [], "links": [], "projects": [],
    },
]

DEMO_THEMES.update({
    # 🔥 Senior Mogger
    "stormsophie": _theme("#0a1228", "lightning", lightning_color="#9ec5ff", lightning_strikes=10, lightning_forks=10, size=16,
                          brightness=70, glow=True),  # a storm overhead
    "gridgrace": _theme("#05121f", "tron", tron_color="#22d3ee", tron_cycles=6, tron_tail=7, tron_grid=True, size=14, speed=6,
                        brightness=55, glow=True),
    # 🧑‍💻 Mid Mogger
    "cubecarla": _theme("#0e1022", "shapes", shape_kind="cube", shape_count=1, shape_color="#38bdf8", size=36, speed=3, brightness=60, glow=True),
    "torustom": _theme("#1a0f0a", "shapes", shape_kind="torus", shape_count=3, shape_color="#fb923c", size=20, speed=5, brightness=60),  # donuts
    "tronteo": _theme("#071a0f", "tron", tron_color="#ff7a3d", tron_cycles=1, tron_tail=10, tron_grid=False, size=18, speed=4, brightness=60),
    # 🐣 Junior Mogger
    "flashfin": _theme("#120a1e", "lightning", lightning_color="#ffd84a", lightning_strikes=1, lightning_forks=0, lightning_flash=False,
                       size=12, speed=3, brightness=50),  # one clean bolt now and then
    "cyclecallie": _theme("#0c1a1a", "tron", tron_color="#a3ff12", tron_cycles=3, tron_tail=2, size=22, speed=7, brightness=50),
    "orbitorla": _theme("#0d0d1a", "shapes", shape_kind="sphere", shape_count=6, shape_color="#a78bfa", size=12, speed=2, brightness=55),  # six planets
    # 🥚 Hello World
    "sparkysid": _theme("#1a1a08", "lightning", lightning_color="#fff2a8", lightning_strikes=3, lightning_forks=3, size=10, brightness=40),
    "wireframewes": _theme("#101820", "shapes", shape_kind="cube", shape_count=6, shape_color="#e2e8f0", size=10, speed=6, brightness=35),
})
