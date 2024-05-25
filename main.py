
import io
import base64
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from transformers import pipeline
from PIL import Image
import torch
import uvicorn

app = FastAPI()

# Check if GPU is available and set the device accordingly
device = 0 if torch.cuda.is_available() else -1
print(device)
# Initialize the image segmentation pipeline
segmentation_pipeline = pipeline("image-segmentation",
                                 model="briaai/RMBG-1.4",
                                 trust_remote_code=True,
                                 device=device)

# Configure logging
logging.basicConfig(level=logging.INFO, filename="app_logs.log",
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def resize_image(image: Image.Image, max_size: int = 1024) -> Image.Image:
    """
    Resize the image to ensure the longest side is at most max_size pixels.

    Args:
        image (Image.Image): The input image to be resized.
        max_size (int): The maximum size for the longest side of the image.

    Returns:
        Image.Image: The resized image.
    """
    if max(image.size) > max_size:
        ratio = max_size / max(image.size)
        new_size = tuple(int(dim * ratio) for dim in image.size)
        return image.resize(new_size, Image.ANTIALIAS)
    return image

@app.post("/remove-background/")
async def remove_background(files: List[UploadFile] = File(...)) -> JSONResponse:
    """
    Remove the background from the uploaded image(s).

    Args:
        files (List[UploadFile]): The uploaded image file(s).

    Returns:
        JSONResponse: A JSON response containing the base64 encoded segmented images.
    """
    results = []
    for file in files:
        # Load the image from the uploaded file
        image_bytes = await file.read()

        try:
            image = Image.open(io.BytesIO(image_bytes))
        except IOError as exc:
            logger.error(f"Invalid image file: {file.filename}")
            raise HTTPException(status_code=400, detail=f"Invalid image file: {file.filename}--{exc}")

        # Convert the image if needed
        if image.format == "WEBP":
            image = image.convert("RGBA")
        elif image.format not in ["JPEG", "JPG", "PNG"]:
            logger.error(f"Unsupported image format for file: {file.filename}")
            raise HTTPException(status_code=400, detail=f"""Unsupported image format 
                                                            for file: {file.filename}.
                                                            Please upload an image in 
                                                            WEBP, JPG, JPEG, or PNG format.""")

        # Resize the image to a manageable size
        image = resize_image(image)

        # Process the image with the segmentation pipeline
        try:
            segmented_image = segmentation_pipeline(image)
        except Exception as e:
            logger.error(f"Segmentation pipeline error for file {file.filename}: {str(e)}")
            raise HTTPException(status_code=500,
            detail=f"Segmentation pipeline error for file {file.filename}: {str(e)}")

        # Convert the segmented image to a base64 encoded string
        buffered = io.BytesIO()
        segmented_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Add the result to the list
        results.append({"filename": file.filename, "image": img_str})

    # Return the base64 encoded images
    return JSONResponse(content={"images": results})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7000)
