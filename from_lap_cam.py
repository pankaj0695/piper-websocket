import asyncio
import websockets
import cv2
import logging

logging.basicConfig(level=logging.INFO)

async def video_stream(websocket, path):
    # Open the default camera
    cap = cv2.VideoCapture(0)
    
    # Check if the camera opened successfully
    if not cap.isOpened():
        logging.error("Error: Could not open camera.")
        return

    # Get the frame rate of the camera (optional)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30  # Default to 30 FPS if fps is not available
    frame_delay = 1 / fps  # Calculate delay per frame

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logging.error("Failed to capture image from camera.")
                break
            
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame_data = buffer.tobytes()
            
            # Send the frame over the WebSocket
            await websocket.send(frame_data)
            await asyncio.sleep(frame_delay)  # Control frame rate based on camera FPS
    finally:
        cap.release()  # Release the camera when done

async def main():
    async with websockets.serve(video_stream, "192.168.1.142", 8765):  # Replace with your local IP address
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
