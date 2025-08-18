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
    overwrite_partial_transparency: Optional[int] = Field(
        None, description="Replace semi-transparent pixels with alpha (0-255)"
    )
    transparency_to_color: Optional[List[int]] = Field(
        None, description="Replace transparency with RGB color [r,g,b]"
    )
    grayscale: Optional[bool] = Field(None, description="Convert to grayscale")
    pdf: Optional[bool] = Field(None, description="Convert output to PDF")
    multi_page: Optional[bool] = Field(
        None, description="Process multi-page PDFs by applying transforms to each page"
    )
    same_pixel_size: Optional[bool] = Field(
        None, description="Maintain pixel size in PDF output"
    )
    stickerise: Optional[Unit] = Field(
        None, description="Add white border for sticker effect"
    )
    expand: Optional[Unit] = Field(
        None, description="Add uniform border by expanding canvas"
    )
    transforms_array: Optional[List[Dict]] = Field(
        None, description="Custom transform sequence array"
    )

class MockupParameters(BaseModel):
    size: List[int] = Field(description="Output dimensions [width, height] in pixels")
    sku: str = Field(description="Product SKU identifier")
    camera: str = Field(description="Camera angle (e.g., 'HeadOn', 'Perspective')")
    orientation: Optional[str] = Field(None, description="Product orientation ('portrait' or 'landscape')")
    color: Optional[str] = Field(None, description="Product color variant")
    wrap: Optional[str] = Field(None, description="Image application method")
    finish: Optional[str] = Field(None, description="Product surface finish")
    blank: Optional[bool] = Field(None, description="Generate empty product preview")

class MockupRequest(BaseModel):
    source_image_url: Optional[str] = Field(None, description="User image to apply to product")
    output_image_url: str = Field(description="URL where mockup will be delivered")
    parameters: MockupParameters = Field(description="Mockup generation parameters")

# @mcp.tool(
#     title="Image Transformer (Sync) - Use async_image_transformation by default!",
#     description="""Transform an image using Porcus Lardum ImageOps transformations (synchronous).
    
#     Parameters:
#     - source_image_url: URL of the image to transform
#     - crop_pixels: Remove pixels from borders [top, right, bottom, left] or single value for all
#     - crop_mm: Remove millimeters from borders [top, right, bottom, left] or single value for all
#     - crop_inches: Remove inches from borders [top, right, bottom, left] or single value for all
#     - crop_box_pixels: Extract rectangle [x1, y1, x2, y2] in pixels
#     - crop_box_mm: Extract rectangle [x1, y1, x2, y2] in millimeters
#     - crop_box_inches: Extract rectangle [x1, y1, x2, y2] in inches
#     - crop_aspect_ratio: Crop to width/height ratio (e.g., 1.77 for 16:9)
#     - pad_pixels: Expand canvas [width, height] in pixels.
#     - pad_mm: Expand canvas [width, height] in millimeters
#     - pad_inches: Expand canvas [width, height] in inches
#     - contain_pixels: Scale to fit within [width, height] in pixels
#     - contain_mm: Scale to fit within [width, height] in millimeters
#     - contain_inches: Scale to fit within [width, height] in inches
#     - override_dpi: Set DPI metadata
#     - rotate: Rotation angle in degrees
#     - rotate_to: Auto-rotate to 'landscape' or 'portrait'
#     - overwrite_partial_transparency: Replace semi-transparent pixels with 
#       alpha value (0-255)
#     - transparency_to_color: Replace transparency with RGB color [r,g,b] 
#       (0-255 each)
#     - grayscale: Convert to grayscale
#     - pdf: Convert output to PDF
#     - multi_page: Process multi-page PDFs by applying transforms to each page
#     - same_pixel_size: Maintain pixel size in PDF output (default: true)
#     - stickerise_pixels: Add white border for sticker or stickerise effect in pixels. If necessary, use the expand_pixels parameter to make sure the image new border doesn't overflow the canvas.
#     - stickerise_mm: Add white border for sticker or stickerise effect in millimeters. If necessary, use the expand_mm parameter to make sure the image new border doesn't overflow the canvas.
#     - stickerise_inches: Add white border for sticker or stickerise effect in inches. If necessary, use the expand_inches parameter to make sure the image new border doesn't overflow the canvas.
#     - expand_pixels: Add uniform border by expanding canvas in pixels. 
#       Useful for padding sticker images.
#     - expand_mm: Add uniform border by expanding canvas in millimeters. 
#       Useful for padding sticker images.
#     - expand_inches: Add uniform border by expanding canvas in inches. 
#       Useful for padding sticker images.

