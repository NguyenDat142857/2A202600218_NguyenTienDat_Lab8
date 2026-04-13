import json

def simple_score(pred, expected):
    return int(expected.lower() in pred.lower())

def run_eval():
    with open("data/test_questions.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    score = 0
    for item in data:
        pred = item["question"]  # mock
        score += simple_score(pred, item["expected"])

    print("Score:", score, "/", len(data))

if __name__ == "__main__":
    run_eval()
