import json
import os
import logging
from typing import Optional, Dict, List
import httpx
from pydantic import BaseModel, Field
import azure.functions as func


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
API_KEY = os.getenv("PORCUS_LARDUM_API_KEY", "")
BASE_URL = os.getenv("PORCUS_LARDUM_BASE_URL", "https://porcus-lardum-func-dev.azurewebsites.net")

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


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="hello_mcp",
    description="Hello world.",
    toolProperties="[]",
)
def hello_mcp(context) -> str:
    """
    A simple function that returns a greeting message.

    Args:
        context: The trigger context (not used in this function).

    Returns:
        str: A greeting message.
    """
    return "Hello I am MCPTool!"

# @app.generic_trigger(
#     arg_name="context",
#     type="mcpToolTrigger",
#     toolName="generate_temp_blob",
#     description="Generate a temporary blob SAS URL with write and read permissions for image storage.",
#     toolProperties="[{\"name\": \"extension\", \"description\": \"File extension (png, jpg, pdf)\", \"required\": false}]",
# )
# def generate_temp_blob(context: func.Context) -> func.HttpResponse:
#     """Generate a temporary blob SAS URL with write and read permissions."""
    
#     if not API_KEY:
#         return func.HttpResponse(
#             json.dumps({"error": "API key not configured. Please set PORCUS_LARDUM_API_KEY environment variable."}),
#             status_code=500,
#             mimetype="application/json"
#         )
    
#     try:
#         req = context.req
#         body = req.get_json()
#         extension = body.get("extension") if body else None
        
#         params = {}
#         if extension and extension in ['png', 'jpg', 'pdf']:
#             params['extension'] = extension
        
#         # Use sync httpx for Azure Functions
#         with httpx.Client() as client:
#             response = client.get(
#                 f"{BASE_URL}/temp_blob",
#                 params=params,
#                 headers={
#                     "x-api-key": API_KEY,
#                 },
#                 timeout=30.0,
#             )
            
#             if response.status_code == 200:
#                 temp_url = response.text.strip().strip('"')
#                 return func.HttpResponse(
#                     json.dumps({
#                         "success": True,
#                         "temp_url": temp_url,
#                         "extension": extension or "no extension",
#                     }),
#                     mimetype="application/json"
#                 )
#             else:
#                 return func.HttpResponse(
#                     json.dumps({
#                         "error": f"API request failed with status {response.status_code}",
#                         "details": response.text,
#                     }),
#                     status_code=response.status_code,
#                     mimetype="application/json"
#                 )

#     except Exception as e:
#         logging.error(f"Error generating temp blob: {str(e)}")
#         return func.HttpResponse(
#             json.dumps({"error": f"Failed to generate temp blob URL: {str(e)}"}),
#             status_code=500,
#             mimetype="application/json"
#         )

# @app.generic_trigger(
#     arg_name="context",
#     type="mcpToolTrigger",
#     toolName="async_image_transformation",
#     description="Queue an image transformation job for asynchronous processing using ImageOps transforms.",
#     toolProperties="[{\"name\": \"source_image_url\", \"description\": \"URL of the source image to transform\", \"required\": true}, {\"name\": \"output_image_url\", \"description\": \"URL where the transformed image will be stored\", \"required\": true}, {\"name\": \"crop_pixels\", \"description\": \"Remove pixels from borders [top, right, bottom, left]\", \"required\": false}, {\"name\": \"crop_aspect_ratio\", \"description\": \"Crop to specific width/height ratio\", \"required\": false}, {\"name\": \"rotate\", \"description\": \"Rotate image in degrees\", \"required\": false}, {\"name\": \"grayscale\", \"description\": \"Convert to grayscale (true/false)\", \"required\": false}]",
# )
# def async_image_transformation(context: func.Context) -> func.HttpResponse:
#     """Queue an image transformation job for asynchronous processing."""
    
#     if not API_KEY:
#         return func.HttpResponse(
#             json.dumps({"error": "API key not configured. Please set PORCUS_LARDUM_API_KEY environment variable."}),
#             status_code=500,
#             mimetype="application/json"
#         )
    
#     try:
#         req = context.req
#         body = req.get_json()
#         if not body:
#             return func.HttpResponse(
#                 json.dumps({"error": "Request body is required"}),
#                 status_code=400,
#                 mimetype="application/json"
#             )
        
#         source_image_url = body.get("source_image_url")
#         output_image_url = body.get("output_image_url")
        
#         if not source_image_url or not output_image_url:
#             return func.HttpResponse(
#                 json.dumps({"error": "source_image_url and output_image_url are required"}),
#                 status_code=400,
#                 mimetype="application/json"
#             )
        