#     Returns the transformed source image URL and metadata."""
# )
# async def transform_image(
#     source_image_url: str,
#     crop_pixels: Optional[List[int]] = None,
#     crop_mm: Optional[List[float]] = None,
#     crop_inches: Optional[List[float]] = None,
#     crop_box_pixels: Optional[List[int]] = None,
#     crop_box_mm: Optional[List[float]] = None,
#     crop_box_inches: Optional[List[float]] = None,
#     crop_aspect_ratio: Optional[float] = None,
#     pad_pixels: Optional[List[int]] = None,
#     pad_mm: Optional[List[float]] = None,
#     pad_inches: Optional[List[float]] = None,
#     contain_pixels: Optional[List[int]] = None,
#     contain_mm: Optional[List[float]] = None,
#     contain_inches: Optional[List[float]] = None,
#     override_dpi: Optional[int] = None,
#     rotate: Optional[int] = None,
#     rotate_to: Optional[str] = None,
#     overwrite_partial_transparency: Optional[int] = None,
#     transparency_to_color: Optional[List[int]] = None,
#     grayscale: Optional[bool] = None,
#     pdf: Optional[bool] = None,
#     multi_page: Optional[bool] = None,
#     same_pixel_size: Optional[bool] = None,
#     stickerise_pixels: Optional[int] = None,
#     stickerise_mm: Optional[float] = None,
#     stickerise_inches: Optional[float] = None,
#     expand_pixels: Optional[int] = None,
#     expand_mm: Optional[float] = None,
#     expand_inches: Optional[float] = None,
# ) -> Dict[str, Any]:
    
#     if not API_KEY:
#         return {"error": "API key not configured. Please set PORCUS_LARDUM_API_KEY environment variable."}
    
#     try:
#         # Convert values to Unit objects
#         crop_units = None
#         if crop_pixels:
#             crop_units = [Unit(pixels=p) for p in crop_pixels]
#         elif crop_mm:
#             crop_units = [Unit(millimeter=p) for p in crop_mm]
#         elif crop_inches:
#             crop_units = [Unit(inches=p) for p in crop_inches]

#         crop_box_units = None
#         if crop_box_pixels:
#             crop_box_units = [[Unit(pixels=p)] for p in crop_box_pixels]
#         elif crop_box_mm:
#             crop_box_units = [[Unit(millimeter=p)] for p in crop_box_mm]
#         elif crop_box_inches:
#             crop_box_units = [[Unit(inches=p)] for p in crop_box_inches]

#         pad_units = None
#         if pad_pixels:
#             pad_units = [Unit(pixels=p) for p in pad_pixels]
#         elif pad_mm:
#             pad_units = [Unit(millimeter=p) for p in pad_mm]
#         elif pad_inches:
#             pad_units = [Unit(inches=p) for p in pad_inches]
        
#         contain_units = None
#         if contain_pixels:
#             contain_units = [Unit(pixels=p) for p in contain_pixels]
#         elif contain_mm:
#             contain_units = [Unit(millimeter=p) for p in contain_mm]
#         elif contain_inches:
#             contain_units = [Unit(inches=p) for p in contain_inches]
        
#         stickerise_unit = None
#         if stickerise_pixels:
#             stickerise_unit = Unit(pixels=stickerise_pixels)
#         elif stickerise_mm:
#             stickerise_unit = Unit(millimeter=stickerise_mm)
#         elif stickerise_inches:
#             stickerise_unit = Unit(inches=stickerise_inches)
        
#         expand_unit = None
#         if expand_pixels:
#             expand_unit = Unit(pixels=expand_pixels)
#         elif expand_mm:
#             expand_unit = Unit(millimeter=expand_mm)
#         elif expand_inches:
#             expand_unit = Unit(inches=expand_inches)
        
#         transform_params = ImageOpsTransformParamsIn(
#             image_ops=True,
#             crop=crop_units,
#             crop_box=crop_box_units,
#             crop_aspect_ratio=crop_aspect_ratio,
#             pad=pad_units,
#             contain=contain_units,
#             override_dpi=override_dpi,
#             rotate=rotate,
#             rotate_to=rotate_to,
#             overwrite_partial_transparency=overwrite_partial_transparency,
#             transparency_to_color=transparency_to_color,
#             grayscale=grayscale,
#             pdf=pdf,
#             multi_page=multi_page,
#             same_pixel_size=same_pixel_size,
#             stickerise=stickerise_unit,
#             expand=expand_unit,
#         )
        
