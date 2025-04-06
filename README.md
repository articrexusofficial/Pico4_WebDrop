# Pico4_WebDrop

A simple web application that allows Pico 4 / Quest VR headset users to easily transfer images from their headset to their PC using a local web server with drag-and-drop functionality and gallery management.

## Features

- **Intuitive Upload Interface**: Drag and drop or browse for image files to upload
- **Multiple File Support**: Upload multiple images at once
- **Image Gallery**: View all uploaded images in a responsive grid layout
- **Image Management**: Delete or download images as needed
- **Cross-Device Access**: Access the interface from any device on the same network
- **Dark Mode UI**: Easy on the eyes, especially in dimly lit environments

## Installation

### Prerequisites

- Python 3.6 or higher
- Flask

### Setup

1. Clone the repository or download the source code:

```bash
git clone https://github.com/articrexusofficial/Pico4_WebDrop.git
cd Pico4_WebDrop
```

2. Install the required dependencies:

```bash
pip install flask
```

3. Run the application:

```bash
python app.py
```

The server will start running on `http://0.0.0.0:5000`. This means you can access it from any device on your local network using your computer's IP address.

## Usage

### Accessing the Application

1. On your computer, find your local IP address:
   - Windows: Open Command Prompt and type `ipconfig`
   - Mac/Linux: Open Terminal and type `ifconfig` or `ip addr`

2. On your Pico 4 headset or any device on the same network, open a web browser and navigate to:
   ```
   http://YOUR_IP_ADDRESS:5000
   ```

### Uploading Images

1. On the main page, either:
   - Drag and drop image files into the drop zone
   - Click "Browse Files" to select images from your device

2. The selected files will appear in the file list below.

3. Click "Upload" to transfer the images to your PC.

### Managing Images

1. Click "View Gallery" to see all uploaded images.

2. In the gallery, you can:
   - Click on an image to view it full-size
   - Download images to your current device
   - Delete images you no longer need

## Project Structure

```
Pico4_WebDrop/
├── app.py                  # Main Flask application
├── static/
│   ├── styles.css          # CSS styling
│   └── script.js           # Client-side JavaScript
├── templates/
│   ├── index.html          # Upload page template
│   └── gallery.html        # Gallery page template
└── output/                 # Directory where uploaded images are stored
└── gallery.db              # SQLite database for image metadata
```

## Technologies Used

- **Backend**: Python with Flask framework
- **Database**: SQLite for image metadata storage
- **Frontend**: HTML, CSS, and JavaScript
- **File Management**: Python's os module for file operations

## Security Considerations

- The application is designed for use on trusted local networks only
- No authentication is implemented by default - anyone on your network can access the application
- Uploaded files are validated to ensure they are valid image files
- Filenames are sanitized to prevent path traversal attacks

## Troubleshooting

**Images not uploading**: 
- Ensure your image files are in supported formats (PNG, JPG, JPEG, GIF, WEBP)
- Check that the `output` directory exists and is writable

**Cannot access from Pico 4**:
- Verify that both devices are on the same network
- Confirm you're using the correct IP address of your computer
- Ensure no firewall is blocking port 5000

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
