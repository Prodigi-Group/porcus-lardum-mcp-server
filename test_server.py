#!/usr/bin/env python3
"""
Simple test script to verify the MCP server functionality.
Run this after starting the server to test basic operations.
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_transform():
    from server import transform_image
    
    test_image_url = "https://picsum.photos/800/600"
    
    print("Testing image transformation...")
    
    # Test with ImageOps transformations
    result = await transform_image(
        source_image_url=test_image_url,
        contain_pixels=[400, 300],
        grayscale=True,
        rotate=45
    )
    
    if "error" in result:
        print(f"Error: {result['error']}")
        if "details" in result:
            print(f"Details: {result['details']}")
    else:
        print(f"Success: {result}")
        print(f"Transformed URL: {result.get('transformed_url')}")
    
    return result

async def test_temp_blob():
    from server import generate_temp_blob
    
    print("Testing temp blob generation...")
    
    # Test without extension
    result = await generate_temp_blob()
    if "error" in result:
        print(f"Error (no extension): {result['error']}")
    else:
        print(f"Success (no extension): Generated URL with {result.get('extension')}")
        print(f"URL: {result.get('temp_url')}")
    
    # Test with PNG extension
    result_png = await generate_temp_blob("png")
    if "error" in result_png:
        print(f"Error (PNG): {result_png['error']}")
    else:
        print(f"Success (PNG): {result_png.get('temp_url')}")
    
    # Test with PDF extension
    result_pdf = await generate_temp_blob("pdf")
    if "error" in result_pdf:
        print(f"Error (PDF): {result_pdf['error']}")
    else:
        print(f"Success (PDF): {result_pdf.get('temp_url')}")
    
    return result

async def test_async_transform():
    from server import async_image_transformation, generate_temp_blob
    
    print("Testing async image transformation...")
    
    # First generate a temp blob URL for output
    print("Generating output URL...")
    temp_result = await generate_temp_blob("jpg")
    if "error" in temp_result:
        print(f"Error generating temp blob: {temp_result['error']}")
        return temp_result
    
    output_url = temp_result.get("temp_url")
    if not output_url:
        print("Failed to get output URL")
        return {"error": "No output URL generated"}
    
    print(f"Output URL: {output_url}")
    
    # Test async transformation
    test_image_url = "https://picsum.photos/800/600"
    result = await async_image_transformation(
        source_image_url=test_image_url,
        output_image_url=output_url,
        contain_pixels=[400, 300],
        grayscale=True,
        rotate=45,
        source="test_script"
    )
    
    if "error" in result:
        print(f"Error: {result['error']}")
        if "details" in result:
            print(f"Details: {result['details']}")
    else:
        print(f"Success: {result}")
        print(f"Job ID: {result.get('transform_job_id')}")
        print(f"Client ID: {result.get('client_transform_id')}")
        print(f"Status: {result.get('status')}")
    
    return result

async def test_mm_inches_units():
    from server import transform_image
    
    print("Testing millimeter and inches units...")
    
    test_image_url = "https://picsum.photos/800/600"
    
    # Test with millimeters
    print("Testing pad_mm parameter...")
    result_mm = await transform_image(
        source_image_url=test_image_url,
        pad_mm=[100.0, 80.0]  # 100mm x 80mm padding
    )
    
    if "error" in result_mm:
        print(f"Error (mm): {result_mm['error']}")
    else:
        print(f"Success (mm): {result_mm.get('message', 'Transformed')}")
    
    # Test with inches
    print("Testing contain_inches parameter...")
    result_inches = await transform_image(
        source_image_url=test_image_url,
        contain_inches=[4.0, 3.0],  # 4" x 3" contain
        grayscale=True
    )
    
    if "error" in result_inches:
        print(f"Error (inches): {result_inches['error']}")
    else:
        print(f"Success (inches): {result_inches.get('message', 'Transformed')}")
    
    # Test crop_mm
    print("Testing crop_mm parameter...")
    result_crop_mm = await transform_image(
        source_image_url=test_image_url,
        crop_mm=[10.0, 10.0, 10.0, 10.0]  # 10mm crop on all sides
    )
    
    if "error" in result_crop_mm:
        print(f"Error (crop_mm): {result_crop_mm['error']}")
    else:
        print(f"Success (crop_mm): {result_crop_mm.get('message', 'Transformed')}")
    
    return result_mm

async def test_prompts():
    from server import (
        crop_image_prompt,
        crop_aspect_ratio_prompt,
        contain_image_prompt,
        rotate_image_prompt,
        convert_to_grayscale_prompt,
        set_dpi_prompt,
        pad_image_prompt
    )
    
    print("\n--- Testing Prompts ---")
    
    print("\n1. Crop Image Prompt:")
    print(crop_image_prompt(100, 100, 500, 400))
    
    print("\n2. Crop Aspect Ratio Prompt:")
    print(crop_aspect_ratio_prompt(16/9))
    
    print("\n3. Contain Image Prompt:")
    print(contain_image_prompt(800, 600))
    
    print("\n4. Rotate Image Prompt:")
    print(rotate_image_prompt(90))
    
    print("\n5. Grayscale Prompt:")
    print(convert_to_grayscale_prompt())
    
    print("\n6. DPI Prompt:")
    print(set_dpi_prompt(300))
    
    print("\n7. Pad Image Prompt:")
    print(pad_image_prompt())

def check_configuration():
    print("--- Configuration Check ---")
    api_key = os.getenv("PORCUS_LARDUM_API_KEY")
    base_url = os.getenv("PORCUS_LARDUM_BASE_URL")
    
    if api_key:
        print(f"✓ API Key configured (length: {len(api_key)})")
    else:
        print("✗ API Key not configured - please set PORCUS_LARDUM_API_KEY in .env")
    
    if base_url:
        print(f"✓ Base URL: {base_url}")
    else:
        print("✓ Using default base URL")
    
    return bool(api_key)

async def main():
    print("=== Porcus Lardum MCP Server Test ===\n")
    
    if not check_configuration():
        print("\nPlease configure your API key before running tests.")
        return
    
    await test_prompts()
    
    print("\n--- Testing Temp Blob Tool ---")
    await test_temp_blob()
    
    print("\n--- Testing Async Transform Tool ---")
    await test_async_transform()
    
    print("\n--- Testing MM/Inches Units ---")
    await test_mm_inches_units()
    
    print("\n--- Testing Transform Tool ---")
    result = await test_transform()
    
    if "success" in result and result["success"]:
        print("\n✓ All tests passed!")
        if "saved_to" in result:
            print(f"✓ Transformed image saved to: {result['saved_to']}")
    else:
        print("\n✗ Transform test failed. Check your API key and network connection.")

if __name__ == "__main__":
    asyncio.run(main())