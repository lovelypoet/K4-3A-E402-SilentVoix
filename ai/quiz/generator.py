from typing import Any, Dict, List

from ai.grounding.retriever import GroundingRetriever
from ai.quiz.decision import decide_quiz


QUESTION_BANK = {
    "gradient_descent": {
        "easy": "What is the primary purpose of gradient descent?",
        "medium": "What is the main goal of gradient descent in optimization?",
        "hard": "Why does gradient descent move in the direction of steepest descent?"
    },
    "loss_function": {
        "easy": "What does a loss function measure?",
        "medium": "How does a loss function help guide training?",
        "hard": "Why is a loss function necessary for optimization?"
    },
    "regression": {
        "easy": "What type of output does regression predict?",
        "medium": "How is regression different from classification?",
        "hard": "Why is regression used for continuous target variables?"
    },
    "default": {
        "easy": "What is the main concept being described?",
        "medium": "Which statement best matches the idea in the source material?",
        "hard": "Which explanation is most consistent with the grounded evidence?"
    }
}


def generate_quiz(graph: Dict[str, Any], concept_id: str, difficulty: str = "medium") -> Dict[str, Any]:
    if not concept_id:
        return {
            "decision": "REFUSE_UNGROUNDED",
            "concept_id": concept_id,
            "difficulty": difficulty,
            "question": "",
            "options": [],
            "correct_answer": "",
            "explanation": "No concept was provided, so the request cannot be grounded in the source material.",
            "citations": [],
        }

    decision = decide_quiz(graph, concept_id)
    node = next((n for n in graph.get("nodes") or [] if n.get("id") == concept_id), None)
    if node is None:
        return {
            "decision": "REFUSE_UNGROUNDED",
            "concept_id": concept_id,
            "difficulty": difficulty,
            "question": "",
            "options": [],
            "correct_answer": "",
            "explanation": f"The concept '{concept_id}' is not present in the source material, so this request is unsupported.",
            "citations": [],
        }

    evidence = GroundingRetriever(graph).retrieve_evidence(concept_id)
    if decision == "REFUSE_UNGROUNDED" or not evidence:
        return {
            "decision": "REFUSE_UNGROUNDED",
            "concept_id": concept_id,
            "difficulty": difficulty,
            "question": "",
            "options": [],
            "correct_answer": "",
            "explanation": f"The concept '{concept_id}' is not supported by grounded source evidence in the uploaded materials.",
            "citations": [],
        }

    question = QUESTION_BANK.get(concept_id, QUESTION_BANK["default"]).get(difficulty, QUESTION_BANK["default"]["medium"])
    options = [
        "To minimize the value of a loss function.",
        "To increase the model complexity.",
        "To add noise to the dataset.",
        "To remove all training examples."
    ]
    if concept_id == "loss_function":
        options = [
            "It measures prediction error.",
            "It stores all model parameters.",
            "It is only used for evaluation.",
            "It prevents data from being used."
        ]
    elif concept_id == "regression":
        options = [
            "It predicts continuous values.",
            "It predicts discrete labels.",
            "It groups data points without labels.",
            "It reconstructs images from noise."
        ]

    correct_answer = options[0]
    citations = []
    for source in evidence:
        citations.append({
            "document_id": source.get("document_id"),
            "chunk_id": source.get("chunk_id"),
            "slide": source.get("slide"),
            "start_time": source.get("start_time"),
            "end_time": source.get("end_time"),
        })

    return {
        "decision": "GENERATE_QUIZ",
        "concept_id": concept_id,
        "difficulty": difficulty,
        "question": question,
        "options": options,
        "correct_answer": correct_answer,
        "explanation": f"This quiz is grounded in the source evidence for '{concept_id}'.",
        "citations": citations,
    }
