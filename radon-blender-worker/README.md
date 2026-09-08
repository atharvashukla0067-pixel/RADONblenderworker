# RADON Blender Worker

A standalone production-ready **Blender generation worker** for RADON. This is a **separate service** from the RADON frontend — it does not modify or depend on the existing RADON application. It exists to serve as the real upstream target of RADON's `BLENDER_WORKER_URL`.

## What It Does

The worker receives HTTP requests describing a 3D entity, generates it using a **real headless Blender runtime**, and returns a downloadable GLB file. It is designed to run as a Docker container that contains an actual Blender installation.

```
Client / RADON
    ↓  HTTP POST /generate
Blender Worker (FastAPI)
    ↓  Headless Blender + Python script
Generated GLB / glTF
    ↓  HTTP response + /assets/<id>/output.glb
```

## Architecture

| Component | Description |
|---|---|
| `app/main.py` | FastAPI HTTP server with `/health` and `/generate` endpoints |
| `app/core/blender_runner.py` | Detects and wraps the real Blender executable |
| `app/core/workspace.py` | Isolated temporary job directories with cleanup |
| `app/core/models.py` | Request/response Pydantic models with input validation |
| `app/core/config.py` | Environment-based configuration |
| `app/strategies/` | Extensible generation strategies (one per category) |
| `app/strategies/registry.py` | Maps categories to strategies (add new ones here) |

### Generation Engine

The system uses a **generic generation abstraction** — not hardcoded shapes:

```
Entity → Category → Generation Strategy → Blender Scene Construction → GLB Export
```

**Supported categories:**

| Category | Strategy | Example Entities |
|---|---|---|
| `anatomy` | `AnatomyStrategy` | heart, brain, kidney, lung, liver, skull |
| `molecule` | `MoleculeStrategy` | DNA, C60, water, methane, benzene, caffeine |
| `astronomy` | `AstronomyStrategy` | Saturn, Earth, Mars, Jupiter, Sun, Moon |
| `vehicle` | `VehicleStrategy` | Boeing 747, car, rocket, ship, helicopter, tank |
| `architecture` | `ArchitectureStrategy` | house, tower, temple, bridge, pyramid, castle |
| `engineering` | `EngineeringStrategy` | gear, engine, turbine, bolt, pipe, I-beam |
| `general` | `GeneralObjectStrategy` | cube, sphere, cylinder, cone, torus, tree, chair, table |

**Adding a new strategy** does not require modifying the HTTP API contract. Just:
1. Create a new class extending `GenerationStrategy` in `app/strategies/`.
2. Implement `build_script()` to return a Blender Python script.
3. Register it in `app/strategies/registry.py`.

### Quality Levels

| Level | Subdivision | Bevel | Use Case |
|---|---|---|---|
| `preview` | 0 | 1 segment | Quick previews |
| `standard` | 1 | 2 segments | Default |
| `high` | 3 | 4 segments | Final quality |

## API

### `GET /health`

Verifies the real Blender executable. Does NOT return `"available"` unless Blender is actually installed and can run.

```json
{
  "status": "healthy",
  "blender": "available",
  "version": "4.2.4",
  "worker": "radon-blender-worker"
}
```

### `POST /generate`

Request:
```json
{
  "requestId": "req-001",
  "entity": "heart",
  "category": "anatomy",
  "description": "A simplified human heart",
  "quality": "standard",
  "outputFormat": "glb"
}
```

Response:
```json
{
  "success": true,
  "requestId": "req-001",
  "origin": "BLENDER_GENERATED",
  "verification": "BLENDER_GENERATED_APPROXIMATION",
  "outputFormat": "glb",
  "assetUrl": "/assets/<job-id>/output.glb",
  "assetPath": "/tmp/radon-output/<job-id>/output.glb",
  "fileSizeBytes": 45230,
  "metadata": {
    "blender_version": "4.2.4",
    "generation_strategy": "AnatomyStrategy",
    "quality": "standard",
    "category": "anatomy",
    "entity": "heart",
    "blender_scene_objects": 5,
    "generation_time_seconds": 3.21
  },
  "limitations": [
    "'heart' is a simplified geometric approximation, NOT a medically accurate model.",
    "..."
  ]
}
```

