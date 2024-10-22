from ninja import NinjaAPI
from UP_Tap.authentication import AuthBearer, InvalidToken

api = NinjaAPI()

api.add_router("/teachers/", "teachers.api.router", auth=AuthBearer())
api.add_router("/attendance/", "attendance.api.router", auth=AuthBearer())
api.add_router("/student/", "students.api.router", auth=AuthBearer())

@api.exception_handler(InvalidToken)
def on_invalid_token(request, exc):
    return api.create_response(request, {"detail": "Invalid token supplied"}, status=401)

