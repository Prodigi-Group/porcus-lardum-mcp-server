import json
import os
import logging
from typing import Optional, Dict, Any, List
import httpx
from pydantic import BaseModel, Field
import azure.functions as func
from azure.functions import FunctionRegister

app = FunctionRegister()

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

@app.generic_trigger(arg_name="req", type="mcpTools")
def generate_temp_blob(req: func.HttpRequest) -> func.HttpResponse:
    """Generate a temporary blob SAS URL with write and read permissions."""
    
    if not API_KEY:
        return func.HttpResponse(
            json.dumps({"error": "API key not configured. Please set PORCUS_LARDUM_API_KEY environment variable."}),
            status_code=500,
            mimetype="application/json"
        )
    
    try:
        body = req.get_json()
        extension = body.get("extension") if body else None
        
        params = {}
        if extension and extension in ['png', 'jpg', 'pdf']:
            params['extension'] = extension
        
        # Use sync httpx for Azure Functions
        with httpx.Client() as client:
            response = client.get(
                f"{BASE_URL}/temp_blob",
                params=params,
                headers={
                    "x-api-key": API_KEY,
                },
                timeout=30.0,
            )
            
            if response.status_code == 200:
                temp_url = response.text.strip().strip('"')
                return func.HttpResponse(
                    json.dumps({
                        "success": True,
                        "temp_url": temp_url,
                        "extension": extension or "no extension",
                    }),
                    mimetype="application/json"
                )
            else:
                return func.HttpResponse(
                    json.dumps({
                        "error": f"API request failed with status {response.status_code}",
                        "details": response.text,
                    }),
                    status_code=response.status_code,
                    mimetype="application/json"
                )
                
    except Exception as e:
        logging.error(f"Error generating temp blob: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Failed to generate temp blob URL: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )

@app.generic_trigger(arg_name="req", type="mcpTools")
def async_image_transformation(req: func.HttpRequest) -> func.HttpResponse:
    """Queue an image transformation job for asynchronous processing."""
    
    if not API_KEY:
        return func.HttpResponse(
            json.dumps({"error": "API key not configured. Please set PORCUS_LARDUM_API_KEY environment variable."}),
            status_code=500,
            mimetype="application/json"
        )
    
    try:
        body = req.get_json()
        if not body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        source_image_url = body.get("source_image_url")
        output_image_url = body.get("output_image_url")
        
        if not source_image_url or not output_image_url:
            return func.HttpResponse(
                json.dumps({"error": "source_image_url and output_image_url are required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        client_transform_id = body.get("client_transform_id")
        if not client_transform_id:
            import uuid
            client_transform_id = str(uuid.uuid4())
        
        # Convert transformation parameters to Unit objects
        crop_units = None
        crop_pixels = body.get("crop_pixels")
        crop_mm = body.get("crop_mm") 
        crop_inches = body.get("crop_inches")
        
        if crop_pixels:
            crop_units = [Unit(pixels=p) for p in crop_pixels]
        elif crop_mm:
            crop_units = [Unit(millimeter=p) for p in crop_mm]
        elif crop_inches:
            crop_units = [Unit(inches=p) for p in crop_inches]
        
        # Handle crop_box parameters
        crop_box_units = None
        crop_box_pixels = body.get("crop_box_pixels")
        crop_box_mm = body.get("crop_box_mm")
        crop_box_inches = body.get("crop_box_inches")
        crop_box_pixels_offset = body.get("crop_box_pixels_offset")
        crop_box_mm_offset = body.get("crop_box_mm_offset")
        crop_box_inches_offset = body.get("crop_box_inches_offset")
        
        if crop_box_pixels:
            crop_box_units = [[Unit(pixels=p) for p in crop_box_pixels]] if not crop_box_pixels_offset else [
                [Unit(pixels=p) for p in crop_box_pixels],
                [Unit(pixels=p) for p in crop_box_pixels_offset]
            ]
        elif crop_box_mm:
            crop_box_units = [[Unit(millimeter=p) for p in crop_box_mm]] if not crop_box_mm_offset else [
                [Unit(millimeter=p) for p in crop_box_mm],
                [Unit(millimeter=p) for p in crop_box_mm_offset]
            ]
        elif crop_box_inches:
            crop_box_units = [[Unit(inches=p) for p in crop_box_inches]] if not crop_box_inches_offset else [
                [Unit(inches=p) for p in crop_box_inches],
                [Unit(inches=p) for p in crop_box_inches_offset]
            ]

        # Handle pad parameters
        pad_units = None
        pad_pixels = body.get("pad_pixels")
        pad_mm = body.get("pad_mm")
        pad_inches = body.get("pad_inches")
        
        if pad_pixels:
            pad_units = [Unit(pixels=p) for p in pad_pixels]
        elif pad_mm:
            pad_units = [Unit(millimeter=p) for p in pad_mm]
        elif pad_inches:
            pad_units = [Unit(inches=p) for p in pad_inches]
        
        # Handle contain parameters
        contain_units = None
        contain_pixels = body.get("contain_pixels")
        contain_mm = body.get("contain_mm")
        contain_inches = body.get("contain_inches")
        
        if contain_pixels:
            contain_units = [Unit(pixels=p) for p in contain_pixels]
        elif contain_mm:
            contain_units = [Unit(millimeter=p) for p in contain_mm]
        elif contain_inches:
            contain_units = [Unit(inches=p) for p in contain_inches]
        
        # Handle stickerise parameters
        stickerise_unit = None
        stickerise_pixels = body.get("stickerise_pixels")
        stickerise_mm = body.get("stickerise_mm")
        stickerise_inches = body.get("stickerise_inches")
        
        if stickerise_pixels:
            stickerise_unit = Unit(pixels=stickerise_pixels)
        elif stickerise_mm:
            stickerise_unit = Unit(millimeter=stickerise_mm)
        elif stickerise_inches:
            stickerise_unit = Unit(inches=stickerise_inches)
        
        # Handle expand parameters
        expand_unit = None
        expand_pixels = body.get("expand_pixels")
        expand_mm = body.get("expand_mm")
        expand_inches = body.get("expand_inches")
        
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
            crop_aspect_ratio=body.get("crop_aspect_ratio"),
            pad=pad_units,
            contain=contain_units,
            override_dpi=body.get("override_dpi"),
            rotate=body.get("rotate"),
            rotate_to=body.get("rotate_to"),
            overwrite_partial_transparency=body.get("overwrite_partial_transparency"),
            transparency_to_color=body.get("transparency_to_color"),
            grayscale=body.get("grayscale"),
            pdf=body.get("pdf"),
            multi_page=body.get("multi_page"),
            same_pixel_size=body.get("same_pixel_size"),
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
        source = body.get("source")
        if source:
            request_body["source"] = source
        
        with httpx.Client() as client:
            response = client.post(
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
                return func.HttpResponse(
                    json.dumps({
                        "success": True,
                        "transform_job_id": result.get("transform_job_id"),
                        "client_transform_id": client_transform_id,
                        "message": "Async transformation job queued successfully",
                        "output_url": output_image_url,
                        "raw_request_body": json.dumps(request_body),
                        "status": "queued"
                    }),
                    mimetype="application/json"
                )
            else:
                return func.HttpResponse(
                    json.dumps({
                        "error": f"API request failed with status {response.status_code}",
                        "details": response.text,
                    }),
                    status_code=response.status_code,
                    mimetype="application/json"
                )
                
    except Exception as e:
        logging.error(f"Error in async image transformation: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Failed to queue async transformation: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )

@app.generic_trigger(arg_name="req", type="mcpTools")
def remove_background(req: func.HttpRequest) -> func.HttpResponse:
    """Remove background from an image using AI processing."""
    
    if not API_KEY:
        return func.HttpResponse(
            json.dumps({"error": "API key not configured. Please set PORCUS_LARDUM_API_KEY environment variable."}),
            status_code=500,
            mimetype="application/json"
        )
    
    try:
        body = req.get_json()
        if not body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        source_image_url = body.get("source_image_url")
        output_image_url = body.get("output_image_url")
        
        if not source_image_url or not output_image_url:
            return func.HttpResponse(
                json.dumps({"error": "source_image_url and output_image_url are required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        request_body = {
            "source_image_url": source_image_url,
            "output_image_url": output_image_url,
            "transform": {
                "remove_background": True
            }
        }
        
        with httpx.Client() as client:
            response = client.post(
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
                return func.HttpResponse(
                    json.dumps({
                        "success": True,
                        "transform_job_id": result.get("transform_job_id"),
                        "message": "Background removal job queued successfully",
                        "output_url": output_image_url,
                        "raw_request_body": json.dumps(request_body),
                        "status": "queued"
                    }),
                    mimetype="application/json"
                )
            else:
                return func.HttpResponse(
                    json.dumps({
                        "error": f"API request failed with status {response.status_code}",
                        "details": response.text,
                    }),
                    status_code=response.status_code,
                    mimetype="application/json"
                )
                
    except Exception as e:
        logging.error(f"Error removing background: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Failed to queue background removal: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )

@app.generic_trigger(arg_name="req", type="mcpTools")  
def validate_mockup_sku(req: func.HttpRequest) -> func.HttpResponse:
    """Validate a product SKU and retrieve available mockup parameters."""
    
    if not API_KEY:
        return func.HttpResponse(
            json.dumps({"error": "API key not configured. Please set PORCUS_LARDUM_API_KEY environment variable."}),
            status_code=500,
            mimetype="application/json"
        )
    
    try:
        body = req.get_json()
        if not body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        sku = body.get("sku")
        if not sku:
            return func.HttpResponse(
                json.dumps({"error": "sku is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        with httpx.Client() as client:
            response = client.get(
                f"{BASE_URL}/mockup/{sku}",
                headers={
                    "x-api-key": API_KEY,
                },
                timeout=30.0,
            )
            
            if response.status_code == 200:
                result = response.json()
                return func.HttpResponse(
                    json.dumps({
                        "success": True,
                        "sku": sku,
                        "valid": True,
                        "parameters": result,
                        "message": f"SKU {sku} is valid and ready for mockup generation"
                    }),
                    mimetype="application/json"
                )
            elif response.status_code == 404:
                return func.HttpResponse(
                    json.dumps({
                        "success": False,
                        "sku": sku,
                        "valid": False,
                        "error": f"SKU {sku} not found or not available for mockups"
                    }),
                    status_code=404,
                    mimetype="application/json"
                )
            else:
                return func.HttpResponse(
                    json.dumps({
                        "error": f"API request failed with status {response.status_code}",
                        "details": response.text,
                    }),
                    status_code=response.status_code,
                    mimetype="application/json"
                )
                
    except Exception as e:
        logging.error(f"Error validating SKU: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Failed to validate SKU: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )

@app.generic_trigger(arg_name="req", type="mcpTools")
def generate_product_mockup(req: func.HttpRequest) -> func.HttpResponse:
    """Generate a 3D product mockup using Blender rendering."""
    
    if not API_KEY:
        return func.HttpResponse(
            json.dumps({"error": "API key not configured. Please set PORCUS_LARDUM_API_KEY environment variable."}),
            status_code=500,
            mimetype="application/json"
        )
    
    try:
        body = req.get_json()
        if not body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Extract required parameters
        sku = body.get("sku")
        width = body.get("width")
        height = body.get("height")
        camera = body.get("camera")
        output_image_url = body.get("output_image_url")
        
        if not all([sku, width, height, camera, output_image_url]):
            return func.HttpResponse(
                json.dumps({"error": "sku, width, height, camera, and output_image_url are required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        mockup_parameters = MockupParameters(
            size=[width, height],
            sku=sku,
            camera=camera,
            orientation=body.get("orientation"),
            color=body.get("color"),
            wrap=body.get("wrap"),
            finish=body.get("finish"),
            blank=body.get("blank"),
        )
        
        mockup_request = MockupRequest(
            source_image_url=body.get("source_image_url"),
            output_image_url=output_image_url,
            parameters=mockup_parameters,
        )
        
        request_body = mockup_request.model_dump(exclude_none=True)
        
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/mockup",
                json=request_body,
                headers={
                    "x-api-key": API_KEY,
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
            
            if response.status_code == 200:
                result = response.json()
                return func.HttpResponse(
                    json.dumps({
                        "success": True,
                        "result": result,
                        "sku": sku,
                        "output_url": output_image_url,
                        "dimensions": [width, height],
                        "camera": camera,
                        "message": "Mockup generation job queued successfully",
                        "status": "queued"
                    }),
                    mimetype="application/json"
                )
            else:
                return func.HttpResponse(
                    json.dumps({
                        "error": f"API request failed with status {response.status_code}",
                        "details": response.text,
                    }),
                    status_code=response.status_code,
                    mimetype="application/json"
                )
                
    except Exception as e:
        logging.error(f"Error generating mockup: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Failed to generate mockup: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )