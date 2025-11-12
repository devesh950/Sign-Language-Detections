# 🤟 Sign Language Detection System

Real-time hand sign language detection using MediaPipe, Keras, and AI. Supports **37 gestures** (A-Z, 0-9, Space) with voice output and beautiful UI.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29-red)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- 🎯 **Real-time Detection** - Instant hand gesture recognition
- 🗣️ **Voice Output** - Text-to-speech for detected gestures
- 📝 **Live Subtitles** - On-screen display with confidence levels
- 🎨 **Beautiful UI** - Modern gradient design with Streamlit
- 📱 **Network Access** - Access from phone/tablet on same network
- 🤖 **37 Gestures** - A-Z letters, 0-9 numbers, Space
- 🎥 **Webcam Support** - Works with any USB/built-in camera
- ⚡ **High Accuracy** - 80%+ confidence threshold

## 🚀 Quick Start

### Option 1: Run Streamlit App (Web Interface)

```powershell
# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run streamlit_app.py
```

**Access at:** http://localhost:8501

### Option 2: Run Flask App (Network Access)

```powershell
# Run Flask app
python perfect_app.py
```

**Access at:** 
- Local: http://localhost:5000
- Network: http://YOUR_IP:5000 (from phone/tablet)

Or double-click: `START_ACCURATE_APP.ps1`

Open your browser at: **http://localhost:8501**

## 📁 Project Structure

```
sign_language_project/
├── streamlit_app.py          # Main Streamlit application
├── live_sign_detect.py        # Detection logic and Detector class
├── capture_images.py          # Tool to capture training images
├── extract_landmarks.py       # Extract MediaPipe landmarks from images
├── train_model.py            # Train the Keras classification model
├── create_dummy_model.py     # Generate test model (for demo only)
├── run_streamlit.ps1         # Quick launch script
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore patterns
└── README.md               # This file
```

## 🎯 Features

### User Interface
- 🎨 Beautiful gradient design with modern UI
- 📹 Real-time camera feed with hand tracking
- 🤖 Live detection with confidence visualization
- 📊 Interactive controls and statistics
- 📜 Detection history with timestamps
- ⚙️ Adjustable confidence threshold
- 👁️ Toggle hand landmark visualization

### Technical
- **MediaPipe Hands**: Real-time hand tracking with 21 landmarks
- **Keras 3**: Neural network classification with JAX backend
- **Streamlit**: Modern, responsive web interface
- **Production Ready**: Clean codebase, error handling, logging

## 📖 How to Use

### Training Your Own Model

1. **Capture Images** (`capture_images.py`):
   - Run the script and enter a sign label (e.g., "A", "B", "Hello")
   - Press `S` to save an image of your hand gesture
   - Capture 50-100 images per sign for best results
   - Repeat for each sign you want to recognize

2. **Extract Landmarks** (`extract_landmarks.py`):
   - Processes all images in `dataset/` folder
   - Extracts 21 hand landmarks (x, y, z coordinates)
   - Creates `landmarks_dataset.csv` file

3. **Train Model** (`train_model.py`):
   - Trains a neural network on the landmark data
   - Normalizes coordinates (wrist-relative, scale-invariant)
   - Saves `sign_model.h5` and `labels.pkl`

### Running the App

1. **Enable Camera**: Check the "Enable Camera" box in the sidebar
2. **Allow Permissions**: Grant camera access when prompted
3. **Show Your Hand**: Position your hand clearly in front of the camera
4. **Make Gestures**: Perform sign language gestures steadily
5. **View Results**: Watch real-time predictions with confidence scores

### Tips for Best Results

- ✅ Use good lighting conditions
- ✅ Keep your hand at a moderate distance
- ✅ Avoid cluttered backgrounds
- ✅ Hold gestures steady for 1-2 seconds
- ✅ Ensure the full hand is visible
- ✅ Train with diverse hand positions and lighting

## ⚙️ Configuration

### Sidebar Controls

- **Enable Camera**: Toggle webcam on/off
- **Confidence Threshold**: Adjust minimum confidence (0-100%)
- **Show Hand Landmarks**: Toggle visualization overlay
- **Clear History**: Reset detection history

### Environment Variables

```powershell
# Required: Set Keras backend
$env:KERAS_BACKEND="jax"
```

## 🐛 Troubleshooting

### Camera Not Working
- Ensure camera is connected and not in use by another app
- Grant browser camera permissions
- Try a different browser (Chrome/Edge recommended)

### Model Not Found
```
Error: Cannot load model
```
**Solution**: Train your model first or run `python create_dummy_model.py` for testing

### Import Errors
```
ModuleNotFoundError: No module named 'streamlit'
```
**Solution**: Install dependencies with `pip install -r requirements.txt`

### Performance Issues
- Close other applications using the camera
- Reduce frame processing by adjusting the sleep duration in code
- Use a machine with better CPU/GPU resources

## 📦 Deployment

### Local Deployment
```powershell
streamlit run streamlit_app.py --server.port 8501
```

### Streamlit Cloud (Free Hosting)
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy with one click!

### Docker Deployment
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV KERAS_BACKEND=jax
CMD ["streamlit", "run", "streamlit_app.py"]
```

Build and run:
```powershell
docker build -t sign-language-app .
docker run -p 8501:8501 sign-language-app
```

## 🔧 Technical Details

### Model Architecture
- **Input**: 63 features (21 landmarks × 3 coordinates)
- **Hidden Layer 1**: 256 neurons, ReLU activation
- **Dropout**: 30% for regularization
- **Hidden Layer 2**: 128 neurons, ReLU activation
- **Output**: Softmax classification

### Normalization
- Wrist-relative coordinates (subtract wrist position)
- Scale-invariant (divide by maximum distance)
- Ensures consistent recognition regardless of hand size or distance

### Detection Pipeline
1. Capture frame from webcam
2. MediaPipe detects hand and extracts landmarks
3. Normalize landmark coordinates
4. Pass through trained Keras model
5. Apply temporal smoothing (8-frame buffer)
6. Display prediction with confidence

## 📝 Notes

- **Keras Backend**: We use JAX instead of TensorFlow to avoid Windows long-path issues
- **Model Training**: The dummy model is for testing only. Train your own model for production use
- **Privacy**: All processing happens locally on your machine. No data is sent to external servers
- **Browser Support**: Best performance in Chrome and Edge. Safari may have limitations

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Support for two-hand gestures
- Additional model architectures
- Mobile app version
- More training data collection tools
- Improved UI themes

## 📄 License

MIT License - Feel free to use this project for personal or commercial purposes.

## 🙏 Acknowledgments

- **MediaPipe**: Google's hand tracking solution
- **Keras**: Deep learning framework
- **Streamlit**: Web app framework
- **JAX**: High-performance ML library

---

**Built with ❤️ for the sign language community**
