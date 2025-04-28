
def make_response(success: bool, message: str, data):
    return {
        "success": success,
        "message": message,
        "data": data
    }