#         client_transform_id = body.get("client_transform_id")
#         if not client_transform_id:
#             import uuid
#             client_transform_id = str(uuid.uuid4())
        
#         # Convert transformation parameters to Unit objects
#         crop_units = None
#         crop_pixels = body.get("crop_pixels")
#         crop_mm = body.get("crop_mm") 
#         crop_inches = body.get("crop_inches")
        
#         if crop_pixels:
#             crop_units = [Unit(pixels=p) for p in crop_pixels]
#         elif crop_mm:
#             crop_units = [Unit(millimeter=p) for p in crop_mm]
#         elif crop_inches:
#             crop_units = [Unit(inches=p) for p in crop_inches]
        
#         # Handle crop_box parameters
#         crop_box_units = None
#         crop_box_pixels = body.get("crop_box_pixels")
#         crop_box_mm = body.get("crop_box_mm")
#         crop_box_inches = body.get("crop_box_inches")
#         crop_box_pixels_offset = body.get("crop_box_pixels_offset")
#         crop_box_mm_offset = body.get("crop_box_mm_offset")
#         crop_box_inches_offset = body.get("crop_box_inches_offset")
        
#         if crop_box_pixels:
#             crop_box_units = [[Unit(pixels=p) for p in crop_box_pixels]] if not crop_box_pixels_offset else [
#                 [Unit(pixels=p) for p in crop_box_pixels],
#                 [Unit(pixels=p) for p in crop_box_pixels_offset]
#             ]
#         elif crop_box_mm:
#             crop_box_units = [[Unit(millimeter=p) for p in crop_box_mm]] if not crop_box_mm_offset else [
#                 [Unit(millimeter=p) for p in crop_box_mm],
#                 [Unit(millimeter=p) for p in crop_box_mm_offset]
#             ]
#         elif crop_box_inches:
#             crop_box_units = [[Unit(inches=p) for p in crop_box_inches]] if not crop_box_inches_offset else [
#                 [Unit(inches=p) for p in crop_box_inches],
#                 [Unit(inches=p) for p in crop_box_inches_offset]
#             ]

#         # Handle pad parameters
#         pad_units = None
#         pad_pixels = body.get("pad_pixels")
#         pad_mm = body.get("pad_mm")
#         pad_inches = body.get("pad_inches")
        
#         if pad_pixels:
#             pad_units = [Unit(pixels=p) for p in pad_pixels]
#         elif pad_mm:
#             pad_units = [Unit(millimeter=p) for p in pad_mm]
#         elif pad_inches:
#             pad_units = [Unit(inches=p) for p in pad_inches]
        
#         # Handle contain parameters
#         contain_units = None
#         contain_pixels = body.get("contain_pixels")
#         contain_mm = body.get("contain_mm")
#         contain_inches = body.get("contain_inches")
        
#         if contain_pixels:
#             contain_units = [Unit(pixels=p) for p in contain_pixels]
#         elif contain_mm:
#             contain_units = [Unit(millimeter=p) for p in contain_mm]
#         elif contain_inches:
#             contain_units = [Unit(inches=p) for p in contain_inches]
        
#         # Handle stickerise parameters
#         stickerise_unit = None
#         stickerise_pixels = body.get("stickerise_pixels")
#         stickerise_mm = body.get("stickerise_mm")
#         stickerise_inches = body.get("stickerise_inches")
        
#         if stickerise_pixels:
#             stickerise_unit = Unit(pixels=stickerise_pixels)
#         elif stickerise_mm:
#             stickerise_unit = Unit(millimeter=stickerise_mm)
#         elif stickerise_inches:
#             stickerise_unit = Unit(inches=stickerise_inches)
        
#         # Handle expand parameters
#         expand_unit = None
#         expand_pixels = body.get("expand_pixels")
#         expand_mm = body.get("expand_mm")
#         expand_inches = body.get("expand_inches")
        
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
#             crop_aspect_ratio=body.get("crop_aspect_ratio"),
#             pad=pad_units,
#             contain=contain_units,
#             override_dpi=body.get("override_dpi"),
#             rotate=body.get("rotate"),
#             rotate_to=body.get("rotate_to"),
#             overwrite_partial_transparency=body.get("overwrite_partial_transparency"),
#             transparency_to_color=body.get("transparency_to_color"),
#             grayscale=body.get("grayscale"),
#             pdf=body.get("pdf"),
#             multi_page=body.get("multi_page"),
#             same_pixel_size=body.get("same_pixel_size"),
#             stickerise=stickerise_unit,
#             expand=expand_unit,
#         )
        
