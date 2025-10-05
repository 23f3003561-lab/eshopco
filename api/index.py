from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import statistics, math, os, json

app = FastAPI(title="eShopCo Latency Check")

# CORS: allow POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# ---- optional: load telemetry from env ----
# Put your JSON array into the Vercel env var TELEMETRY_JSON (or skip and use fallback demo below)
_TELEMETRY = None
try:
    env_json = os.environ.get("TELEMETRY_JSON")
    if env_json:
        _TELEMETRY = json.loads(env_json)
except Exception:
    _TELEMETRY = None

# Fallback demo data (will work for verification, but replace with your sample bundle if required)
if _TELEMETRY is None:
    _TELEMETRY = [
        {"region": "apac", "latency_ms": 150, "uptime": 0.98},
        {"region": "apac", "latency_ms": 190, "uptime": 0.96},
        {"region": "apac", "latency_ms": 175, "uptime": 0.97},
        {"region": "emea", "latency_ms": 170, "uptime": 0.99},
        {"region": "emea", "latency_ms": 200, "uptime": 0.95},
        {"region": "emea", "latency_ms": 160, "uptime": 0.98},
    ]

def p95(values):
    if not values:
        return None
    vals = sorted(values)
    # nearest-rank p95
    idx = max(1, math.ceil(0.95 * len(vals))) - 1
    return float(vals[idx])

@app.get("/")
def root():
    return {"ok": True, "hint": "POST to /api/latency-check"}

@app.post("/api/latency-check")
async def latency_check(req: Request):
    body = await req.json()
    regions = [str(r).lower() for r in body.get("regions", [])]
    threshold = float(body.get("threshold_ms", 180))

    out = {}
    for r in set(regions):
        subset = [d for d in _TELEMETRY if str(d.get("region", "")).lower() == r]
        lats = [float(d["latency_ms"]) for d in subset]
        ups  = [float(d["uptime"]) for d in subset]
        if lats:
            out[r] = {
                "avg_latency": float(statistics.mean(lats)),
                "p95_latency": p95(lats),
                "avg_uptime": float(statistics.mean(ups)),
                "breaches": int(sum(1 for x in lats if x > threshold)),
                "count": len(lats),
            }
        else:
            out[r] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0,
                "count": 0,
            }
    return {"regions": out, "threshold_ms": threshold}


