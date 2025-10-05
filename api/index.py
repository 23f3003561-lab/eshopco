from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import statistics

app = FastAPI()

# allow any website to send POSTs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/api/latency-check")
async def latency_check(req: Request):
    body = await req.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    # pretend telemetry (replace with real sample later)
    data = [
        {"region":"apac","latency_ms":150,"uptime":0.98},
        {"region":"apac","latency_ms":190,"uptime":0.96},
        {"region":"emea","latency_ms":170,"uptime":0.99},
        {"region":"emea","latency_ms":200,"uptime":0.95},
    ]

    result = {}
    for r in regions:
        subset = [d for d in data if d["region"] == r]
        lats = [d["latency_ms"] for d in subset]
        ups = [d["uptime"] for d in subset]
        breaches = sum(1 for x in lats if x > threshold)
        result[r] = {
            "avg_latency": statistics.mean(lats),
            "p95_latency": sorted(lats)[int(0.95*len(lats))-1],
            "avg_uptime": statistics.mean(ups),
            "breaches": breaches
        }
    return result
