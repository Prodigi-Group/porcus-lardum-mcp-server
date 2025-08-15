#!/usr/bin/env python3
import os
from typing import Optional, Dict, Any, List
import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

load_dotenv()

API_KEY = os.getenv("PORCUS_LARDUM_API_KEY", "")
BASE_URL = os.getenv("PORCUS_LARDUM_BASE_URL", "https://porcus-lardum-func-dev.azurewebsites.net")

mcp = FastMCP("Porcus Lardum Image Transformer")

class Unit(BaseModel):
    pixels: Optional[int] = Field(None, ge=0, le=100000)
    inches: Optional[float] = Field(None, ge=0, le=100000)
    millimeter: Optional[float] = Field(None, ge=0, le=100000)

class ImageOpsTransformParamsIn(BaseModel):
    image_ops: bool = Field(True, description="Enable ImageOps transformations")
    crop: Optional[List[Unit]] = Field(None, description="Remove pixels from image borders")
    crop_box: Optional[List[List[Unit]]] = Field(None, description="Extract rectangular region [x1, y1, x2, y2]")
    crop_aspect_ratio: Optional[float] = Field(None, description="Crop to specific width/height ratio")
    pad: Optional[List[Unit]] = Field(None, description="Expand canvas to target dimensions")
    contain: Optional[List[Unit]] = Field(None, description="Scale image to fit within bounds [width, height]")
    override_dpi: Optional[int] = Field(None, description="Set image DPI metadata")
    rotate: Optional[int] = Field(None, description="Rotate image in degrees")
    rotate_to: Optional[str] = Field(None, description="Auto-rotate to 'landscape' or 'portrait'")
    grayscale: Optional[bool] = Field(None, description="Convert to grayscale")
    pdf: Optional[bool] = Field(None, description="Convert output to PDF")

