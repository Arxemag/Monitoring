from fastapi.responses import JSONResponse

def make_response(success: bool, message: str, data):
    return JSONResponse(
        status_code=200,
        content={
            "success": success,
            "message": message,
            "data": data
        },
        media_type="application/json"
    )