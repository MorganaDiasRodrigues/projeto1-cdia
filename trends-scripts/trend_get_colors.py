import cv2
import numpy as np
import os
from sklearn.cluster import KMeans
import json

def get_dominant_colors(image_path, n_colors):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image.reshape(-1, 3)

    kmeans = KMeans(n_clusters=n_colors)
    kmeans.fit(image)

    # convert color codes to hexadecimal
    colors = kmeans.cluster_centers_.astype(int)
    hex_colors = ['#{:02x}{:02x}{:02x}'.format(c[0], c[1], c[2]) for c in colors]

    # get color proportions
    labels = list(kmeans.labels_)
    proportions = [labels.count(i)/len(labels) for i in range(n_colors)]

    return dict(zip(hex_colors, proportions))

def main():
    trends_images = {}
    base_path = "..\img"  # base folder for images

    for image_file in os.listdir(base_path):
        if image_file.endswith('.jpg') or image_file.endswith('.png'):  # check for image files
            image_path = os.path.join(base_path, image_file)
            dominant_colors = get_dominant_colors(image_path, 5)

            # Extract trend name from the filename by removing the extension and any trailing numbers
            trend = os.path.splitext(image_file)[0].rstrip('-1234567890')
            if trend not in trends_images:
                trends_images[trend] = {"images": []}

            trends_images[trend]["images"].append({
                "path": image_path,
                "dominant_colors": dominant_colors
            })

    with open('trends_images.json', 'w') as f:
        json.dump(trends_images, f, indent=4)

if __name__ == "__main__":
    main()
