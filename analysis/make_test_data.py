
import numpy as np
import pandas as pd
import os

def create_synthetic_data(duration_sec=3, fps=30, output_dir="."):
    frames = duration_sec * fps
    
    flow_path = os.path.join(output_dir, "mock_flow.csv")
    gyro_path = os.path.join(output_dir, "mock_gyro.csv")
    
    timestamps = []
    
    # Mock Data:
    # 1. Gyro Y (Yaw) = Sine wave
    # 2. Flow X (Visual Pan) = -Sine wave (Correlated!)
    
    gyro_x_list = []
    gyro_y_list = []
    gyro_z_list = []
    
    flow_x_list = []
    flow_y_list = []
    
    start_time_ns = 1000000000 
    
    for i in range(frames):
        t = i / fps
        
        # Signal
        signal = np.sin(t * 3) # 3 rad/s frequency
        
        gyro_val = signal
        flow_val = -signal * 20 # Inverted and scaled (pixels)
        
        timestamps.append(t)
        
        gyro_x_list.append(0)
        gyro_y_list.append(gyro_val)
        gyro_z_list.append(0)
        
        flow_x_list.append(flow_val)
        flow_y_list.append(0)
        
    # Flow CSV
    df_flow = pd.DataFrame({
        'timestamp': timestamps,
        'flow_x': flow_x_list,
        'flow_y': flow_y_list
    })
    df_flow.to_csv(flow_path, index=False)
    
    # Gyro CSV needs nanoseconds usually for real data, 
    # but verify_flow handles seconds if 'seconds' col exists or converts timestamp
    # Let's write standard timestamp format
    df_gyro = pd.DataFrame({
        'timestamp': [(start_time_ns + int(t*1e9)) for t in timestamps],
        'x': gyro_x_list,
        'y': gyro_y_list,
        'z': gyro_z_list
    })
    df_gyro.to_csv(gyro_path, index=False)
    
    print(f"Created {flow_path} and {gyro_path}")

if __name__ == "__main__":
    create_synthetic_data(output_dir="analysis")