#         request_body = {
#             "source_image_url": source_image_url,
#             "output_image_url": output_image_url,
#             "client_transform_id": client_transform_id,
#             "transform": transform_params.model_dump(exclude_none=True)
#         }
        
#         # Add source if provided
#         source = body.get("source")
#         if source:
#             request_body["source"] = source
        
#         with httpx.Client() as client:
#             response = client.post(
#                 f"{BASE_URL}/transform",
#                 json=request_body,
#                 headers={
#                     "x-api-key": API_KEY,
#                     "Content-Type": "application/json",
#                 },
#                 timeout=30.0,
#             )
            
#             if response.status_code == 200:
#                 result = response.json()
#                 return func.HttpResponse(
#                     json.dumps({
#                         "success": True,
#                         "transform_job_id": result.get("transform_job_id"),
#                         "client_transform_id": client_transform_id,
#                         "message": "Async transformation job queued successfully",
#                         "output_url": output_image_url,
#                         "raw_request_body": json.dumps(request_body),
#                         "status": "queued"
#                     }),
#                     mimetype="application/json"
#                 )
#             else:
#                 return func.HttpResponse(
#                     json.dumps({
#                         "error": f"API request failed with status {response.status_code}",
#                         "details": response.text,
#                     }),
#                     status_code=response.status_code,
#                     mimetype="application/json"
#                 )
                
#     except Exception as e:
#         logging.error(f"Error in async image transformation: {str(e)}")
#         return func.HttpResponse(
#             json.dumps({"error": f"Failed to queue async transformation: {str(e)}"}),
#             status_code=500,
#             mimetype="application/json"
#         )

# @app.generic_trigger(
#     arg_name="context",
#     type="mcpToolTrigger",
#     toolName="remove_background",
#     description="Remove background from an image using AI processing.",
#     toolProperties="[{\"name\": \"source_image_url\", \"description\": \"URL of the source image\", \"required\": true}, {\"name\": \"output_image_url\", \"description\": \"URL where the processed image will be stored\", \"required\": true}]",
# )
# def remove_background(context: func.Context) -> func.HttpResponse:
#     """Remove background from an image using AI processing."""
    
#     if not API_KEY:
#         return func.HttpResponse(
#             json.dumps({"error": "API key not configured. Please set PORCUS_LARDUM_API_KEY environment variable."}),
#             status_code=500,
#             mimetype="application/json"
#         )
    
#     try:
#         req = context.req
#         body = req.get_json()
#         if not body:
#             return func.HttpResponse(
#                 json.dumps({"error": "Request body is required"}),
#                 status_code=400,
#                 mimetype="application/json"
#             )
        
#         source_image_url = body.get("source_image_url")
#         output_image_url = body.get("output_image_url")
        
#         if not source_image_url or not output_image_url:
#             return func.HttpResponse(
#                 json.dumps({"error": "source_image_url and output_image_url are required"}),
#                 status_code=400,
#                 mimetype="application/json"
#             )
        
#         request_body = {
#             "source_image_url": source_image_url,
#             "output_image_url": output_image_url,
#             "transform": {
#                 "remove_background": True
#             }
#         }
        
#         with httpx.Client() as client:
#             response = client.post(
#                 f"{BASE_URL}/transform",
#                 json=request_body,
#                 headers={
#                     "x-api-key": API_KEY,
#                     "Content-Type": "application/json",
#                 },
#                 timeout=30.0,
#             )
            
#             if response.status_code == 200:
#                 result = response.json()
#                 return func.HttpResponse(
#                     json.dumps({
#                         "success": True,
#                         "transform_job_id": result.get("transform_job_id"),
#                         "message": "Background removal job queued successfully",
#                         "output_url": output_image_url,
#                         "raw_request_body": json.dumps(request_body),
#                         "status": "queued"
#                     }),
#                     mimetype="application/json"
#                 )
#             else:
#                 return func.HttpResponse(
#                     json.dumps({
#                         "error": f"API request failed with status {response.status_code}",
#                         "details": response.text,
#                     }),
#                     status_code=response.status_code,
#                     mimetype="application/json"
#                 )
                
#     except Exception as e:
#         logging.error(f"Error removing background: {str(e)}")
#         return func.HttpResponse(
#             json.dumps({"error": f"Failed to queue background removal: {str(e)}"}),
#             status_code=500,
#             mimetype="application/json"
#         )

