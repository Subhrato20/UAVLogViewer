# UAV Log Viewer

A web-based tool for viewing and analyzing MAVLink and Dataflash logs from ArduPilot-based vehicles.

## Features

- View flight paths on a 3D map
- Plot flight data
- Analyze flight parameters
- Chat with an AI assistant about your flight data
- Detect flight anomalies
- View and analyze mission data
- Export data to various formats

## Prerequisites

- Node.js (v14 or higher)
- Python 3.8 or higher
- Cesium ion account (for 3D map visualization)
- OpenAI API key (for AI chat functionality)

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Subhrato20/uavlogviewer.git
cd uavlogviewer
```

### 2. Frontend Setup

```bash
# Install dependencies
npm install

# Create .env file for Cesium token
echo "VUE_APP_CESIUM_TOKEN=your_cesium_token_here" > .env
```

### 3. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file for OpenAI API
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

### 4. Get Cesium Token

1. Go to [Cesium ion](https://cesium.com/ion/signup)
2. Create a free account
3. After signing in, go to your [Access Tokens](https://cesium.com/ion/tokens)
4. Create a new token or use the default token
5. Copy the token and paste it in your `.env` file

### 5. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/signup)
2. Create an account or sign in
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Give your key a name (e.g., "UAV Log Viewer")
6. Copy the generated API key
7. Create a `.env` file in the backend directory if it doesn't exist
8. Add your API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

Note: Keep your API key secure and never commit it to version control. The `.env` file is already in `.gitignore`.

## Running the Application

### 1. Start the Backend Server

```bash
# Make sure you're in the backend directory and virtual environment is activated
cd backend
source venv/bin/activate  # On Windows use: venv\Scripts\activate
uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

### 2. Start the Frontend Development Server

```bash
# In a new terminal, from the project root
npm run serve
```

The application will be available at `http://localhost:8080`

## Using the Application

1. Open your browser and navigate to `http://localhost:8080`
2. Upload a MAVLink (.tlog) or Dataflash (.bin) log file
3. Use the interface to:
   - View the flight path on the 3D map
   - Plot flight data
   - Chat with the AI assistant about your flight
   - Analyze flight anomalies
   - View mission data

## Features in Detail

### Chat with AI Assistant
- Ask questions about your flight data
- Get insights about flight performance
- Identify potential issues
- Understand flight parameters

### Anomaly Detection
- Automatic detection of flight anomalies
- Analysis of GPS signal quality
- Battery and power system monitoring
- Attitude and control surface analysis

### 3D Visualization
- Interactive 3D flight path
- Terrain visualization
- Mission waypoint display
- Real-time playback

### Data Analysis
- Plot multiple parameters
- Export data to CSV
- Compare different flights
- Analyze mission performance

## Troubleshooting

### Common Issues

1. **Backend Connection Error**
   - Ensure the backend server is running on port 8001
   - Check if all dependencies are installed
   - Verify the virtual environment is activated
   - Check if OpenAI API key is correctly set in the .env file

2. **Cesium Map Not Loading**
   - Verify your Cesium token is correctly set in the .env file
   - Check if the token is valid in your Cesium ion account
   - Ensure you have an active internet connection

3. **File Upload Issues**
   - Check if the file is a valid MAVLink or Dataflash log
   - Ensure the file size is within limits
   - Verify the file format is supported

4. **AI Chat Not Working**
   - Verify your OpenAI API key is correctly set in the backend .env file
   - Check if you have sufficient API credits
   - Ensure the backend server is running
   - Check the backend logs for any API-related errors