@mcp.tool(
    title="Image Transformer",
    description="""Transform an image using Porcus Lardum ImageOps transformations.
    
    Parameters:
    - source_image_url: URL of the image to transform
    - crop_pixels: Remove pixels from borders [top, right, bottom, left] or single value for all
    - crop_mm: Remove millimeters from borders [top, right, bottom, left] or single value for all
    - crop_inches: Remove inches from borders [top, right, bottom, left] or single value for all
    - crop_box_pixels: Extract rectangle [x1, y1, x2, y2] in pixels
    - crop_box_mm: Extract rectangle [x1, y1, x2, y2] in millimeters
    - crop_box_inches: Extract rectangle [x1, y1, x2, y2] in inches
    - crop_aspect_ratio: Crop to width/height ratio (e.g., 1.77 for 16:9)
    - pad_pixels: Expand canvas [width, height] in pixels
    - pad_mm: Expand canvas [width, height] in millimeters
    - pad_inches: Expand canvas [width, height] in inches
    - contain_pixels: Scale to fit within [width, height] in pixels
    - contain_mm: Scale to fit within [width, height] in millimeters
    - contain_inches: Scale to fit within [width, height] in inches
    - override_dpi: Set DPI metadata
    - rotate: Rotation angle in degrees
    - rotate_to: Auto-rotate to 'landscape' or 'portrait'
    - grayscale: Convert to grayscale
    - pdf: Convert output to PDF

    Returns the transformed source image URL and metadata."""
)
async def transform_image(
    source_image_url: str,
    crop_pixels: Optional[List[int]] = None,
    crop_mm: Optional[List[float]] = None,
    crop_inches: Optional[List[float]] = None,
    crop_box_pixels: Optional[List[int]] = None,
    crop_box_mm: Optional[List[float]] = None,
    crop_box_inches: Optional[List[float]] = None,
    crop_aspect_ratio: Optional[float] = None,
    pad_pixels: Optional[List[int]] = None,
    pad_mm: Optional[List[float]] = None,
    pad_inches: Optional[List[float]] = None,
    contain_pixels: Optional[List[int]] = None,
    contain_mm: Optional[List[float]] = None,
    contain_inches: Optional[List[float]] = None,
    override_dpi: Optional[int] = None,
    rotate: Optional[int] = None,
    rotate_to: Optional[str] = None,
    grayscale: Optional[bool] = None,
    pdf: Optional[bool] = None,
) -> Dict[str, Any]:
    
    if not API_KEY:
        return {"error": "API key not configured. Please set PORCUS_LARDUM_API_KEY environment variable."}
    
    try:
        # Convert values to Unit objects
        crop_units = None
        if crop_pixels:
            crop_units = [Unit(pixels=p) for p in crop_pixels]
        elif crop_mm:
            crop_units = [Unit(millimeter=p) for p in crop_mm]
        elif crop_inches:
            crop_units = [Unit(inches=p) for p in crop_inches]
        
        crop_box_units = None
        if crop_box_pixels:
            crop_box_units = [[Unit(pixels=p)] for p in crop_box_pixels]
        elif crop_box_mm:
            crop_box_units = [[Unit(millimeter=p)] for p in crop_box_mm]
        elif crop_box_inches:
            crop_box_units = [[Unit(inches=p)] for p in crop_box_inches]
        
        pad_units = None
        if pad_pixels:
            pad_units = [Unit(pixels=p) for p in pad_pixels]
        elif pad_mm:
            pad_units = [Unit(millimeter=p) for p in pad_mm]
        elif pad_inches:
            pad_units = [Unit(inches=p) for p in pad_inches]
        
        contain_units = None
        if contain_pixels:
            contain_units = [Unit(pixels=p) for p in contain_pixels]
        elif contain_mm:
            contain_units = [Unit(millimeter=p) for p in contain_mm]
        elif contain_inches:
            contain_units = [Unit(inches=p) for p in contain_inches]
        
        transform_params = ImageOpsTransformParamsIn(
            image_ops=True,
            crop=crop_units,
            crop_box=crop_box_units,
            crop_aspect_ratio=crop_aspect_ratio,
            pad=pad_units,
            contain=contain_units,
            override_dpi=override_dpi,
            rotate=rotate,
            rotate_to=rotate_to,
            grayscale=grayscale,
            pdf=pdf,
        )
        
        request_body = {
            "source_image_url": source_image_url,
            "transform": transform_params.model_dump(exclude_none=True)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/sync_transform",
                json=request_body,
                headers={
                    "x-api-key": API_KEY,
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            
            if response.status_code == 200:
                # Check if response is JSON or binary image data
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    result = response.json()
                    return {
                        "success": True,
                        "transformed_url": result.get("url"),
                        "metadata": result.get("metadata", {}),
                        "processing_time": result.get("processing_time"),
                    }
                else:
                    # Response is binary image data
                    # Save to disk with appropriate extension
                    ext = "jpg"
                    if "png" in content_type:
                        ext = "png"
                    elif "gif" in content_type:
                        ext = "gif"
                    elif "webp" in content_type:
                        ext = "webp"
                    
                    filename = f"transformed_image.{ext}"
                    with open(filename, "wb") as f:
                        f.write(response.content)
                    
                    return {
                        "success": True,
                        "message": "Image transformed successfully",
                        "saved_to": filename,
                        "content_type": content_type,
                        "size": len(response.content),
                    }
            else:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "details": response.text,
                }
                
    except Exception as e:
        return {"error": f"Failed to transform image: {str(e)}"}

@mcp.tool(
    title="Generate Temp Blob URL",
    description="""Generate a temporary blob SAS URL with write and read permissions.
    
    Parameters:
    - extension: Optional file extension ('png', 'jpg', or 'pdf')
    
    Returns a temporary URL that can be used to upload/download files."""
)
async def generate_temp_blob(extension: Optional[str] = None) -> Dict[str, Any]:
    
    if not API_KEY:
        return {"error": "API key not configured. Please set PORCUS_LARDUM_API_KEY environment variable."}
    
    try:
        params = {}
        if extension and extension in ['png', 'jpg', 'pdf']:
            params['extension'] = extension
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/temp_blob",
                params=params,
                headers={
                    "x-api-key": API_KEY,
                },
                timeout=30.0,
            )
            
            if response.status_code == 200:
                # The API returns a JSON-encoded string, strip quotes to get plain URL
                temp_url = response.text.strip().strip('"')
                return {
                    "success": True,
                    "temp_url": temp_url,
                    "extension": extension or "no extension",
                }
            else:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "details": response.text,
                }
                
    except Exception as e:
        return {"error": f"Failed to generate temp blob URL: {str(e)}"}