# @app.generic_trigger(
#     arg_name="context",
#     type="mcpToolTrigger",
#     toolName="validate_mockup_sku",
#     description="Validate a product SKU and retrieve available mockup parameters.",
#     toolProperties="[{\"name\": \"sku\", \"description\": \"Product SKU identifier to validate\", \"required\": true}]",
# )
# def validate_mockup_sku(context: func.Context) -> func.HttpResponse:
#     """Validate a product SKU and retrieve available mockup parameters."""
    
#     if not API_KEY:
#         return func.HttpResponse(
#             json.dumps({"error": "API key not configured. Please set PORCUS_LARDUM_API_KEY environment variable."}),
#             status_code=500,
#             mimetype="application/json"
#         )
    
#     try:
#         req = context.req
#         body = req.get_json()
#         if not body:
#             return func.HttpResponse(
#                 json.dumps({"error": "Request body is required"}),
#                 status_code=400,
#                 mimetype="application/json"
#             )
        
#         sku = body.get("sku")
#         if not sku:
#             return func.HttpResponse(
#                 json.dumps({"error": "sku is required"}),
#                 status_code=400,
#                 mimetype="application/json"
#             )
        
#         with httpx.Client() as client:
#             response = client.get(
#                 f"{BASE_URL}/mockup/{sku}",
#                 headers={
#                     "x-api-key": API_KEY,
#                 },
#                 timeout=30.0,
#             )
            
#             if response.status_code == 200:
#                 result = response.json()
#                 return func.HttpResponse(
#                     json.dumps({
#                         "success": True,
#                         "sku": sku,
#                         "valid": True,
#                         "parameters": result,
#                         "message": f"SKU {sku} is valid and ready for mockup generation"
#                     }),
#                     mimetype="application/json"
#                 )
#             elif response.status_code == 404:
#                 return func.HttpResponse(
#                     json.dumps({
#                         "success": False,
#                         "sku": sku,
#                         "valid": False,
#                         "error": f"SKU {sku} not found or not available for mockups"
#                     }),
#                     status_code=404,
#                     mimetype="application/json"
#                 )
#             else:
#                 return func.HttpResponse(
#                     json.dumps({
#                         "error": f"API request failed with status {response.status_code}",
#                         "details": response.text,
#                     }),
#                     status_code=response.status_code,
#                     mimetype="application/json"
#                 )
                
#     except Exception as e:
#         logging.error(f"Error validating SKU: {str(e)}")
#         return func.HttpResponse(
#             json.dumps({"error": f"Failed to validate SKU: {str(e)}"}),
#             status_code=500,
#             mimetype="application/json"
#         )

# @app.generic_trigger(
#     arg_name="context",
#     type="mcpToolTrigger",
#     toolName="generate_product_mockup",
#     description="Generate a 3D product mockup using Blender rendering.",
#     toolProperties="[{\"name\": \"sku\", \"description\": \"Product SKU identifier\", \"required\": true}, {\"name\": \"width\", \"description\": \"Output width in pixels\", \"required\": true}, {\"name\": \"height\", \"description\": \"Output height in pixels\", \"required\": true}, {\"name\": \"camera\", \"description\": \"Camera angle (HeadOn, Perspective)\", \"required\": true}, {\"name\": \"output_image_url\", \"description\": \"URL where mockup will be stored\", \"required\": true}, {\"name\": \"source_image_url\", \"description\": \"User image to apply to product\", \"required\": false}]",
# )
# def generate_product_mockup(context: func.Context) -> func.HttpResponse:
#     """Generate a 3D product mockup using Blender rendering."""
    
#     if not API_KEY:
#         return func.HttpResponse(
#             json.dumps({"error": "API key not configured. Please set PORCUS_LARDUM_API_KEY environment variable."}),
#             status_code=500,
#             mimetype="application/json"
#         )
    
#     try:
#         req = context.req
#         body = req.get_json()
#         if not body:
#             return func.HttpResponse(
#                 json.dumps({"error": "Request body is required"}),
#                 status_code=400,
#                 mimetype="application/json"
#             )
        
#         # Extract required parameters
#         sku = body.get("sku")
#         width = body.get("width")
#         height = body.get("height")
#         camera = body.get("camera")
#         output_image_url = body.get("output_image_url")
        
#         if not all([sku, width, height, camera, output_image_url]):
#             return func.HttpResponse(
#                 json.dumps({"error": "sku, width, height, camera, and output_image_url are required"}),
#                 status_code=400,
#                 mimetype="application/json"
#             )
        
#         mockup_parameters = MockupParameters(
#             size=[width, height],
#             sku=sku,
#             camera=camera,
#             orientation=body.get("orientation"),
#             color=body.get("color"),
#             wrap=body.get("wrap"),
#             finish=body.get("finish"),
#             blank=body.get("blank"),
#         )
        
