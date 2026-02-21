from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
import time 
import uuid
import json 


app = FastAPI()

@app.middleware("http")
async def simple_timer(request: Request , call_next):
    request_id = str(uuid.uuid4()) #generating unique id 
    start_time = time.time()
    
    try:
        response = await call_next(request)
    except Exception as e:
        duration = time.time() - start_time

        #Structure error log 
        log_data = {
            "event":"request_failed",
            "request_id":request_id,
            "path":request.url.path,
            "method":request.method,
            "latency_ms":round(duration * 1000,2),
            "error_type":type(e).__name__,
        }
        print(json.dumps(log_data))

        #Return clean JSON error
        return JSONResponse(
            status_code=500,
            content={"error":"internal_error","request_id":request_id},
            headers={"X-Request-ID":request_id}
        )


    duration = time.time() - start_time
    ## Adding request id to response headers 
    response.headers["X-Request-ID"] = request_id
    
    log_data = {
        "event":"request_completed",
        "request_id":request_id,
        "path":request.url.path,
        "method":request.method,
        "latency_ms":round(duration*1000,2)
    }
    print(json.dumps(log_data))
    return response 

@app.get("/health")
def health():
    return {"status": "ok"}  

@app.get("/boom")
def boom():
    1 / 0 

READY = True 

@app.get("/ready")
def ready():
    if not READY:
        return JSONResponse(status_code=503,content={"status":"not_ready"})
    return {"status":"ready"}