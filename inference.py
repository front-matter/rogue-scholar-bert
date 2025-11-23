from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)

model_name = "OpenAlex/bert-base-multilingual-cased-finetuned-openalex-topic-classification-title-abstract"
classifier = pipeline(
    "text-classification", model=model_name, truncation=True, max_length=512
)


@app.route("/classify", methods=["POST"])
def classify():
    data = request.json
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400
    result = classifier(text, top_k=5)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)