#         request_body = {
#             "source_image_url": source_image_url,
#             "transform": transform_params.model_dump(exclude_none=True)
#         }
        
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 f"{BASE_URL}/sync_transform",
#                 json=request_body,
#                 headers={
#                     "x-api-key": API_KEY,
#                     "Content-Type": "application/json",
#                 },
#                 timeout=30.0,
#             )
            
#             if response.status_code == 200:
#                 # Check if response is JSON or binary image data
#                 content_type = response.headers.get("content-type", "")
#                 if "application/json" in content_type:
#                     result = response.json()
#                     return {
#                         "success": True,
#                         "transformed_url": result.get("url"),
#                         "metadata": result.get("metadata", {}),
#                         "processing_time": result.get("processing_time"),
#                     }
#                 else:
#                     # Response is binary image data
#                     # Save to disk with appropriate extension
#                     ext = "jpg"
#                     if "png" in content_type:
#                         ext = "png"
#                     elif "gif" in content_type:
#                         ext = "gif"
#                     elif "webp" in content_type:
#                         ext = "webp"
                    
#                     filename = f"transformed_image.{ext}"
#                     with open(filename, "wb") as f:
#                         f.write(response.content)
                    
#                     return {
#                         "success": True,
#                         "message": "Image transformed successfully",
#                         "saved_to": filename,
#                         "content_type": content_type,
#                         "size": len(response.content),
#                     }
#             else:
#                 return {
#                     "error": f"API request failed with status {response.status_code}",
#                     "details": response.text,
#                 }
                
#     except Exception as e:
#         return {"error": f"Failed to transform image: {str(e)}"}

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
    title="Image Transformer (Async) - DEFAULT - Use this for transformations!",
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
    - pad_pixels: Expand canvas to a specific size [width, height] in pixels
    - pad_mm: Expand canvas to a specific size [width, height] in millimeters
    - pad_inches: Expand canvas to a specific size [width, height] in inches
    - contain_pixels: Scale to fit within [width, height] in pixels
    - contain_mm: Scale to fit within [width, height] in millimeters
    - contain_inches: Scale to fit within [width, height] in inches
    - override_dpi: Set DPI metadata
    - rotate: Rotation angle in degrees
    - rotate_to: Auto-rotate to 'landscape' or 'portrait'
    - overwrite_partial_transparency: Replace semi-transparent pixels with 
      alpha value (0-255)
    - transparency_to_color: Replace transparency with RGB color [r,g,b] 
      (0-255 each)
    - grayscale: Convert to grayscale
    - pdf: Convert output to PDF
    - multi_page: Process multi-page PDFs by applying transforms to each page
    - same_pixel_size: Maintain pixel size in PDF output (default: true)
    - stickerise_pixels: Add white border for sticker effect or stickerise effect in pixels. 
      Use expand_pixels for padding. If necessary, use the expand_pixels parameter to make sure the image new border doesn't overflow the canvas.
    - stickerise_mm: Add white border for sticker effect or stickerise effect in millimeters. 
      Use expand_mm for padding. If necessary, use the expand_mm parameter to make sure the image new border doesn't overflow the canvas.
    - stickerise_inches: Add white border for sticker effect or stickerise effect in inches. 
      Use expand_inches for padding. If necessary, use the expand_inches parameter to make sure the image new border doesn't overflow the canvas.
    - expand_pixels: Add uniform border by expanding canvas in pixels. 
      Useful for padding sticker images.
    - expand_mm: Add uniform border by expanding canvas in millimeters. 
      Useful for padding sticker images.
    - expand_inches: Add uniform border by expanding canvas in inches. 
      Useful for padding sticker images.

    Returns a transform_job_id for tracking the asynchronous job.

    * If user didn't provide a output_image_url, a new temporary URL will be generated using the temp_blob tool
    * Very Important:Always return the signed url output_image_url when completing the task.
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
    overwrite_partial_transparency: Optional[int] = None,
    transparency_to_color: Optional[List[int]] = None,
    grayscale: Optional[bool] = None,
    pdf: Optional[bool] = None,
    multi_page: Optional[bool] = None,
    same_pixel_size: Optional[bool] = None,
    stickerise_pixels: Optional[int] = None,
    stickerise_mm: Optional[float] = None,
    stickerise_inches: Optional[float] = None,
    expand_pixels: Optional[int] = None,
    expand_mm: Optional[float] = None,
    expand_inches: Optional[float] = None,
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
        
        stickerise_unit = None
        if stickerise_pixels:
            stickerise_unit = Unit(pixels=stickerise_pixels)
        elif stickerise_mm:
            stickerise_unit = Unit(millimeter=stickerise_mm)
        elif stickerise_inches:
            stickerise_unit = Unit(inches=stickerise_inches)
        
        expand_unit = None
        if expand_pixels:
            expand_unit = Unit(pixels=expand_pixels)
        elif expand_mm:
            expand_unit = Unit(millimeter=expand_mm)
        elif expand_inches:
            expand_unit = Unit(inches=expand_inches)
        
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
            overwrite_partial_transparency=overwrite_partial_transparency,
            transparency_to_color=transparency_to_color,
            grayscale=grayscale,
            pdf=pdf,
            multi_page=multi_page,
            same_pixel_size=same_pixel_size,
            stickerise=stickerise_unit,
            expand=expand_unit,
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

