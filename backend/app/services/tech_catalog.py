"""Known languages, frameworks and developer tools for project technologies.

Lookups ignore case, spaces, dots, hyphens and underscores, so "nodejs", "Node JS" and
"node.js" all resolve to "Node.js". Add new entries to the matching category; add common
nicknames to ALIASES.
"""

import re

TECH_CATALOG: dict[str, list[str]] = {
    # Broad areas people list as skills (and filter Discover by).
    "specialties": [
        "Frontend", "Backend", "Full-stack", "Mobile", "Machine Learning", "AI", "Data Science",
        "Data Engineering", "DevOps", "Cloud", "Security", "Reverse Engineering", "Game Dev",
        "Embedded", "Systems Programming", "Networking", "Robotics", "AR/VR", "Blockchain",
        "UI/UX Design", "QA", "Technical Writing",
    ],
    "languages": [
        "Ada", "Assembly", "Bash", "C", "C#", "C++", "Clojure", "COBOL", "CoffeeScript",
        "Crystal", "CSS", "Dart", "Elixir", "Elm", "Erlang", "F#", "Fortran", "GDScript",
        "GLSL", "Go", "GraphQL", "Groovy", "Haskell", "HCL", "HLSL", "HTML", "Java",
        "JavaScript", "Julia", "Kotlin", "Lisp", "Lua", "MATLAB", "Mojo", "Nim", "Objective-C",
        "OCaml", "Pascal", "Perl", "PHP", "PowerShell", "Prolog", "Python", "R", "Racket",
        "Ruby", "Rust", "Sass", "Scala", "Scheme", "Shell", "Solidity", "SQL", "Swift",
        "TypeScript", "V", "VB.NET", "Verilog", "VHDL", "WebAssembly", "Zig",
    ],
    "frontend": [
        "Alpine.js", "Angular", "Astro", "Bootstrap", "Chakra UI", "D3.js", "Ember.js",
        "Gatsby", "htmx", "jQuery", "Less", "Lit", "Material UI", "Next.js", "Nuxt",
        "Preact", "Qwik", "Radix UI", "React", "React Router", "Redux", "Remix", "shadcn/ui",
        "Solid.js", "Styled Components", "Svelte", "SvelteKit", "Tailwind CSS", "Three.js",
        "TanStack Query", "Vue", "WebGL", "WebGPU", "Web Audio API", "Zustand",
    ],
    "backend": [
        ".NET", "ASP.NET Core", "Actix", "Axum", "Bun", "CakePHP", "Deno", "Django",
        "Django REST Framework", "Echo", "Elysia", "Express", "FastAPI", "Fastify", "Fiber",
        "Flask", "Gin", "gRPC", "Hapi", "Hono", "Koa", "Ktor", "Laravel", "Micronaut",
        "NestJS", "Node.js", "Phoenix", "Quarkus", "Rails", "Rocket", "Sinatra", "Spring",
        "Spring Boot", "Symfony", "tRPC", "Tokio", "Tornado", "Vapor",
    ],
    "mobile_desktop": [
        "Android", "Capacitor", "Compose Multiplatform", "Electron", "Expo", "Flutter",
        "Ionic", "Jetpack Compose", "Kotlin Multiplatform", ".NET MAUI", "React Native",
        "SwiftUI", "Tauri", "UIKit", "WPF", "Xamarin", "iOS",
    ],
    "game_graphics": [
        "Bevy", "Blender", "Defold", "GameMaker", "Godot", "LibGDX", "Love2D", "MonoGame",
        "OpenGL", "Phaser", "Pygame", "Raylib", "SDL", "Unity", "Unreal Engine", "Vulkan",
        "DirectX", "Metal",
    ],
    "data_ml_ai": [
        "Airflow", "Apache Beam", "Apache Flink", "Apache Kafka", "Apache Spark", "dbt",
        "Dagster", "Hugging Face", "JAX", "Jupyter", "Keras", "LangChain", "LlamaIndex",
        "LLMs", "Matplotlib", "MLflow", "NumPy", "OpenCV", "Pandas", "Polars", "Prefect",
        "PyTorch", "scikit-learn", "SciPy", "Seaborn", "spaCy", "Streamlit", "TensorFlow",
        "Transformers", "Weights & Biases", "XGBoost", "Claude API", "OpenAI API",
        "Gemini API", "Ollama", "Gradio", "Plotly", "Tableau", "Power BI", "Snowflake",
        "Databricks", "BigQuery",
    ],
    "databases": [
        "Cassandra", "ClickHouse", "CockroachDB", "Couchbase", "DuckDB", "DynamoDB",
        "Elasticsearch", "Firebase", "Firestore", "InfluxDB", "MariaDB", "Memcached",
        "MongoDB", "MySQL", "Neo4j", "OpenSearch", "Oracle Database", "pgvector",
        "Pinecone", "PlanetScale", "PostgreSQL", "Prisma", "Qdrant", "Redis", "SQLAlchemy",
        "SQL Server", "SQLite", "Supabase", "TimescaleDB", "Turso", "Weaviate", "Chroma",
        "Drizzle", "Sequelize", "TypeORM", "Mongoose", "Entity Framework", "Hibernate",
    ],
    "cloud_devops": [
        "Ansible", "Argo CD", "AWS", "AWS Lambda", "Azure", "Cloudflare",
        "Cloudflare Workers", "CircleCI", "DigitalOcean", "Docker", "Docker Compose",
        "eBPF", "Fly.io", "GitHub Actions", "GitLab CI", "Google Cloud", "Grafana", "Helm",
        "Heroku", "Istio", "Jenkins", "Kubernetes", "Linux", "Netlify", "Nginx",
        "OpenTelemetry", "Podman", "Prometheus", "Pulumi", "RabbitMQ", "Railway", "Render",
        "Sentry", "Serverless Framework", "Terraform", "Traefik", "Vercel", "Datadog",
        "Apache", "Caddy", "Consul", "Vault", "Nomad",
    ],
    "testing": [
        "Cypress", "Jest", "JUnit", "Mocha", "Playwright", "pytest", "RSpec", "Selenium",
        "Storybook", "Testing Library", "Vitest", "Postman", "k6", "Chai", "xUnit", "NUnit",
    ],
    "build_package": [
        "Babel", "Bazel", "CMake", "Cargo", "Composer", "Gradle", "Make", "Maven", "npm",
        "pip", "pnpm", "Poetry", "Rollup", "esbuild", "Turborepo", "Nx", "uv", "Vite",
        "Webpack", "Yarn", "Conda", "NuGet", "Homebrew", "Nix", "Parcel", "SWC", "Biome",
        "ESLint", "Prettier", "Ruff", "Black", "mypy",
    ],
    "dev_tools": [
        "Git", "GitHub", "GitLab", "Bitbucket", "VS Code", "Visual Studio", "IntelliJ IDEA",
        "PyCharm", "WebStorm", "JetBrains Rider", "CLion", "GoLand", "Android Studio",
        "Xcode", "Neovim", "Vim", "Emacs", "Zed", "Cursor", "Sublime Text", "Eclipse",
        "Claude Code", "GitHub Copilot", "Codex", "Windsurf", "Figma", "Jira", "Notion",
        "Linear", "Slack API", "Discord API", "Swagger", "OpenAPI", "Insomnia",
        "Chrome DevTools", "tmux", "WSL",
    ],
    "apis_protocols": [
        "REST", "WebSockets", "WebRTC", "Socket.IO", "OAuth", "JWT", "MQTT", "Protocol Buffers",
        "Server-Sent Events", "Stripe", "Twilio", "Auth0", "Clerk", "Mapbox", "SignalR",
    ],
    "embedded_hardware": [
        "Arduino", "ESP32", "FPGA", "FreeRTOS", "Raspberry Pi", "STM32", "Zephyr", "ROS",
        "PlatformIO",
    ],
    "web3": ["Ethereum", "Foundry", "Hardhat", "Solana", "Web3.js", "Ethers.js", "IPFS"],
}

