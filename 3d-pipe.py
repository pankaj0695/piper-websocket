import asyncio
import websockets
import logging

logging.basicConfig(level=logging.INFO)
# WebSocket server to send both files
async def send_obj_and_mtl_files(websocket, path):
    with open("3d-pipe.obj", "r") as obj_file, open("3d-pipe.mtl", "r") as mtl_file:
        obj_data = obj_file.read()
        mtl_data = mtl_file.read()
        payload = f"OBJ_START\n{obj_data}\nOBJ_END\nMTL_START\n{mtl_data}\nMTL_END"
    await websocket.send(payload)  # Send both files as a single payload

start_server = websockets.serve(send_obj_and_mtl_files, "192.168.1.142", 8766)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()