Use the async_image_transformation tool with these parameters:
- crop_box_pixels: [{x1}, {y1}, {x2}, {y2}]"""

@mcp.prompt()
def crop_aspect_ratio_prompt(aspect_ratio: float = 1.0) -> str:
    """
    Prompt for cropping to a specific aspect ratio.
    """
    return f"""Please crop the image to an aspect ratio of {aspect_ratio}.

Use the async_image_transformation tool with:
- crop_aspect_ratio: {aspect_ratio}"""

@mcp.prompt()
def contain_image_prompt(width: int = 800, height: int = 600) -> str:
    """
    Prompt for containing an image within specific dimensions.
    """
    return f"""Please contain the image within {width}x{height} pixels.

Use the async_image_transformation tool with:
- contain_pixels: [{width}, {height}]"""

@mcp.prompt()
def rotate_image_prompt(angle: int = 90) -> str:
    """
    Prompt for rotating an image.
    """
    return f"""Please rotate the image by {angle} degrees.

Use the async_image_transformation tool with:
- rotate: {angle}"""

@mcp.prompt()
def convert_to_grayscale_prompt() -> str:
    """
    Prompt for converting an image to grayscale.
    """
    return """Please convert this image to grayscale.

Use the async_image_transformation tool with:
- grayscale: true"""

@mcp.prompt()
def set_dpi_prompt(dpi: int = 300) -> str:
    """
    Prompt for setting image DPI.
    """
    return f"""Please set the image DPI to {dpi}.

Use the async_image_transformation tool with:
- override_dpi: {dpi}"""

@mcp.prompt()
def pad_image_prompt(width: int = 1000, height: int = 800) -> str:
    """
    Prompt for adding padding to an image.
    """
    return f"""Please add padding to expand the canvas to {width}x{height} pixels.

Use the async_image_transformation tool with:
- pad_pixels: [{width}, {height}]"""

@mcp.prompt()
def stickerise_image_prompt(border_size: int = 20) -> str:
    """
    Prompt for adding a sticker effect border to an image.
    """
    return f"""Please 'stickerise' or add a white border sticker effect to the image.

Use the async_image_transformation tool with:
- stickerise_inches: {border_size}
- expand_inches: {border_size+(border_size*20/100)}
where expand_inches must be larger than stickerise_inches."""

@mcp.prompt()
def expand_border_prompt(border_size: int = 10) -> str:
    """
    Prompt for expanding canvas with a uniform border.
    """
    return f"""Please expand the canvas by adding a {border_size}px border on all sides.

Use the async_image_transformation tool with:
- expand_pixels: {border_size}"""

@mcp.prompt()
def transparency_to_white_prompt() -> str:
    """
    Prompt for replacing transparency with white background.
    """
    return """Please replace transparent areas with a white background.

Use the async_image_transformation tool with:
- transparency_to_color: [255, 255, 255]"""

@mcp.prompt()
def clean_transparency_prompt(alpha_value: int = 255) -> str:
    """
    Prompt for cleaning up semi-transparent pixels.
    """
    return f"""Please clean up semi-transparent pixels by setting them to alpha {alpha_value}.