@mcp.tool(
    title="Async Image Transformation",
    description="""Queue an image transformation job for asynchronous processing.
    
    Parameters:
    - source_image_url: URL of the image to transform
    - output_image_url: (optional*) URL where the transformed image will be delivered
    - client_transform_id: Optional client ID for tracking (default: generated UUID)
    - source: Optional source identifier for job correlation
    - crop_pixels: Remove pixels from borders [top, right, bottom, left] or single value for all
    - crop_mm: Remove millimeters from borders [top, right, bottom, left] or single value for all
    - crop_inches: Remove inches from borders [top, right, bottom, left] or single value for all
    - crop_box_pixels: Extract rectangle [x1, y1, x2, y2] in pixels
    - crop_box_mm: Extract rectangle [x1, y1, x2, y2] in millimeters
    - crop_box_inches: Extract rectangle [x1, y1, x2, y2] in inches
    - crop_aspect_ratio: Crop to width/height ratio (e.g., 1.77 for 16:9)
    - pad_pixels: Expand canvas [width, height] in pixels
    - pad_mm: Expand canvas [width, height] in millimeters
    - pad_inches: Expand canvas [width, height] in inches
    - contain_pixels: Scale to fit within [width, height] in pixels
    - contain_mm: Scale to fit within [width, height] in millimeters
    - contain_inches: Scale to fit within [width, height] in inches
    - override_dpi: Set DPI metadata
    - rotate: Rotation angle in degrees
    - rotate_to: Auto-rotate to 'landscape' or 'portrait'
    - grayscale: Convert to grayscale
    - pdf: Convert output to PDF
    
    Returns a transform_job_id for tracking the asynchronous job.

    * If user didn't provide a output_image_url, a new temporary URL will be generated using the temp_blob tool
    """
)
async def async_image_transformation(
    source_image_url: str,
    output_image_url: str,
    client_transform_id: Optional[str] = None,
    source: Optional[str] = None,
    crop_pixels: Optional[List[int]] = None,
    crop_mm: Optional[List[float]] = None,
    crop_inches: Optional[List[float]] = None,
    crop_box_pixels: Optional[List[int]] = None,
    crop_box_mm: Optional[List[float]] = None,
    crop_box_inches: Optional[List[float]] = None,
    crop_aspect_ratio: Optional[float] = None,
    pad_pixels: Optional[List[int]] = None,
    pad_mm: Optional[List[float]] = None,
    pad_inches: Optional[List[float]] = None,
    contain_pixels: Optional[List[int]] = None,
    contain_mm: Optional[List[float]] = None,
    contain_inches: Optional[List[float]] = None,
    override_dpi: Optional[int] = None,
    rotate: Optional[int] = None,
    rotate_to: Optional[str] = None,
    grayscale: Optional[bool] = None,
    pdf: Optional[bool] = None,
) -> Dict[str, Any]:
    
    if not API_KEY:
        return {"error": "API key not configured. Please set PORCUS_LARDUM_API_KEY environment variable."}
    
    try:
        # Generate client_transform_id if not provided
        import uuid
        if not client_transform_id:
            client_transform_id = str(uuid.uuid4())
        
        # Convert values to Unit objects
        crop_units = None
        if crop_pixels:
            crop_units = [Unit(pixels=p) for p in crop_pixels]
        elif crop_mm:
            crop_units = [Unit(millimeter=p) for p in crop_mm]
        elif crop_inches:
            crop_units = [Unit(inches=p) for p in crop_inches]
        
        crop_box_units = None
        if crop_box_pixels:
            crop_box_units = [[Unit(pixels=p)] for p in crop_box_pixels]
        elif crop_box_mm:
            crop_box_units = [[Unit(millimeter=p)] for p in crop_box_mm]
        elif crop_box_inches:
            crop_box_units = [[Unit(inches=p)] for p in crop_box_inches]
        
        pad_units = None
        if pad_pixels:
            pad_units = [Unit(pixels=p) for p in pad_pixels]
        elif pad_mm:
            pad_units = [Unit(millimeter=p) for p in pad_mm]
        elif pad_inches:
            pad_units = [Unit(inches=p) for p in pad_inches]
        
        contain_units = None
        if contain_pixels:
            contain_units = [Unit(pixels=p) for p in contain_pixels]
        elif contain_mm:
            contain_units = [Unit(millimeter=p) for p in contain_mm]
        elif contain_inches:
            contain_units = [Unit(inches=p) for p in contain_inches]
        
        transform_params = ImageOpsTransformParamsIn(
            image_ops=True,
            crop=crop_units,
            crop_box=crop_box_units,
            crop_aspect_ratio=crop_aspect_ratio,
            pad=pad_units,
            contain=contain_units,
            override_dpi=override_dpi,
            rotate=rotate,
            rotate_to=rotate_to,
            grayscale=grayscale,
            pdf=pdf,
        )
        
        request_body = {
            "source_image_url": source_image_url,
            "output_image_url": output_image_url,
            "client_transform_id": client_transform_id,
            "transform": transform_params.model_dump(exclude_none=True)
        }
        
        # Add source if provided
        if source:
            request_body["source"] = source
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/transform",
                json=request_body,
                headers={
                    "x-api-key": API_KEY,
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "transform_job_id": result.get("transform_job_id"),
                    "client_transform_id": client_transform_id,
                    "message": "Async transformation job queued successfully",
                    "output_url": output_image_url,
                    "status": "queued"
                }
            else:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "details": response.text,
                }
                
    except Exception as e:
        return {"error": f"Failed to queue async transformation: {str(e)}"}

