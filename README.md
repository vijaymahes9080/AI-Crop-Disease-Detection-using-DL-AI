# AgroVision AI — Crop Disease Detection Platform

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![React Version](https://img.shields.io/badge/react-18.2-cyan.svg)](https://react.dev/)
[![Vite Version](https://img.shields.io/badge/vite-5.0-purple.svg)](https://vitejs.dev/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

AgroVision AI is a production-ready, edge-optimized crop disease detection platform that empowers smallholder farmers and extension officers with real-time deep learning diagnostics. Utilizing a hybrid cloud/edge computing architecture, the application provides classification, severity estimation, and localized treatment recommendations both online and offline.

This codebase is configured to run fully on a local Python Virtual Environment and Vite dev server, avoiding Docker overhead for simpler deployment and testing.

---

## 📖 Architectural Blueprint & Implementation Specs

The entire enterprise architecture, implementation codebase structures, and data schemas are split into targeted engineering specification documents:

| Specification Document | Purpose & Core Focus | Clickable File Reference |
| :--- | :--- | :--- |
| **Product Requirement Document (PRD)** | Objective, success metrics (KPIs), target users, in-the-wild field constraints, and competitive analysis. | [AgroVision_AI_PRD.md](file:///d:/current%20project/AI%20Crop%20Disease%20Detection%20using%20DL%20&%20AI/md%20files/AgroVision_AI_PRD.md) |
| **Enterprise Architecture (HLD/LLD)** | Overall topology, sequence data flows, gRPC interface contracts, component boundaries, and directory layout blueprints. | [AgroVision_AI_Enterprise_Architecture.md](file:///d:/current%20project/AI%20Crop%20Disease%20Detection%20using%20DL%20&%20AI/md%20files/AgroVision_AI_Enterprise_Architecture.md) |
| **UI/UX Design System** | WCAG AA accessible dark mode color palette design tokens, page wireframes, and camera centering overlays. | [AgroVision_AI_UI_UX_Design_System.md](file:///d:/current%20project/AI%20Crop%20Disease%20Detection%20using%20DL%20&%20AI/md%20files/AgroVision_AI_UI_UX_Design_System.md) |
| **Production Database Design** | Relational schemas (DDL), primary and spatial PostGIS GIST indexes, partitioning playbooks, and materialized views query optimizations. | [AgroVision_AI_Database_Design.md](file:///d:/current%20project/AI%20Crop%20Disease%20Detection%20using%20DL%20&%20AI/md%20files/AgroVision_AI_Database_Design.md) |
| **Data Processing Pipeline** | Image checking and metadata stripping routines, 70/15/15 partitions split scripts, Albumentations configurations, and DVC steps. | [AgroVision_AI_Data_Pipeline.md](file:///d:/current%20project/AI%20Crop%20Disease%20Detection%20using%20DL%20&%20AI/md%20files/AgroVision_AI_Data_Pipeline.md) |
| **ML Model Development** | Custom CNN model implementations, PyTorch training/auto-save loops, best checkpoint serialization, and evaluation metrics scripts. | [AgroVision_AI_Model_Development.md](file:///d:/current%20project/AI%20Crop%20Disease%20Detection%20using%20DL%20&%20AI/md%20files/AgroVision_AI_Model_Development.md) |
| **Model Interpretability (Explainability)** | Grad-CAM activation heatmaps extraction layers, SHAP GradientExplainer scripts, FastAPI endpoint, and React blend slider integration components. | [AgroVision_AI_Explainability.md](file:///d:/current%20project/AI%20Crop%20Disease%20Detection%20using%20DL%20&%20AI/md%20files/AgroVision_AI_Explainability.md) |
| **Backend Implementation** | FastAPI routers, OAuth2 JWT auth modules, Pydantic inputs/outputs validation decorators, and test files using PyTest. | [AgroVision_AI_Backend_Implementation.md](file:///d:/current%20project/AI%20Crop%20Disease%20Detection%20using%20DL%20&%20AI/md%20files/AgroVision_AI_Backend_Implementation.md) |
| **Frontend Implementation** | React client AuthProvider contexts, custom geolocation/camera hooks, CameraUpload scan overlay components, and SPA pages. | [AgroVision_AI_Frontend_Implementation.md](file:///d:/current%20project/AI%20Crop%20Disease%20Detection%20using%20DL%20&%20AI/md%20files/AgroVision_AI_Frontend_Implementation.md) |
| **End-to-End System Integration** | Auto-retry client wrappers, state machine React hooks, offline sync queues, and backend to AI engine wrappers. | [AgroVision_AI_Integration_Spec.md](file:///d:/current%20project/AI%20Crop%20Disease%20Detection%20using%20DL%20&%20AI/md%20files/AgroVision_AI_Integration_Spec.md) |
| **Remedy Recommendation Engine** | JSON knowledge base configurations, weather-aware risk scoring filters, treatments endpoint, and tabbed guide components. | [AgroVision_AI_Recommendation_System.md](file:///d:/current%20project/AI%20Crop%20Disease%20Detection%20using%20DL%20&%20AI/md%20files/AgroVision_AI_Recommendation_System.md) |
| **Analytics & Data Export** | SQL aggregates routers, CSV reports generation, and React SVG metric charting templates. | [AgroVision_AI_Analytics.md](file:///d:/current%20project/AI%20Crop%20Disease%20Detection%20using%20DL%20&%20AI/md%20files/AgroVision_AI_Analytics.md) |
| **Edge Optimization** | PyTorch to ONNX graph exports, full integer INT8 converters, Kotlin bindings, and tflite_runtime scripts. | [AgroVision_AI_Edge_Optimization.md](file:///d:/current%20project/AI%20Crop%20Disease%20Detection%20using%20DL%20&%20AI/md%20files/AgroVision_AI_Edge_Optimization.md) |
| **Testing & Verification Framework** | PyTest unit cases, mock database tests, Locust files, security traversal audits, and automated shells. | [AgroVision_AI_Testing_Framework.md](file:///d:/current%20project/AI%20Crop%20Disease%20Detection%20using%20DL%20&%20AI/md%20files/AgroVision_AI_Testing_Framework.md) |
| **Production Pre-Flight Checklist** | EKS deployments manifests, Prometheus metrics targets configs, S3 bucket access policies, and build registries commands. | [AgroVision_AI_Production_Checklist.md](file:///d:/current%20project/AI%20Crop%20Disease%20Detection%20using%20DL%20&%20AI/md%20files/AgroVision_AI_Production_Checklist.md) |
| **Agriculture AI Scaling Roadmap** | Phased plans covering satellite analytics pipelines, drone segmenters, RAG chatbot helpers, and Multi-Agent structures. | [AgroVision_AI_Agriculture_AI_Platform_Roadmap.md](file:///d:/current%20project/AI%20Crop%20Disease%20Detection%20using%20DL%20&%20AI/md%20files/AgroVision_AI_Agriculture_AI_Platform_Roadmap.md) |

---

## 🛠️ Core Technology Stack

- **Frontend client:** React 18.2 (Vite) + Tailwind CSS (including glassmorphism & accessibility tokens)
- **Backend API:** FastAPI (Asynchronous Python framework)
- **Database Engine:** SQLite (Local development/mock) / PostgreSQL (Production relational & geolocational index)
- **Task Worker Pipeline:** Celery + Redis (Background geofencing audits and SMS alerts queue)
- **Deep Learning Suite:** PyTorch (Capable of running on local CPU mock mode automatically when PyTorch is not installed)

---

## 📁 Repository Directory Structure

```
AI Crop Disease Detection using DL & AI/
├── AgroVision_AI_PRD.md                     # Product Requirement Document
├── AgroVision_AI_Enterprise_Architecture.md # Enterprise Architecture Blueprint
├── AgroVision_AI_UI_UX_Design_System.md     # Graphic layout wireframes
├── AgroVision_AI_Database_Design.md         # DDL Database layouts
├── AgroVision_AI_Data_Pipeline.md           # DVC pipeline orchestration
├── AgroVision_AI_Model_Development.md       # PyTorch model configurations
├── AgroVision_AI_Explainability.md          # Grad-CAM heatmap hooks
├── AgroVision_AI_Backend_Implementation.md  # FastAPI routers & JWT auth
├── AgroVision_AI_Frontend_Implementation.md # React contexts & camera hooks
├── AgroVision_AI_Integration_Spec.md        # Axios auto-retry & sync queue config
├── AgroVision_AI_Recommendation_System.md   # Agronomic remedies & risk engine
├── AgroVision_AI_Analytics.md               # DB statistics routers & CSV exports
├── AgroVision_AI_Edge_Optimization.md       # ONNX export & INT8 TFLite converters
├── AgroVision_AI_Testing_Framework.md       # PyTest suites & Locust load files
├── AgroVision_AI_Production_Checklist.md    # EKS deployment YAMLs & preflight audits
├── AgroVision_AI_Agriculture_AI_Platform_Roadmap.md # Satellite, Drone & Agentic roadmap
├── README.md                                # Root Guide Document
│
├── agrovision-frontend/                     # React Client SPA (Vite + Tailwind)
│   ├── src/
│   │   ├── components/                      # Common UI elements
│   │   ├── context/                         # AuthContext provider
│   │   ├── features/                        # Feature modules (Diagnostics: Camera, Heatmap, Remedies)
│   │   ├── hooks/                           # Custom hooks (useCamera, useGeoLocation)
│   │   ├── pages/                           # Screen Pages (Dashboard, Profile, Analytics)
│   │   └── services/                        # Axios API client setup
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── nginx.conf                       # Production Nginx reverse-proxy setup
│
├── agrovision-backend/                      # FastAPI Application API Server
│   ├── app/
│   │   ├── api/                             # Routers (Auth, Scans, Treatments, Analytics)
│   │   ├── core/                            # Celery configuration
│   │   ├── models/                          # SQLAlchemy relational database mapping
│   │   ├── schemas/                         # Pydantic validation schemas
│   │   ├── services/                        # Business logic helpers (S3, recommendations, exports)
│   │   └── tasks/                           # Celery geofencing/notification workers
│   ├── requirements.txt
│   └── alembic.ini                      # Database migrations
│
└── agrovision-ml/                           # Deep Learning pipeline
    ├── training/                            # EfficientNet model and training scripts
    ├── inference/                           # Custom TorchServe handlers
    └── scripts/                             # ONNX compile & INT8 TFLite conversion scripts
```

---

## 🚀 Getting Started (Local Development)

Follow these directions to run both the FastAPI backend and the React Vite client on your local computer.

### Step 1: Environment Setup & Python Virtual Environment
First, ensure you have Python 3.11+ installed. Create and activate a local virtual environment in the workspace root:

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

Next, navigate into `agrovision-backend/` and install requirements:
```bash
cd agrovision-backend
pip install -r requirements.txt
```

### Step 2: Running the FastAPI Backend Server
Start the development server using `uvicorn`:
```bash
uvicorn app.main:app --reload --port 8000
```
- **Interactive API Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Local Database:** The application dynamically provisions and structures a SQLite file database (`test.db` / `dev.db`) using SQLAlchemy if no PostgreSQL credentials are set in environment variables.
- **Dynamic PyTorch Decoupling:** If PyTorch isn't installed in the virtual environment, the `/scans/analyze` endpoint automatically falls back to a high-fidelity diagnostic mock response. This allows testing all core database, logging, and recommendation code flows on standard CPUs without installing heavy ML runtimes.

---

### Step 3: Run the Frontend UI Client
Navigate to the frontend directory:
```bash
cd ../agrovision-frontend
```

Install standard Node packages:
```bash
npm install
```

Start the Vite React development server:
```bash
npm run dev
```
- **Local Client Web Address:** [http://localhost:5173](http://localhost:5173)

---

## 🛠️ Building Frontend for Production

### Troubleshooting Windows Directory Paths containing ampersands (`&`)
Because the folder name contains a special character (`AI Crop Disease Detection using DL & AI`), running standard `npm run build` directly inside Windows CMD/Powershell will trigger parsing errors.

To successfully compile the React bundle for production on Windows, bypass the shell wrapper and invoke the Vite script directly through Node:

```powershell
node node_modules/vite/bin/vite.js build
```

This compiles all React components, contexts, and Tailwind utility classes into production-optimized assets inside the `dist/` directory.

---

## 🧪 Testing the API Endpoint

You can test database insertion and ML inference using `curl`:

```bash
# 1. Register a new agricultural officer account
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"phone_number\":\"+919876543210\", \"full_name\":\"John Doe\", \"password\":\"securepass123\"}"

# 2. Login to retrieve the JWT Token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=%2B919876543210&password=securepass123"

# 3. Request crop disease analysis (Multipart Upload)
curl -X POST "http://localhost:8000/api/v1/scans/analyze" \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
  -H "Content-Type: multipart/form-data" \
  -F "crop_category_id=1" \
  -F "latitude=12.9716" \
  -F "longitude=77.5946" \
  -F "image=@suspected_leaf.jpg"
```

---

## 🧪 Automated Testing Verification

The test framework uses `pytest` to run unit, integration, and security checks.

To run tests, set the `PYTHONPATH` from the root directory to include the backend and machine learning folders:

```powershell
# Set environment path and run test suite
$env:PYTHONPATH="agrovision-backend;agrovision-ml"
.venv\Scripts\python -m pytest tests/
```

### Coverage Scope:
- **`tests/test_unit.py`**: Validates JWT token extraction, token expiry, password hashing, and geolocational distance metrics.
- **`tests/test_backend.py`**: Evaluates mock user login, database scan history queries, and treatment lookup endpoints.
- **`tests/test_security.py`**: Audits headers, verifies token manipulation resilience, and validates SQLite relational injection boundaries.
- **`tests/test_ai_validation.py`**: Ensures PyTorch neural layers conform to specified image sizes and checkpoint threshold tolerances.

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