# Nicknames and common alternate spellings -> canonical name.
ALIASES: dict[str, str] = {
    "fe": "Frontend", "be": "Backend", "fullstackdevelopment": "Full-stack", "ml": "Machine Learning",
    "ai/ml": "Machine Learning", "artificialintelligence": "AI", "datascience": "Data Science",
    "dataeng": "Data Engineering", "cybersecurity": "Security", "infosec": "Security",
    "appsec": "Security", "gamedevelopment": "Game Dev", "embeddedsystems": "Embedded",
    "vr": "AR/VR", "ar": "AR/VR", "web3": "Blockchain", "ux": "UI/UX Design", "uiux": "UI/UX Design",
    "uidesign": "UI/UX Design", "uxdesign": "UI/UX Design", "testing": "QA", "sre": "DevOps",
    "js": "JavaScript", "ts": "TypeScript", "py": "Python", "golang": "Go", "rb": "Ruby",
    "cpp": "C++", "cplusplus": "C++", "csharp": "C#", "fsharp": "F#", "objc": "Objective-C",
    "html5": "HTML", "css3": "CSS", "scss": "Sass", "wasm": "WebAssembly", "sh": "Shell",
    "node": "Node.js", "reactjs": "React", "vuejs": "Vue", "vue3": "Vue", "angularjs": "Angular",
    "nuxtjs": "Nuxt", "sveltejs": "Svelte", "solid": "Solid.js", "tailwind": "Tailwind CSS",
    "mui": "Material UI", "threejs": "Three.js", "d3": "D3.js", "expressjs": "Express",
    "nest": "NestJS", "rubyonrails": "Rails", "ror": "Rails", "springframework": "Spring",
    "dotnet": ".NET", "aspnet": "ASP.NET Core", "aspnetcore": "ASP.NET Core", "maui": ".NET MAUI",
    "rn": "React Native", "postgres": "PostgreSQL", "psql": "PostgreSQL", "mongo": "MongoDB",
    "mssql": "SQL Server", "elastic": "Elasticsearch", "k8s": "Kubernetes", "gcp": "Google Cloud",
    "googlecloudplatform": "Google Cloud", "amazonwebservices": "AWS", "lambda": "AWS Lambda",
    "gha": "GitHub Actions", "kafka": "Apache Kafka", "spark": "Apache Spark", "pyspark": "Apache Spark",
    "flink": "Apache Flink", "sklearn": "scikit-learn", "tf": "TensorFlow", "torch": "PyTorch",
    "huggingface": "Hugging Face", "hf": "Hugging Face", "wandb": "Weights & Biases",
    "llm": "LLMs", "openai": "OpenAI API", "claude": "Claude API", "anthropic": "Claude API",
    "unreal": "Unreal Engine", "ue5": "Unreal Engine", "ue4": "Unreal Engine", "love": "Love2D",
    "vscode": "VS Code", "visualstudiocode": "VS Code", "intellij": "IntelliJ IDEA",
    "nvim": "Neovim", "rider": "JetBrains Rider", "copilot": "GitHub Copilot",
    "websocket": "WebSockets", "socketio": "Socket.IO", "protobuf": "Protocol Buffers",
    "grpcweb": "gRPC", "sse": "Server-Sent Events", "rpi": "Raspberry Pi", "eth": "Ethereum",
    "tanstackreactquery": "TanStack Query", "reactquery": "TanStack Query", "dockercompose": "Docker Compose",
    "ghactions": "GitHub Actions", "rest api": "REST", "restapi": "REST", "restful": "REST",
}

_SEPARATORS = re.compile(r"[\s._\-]+")


def _key(name: str) -> str:
    """Comparison key: lowercase with spaces, dots, hyphens and underscores removed."""
    return _SEPARATORS.sub("", name.strip().lower())


ALL_TECHNOLOGIES: frozenset[str] = frozenset(t for techs in TECH_CATALOG.values() for t in techs)

_LOOKUP: dict[str, str] = {_key(tech): tech for tech in ALL_TECHNOLOGIES}
_LOOKUP.update({_key(alias): canonical for alias, canonical in ALIASES.items()})


def normalize_technology(name: str) -> str | None:
    """Return the catalog spelling for `name`, or None if it isn't a known technology."""
    return _LOOKUP.get(_key(name))