@mcp.prompt()
def crop_image_prompt(x1: int = 0, y1: int = 0, x2: int = 100, y2: int = 100) -> str:
    """
    Prompt for cropping an image to specific coordinates.
    """
    return f"""Please crop the image to the specified region.

Use the transform_image tool with these parameters:
- crop_box_pixels: [{x1}, {y1}, {x2}, {y2}]"""

@mcp.prompt()
def crop_aspect_ratio_prompt(aspect_ratio: float = 1.0) -> str:
    """
    Prompt for cropping to a specific aspect ratio.
    """
    return f"""Please crop the image to an aspect ratio of {aspect_ratio}.

Use the transform_image tool with:
- crop_aspect_ratio: {aspect_ratio}"""

@mcp.prompt()
def contain_image_prompt(width: int = 800, height: int = 600) -> str:
    """
    Prompt for containing an image within specific dimensions.
    """
    return f"""Please contain the image within {width}x{height} pixels.

Use the transform_image tool with:
- contain_pixels: [{width}, {height}]"""

@mcp.prompt()
def rotate_image_prompt(angle: int = 90) -> str:
    """
    Prompt for rotating an image.
    """
    return f"""Please rotate the image by {angle} degrees.

Use the transform_image tool with:
- rotate: {angle}"""

@mcp.prompt()
def convert_to_grayscale_prompt() -> str:
    """
    Prompt for converting an image to grayscale.
    """
    return """Please convert this image to grayscale.

Use the transform_image tool with:
- grayscale: true"""

@mcp.prompt()
def set_dpi_prompt(dpi: int = 300) -> str:
    """
    Prompt for setting image DPI.
    """
    return f"""Please set the image DPI to {dpi}.

Use the transform_image tool with:
- override_dpi: {dpi}"""

@mcp.prompt()
def pad_image_prompt(width: int = 1000, height: int = 800) -> str:
    """
    Prompt for adding padding to an image.
    """
    return f"""Please add padding to expand the canvas to {width}x{height} pixels.

Use the transform_image tool with:
- pad_pixels: [{width}, {height}]"""


if __name__ == "__main__":
    mcp.run(transport="streamable-http")