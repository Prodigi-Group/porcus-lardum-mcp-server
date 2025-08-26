# Porcus Lardum MCP Azure Functions Server

This is an Azure Functions implementation of the Porcus Lardum MCP (Model Context Protocol) server for image transformations and mockup generation.

## Features

- **Image Transformations**: Crop, resize, rotate, and apply various effects to images
- **Background Removal**: AI-powered background removal service
- **Product Mockups**: Generate 3D product mockups using Blender rendering
- **Temp Blob Storage**: Generate temporary URLs for image uploads/downloads

## Functions

### Core Image Processing
- `generate_temp_blob` - Generate temporary blob SAS URLs
- `async_image_transformation` - Queue image transformation jobs
- `remove_background` - AI-powered background removal

### Product Mockups
- `validate_mockup_sku` - Validate product SKUs for mockup generation
- `generate_product_mockup` - Create 3D product mockups

## Setup

### Prerequisites
- Python 3.8+
- Azure Functions Core Tools
- Azure CLI (for deployment)

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables in `local.settings.json`**:
   ```json
   {
     "Values": {
       "PORCUS_LARDUM_API_KEY": "your-api-key-here",
       "PORCUS_LARDUM_BASE_URL": "https://porcus-lardum-func-dev.azurewebsites.net"
     }
   }
   ```

3. **Start local development server**:
   ```bash
   func start
   ```

### Deployment

1. **Create Azure Resources**:
   ```bash
   # Create resource group
   az group create --name my-resource-group --location eastus

   # Create function app
   az functionapp create \
     --resource-group my-resource-group \
     --consumption-plan-location eastus \
     --runtime python \
     --runtime-version 3.9 \
     --functions-version 4 \
     --name my-function-app \
     --storage-account my-storage-account
   ```

2. **Deploy the function**:
   ```bash
   func azure functionapp publish my-function-app
   ```

3. **Set environment variables**:
   ```bash
   az functionapp config appsettings set \
     --name my-function-app \
     --resource-group my-resource-group \
     --settings PORCUS_LARDUM_API_KEY=your-api-key
   ```

## API Usage

Each function accepts HTTP POST requests with JSON payloads. The functions are designed to work with the MCP experimental extension bundle.

### Example: Image Transformation
```bash
curl -X POST "https://your-function-app.azurewebsites.net/api/async_image_transformation" \
  -H "Content-Type: application/json" \
  -d '{
    "source_image_url": "https://example.com/image.jpg",
    "output_image_url": "https://example.com/output.jpg",
    "crop_pixels": [10, 10, 10, 10],
    "rotate": 90
  }'
```

### Example: Generate Temp Blob
```bash
curl -X POST "https://your-function-app.azurewebsites.net/api/generate_temp_blob" \
  -H "Content-Type: application/json" \
  -d '{"extension": "png"}'
```

## Migration Notes

This Azure Functions implementation maintains compatibility with the original MCP server while providing:
- Serverless scaling capabilities
- Built-in monitoring and logging
- Azure security and compliance features
- Cost-effective pay-per-use pricing

The function endpoints can be used directly or integrated with MCP clients that support HTTP-based MCP servers.