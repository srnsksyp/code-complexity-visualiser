# Code Complexity Visualizer

A deterministic, production-grade web application for Python static code complexity analysis, AST structural flow visualization, and theoretical asymptotic growth modeling.

---

## Overview

**Code Complexity Visualizer** parses user-submitted Python code safely into an Abstract Syntax Tree (AST), statically inspects nested loops, recursive branches, container allocations, and operations, and derives:
- **Time Complexity** (e.g., $\mathcal{O}(1)$, $\mathcal{O}(\log n)$, $\mathcal{O}(n)$, $\mathcal{O}(n \log n)$, $\mathcal{O}(n^2)$, $\mathcal{O}(n^3)$, $\mathcal{O}(2^n)$)
- **Auxiliary Space Complexity** (e.g., $\mathcal{O}(1)$, $\mathcal{O}(\log n)$, $\mathcal{O}(n)$, $\mathcal{O}(n^2)$)
- **Static Confidence Level** (`HIGH`, `MEDIUM`, `LOW`)
- **Step-by-step Mathematical Reasoning**
- **AST Control Flow & Hierarchy Graph** (rendered dynamically using React Flow)
- **Theoretical Asymptotic Growth Curves** (rendered with Recharts)
- **Rule-based Optimization Suggestions**

> **Zero Mock Data & No Arbitrary Execution**: Analysis is generated strictly via Python AST static analysis without running user code (`eval`/`exec` are strictly forbidden).

---

## System Architecture

```
code-complexity/
├── backend/
│   ├── alembic/              # Database migration environments & revisions
│   ├── alembic.ini           # Alembic migration configuration
│   ├── app/
│   │   ├── analyzers/        # Core static analysis engines
│   │   │   ├── ast_parser.py          # Safe AST parsing & syntax error boundaries
│   │   │   ├── loop_analyzer.py       # For/While loop nesting, step & halving
│   │   │   ├── recursion_analyzer.py  # Branching factor, depth & Master theorem
│   │   │   ├── operation_analyzer.py  # Allocations, container costs, pitfalls
│   │   │   ├── structure_analyzer.py  # Graph nodes/edges & AST statistics
│   │   │   └── complexity_analyzer.py # Asymptotic synthesis & Big-O derivation
│   │   ├── api/
│   │   │   └── routes/       # API endpoints (/analyze, /history, /health)
│   │   ├── core/             # Configuration & environment variable settings
│   │   ├── db/               # SQLAlchemy 2.x engine & session management
│   │   ├── models/           # Relational models (User, Project, Submission, Result)
│   │   ├── schemas/          # Pydantic v2 validation models
│   │   ├── services/         # Analysis orchestration & DB persistence
│   │   └── main.py           # FastAPI application entrypoint
│   ├── tests/                # Pytest comprehensive test suite (17 tests)
│   ├── conftest.py
│   └── requirements.txt
├── frontend/
│   ├── app/                  # Next.js App Router (page.tsx, layout.tsx, globals.css)
│   ├── components/           # UI components
│   │   ├── CodeEditor.tsx         # Monaco Editor with hotkeys & presets
│   │   ├── ComplexityOverview.tsx # Metric badges (Time, Space, Confidence)
│   │   ├── StatisticsGrid.tsx     # Counters for loops, depth, functions, etc.
│   │   ├── ComplexityChart.tsx    # Recharts comparative Big-O growth curves
│   │   ├── StructureFlow.tsx      # React Flow interactive AST graph
│   │   ├── ReasoningPanel.tsx     # Explanations & optimization hints
│   │   ├── HistoryDrawer.tsx      # Past analysis browser & restore
│   │   ├── ReportModal.tsx        # Exportable Markdown analysis report
│   │   └── Navbar.tsx             # Header with live engine status indicator
│   ├── lib/                  # API client & sample algorithm library
│   ├── types/                # TypeScript type definitions
│   └── package.json
├── .env.example              # Environment variables template
├── .gitignore
└── README.md
```

---

## Technology Stack

### Backend
- **Language**: Python 3.14 / 3.11+
- **API Framework**: FastAPI
- **Data Validation**: Pydantic v2 & Pydantic-Settings
- **ORM**: SQLAlchemy 2.x
- **Database Migrations**: Alembic
- **PostgreSQL Driver**: Psycopg 3 (`psycopg[binary]`)
- **Server**: Uvicorn
- **Testing**: Pytest & HTTPX

### Frontend
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript 5
- **UI Library**: React 19
- **Styling**: Tailwind CSS v4
- **Code Editor**: Monaco Editor (`@monaco-editor/react`)
- **Visual Graphs**: React Flow (`@xyflow/react`)
- **Mathematical Charts**: Recharts
- **Icons**: Lucide React

### Database
- **Primary / Production**: Supabase PostgreSQL (via `postgresql+psycopg://...`)
- **Local Fallback**: SQLite (`sqlite+pysqlite:///./complexity.db`)

