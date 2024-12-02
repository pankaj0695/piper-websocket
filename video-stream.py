import asyncio
import websockets
import cv2
import logging
logging.basicConfig(level=logging.INFO)

# Path to the video file
video_path = "pipe-video.mp4"

async def video_stream(websocket, path):
  while True:  # Loop the video stream
    cap = cv2.VideoCapture(video_path)
        
    while cap.isOpened():
      ret, frame = cap.read()
      if not ret:
        break  # End of video reached, exit inner loop to restart the video
            
      # Encode frame as JPEG
      _, buffer = cv2.imencode('.jpg', frame)
      frame_data = buffer.tobytes()
            
      # Send the frame over the WebSocket
      await websocket.send(frame_data)
      await asyncio.sleep(0.1)
        
    cap.release()  # Release the capture and loop back to the start of the video

async def main():
  async with websockets.serve(video_stream, "192.168.1.142", 8765): # Replace with your local IP address
    await asyncio.Future()  # Run forever

if __name__ == "__main__":
  asyncio.run(main())
