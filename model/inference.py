
from .utils import *
from scipy.spatial.distance import cosine

def verify_face_similarity(face1_string, face2_string):
    # Face detection + cropping
    face1 = detect_and_crop_face(face1_string)
    face2 = detect_and_crop_face(face2_string)

    # Compute embeddings
    embedding1 = compute_embedding(face1)
    embedding2 = compute_embedding(face2)

    # distance = norm(embedding1 - embedding2)
    similarity = 1 - cosine(embedding1, embedding2)

    return similarity > 0.6
    
