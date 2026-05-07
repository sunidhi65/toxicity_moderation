import requests
import time
import random

API_URL = "http://127.0.0.1:8000/predict"

# Subjects
subjects = [
    "you",
    "this app",
    "your project",
    "this game",
    "that idea",
    "your code",
    "this update",
    "the movie",
    "the design",
]

# Positive phrases
positive_phrases = [
    "is amazing",
    "looks fantastic",
    "is really helpful",
    "is brilliant",
    "is wonderful",
    "made my day",
    "is super impressive",
    "is excellent",
]

# Toxic phrases
toxic_phrases = [
    "is garbage",
    "is stupid",
    "is the worst thing ever",
    "is pathetic",
    "is horrible",
    "makes no sense",
    "is trash",
    "is idiotic",
]

# Extreme toxic phrases
extreme_toxic = [
    "go kill yourself",
    "nobody likes you",
    "you're worthless",
    "you are an idiot",
]

while True:

    # Randomly choose type
    comment_type = random.choice([
        "safe",
        "toxic",
        "extreme"
    ])

    # Generate comment
    if comment_type == "safe":
        comment = f"{random.choice(subjects)} {random.choice(positive_phrases)}"

    elif comment_type == "toxic":
        comment = f"{random.choice(subjects)} {random.choice(toxic_phrases)}"

    else:
        comment = random.choice(extreme_toxic)

    # Send to API
    response = requests.post(
        API_URL,
        params={"text": comment}
    )

    print(response.json())

    # Random delay (more realistic)
    time.sleep(random.uniform(1, 3))