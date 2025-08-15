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