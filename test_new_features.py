#!/usr/bin/env python3
"""
Test script for new ImageOps features in Porcus Lardum MCP Server
"""

import asyncio
import os
from server import (
    transform_image,
    async_image_transformation,
    generate_temp_blob
)


async def test_stickerise_feature():
    """Test the stickerise (sticker effect) feature"""
    print("Testing stickerise feature...")
    
    test_image_url = "https://pwintytest.blob.core.windows.net/sample-media/ProdigiTestImage.png"
    
    # Test stickerise with pixels
    result = await transform_image(
        source_image_url=test_image_url,
        stickerise_pixels=20,
        expand_pixels=10  # Add padding to prevent overflow
    )
    
    print(f"Stickerise result: {result}")
    assert result.get("success") or "transformed_url" in result or "saved_to" in result
    

async def test_expand_feature():
    """Test the expand (border) feature"""
    print("Testing expand feature...")
    
    test_image_url = "https://pwintytest.blob.core.windows.net/sample-media/ProdigiTestImage.png"
    
    # Test expand with pixels
    result = await transform_image(
        source_image_url=test_image_url,
        expand_pixels=15
    )
    
    print(f"Expand result: {result}")
    assert result.get("success") or "transformed_url" in result or "saved_to" in result


async def test_transparency_features():
    """Test transparency handling features"""
    print("Testing transparency features...")
    
    test_image_url = "https://pwintytest.blob.core.windows.net/sample-media/ProdigiTestImage.png"
    
    # Test transparency to color
    result = await transform_image(
        source_image_url=test_image_url,
        transparency_to_color=[255, 255, 255]  # White background
    )
    
    print(f"Transparency to color result: {result}")
    assert result.get("success") or "transformed_url" in result or "saved_to" in result
    
    # Test overwrite partial transparency
    result2 = await transform_image(
        source_image_url=test_image_url,
        overwrite_partial_transparency=255
    )
    
    print(f"Overwrite partial transparency result: {result2}")
    assert result2.get("success") or "transformed_url" in result2 or "saved_to" in result2


async def test_pdf_features():
    """Test PDF processing features"""
    print("Testing PDF features...")
    
    test_image_url = "https://pwintytest.blob.core.windows.net/sample-media/ProdigiTestImage.png"
    
    # Test PDF output with multi-page processing
    result = await transform_image(
        source_image_url=test_image_url,
        pdf=True,
        multi_page=True,
        same_pixel_size=True
    )
    
    print(f"PDF features result: {result}")
    assert result.get("success") or "transformed_url" in result or "saved_to" in result


async def test_combined_transformations():
    """Test combining multiple new features"""
    print("Testing combined transformations...")
    
    test_image_url = "https://pwintytest.blob.core.windows.net/sample-media/ProdigiTestImage.png"
    
    # Combine multiple new features
    result = await transform_image(
        source_image_url=test_image_url,
        stickerise_pixels=15,
        expand_pixels=20,
        transparency_to_color=[240, 240, 240],  # Light gray background
        override_dpi=300,
        pdf=True
    )
    
    print(f"Combined transformations result: {result}")
    assert result.get("success") or "transformed_url" in result or "saved_to" in result


async def test_async_transformations():
    """Test async transformation with new features"""
    print("Testing async transformations...")
    
    # Generate temp blob for output
    temp_result = await generate_temp_blob("png")
    if not temp_result.get("success"):
        print(f"Failed to generate temp blob: {temp_result}")
        return
    
    output_url = temp_result["temp_url"]
    test_image_url = "https://pwintytest.blob.core.windows.net/sample-media/ProdigiTestImage.png"
    
    # Test async transformation with new features
    result = await async_image_transformation(
        source_image_url=test_image_url,
        output_image_url=output_url,
        stickerise_pixels=25,
        expand_pixels=15,
        grayscale=True
    )
    
    print(f"Async transformation result: {result}")
    assert result.get("success") and "transform_job_id" in result


async def test_millimeter_inch_units():
    """Test new features with millimeter and inch units"""
    print("Testing millimeter and inch units...")
    
    test_image_url = "https://pwintytest.blob.core.windows.net/sample-media/ProdigiTestImage.png"
    
    # Test stickerise with millimeters
    result1 = await transform_image(
        source_image_url=test_image_url,
        stickerise_mm=5.0,
        expand_mm=3.0
    )
    
    print(f"Millimeter units result: {result1}")
    assert result1.get("success") or "transformed_url" in result1 or "saved_to" in result1
    
    # Test stickerise with inches
    result2 = await transform_image(
        source_image_url=test_image_url,
        stickerise_inches=0.2,
        expand_inches=0.1
    )
    
    print(f"Inch units result: {result2}")
    assert result2.get("success") or "transformed_url" in result2 or "saved_to" in result2


async def run_all_tests():
    """Run all tests"""
    tests = [
        test_stickerise_feature,
        test_expand_feature,
        test_transparency_features,
        test_pdf_features,
        test_combined_transformations,
        test_async_transformations,
        test_millimeter_inch_units
    ]
    
    print("=== Running New ImageOps Features Tests ===\n")
    
    for test in tests:
        try:
            await test()
            print(f"✅ {test.__name__} passed\n")
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}\n")
    
    print("=== Tests completed ===")


if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("PORCUS_LARDUM_API_KEY"):
        print("⚠️  PORCUS_LARDUM_API_KEY environment variable not set")
        print("Set it before running tests:")
        print("export PORCUS_LARDUM_API_KEY=your_api_key_here")
        exit(1)
    
    asyncio.run(run_all_tests())
