# not good, it usually doesn't recognize the person
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import torch

# Initialize MTCNN for face detection
mtcnn = MTCNN()

# Load pre-trained Inception ResNet model
resnet = InceptionResnetV1(pretrained='casia-webface').eval()

# Load two face images to be verified
img1 = Image.open('caleb_1.jpg')
img2 = Image.open('caleb_2.jpg')

# Detect faces and extract embeddings
faces1, _ = mtcnn.detect(img1)
faces2, _ = mtcnn.detect(img2)

if faces1 is not None and faces2 is not None:
    aligned1 = mtcnn(img1)
    aligned2 = mtcnn(img2)

    # Add batch dimension
    aligned1 = aligned1.unsqueeze(0)
    aligned2 = aligned2.unsqueeze(0)

    embeddings1 = resnet(aligned1).detach()
    embeddings2 = resnet(aligned2).detach()

    # Calculate the Euclidean distance between embeddings
    distance = (embeddings1 - embeddings2).norm().item()
    print("distance: " + str(distance))
    if distance < 1.0:  # You can adjust the threshold for verification
        print("Same person")
    else:
        print("Different persons")
else:
    print("Face not detected in one or both images")
