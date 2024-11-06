import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1' 

from deepface import DeepFace

def verify_face(student_face_data, input_face_data):
    try:
        check_face = DeepFace.verify(student_face_data, input_face_data, anti_spoofing=True, model_name='Facenet')
        if not check_face['verified']:
            return False, {"success": False, "message": "Face data mismatch!"}
        return True, None
    except ValueError:
        return False, {"success": False, "message": "Spoof image or no face detected!"}