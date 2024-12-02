import asyncio
import websockets
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)

# Function to generate a circle (cross-section of the pipe) at a given position
def generate_circle(radius, num_points, position, axis="z"):
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    if axis == "z":
        x_coords = radius * np.cos(angles) + position[0]
        y_coords = radius * np.sin(angles) + position[1]
        z_coords = np.full(num_points, position[2])
    elif axis == "x":
        x_coords = np.full(num_points, position[0])
        y_coords = radius * np.cos(angles) + position[1]
        z_coords = radius * np.sin(angles) + position[2]
    return np.vstack((x_coords, y_coords, z_coords)).T

# Parameters for the pipe
radius = 5
height = 50
num_cross_sections = 100
points_per_section = 50

point_cloud_data = []
colors = []

# Generate the first segment (along Z-axis) with green color
z_positions = np.linspace(0, height, num_cross_sections, endpoint=False)
for i, z in enumerate(z_positions):
    points = generate_circle(radius, points_per_section, (0, 0, z), axis="z")
    color = [0.0, 1.0, 0.0]  # Green color
    point_cloud_data.extend(points.tolist())
    colors.extend([color] * points_per_section)

# Generate the second segment (along X-axis) with red color
x_positions = np.linspace(0, height, num_cross_sections)
for i, x in enumerate(x_positions):
    points = generate_circle(radius, points_per_section, (x, 0, height), axis="x")
    color = [1.0, 0.0, 0.0]  # Red color
    point_cloud_data.extend(points.tolist())
    colors.extend([color] * points_per_section)

# Save the .obj and .mtl files
def save_as_obj_with_colors(point_cloud, colors, filename="pipe.obj"):
    obj_filename = filename
    mtl_filename = filename.replace(".obj", ".mtl")
    green_material = "GreenMaterial"
    red_material = "RedMaterial"

    # Write the .obj file
    with open(obj_filename, 'w') as obj_file:
        obj_file.write(f"mtllib {mtl_filename}\n")  # Reference the .mtl file
        for i, point in enumerate(point_cloud):
            obj_file.write(f"v {point[0]} {point[1]} {point[2]}\n")  # Write vertex
        obj_file.write(f"usemtl {green_material}\n")
        for i in range(len(z_positions) * points_per_section):
            obj_file.write(f"f {i + 1}\n")
        obj_file.write(f"usemtl {red_material}\n")
        for i in range(len(z_positions) * points_per_section, len(point_cloud)):
            obj_file.write(f"f {i + 1}\n")

    # Write the .mtl file
    with open(mtl_filename, 'w') as mtl_file:
        mtl_file.write(f"newmtl {green_material}\n")
        mtl_file.write("Kd 0.0 1.0 0.0\n")  # Green diffuse color
        mtl_file.write(f"newmtl {red_material}\n")
        mtl_file.write("Kd 1.0 0.0 0.0\n")  # Red diffuse color

save_as_obj_with_colors(point_cloud_data, colors)

# WebSocket server to send both files
async def send_obj_and_mtl_files(websocket, path):
    with open("pipe.obj", "r") as obj_file, open("pipe.mtl", "r") as mtl_file:
        obj_data = obj_file.read()
        mtl_data = mtl_file.read()
        payload = f"OBJ_START\n{obj_data}\nOBJ_END\nMTL_START\n{mtl_data}\nMTL_END"
    await websocket.send(payload)  # Send both files as a single payload

start_server = websockets.serve(send_obj_and_mtl_files, "192.168.1.142", 8766)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()