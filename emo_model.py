from transformers import AutoTokenizer, pipeline

MODEL_NAME = "SamLowe/roberta-base-go_emotions"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
emotion_classifier = pipeline(
    task="text-classification",
    model=MODEL_NAME,
    tokenizer=tokenizer,
    top_k=None
)
def split_diary_text(diary_text: str):
    token_ids = tokenizer.encode(
        diary_text,
        add_special_tokens=False
    )
    max_chunk_size = 510
    chunks = []

    for start in range(0, len(token_ids), max_chunk_size):
        chunk_tokens = token_ids[
            start:start + max_chunk_size
        ]
        chunk_text = tokenizer.decode(
            chunk_tokens,
            skip_special_tokens=True
        )

        chunks.append(chunk_text)
    if not chunks:
        chunks.append("")

    return chunks
def analyze_emotions(diary_text: str):
    text_chunks = split_diary_text(diary_text)
    chunk_predictions = emotion_classifier(
        text_chunks,
        truncation=True)
    
    emotion_scores = {}

    for predictions in chunk_predictions:
        for prediction in predictions:
            emotion = prediction["label"]
            score = prediction["score"]

            if emotion not in emotion_scores or score > emotion_scores[emotion]:
                emotion_scores[emotion] = score

    detected_emotions = []

    for emotion, score in emotion_scores.items():
        if score >= 0.5:
            detected_emotions.append({
                "emotion": emotion,
                "score": round(score, 4)
            })
    detected_emotions.sort(
        key=lambda result: result["score"],
        reverse=True
    )

    if not detected_emotions:
        strongest_emotion = max(
            emotion_scores,
            key=emotion_scores.get
        )
        detected_emotions.append({
            "emotion": strongest_emotion,
            "score": round(emotion_scores[strongest_emotion], 4)
        })
    return detected_emotions