Use the async_image_transformation tool with:
- overwrite_partial_transparency: {alpha_value}"""


@mcp.prompt()
def create_sticker_with_padding_prompt(sticker_border: int = 20, padding: int = 15) -> str:
    """
    Prompt for creating a sticker effect with proper padding.
    """
    return f"""Please create a sticker effect with a {sticker_border}px white border and {padding}px padding.

Use the async_image_transformation tool with:
- stickerise_pixels: {sticker_border}
- expand_pixels: {padding}"""


@mcp.prompt()
def pdf_multipage_processing_prompt() -> str:
    """
    Prompt for processing multi-page PDFs.
    """
    return """Please process this multi-page PDF by applying transforms to each page.

Use the async_image_transformation tool with:
- pdf: true
- multi_page: true
- same_pixel_size: true"""


@mcp.prompt()
def transparency_to_black_prompt() -> str:
    """
    Prompt for replacing transparency with black background.
    """
    return """Please replace transparent areas with a black background.

Use the async_image_transformation tool with:
- transparency_to_color: [0, 0, 0]"""


@mcp.prompt()
def transparency_to_custom_color_prompt(red: int = 128, green: int = 128, blue: int = 128) -> str:
    """
    Prompt for replacing transparency with custom RGB color.
    """
    return f"""Please replace transparent areas with RGB color ({red}, {green}, {blue}).

Use the async_image_transformation tool with:
- transparency_to_color: [{red}, {green}, {blue}]"""


@mcp.prompt()
def create_print_ready_image_prompt(dpi: int = 300) -> str:
    """
    Prompt for creating a print-ready image with specific DPI.
    """
    return f"""Please create a print-ready image with {dpi} DPI and clean transparency.

Use the async_image_transformation tool with:
- transparency_to_color: [255, 255, 255]
- pdf: true
- same_pixel_size: true"""


@mcp.prompt()
def sticker_design_workflow_prompt(size_mm: float = 10.0) -> str:
    """
    Prompt for a complete sticker design workflow.
    """
    return f"""Please create a sticker design with {size_mm}mm border and proper formatting.

Use the async_image_transformation tool with:
- stickerise_mm: {size_mm}
- expand_mm: {size_mm * 0.5}"""


@mcp.prompt()
def remove_background_prompt() -> str:
    """
    Prompt for removing background from an image.
    """
    return """Please remove the background from this image using AI processing.

Use the remove_background tool to automatically detect and remove the background,
leaving only the main subject with transparent background."""

@mcp.prompt()
def create_product_mockup_prompt(sku: str = "tshirt-basic", 
                                camera: str = "HeadOn") -> str:
    """
    Prompt for creating a product mockup.
    """
    return f"""Please create a product mockup using the specified design.

Steps:
1. Ensure source image is sized to exactly the SKU size with get_prodigi_product_specs_prompt with sku: {sku}
3. Pad the image to match the Produt/SKU size async_image_transformation pad_pixels [x,y]
2. Validate the SKU is available for generating Mockups and get its parameters using validate_mockup_sku with sku: {sku}
3. Pad the image to match the Product/SKU size async_image_transformation pad_pixels [x,y]
4. Generate a temp blob URL for the output
5. Use generate_product_mockup with:
   - sku: {sku}
   - camera: {camera}
   - width: 1200, height: 1200
   - source_image_url: [your design image URL]
   - output_image_url: [generated temp blob URL]"""

@mcp.prompt()
def blank_product_preview_prompt(sku: str = "hoodie-basic") -> str:
    """
    Prompt for generating blank product previews.
    """
    return f"""Please generate blank product previews for catalog display.

Steps:
1. Validate SKU {sku} using validate_mockup_sku
2. Generate mockup with blank: true (no user design applied)
3. Use standard e-commerce dimensions: 1000x1000
4. Try multiple camera angles if available
5. This shows the base product without any custom design"""

@mcp.prompt()
def browse_mockups_catalog_prompt() -> str:
    """
    Prompt for browsing the available mockups catalog.
    """
    return """Please show me the available product mockups catalog.