---

## Quickstart & Local Setup

### 1. Prerequisites
- Python 3.11+ (tested with Python 3.14)
- Node.js 20+ (tested with Node.js v24)
- npm 10+

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations with Alembic
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```
Backend will be available at: `http://localhost:8000` (API documentation at `http://localhost:8000/docs`).

### 3. Frontend Setup

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```
Frontend will be available at: `http://localhost:3000`.

---

## Supabase PostgreSQL Configuration

To connect the application to a hosted Supabase PostgreSQL instance:

1. Copy `.env.example` to `backend/.env`:
   ```bash
   cp .env.example backend/.env
   ```
2. Update `DATABASE_URL` with your Supabase connection string using the `psycopg` driver scheme:
   ```env
   DATABASE_URL=postgresql+psycopg://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```
3. Run Alembic migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```
4. Verify the database tables (`users`, `projects`, `code_submissions`, `analysis_results`) in your Supabase dashboard table editor.

---

## Static Complexity Rules & Detection Capabilities

| Pattern | Detected Static Clues | Derived Complexity |
| :--- | :--- | :--- |
| **Sequential Operations** | No loops or recursion, scalar variables | $\mathcal{O}(1)$ Time, $\mathcal{O}(1)$ Space |
| **Single Loop** | `for i in range(n)` or `for x in arr:` | $\mathcal{O}(n)$ Time, $\mathcal{O}(1)$ Space |
| **Sequential Loops** | Independent loops at same level | $\mathcal{O}(n)$ Time (Additive $\max$) |
| **Halving While Loop** | `while n > 1: n //= 2` or `n >>= 1` | $\mathcal{O}(\log n)$ Time, $\mathcal{O}(1)$ Space |
| **Binary Search** | Pointer convergence `mid = (low+high)//2` | $\mathcal{O}(\log n)$ Time, $\mathcal{O}(1)$ Space |
| **Nested Loops** | Two nested loops over input $n$ | $\mathcal{O}(n^2)$ Time |
| **Multi-variable Loops**| Outer loop over $n$, inner loop over $m$ | $\mathcal{O}(n \times m)$ Time |
| **Triple Nested Loops** | Three nested loops over input $n$ | $\mathcal{O}(n^3)$ Time |
| **Linear Recursion** | Single self-call with linear decrement | $\mathcal{O}(n)$ Time, $\mathcal{O}(n)$ Stack Space |
| **Branching Recursion**| Multiple self-calls per frame (e.g. Fibonacci)| $\mathcal{O}(2^n)$ Time, $\mathcal{O}(n)$ Stack Space |
| **Divide-and-Conquer** | Halved subproblems + linear merge | $\mathcal{O}(n \log n)$ Time |
| **Buffer Allocation** | `arr = [0] * n` | $\mathcal{O}(n)$ Auxiliary Space |
| **Matrix Allocation** | `[[0] * n for _ in range(n)]` | $\mathcal{O}(n^2)$ Auxiliary Space |

---

## Running Automated Tests

Run backend tests using Pytest:

```bash
cd backend
pytest -v
```

The test suite exercises:
- $\mathcal{O}(1)$ scalar code
- $\mathcal{O}(n)$ linear loops
- $\mathcal{O}(n^2)$ quadratic nested loops
- $\mathcal{O}(n^3)$ cubic nested loops
- $\mathcal{O}(n) + \mathcal{O}(n) = \mathcal{O}(n)$ sequential loops
- $\mathcal{O}(\log n)$ halving while loops
- Binary search pointer updates
- Linear & branching recursion ($\mathcal{O}(2^n)$)
- Linear & matrix auxiliary space allocations
- Graceful syntax error reporting (line, column, message)
- FastAPI endpoints (`/api/health`, `/api/analyze`, `/api/history`)

---

## Security & Reliability

- **No Code Execution**: User code is strictly parsed by Python's `ast.parse` into AST data nodes. `exec` and `eval` are never called.
- **Request Size Boundaries**: Enforces configurable maximum byte sizes (100KB) and line limits (3,000 lines) to prevent denial of service.
- **Error Sandboxing**: Syntax and parsing errors are intercepted and returned as clean JSON responses without exposing internal server stack traces.
- **Credential Hygiene**: Connection strings are retrieved from environment variables; `.env` is ignored by Git.

---

## Complexity Analysis Limitations

Static AST analysis operates on program syntax. In accordance with the Halting Problem and Rice's Theorem:
1. Loops with data-dependent early exits (e.g. `break` on random inputs) are estimated according to their worst-case static bounds.
2. Complex non-linear recurrences without recognizable divide-and-conquer structures are explicitly flagged with `MEDIUM` or `LOW` confidence.
3. Dynamically generated code (`exec`, `eval`) cannot be analyzed statically.
