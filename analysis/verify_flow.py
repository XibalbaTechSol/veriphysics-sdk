
import cv2
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import sys
import os

def calculate_optical_flow(video_path):
    # ... (Keep existing code, but add check)
    try:
        cap = cv2.VideoCapture(video_path)
    except Exception:
        print("OpenCV VideoCapture failed. Is cv2 installed correctly?")
        return None, None, None

    if not cap.isOpened():
        print(f"Error opening video: {video_path}")
        return None, None, None

    fps = cap.get(cv2.CAP_PROP_FPS)
    ret, prev_frame = cap.read()
    if not ret:
        return None, None, None
    
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    
    flow_x_list = []
    flow_y_list = []
    timestamps = []
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        
        h, w = flow.shape[:2]
        margin_x = int(w * 0.1)
        margin_y = int(h * 0.1)
        valid_flow = flow[margin_y:h-margin_y, margin_x:w-margin_x]
        
        avg_flow = np.mean(valid_flow, axis=(0, 1))
        
        flow_x_list.append(avg_flow[0])
        flow_y_list.append(avg_flow[1])
        timestamps.append(frame_count / fps)
        
        prev_gray = gray
        frame_count += 1
        
    cap.release()
    return np.array(timestamps), np.array(flow_x_list), np.array(flow_y_list)

def process_gyro_data(csv_path):
    try:
        df = pd.read_csv(csv_path)
        # Handle 'seconds' or 'timestamp'
        if 'seconds' in df.columns:
            return df['seconds'].values, df['x'].values, df['y'].values, df['z'].values
        
        t0 = df.iloc[0]['timestamp']
        df['seconds'] = (df['timestamp'] - t0) / 1e9 
        return df['seconds'].values, df['x'].values, df['y'].values, df['z'].values
    except Exception as e:
        print(f"Error reading Gyro CSV: {e}")
        return None, None, None, None

def process_flow_csv(csv_path):
    """
    Reads pre-computed optical flow CSV.
    Format: timestamp, flow_x, flow_y
    """
    try:
        df = pd.read_csv(csv_path)
        return df['timestamp'].values, df['flow_x'].values, df['flow_y'].values
    except Exception as e:
        print(f"Error reading Flow CSV: {e}")
        return None, None, None

def verify_content(input_path, gyro_path):
    print(f"Processing {input_path} and {gyro_path}...")
    
    # 1. Get Visual Flow
    if input_path.endswith('.csv'):
        v_time, v_flow_x, v_flow_y = process_flow_csv(input_path)
    else:
        v_time, v_flow_x, v_flow_y = calculate_optical_flow(input_path)
        
    if v_time is None:
        print("Failed to load visual flow.")
        return
        
    # 2. Get Gyro Data
    g_time, g_x, g_y, g_z = process_gyro_data(gyro_path)
    if g_time is None:
        print("Failed to load gyro data.")
        return
        
    # 3. Synchronize / Resample
    f_gyro_y = interp1d(g_time, g_y, kind='linear', fill_value="extrapolate")
    
    # Ensure range intersection
    t_min = max(v_time[0], g_time[0])
    t_max = min(v_time[-1], g_time[-1])
    
    if t_max < t_min:
        print("Timestamp mismatch: Time ranges do not overlap.")
        print(f"Video: {v_time[0]}-{v_time[-1]}")
        print(f"Gyro: {g_time[0]}-{g_time[-1]}")
        temp_g_y = f_gyro_y(v_time) # Try anyway for mock data
        # return

    # Select valid video frames within range
    valid_mask = (v_time >= t_min) & (v_time <= t_max)
    v_time_valid = v_time[valid_mask]
    v_flow_x_valid = v_flow_x[valid_mask]
    
    g_y_resampled = f_gyro_y(v_time_valid)
    
    # Trim logic
    trim = 2
    if len(v_flow_x_valid) > trim:
        v_flow_x_valid = v_flow_x_valid[trim:]
        g_y_resampled = g_y_resampled[trim:]
    
    if len(v_flow_x_valid) < 5:
        print("Not enough data points.")
        return

    # 4. Normalize (Z-Score)
    def z_score(x): return (x - np.mean(x)) / np.std(x) if np.std(x) > 1e-6 else x
    
    vf_norm = z_score(v_flow_x_valid)
    gy_norm = z_score(g_y_resampled)
    
    # 5. Calculate Correlation
    correlation = np.corrcoef(vf_norm, gy_norm)[0, 1]
    
    # 6. DTW
    # Use simple absolute difference for 1D scalar data
    distance, path = fastdtw(vf_norm, gy_norm, dist=lambda x, y: abs(x - y))
    
    normalized_distance = distance / len(vf_norm)
    
    print("\n--- Verification Results ---")
    print(f"Algorithm: Optical Flow X (Visual Pan) vs Gyro Y (Yaw)")
    print(f"Data Points: {len(vf_norm)}")
    print(f"Pearson Correlation: {correlation:.4f}")
    print(f"DTW Distance: {normalized_distance:.4f}")
    
    score = abs(correlation)
    print(f"FINAL PROBABILITY SCORE: {score * 100:.1f}%")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python verify_flow.py <video.mp4 or flow.csv> <gyro.csv>")
    else:
        verify_content(sys.argv[1], sys.argv[2])
