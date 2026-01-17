from __future__ import annotations

import csv
import random
from pathlib import Path

OUT = Path("training/data/role_dataset.csv")
random.seed(42)

LABEL_TEMPLATES = {
    "android_developer": [
        "Kotlin Java Android SDK Android Studio Jetpack MVVM Retrofit Room Git",
        "Built Android apps using Kotlin, Jetpack components, REST APIs, Firebase, Room DB",
        "Worked on Android app performance, bug fixing, API integration, and releases",
        "Implemented MVVM with ViewModel LiveData, Retrofit, Room, and Hilt",
        "Experience with Git, CI/CD, unit testing, and Play Store deployment",
    ],
    "flutter_developer": [
        "Flutter Dart Bloc Clean Architecture Firebase REST API Git",
        "Built cross-platform apps in Flutter with Firebase, REST APIs, and state management",
        "Developed UI screens, API integration, and performance optimization in Flutter",
        "Worked with Provider/Bloc, clean architecture, and responsive UI in Flutter",
        "Integrated Firebase Auth, Firestore, FCM, and analytics in Flutter apps",
    ],
    "backend_java": [
        "Java Spring Boot REST API Microservices Hibernate JPA MySQL Docker Git",
        "Built backend services using Spring Boot, PostgreSQL, Redis, Docker, CI/CD",
        "Designed RESTful APIs, implemented auth, logging, and database integration",
        "Worked on microservices, Kafka, caching, and performance tuning",
        "Experience with unit testing, integration testing, and deployment pipelines",
    ],
    "python_ml": [
        "Python Machine Learning scikit-learn pandas numpy classification NLP",
        "Built ML pipelines using sklearn, feature engineering, model evaluation",
        "Worked on NLP text processing, vectorization, and classification models",
        "Trained models with TF-IDF, logistic regression, and saved pipelines",
        "Experience with data cleaning, pandas, numpy, and model deployment basics",
    ],
    "frontend_react": [
        "React JavaScript TypeScript Redux HTML CSS REST API",
        "Built frontend UI with React, API integration, and state management",
        "Experience with hooks, component design, and responsive web UI",
        "Worked with TypeScript, REST APIs, and modern frontend tooling",
        "Built reusable components and integrated backend services",
    ],
}

def main() -> None:
    rows = []
    # generate 50 samples per class (adjust as you like)
    per_class = 50

    for label, templates in LABEL_TEMPLATES.items():
        for _ in range(per_class):
            base = random.choice(templates)
            # small random noise to reduce duplicates
            extra = random.sample(
                ["agile", "scrum", "documentation", "debugging", "testing", "code review", "design patterns"],
                k=random.randint(0, 3),
            )
            text = base + (" " + " ".join(extra) if extra else "")
            rows.append((label, text))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["label", "text"])
        w.writerows(rows)

    print(f"✅ Generated dataset: {OUT} ({len(rows)} rows)")

if __name__ == "__main__":
    main()