#         mockup_request = MockupRequest(
#             source_image_url=body.get("source_image_url"),
#             output_image_url=output_image_url,
#             parameters=mockup_parameters,
#         )
        
#         request_body = mockup_request.model_dump(exclude_none=True)
        
#         with httpx.Client() as client:
#             response = client.post(
#                 f"{BASE_URL}/mockup",
#                 json=request_body,
#                 headers={
#                     "x-api-key": API_KEY,
#                     "Content-Type": "application/json",
#                 },
#                 timeout=60.0,
#             )
            
#             if response.status_code == 200:
#                 result = response.json()
#                 return func.HttpResponse(
#                     json.dumps({
#                         "success": True,
#                         "result": result,
#                         "sku": sku,
#                         "output_url": output_image_url,
#                         "dimensions": [width, height],
#                         "camera": camera,
#                         "message": "Mockup generation job queued successfully",
#                         "status": "queued"
#                     }),
#                     mimetype="application/json"
#                 )
#             else:
#                 return func.HttpResponse(
#                     json.dumps({
#                         "error": f"API request failed with status {response.status_code}",
#                         "details": response.text,
#                     }),
#                     status_code=response.status_code,
#                     mimetype="application/json"
#                 )
                
#     except Exception as e:
#         logging.error(f"Error generating mockup: {str(e)}")
#         return func.HttpResponse(
#             json.dumps({"error": f"Failed to generate mockup: {str(e)}"}),
#             status_code=500,
#             mimetype="application/json"
#         )

# # MCP Prompts for common image transformations
# @app.generic_trigger(
#     arg_name="context",
#     type="mcpPromptTrigger",
#     promptName="crop_image_square",
#     description="Crop an image to a square aspect ratio (1:1) from the center.",
# )
# def crop_image_square_prompt(context: func.Context) -> str:
#     return """To crop an image to a square aspect ratio:

# 1. Use the async_image_transformation tool with:
#    - source_image_url: URL of your source image
#    - output_image_url: URL where cropped image will be stored
#    - crop_aspect_ratio: 1.0 (for 1:1 square ratio)

# This will crop the image from the center to create a perfect square."""

# @app.generic_trigger(
#     arg_name="context",
#     type="mcpPromptTrigger",
#     promptName="resize_image_instagram",
#     description="Resize an image for Instagram post (1080x1080 pixels).",
# )
# def resize_image_instagram_prompt(context: func.Context) -> str:
#     return """To resize an image for Instagram (1080x1080):

# 1. Use the async_image_transformation tool with:
#    - source_image_url: URL of your source image
#    - output_image_url: URL where resized image will be stored  
#    - contain_pixels: [1080, 1080] (fits image within 1080x1080 bounds)
#    - crop_aspect_ratio: 1.0 (ensures square format)

# This will resize and crop your image to Instagram's preferred square format."""

# @app.generic_trigger(
#     arg_name="context",
#     type="mcpPromptTrigger",
#     promptName="convert_to_grayscale",
#     description="Convert a color image to grayscale/black and white.",
# )
# def convert_to_grayscale_prompt(context: func.Context) -> str:
#     return """To convert an image to grayscale:

# 1. Use the async_image_transformation tool with:
#    - source_image_url: URL of your source image
#    - output_image_url: URL where grayscale image will be stored
#    - grayscale: true

# This will convert your color image to black and white/grayscale."""

# @app.generic_trigger(
#     arg_name="context",
#     type="mcpPromptTrigger", 
#     promptName="rotate_image_landscape",
#     description="Auto-rotate an image to landscape orientation.",
# )
# def rotate_image_landscape_prompt(context: func.Context) -> str:
#     return """To auto-rotate an image to landscape orientation:

# 1. Use the async_image_transformation tool with:
#    - source_image_url: URL of your source image
#    - output_image_url: URL where rotated image will be stored
#    - rotate_to: "landscape"

# This will automatically rotate your image to landscape orientation if needed."""

# @app.generic_trigger(
#     arg_name="context", 
#     type="mcpPromptTrigger",
#     promptName="add_white_border_sticker",
#     description="Add a white border around an image to create a sticker effect.",
# )
# def add_white_border_sticker_prompt(context: func.Context) -> str:
#     return """To add a white border for a sticker effect:

# 1. Use the async_image_transformation tool with:
#    - source_image_url: URL of your source image
#    - output_image_url: URL where bordered image will be stored
#    - stickerise_pixels: 50 (adds 50-pixel white border all around)

# Adjust the pixel value (e.g., 20, 100) to make the border thinner or thicker."""