Use the list_available_mockups tool to:
1. Get the complete list of available products
2. Show product categories and SKUs
3. Display available camera angles and orientations
4. List color variants and customization options
5. Help me choose the right product for my design"""

@mcp.prompt()
def get_prodigi_product_specs_prompt(sku: str = "GLOBAL-CFP-18X24") -> str:
    """
    Prompt for getting detailed product specifications including pixel dimensions for a SKU.
    """
    return f"""Please get the detailed specifications and pixel dimensions for product SKU {sku}.

Use the get_product_pixel_dimensions tool with:
- sku: {sku}

This will return:
- Exact pixel dimensions needed for image preparation
- Physical dimensions and product details
- Available color variants and finishes
- Print area specifications for optimal image sizing"""


@mcp.tool(
    title="Remove Background",
    description="""Remove background from an image using AI processing.
    
    Parameters:
    - source_image_url: URL of the image to process
    - output_image_url: (optional) URL where the processed image will be delivered
    - client_transform_id: Optional client ID for tracking (default: generated UUID)
    - source: Optional source identifier for job correlation
    
    This uses AI-powered background removal on Azure Kubernetes GPU cluster.
    Returns a transform_job_id for tracking the asynchronous job.
    
    * If user didn't provide output_image_url, use generate_temp_blob tool first
    * Always return the output_image_url when completing the task."""
)
async def remove_background(
    source_image_url: str,
    output_image_url: str,
) -> Dict[str, Any]:
    
    if not API_KEY:
        return {"error": "API key not configured. Please set PORCUS_LARDUM_API_KEY environment variable."}
    
    try:
        # Generate client_transform_id if not provided
        import uuid
        if not client_transform_id:
            client_transform_id = str(uuid.uuid4())
        
        request_body = {
            "source_image_url": source_image_url,
            "output_image_url": output_image_url,
            "client_transform_id": client_transform_id,
            "transform": {
                "remove_background": True
            }
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
                    "message": "Background removal job queued successfully",
                    "output_url": output_image_url,
                    "status": "queued"
                }
            else:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "details": response.text,
                }
                
    except Exception as e:
        return {"error": f"Failed to queue background removal: {str(e)}"}


@mcp.tool(
    title="Validate Mockup SKU",
    description="""Validate a product SKU and retrieve available mockup parameters.
    
    Parameters:
    - sku: Product SKU identifier to validate
    
    Returns available camera angles, colors, orientations, and other 
    customization options for the specified product."""
)
async def validate_mockup_sku(sku: str) -> Dict[str, Any]:
    
    if not API_KEY:
        return {
            "error": "API key not configured. Please set "
                     "PORCUS_LARDUM_API_KEY environment variable."
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/mockup/{sku}",
                headers={
                    "x-api-key": API_KEY,
                },
                timeout=30.0,
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "sku": sku,
                    "valid": True,
                    "parameters": result,
                    "message": f"SKU {sku} is valid and ready for mockup generation"
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "sku": sku,
                    "valid": False,
                    "error": f"SKU {sku} not found or not available for mockups"
                }
            else:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "details": response.text,
                }
                
    except Exception as e:
        return {"error": f"Failed to validate SKU: {str(e)}"}


@mcp.tool(
    title="List Available Mockups",
    description="""Get a complete list of all available product mockups with their parameters.
    
    Returns a comprehensive catalog of all available products including:
    - Product SKUs and names
    - Available camera angles
    - Supported orientations
    - Color variants
    - Product categories
    - Dimensions and specifications
    
    Use this to discover available products before creating mockups."""
)
async def list_available_mockups() -> Dict[str, Any]:
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://blender-mockups-func-dev.azurewebsites.net/api/json",
                timeout=30.0,
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "mockups": result,
                    "total_products": len(result) if isinstance(result, list) else "unknown",
                    "message": "Successfully retrieved available mockups catalog"
                }
            else:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "details": response.text,
                }
                
    except Exception as e:
        return {"error": f"Failed to fetch mockups catalog: {str(e)}"}


@mcp.tool(
    title="Get Product Pixel Dimensions",
    description="""Get pixel dimensions and product details from Prodigi API.
    
    Parameters:
    - sku: Product SKU identifier (e.g., 'GLOBAL-CFP-18X24')
    - api_key: Prodigi API key for authentication
    
    Returns detailed product information including:
    - Print area pixel dimensions (horizontalResolution, verticalResolution)
    - Physical dimensions and units
    - Available colors, finishes, and variants
    - Shipping regions
    - Product description and attributes
    
    This is essential for determining the correct pixel dimensions for image preparation."""
)
async def get_product_pixel_dimensions(sku: str) -> Dict[str, Any]:
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.sandbox.prodigi.com/v4.0/products/{sku}",
                headers={
                    "X-API-Key": "test_90fc77b9-0407-4c0d-99af-c531fe047363",
                },
                timeout=30.0,
            )
            
            if response.status_code == 200:
                result = response.json()
                product = result.get("product", {})
                
                # Extract pixel dimensions from first variant
                pixel_dimensions = None
                variants = product.get("variants", [])
                if variants:
                    first_variant = variants[0]
                    print_area_sizes = first_variant.get("printAreaSizes", {})
                    default_area = print_area_sizes.get("default", {})
                    if default_area:
                        pixel_dimensions = {
                            "width": default_area.get("horizontalResolution"),
                            "height": default_area.get("verticalResolution")
                        }
                
                return {
                    "success": True,
                    "sku": sku,
                    "description": product.get("description"),
                    "physical_dimensions": product.get("productDimensions", {}),
                    "pixel_dimensions": pixel_dimensions,
                    "attributes": product.get("attributes", {}),
                    "available_colors": product.get("attributes", {}).get("color", []),
                    "variants_count": len(variants),
                    "product_data": product
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "sku": sku,
                    "error": f"Product SKU {sku} not found"
                }
            else:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "details": response.text,
                }
                
    except Exception as e:
        return {"error": f"Failed to get product dimensions: {str(e)}"}


@mcp.tool(
    title="Generate Product Mockup",
    description="""Generate a 3D product mockup using Blender rendering.
    
    Parameters:
    - sku: Product SKU identifier (validate first with validate_mockup_sku)
    - width: Output image width in pixels
    - height: Output image height in pixels  
    - camera: Camera angle (e.g., 'HeadOn', 'Perspective')
    - output_image_url: URL where mockup will be delivered
    - source_image_url: (optional) User image to apply to product
    - orientation: Product orientation ('portrait' or 'landscape')
    - color: Product color variant
    - wrap: Image application method
    - finish: Product surface finish
    - blank: Generate empty product preview without user image
    
    This creates photo-realistic 3D mockups for e-commerce and marketing.
    Always validate the SKU first to ensure compatibility."""
)
async def generate_product_mockup(
    sku: str,
    width: int,
    height: int,
    camera: str,
    output_image_url: str,
    source_image_url: Optional[str] = None,
    orientation: Optional[str] = None,
    color: Optional[str] = None,
    wrap: Optional[str] = None,
    finish: Optional[str] = None,
    blank: Optional[bool] = None,
) -> Dict[str, Any]:
    
    if not API_KEY:
        return {
            "error": "API key not configured. Please set "
                     "PORCUS_LARDUM_API_KEY environment variable."
        }
    
    try:
        mockup_parameters = MockupParameters(
            size=[width, height],
            sku=sku,
            camera=camera,
            orientation=orientation,
            color=color,
            wrap=wrap,
            finish=finish,
            blank=blank,
        )
        
        mockup_request = MockupRequest(
            source_image_url=source_image_url,
            output_image_url=output_image_url,
            parameters=mockup_parameters,
        )
        
        request_body = mockup_request.model_dump(exclude_none=True)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/mockup",
                json=request_body,
                headers={
                    "x-api-key": API_KEY,
                    "Content-Type": "application/json",
                },
                timeout=60.0,  # Mockups may take longer
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "result": result,
                    "sku": sku,
                    "output_url": output_image_url,
                    "dimensions": [width, height],
                    "camera": camera,
                    "message": "Mockup generation job queued successfully",
                    "status": "queued"
                }
            else:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "details": response.text,
                }
                
    except Exception as e:
        return {"error": f"Failed to generate mockup: {str(e)}"}


@mcp.tool(
    title="Get OpenAPI Schema",
    description="""Fetch the complete OpenAPI schema from Porcus Lardum API to aid with code generation.
    
    Returns the raw OpenAPI specification JSON which contains all available endpoints,
    parameters, schemas, and documentation to help with building integrations and
    generating client code."""
)
async def get_openapi_schema() -> Dict[str, Any]:
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/openapi.json",
                timeout=30.0,
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"Failed to fetch OpenAPI schema. Status: {response.status_code}",
                    "details": response.text,
                }
                
    except Exception as e:
        return {"error": f"Failed to fetch OpenAPI schema: {str(e)}"}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
