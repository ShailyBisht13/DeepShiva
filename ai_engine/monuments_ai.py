import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

# Load CLIP model once (so it's fast)
model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

# List of monuments you want to classify
MONUMENTS = [
    "Taj Mahal",
    "Kedarnath Temple",
    "Badrinath Temple",
    "Golden Temple",
    "Hawa Mahal",
    "India Gate",
    "Charminar",
    "Jagannath Puri Temple"
]

def recognize_monument(image_path):
    """
    CLASSIFIES the input image & returns result with a CLEAR confidence score.
    """

    # --------------------
    # 1. Load the image safely
    # --------------------
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        return {"error": f"Could not load image: {str(e)}"}

    # --------------------
    # 2. Run CLIP processor
    # --------------------
    inputs = processor(
        text=MONUMENTS,
        images=image,
        return_tensors="pt",
        padding=True
    )

    outputs = model(**inputs)
    probs = outputs.logits_per_image.softmax(dim=1)[0]

    # --------------------
    # 3. Find best match
    # --------------------
    idx = torch.argmax(probs).item()
    confidence = float(probs[idx].item())  # convert tensor → float

    result = {
        "monument": MONUMENTS[idx],
        "confidence": round(confidence * 100, 2),   # percentage format
        "raw_score": confidence                     # keep original if needed
    }

    return result
