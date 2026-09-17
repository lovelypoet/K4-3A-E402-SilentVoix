# Mock Data for Machine Learning Lesson

MOCK_CONCEPTS = {
    "c1": {"name": "Machine Learning Basics"},
    "c2": {"name": "Supervised Learning"},
    "c3": {"name": "Unsupervised Learning"},
    "c4": {"name": "Linear Regression"},
    "c5": {"name": "Loss Function"},
    "c6": {"name": "Gradient Descent"},
}

# Mapping: Concept -> List of Prerequisites (Backward edges)
# e.g., to understand "Gradient Descent" (c6), you need to understand "Loss Function" (c5)
MOCK_PREREQUISITES = {
    "c1": [],
    "c2": ["c1"],
    "c3": ["c1"],
    "c4": ["c2"],
    "c5": ["c2"],
    "c6": ["c5"]
}

MOCK_SOURCE_MAPPING = {
    "c1": {"slide": 1, "start_time": 0, "end_time": 120},
    "c2": {"slide": 3, "start_time": 121, "end_time": 300},
    "c3": {"slide": 7, "start_time": 301, "end_time": 450},
    "c4": {"slide": 10, "start_time": 451, "end_time": 600},
    "c5": {"slide": 17, "start_time": 601, "end_time": 750},
    "c6": {"slide": 20, "start_time": 751, "end_time": 900}
}

# A mock database of student attempts
# Mapping: student_id -> list of attempts
MOCK_STUDENT_ATTEMPTS = {
    "student_1": [
        {"quiz_id": "q1", "concept_id": "c1", "is_correct": True, "difficulty": 1.0},
        {"quiz_id": "q2", "concept_id": "c2", "is_correct": True, "difficulty": 1.0},
        {"quiz_id": "q5", "concept_id": "c5", "is_correct": False, "difficulty": 1.0},
        {"quiz_id": "q6", "concept_id": "c6", "is_correct": False, "difficulty": 1.0},
    ],
    "student_perfect": [
        {"quiz_id": "q1", "concept_id": "c1", "is_correct": True, "difficulty": 1.0},
        {"quiz_id": "q2", "concept_id": "c2", "is_correct": True, "difficulty": 1.0},
        {"quiz_id": "q6", "concept_id": "c6", "is_correct": True, "difficulty": 1.0},
    ]
}
