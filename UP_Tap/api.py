from ninja import NinjaAPI, Swagger, Redoc
from UP_Tap.authentication import AuthBearer, InvalidToken

api = NinjaAPI(
    docs=Swagger(settings={"persistAuthorization": True}), 
    auth=AuthBearer(),
    )

api.add_router("/teachers/", "teachers.api.router", tags=["Teachers API"])
api.add_router("/attendance/", "attendance.api.router", tags=["Attendance API"])
api.add_router("/student/", "students.api.router", tags=["Student API"])

@api.exception_handler(InvalidToken)
def on_invalid_token(request, exc):
    return api.create_response(request, {"detail": "Invalid token supplied"}, status=401)
