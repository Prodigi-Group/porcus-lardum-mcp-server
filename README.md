# Porcus Lardum MCP Server

An MCP (Model Context Protocol) server that provides image transformation capabilities using the Porcus Lardum API's ImageOpsTransformParamsIn model.

## Features

- **ImageOps Transformations**: Uses the ImageOpsTransformParamsIn model exclusively
- **Cropping**: Crop by coordinates, aspect ratio, or borders
- **Containment**: Scale images to fit within bounds
- **Padding**: Expand canvas to target dimensions
- **Rotation**: Rotate images by degrees or auto-rotate to landscape/portrait
- **DPI Control**: Set image DPI metadata
- **Grayscale**: Convert images to grayscale
- **PDF Conversion**: Convert images to PDF format
- **Pre-built Prompts**: Common transformation scenarios ready to use

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd porcus-lardum-mcp-server
```

2. Install dependencies using uv:
```bash
uv pip install -e .
```

Or using pip:
```bash
pip install -e .
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your Porcus Lardum API key
```

## Configuration

Set the following environment variables in your `.env` file:

- `PORCUS_LARDUM_API_KEY`: Your Porcus Lardum API key (required)
- `PORCUS_LARDUM_BASE_URL`: API base URL (optional, defaults to https://porcus-lardum-func-dev.azurewebsites.net)

## Usage

### Running the Server

For development:
```bash
uv run mcp dev server.py
```

### Installing in Claude Desktop

```bash
uv run mcp install server.py
```

Or manually add to Claude Desktop configuration:

```json
{
  "mcpServers": {
    "porcus-lardum": {
      "command": "uv",
      "args": ["run", "python", "/path/to/server.py"],
      "env": {
        "PORCUS_LARDUM_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Available Tools

### transform_image

Transforms an image using ImageOpsTransformParamsIn model:

- **crop_pixels**: Remove pixels from borders [top, right, bottom, left]
- **crop_box_pixels**: Extract rectangle [x1, y1, x2, y2] in pixels
- **crop_aspect_ratio**: Crop to width/height ratio (e.g., 1.77 for 16:9)
- **pad_pixels**: Expand canvas [width, height] in pixels
- **contain_pixels**: Scale to fit within [width, height] in pixels
- **override_dpi**: Set DPI metadata
- **rotate**: Rotation angle in degrees
- **rotate_to**: Auto-rotate to 'landscape' or 'portrait'
- **grayscale**: Convert to grayscale
- **pdf**: Convert output to PDF

## Available Prompts

The server includes pre-configured prompts for common use cases:

- `crop_image_prompt`: Crop to specific pixel coordinates
- `crop_aspect_ratio_prompt`: Crop to a specific aspect ratio
- `contain_image_prompt`: Scale image to fit within dimensions
- `rotate_image_prompt`: Rotate images by degrees
- `convert_to_grayscale_prompt`: Convert to grayscale
- `set_dpi_prompt`: Set image DPI metadata
- `pad_image_prompt`: Add padding to expand canvas

## Example Usage in Claude

```
User: "Please contain this image within 800x600 pixels"
Assistant: [Uses contain_image_prompt to scale the image]

User: "Crop this image to 16:9 aspect ratio"
Assistant: [Uses crop_aspect_ratio_prompt with aspect_ratio=1.77]

User: "Convert this image to grayscale and rotate 90 degrees"
Assistant: [Uses transform_image with grayscale=true and rotate=90]
```

## Development

### Running Tests

```bash
# Test the server locally
uv run python server.py
```

### Adding New Transformations

To add new transformation capabilities, modify the `ImageOpsTransformParamsIn` class in `server.py` and update the corresponding tool parameters.

## License

[Your License Here]

## Support

For issues or questions about the MCP server, please open an issue in this repository.
For Porcus Lardum API documentation, refer to the OpenAPI specification.


## Azure Function


### Get Key
```
az functionapp keys list --resource-group porcus-lardum-mcp-rg-dev --name porcus-lardum-mcp-func-dev --query systemKeys.mcp_extension --output tsv
```