### `GET /categories`

Returns all supported generation categories.

## Docker Deployment

### Build

```bash
docker build -t radon-blender-worker .
```

### Run

```bash
docker run -d -p 8001:8001 --name radon-blender radon-blender-worker
```

### Verify

```bash
curl http://localhost:8001/health
curl -X POST http://localhost:8001/generate \
  -H "Content-Type: application/json" \
  -d '{"requestId":"test-001","entity":"heart","category":"anatomy","quality":"standard","outputFormat":"glb"}'
```

### Docker Compose

```bash
docker-compose up -d
```

The Docker image contains **Blender 4.2 LTS** installed from the official Blender download server. The Dockerfile verifies Blender runs during build (`RUN blender --background --version`).

## Running Locally (without Docker)

If Blender is installed on your system:

```bash
cd radon-blender-worker
pip install -r requirements.txt
export BLENDER_PATH=/usr/bin/blender  # or wherever Blender is installed
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## Tests

### Automated tests (pytest)

```bash
cd radon-blender-worker
pip install -r requirements.txt
pytest tests/ -v
```

### Standalone test (no pytest needed)

```bash
python tests/test_standalone.py
```

The tests verify:
1. Blender process launched.
2. Blender generated geometry.
3. GLB export succeeded.
4. GLB exists.
5. GLB is non-empty.
6. The API returned success.

## Security

- **No arbitrary code execution**: Entity and description inputs are sanitized — never passed as Python code or shell commands to Blender.
- **No shell injection**: All input goes through Pydantic validation with control-character stripping and length limits.
- **No path traversal**: Inputs are never used as file paths. Job directories use generated UUIDs.
- **Isolated workspaces**: Each job gets a unique temporary directory that is cleaned up after completion.
- **Request timeouts**: Blender processes are killed after `JOB_TIMEOUT` seconds (default 120).
- **Output size limits**: GLB files exceeding `MAX_OUTPUT_SIZE_MB` (default 100MB) are rejected.
- **Concurrent safety**: A thread lock prevents overlapping Blender processes from corrupting shared state.
- **No secret exposure**: Internal errors are sanitized before returning to the client.

## Provenance

Every generated asset carries `origin: "BLENDER_GENERATED"` and `verification: "BLENDER_GENERATED_APPROXIMATION"`. The `limitations` array explicitly states that generated geometry is an approximation, not a verified scientific/anatomical/engineering model.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `BLENDER_PATH` | `/usr/bin/blender` | Path to the Blender executable |
| `OUTPUT_DIR` | `/tmp/radon-output` | Directory for generated GLB files |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8001` | Server port |
| `JOB_TIMEOUT` | `120` | Blender process timeout (seconds) |
| `MAX_OUTPUT_SIZE_MB` | `100` | Maximum GLB file size |

## Project Structure

```
radon-blender-worker/
├── Dockerfile              # Docker image with real Blender 4.2 LTS
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment configuration
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI application
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py       # Settings
│   │   ├── models.py       # Request/response models
│   │   ├── blender_runner.py  # Blender executable wrapper
│   │   └── workspace.py    # Job workspace management
│   └── strategies/
│       ├── __init__.py
│       ├── base.py         # Abstract base strategy
│       ├── registry.py     # Strategy registry
│       ├── anatomy.py      # Anatomical structures
│       ├── molecule.py     # Molecular structures
│       ├── astronomy.py    # Celestial bodies
│       ├── vehicle.py      # Vehicles
│       ├── architecture.py # Buildings
│       ├── engineering.py  # Engineering objects
│       └── general.py      # General objects (fallback)
└── tests/
    ├── test_worker.py      # pytest test suite
    └── test_standalone.py  # Standalone test script
```
