from transformers import pipeline
import torch

# Detect device: use MPS (Metal Performance Shaders) on Apple Silicon if available
device = "mps" if torch.backends.mps.is_available() else "cpu"

model_name = "OpenAlex/bert-base-multilingual-cased-finetuned-openalex-topic-classification-title-abstract"

# Minimum confidence score threshold for classification results
MIN_SCORE = 0.2

classifier = pipeline(
    "text-classification",
    model=model_name,
    top_k=5,
    truncation=True,
    max_length=512,
    device=device,
)


async def classify(title: str | None, abstract: str | None) -> dict:
    if not title and not abstract:
        return {"error": "No input provided"}
    if title is None:
        title = "NONE"
    input = f"<TITLE>{title}"
    if abstract is not None:
        input += f"<ABSTRACT>{abstract}"
    result = classifier(input)

    # Filter results by minimum score
    if isinstance(result, list) and len(result) > 0:
        filtered_result = [r for r in result[0] if r["score"] >= MIN_SCORE]
        return filtered_result

    return result
