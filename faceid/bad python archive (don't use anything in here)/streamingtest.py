from deepface import DeepFace

stream = DeepFace.stream(
    db_path='./raw_data', model_name='VGG-Face')
