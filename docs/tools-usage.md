# KOMIHUB Tools Usage Guide

This guide explains how to use the Go-based image processing tools built with the `advancegg` package.

## Arrest Tool

Create arrest composition images using the `-arrest` flag.

### Basic Usage
```bash
go run tools/main.go -arrest -img1 "path/to/first_image.jpg" -img2 "path/to/second_image.jpg"
```

### Advanced Usage with Options
```bash
go run tools/main.go -arrest \
    -img1 "imgs/ava1.jpg" \
    -img2 "imgs/ava2.jpg" \
    -bg "imgs/bg.png" \
    -output "my_arrest.png" \
    -v
```

### Parameters
- `-arrest`: Enable arrest image creation (required)
- `-img1`: Path to first image (arrester) - **Required**
- `-img2`: Path to second image (arrested) - **Required**
- `-bg`: Background image path (default: "bg.png")
- `-output`: Output filename (default: "arrest_output.png")
- `-v`: Verbose output with progress information

### Example
```bash
# Create arrest image with default settings
go run tools/main.go -arrest -img1 "ava1.jpg" -img2 "ava2.jpg"

# Create with custom background and verbose output
go run tools/main.go -arrest -img1 "imgs/user1.jpg" -img2 "imgs/user2.jpg" -bg "imgs/custom_bg.png" -v
```

## General Image Processing

Create and manipulate images using various drawing commands.

### Text Rendering
```bash
go run tools/main.go -text "Hello World" -font-size 36 -text-x 200 -text-y 150 -text-color "#FF0000"
```

### Shape Drawing
```bash
# Draw rectangle
go run tools/main.go -rect-x 50 -rect-y 50 -rect-w 200 -rect-h 100 -rect-fill "#00FF00"

# Draw circle
go run tools/main.go -circle-x 400 -circle-y 300 -circle-r 50 -circle-fill "#0000FF"
```

### Image Composition
```bash
# Draw image on canvas
go run tools/main.go -image "avatar.png" -image-x 100 -image-y 100

# Load and modify existing image
go run tools/main.go -input "base.jpg" -text "Sample Text" -text-color "#FF0000" -output "modified.png"
```

## Available Commands

### Text Options
- `-text`: Text content to draw
- `-font-size`: Font size (default: 24)
- `-font`: Font file path (optional)
- `-text-color`: Text color in hex format (default: #000000)
- `-text-x`: Text X position (default: 400)
- `-text-y`: Text Y position (default: 300)

### Rectangle Options
- `-rect-x`: Rectangle X position
- `-rect-y`: Rectangle Y position
- `-rect-w`: Rectangle width
- `-rect-h`: Rectangle height
- `-rect-fill`: Rectangle fill color (hex)
- `-rect-stroke`: Rectangle stroke color (hex)
- `-rect-stroke-width`: Rectangle stroke width

### Circle Options
- `-circle-x`: Circle center X position
- `-circle-y`: Circle center Y position
- `-circle-r`: Circle radius
- `-circle-fill`: Circle fill color (hex)
- `-circle-stroke`: Circle stroke color (hex)
- `-circle-stroke-width`: Circle stroke width
- `-circle-image`: Image to draw in circle

### General Options
- `-width`: Canvas width (default: 800)
- `-height`: Canvas height (default: 600)
- `-input`: Input image path
- `-output`: Output image filename (default: "output.png")

## Examples

### Complete Arrest Example
```bash
cd tools
go run main.go -arrest \
    -img1 "imgs/ava1.jpg" \
    -img2 "imgs/ava2.jpg" \
    -bg "imgs/bg.png" \
    -output "arrest_result.png" \
    -v
```

### Text and Shapes Example
```bash
go run tools/main.go \
    -width 800 -height 600 \
    -text "KOMIHUB" -font-size 48 -text-x 400 -text-y 100 \
    -rect-x 50 -rect-y 200 -rect-w 300 -rect-h 150 \
    -rect-fill "#2ECC71" -rect-stroke "#27AE60" -rect-stroke-width 2 \
    -circle-x 600 -circle-y 300 -circle-r 75 \
    -circle-fill "#3498DB" -circle-stroke "#2980B9" -circle-stroke-width 3 \
    -output "demo.png"
```

### Image Processing Example
```bash
go run tools/main.go \
    -input "base_image.jpg" \
    -text "Watermark" -text-color "#FFFFFF" -text-x 650 -text-y 550 \
    -output "watermarked.png"
```

## Technical Details

### advancegg Package
The tools use the `github.com/GrandpaEJ/advancegg` package for:
- Image loading and saving (PNG format)
- 2D drawing context management
- Text rendering with fonts
- Shape drawing (rectangles, circles)
- Image composition and positioning

### Output Format
All output images are saved in PNG format with high quality.

### Error Handling
The tools provide detailed error messages for:
- Missing required parameters
- Invalid file paths
- Unsupported color formats
- Drawing operations failures

### Performance
- Optimized for batch processing
- Minimal memory footprint
- Fast image loading and saving operations