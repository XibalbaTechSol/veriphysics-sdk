#include "MotionVerifier.h"
#include <fstream>
#include <sstream>
#include <cmath>
#include <numeric>
#include <algorithm>
#include <iostream>

MotionVerifier::MotionVerifier() {}
MotionVerifier::~MotionVerifier() {}

std::vector<GyroSample> MotionVerifier::loadGyroData(const std::string& path) {
    std::vector<GyroSample> data;
    std::ifstream file(path);
    std::string line;
    
    // Check if file opened
    if (!file.is_open()) {
        std::cerr << "Failed to open gyro CSV: " << path << std::endl;
        return data; 
    }

    // Skip header
    std::getline(file, line);
    
    double t0 = -1.0;
    
    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string val;
        GyroSample sample;
        double raw_ts;
        
        // CSV: timestamp,x,y,z
        // Handle comma separation
        if (std::getline(ss, val, ',')) raw_ts = std::stod(val);
        if (std::getline(ss, val, ',')) sample.x = std::stod(val);
        if (std::getline(ss, val, ',')) sample.y = std::stod(val);
        if (std::getline(ss, val, ',')) sample.z = std::stod(val);
        
        // Normalize time
        if (t0 < 0) t0 = raw_ts;
        
        // Determine if timestamp is ns (huge) or seconds
        // Lowered threshold to 1e8 to catch early boot timestamps (100ms+)
        if (raw_ts > 100000000.0) { 
             sample.timestamp = (raw_ts - t0) / 1e9;
        } else {
             sample.timestamp = raw_ts - t0;
        }
        
        data.push_back(sample);
    }
    return data;
}

std::vector<double> MotionVerifier::normalizeVector(const std::vector<double>& v) {
    if (v.empty()) return v;
    double sum = std::accumulate(v.begin(), v.end(), 0.0);
    double mean = sum / v.size();
    
    double sq_sum = std::inner_product(v.begin(), v.end(), v.begin(), 0.0);
    double stdev = std::sqrt(sq_sum / v.size() - mean * mean);
    
    std::vector<double> res;
    // Python code checks if std < 1e-6 returns original, so we match that roughly
    if (stdev < 1e-6) {
        return v;
    }
    
    for (double val : v) {
        res.push_back((val - mean) / stdev);
    }
    return res;
}

std::pair<std::vector<double>, std::vector<double>> MotionVerifier::loadFlowCSV(const std::string& path) {
    std::vector<double> timestamps;
    std::vector<double> flowX;
    std::ifstream file(path);
    std::string line;
    
    if (!file.is_open()) {
        std::cerr << "Failed to open flow CSV: " << path << std::endl;
        return {timestamps, flowX};
    }
    
    // Header
    std::getline(file, line);
    
    while(std::getline(file, line)) {
        std::stringstream ss(line);
        std::string val;
        double t, fx;
        
        // CSV: timestamp,flow_x,flow_y OR index,timestamp,flow_x,flow_y
        // Assuming consistent simple format timestamp,flow_x,...
        // Using basic parsing attempting to be robust
        
        if (std::getline(ss, val, ',')) t = std::stod(val);
        if (std::getline(ss, val, ',')) fx = std::stod(val);
        // ignore rest
        
        timestamps.push_back(t);
        flowX.push_back(fx);
    }
    return {timestamps, flowX};
}

std::pair<std::vector<double>, std::vector<double>> MotionVerifier::calculateOpticalFlow(const std::string& videoPath) {
    std::vector<double> timestamps;
    std::vector<double> flowX;
    
    cv::VideoCapture cap(videoPath);
    if (!cap.isOpened()) {
        std::cerr << "Failed to open video: " << videoPath << std::endl;
        return {timestamps, flowX};
    }
    
    double fps = cap.get(cv::CAP_PROP_FPS);
    if (fps <= 0) fps = 30.0;
    
    cv::Mat prevGray, frame, gray;
    cap >> frame;
    if (frame.empty()) return {timestamps, flowX};
    
    cv::cvtColor(frame, prevGray, cv::COLOR_BGR2GRAY);
    
    int frameCount = 0;
    
    while (true) {
        cap >> frame;
        if (frame.empty()) break;
        
        cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);
        
        cv::Mat flow;
        // Basic Farneback
        cv::calcOpticalFlowFarneback(prevGray, gray, flow, 0.5, 3, 15, 3, 5, 1.2, 0);
        
        // Calculate mean flow
        // Crop margins 10%
        int h = flow.rows;
        int w = flow.cols;
        int mX = w * 0.1;
        int mY = h * 0.1;
        
        cv::Rect roi(mX, mY, w - 2*mX, h - 2*mY);
        cv::Scalar meanFlow = cv::mean(flow(roi));
        
        // meanFlow[0] is X, [1] is Y
        flowX.push_back(meanFlow[0]);
        timestamps.push_back((double)frameCount / fps);
        
        frameCount++;
        prevGray = gray.clone(); // Important clone
    }
    
    return {timestamps, flowX};
}

std::vector<double> MotionVerifier::resampleGyro(
    const std::vector<double>& targetTimestamps, 
    const std::vector<GyroSample>& gyroData, 
    int axisIndex
) {
    std::vector<double> resampled;
    if (gyroData.empty() || targetTimestamps.empty()) return resampled;
    
    // Linear Interpolation
    size_t gIdx = 0;
    
    for (double t : targetTimestamps) {
        // Find surrounding gyro samples
        while (gIdx + 1 < gyroData.size() && gyroData[gIdx + 1].timestamp < t) {
            gIdx++;
        }
        
        if (gIdx + 1 >= gyroData.size()) {
            // End of gyro data, clamp
             double val = (axisIndex == 0) ? gyroData.back().x : (axisIndex == 1) ? gyroData.back().y : gyroData.back().z;
             resampled.push_back(val);
             continue;
        }
        
        const GyroSample& p0 = gyroData[gIdx];
        const GyroSample& p1 = gyroData[gIdx+1];
        
        double dt = p1.timestamp - p0.timestamp;
        double alpha = (dt > 1e-9) ? (t - p0.timestamp) / dt : 0.0;
        
        double v0 = (axisIndex == 0) ? p0.x : (axisIndex == 1) ? p0.y : p0.z;
        double v1 = (axisIndex == 0) ? p1.x : (axisIndex == 1) ? p1.y : p1.z;
        
        resampled.push_back(v0 * (1.0 - alpha) + v1 * alpha);
    }
    return resampled;
}

double MotionVerifier::calculatePearsonCorrelation(const std::vector<double>& x, const std::vector<double>& y) {
    if (x.size() != y.size() || x.empty()) return 0.0;
    
    double n = x.size();
    double sum_x = 0, sum_y = 0, sum_xy = 0;
    double sum_sq_x = 0, sum_sq_y = 0;
    
    for (size_t i = 0; i < n; i++) {
        sum_x += x[i];
        sum_y += y[i];
        sum_xy += x[i] * y[i];
        sum_sq_x += x[i] * x[i];
        sum_sq_y += y[i] * y[i];
    }
    
    double numerator = n * sum_xy - sum_x * sum_y;
    double denominator = std::sqrt((n * sum_sq_x - sum_x * sum_x) * (n * sum_sq_y - sum_y * sum_y));
    
    if (std::abs(denominator) < 1e-9) return 0.0;
    return numerator / denominator;
}

VerificationResult MotionVerifier::verify(const std::string& videoPath, const std::string& gyroCSVPath) {
    VerificationResult result;
    result.success = false;
    result.score = 0.0;
    
    std::cout << "DEBUG: Checking path: '" << videoPath << "'" << std::endl;
    std::pair<std::vector<double>, std::vector<double>> opticalFlow;
    if (videoPath.length() >= 4 && videoPath.substr(videoPath.length() - 4) == ".csv") {
         std::cout << "DEBUG: Detected CSV flow input." << std::endl;
         opticalFlow = loadFlowCSV(videoPath);
    } else {
         std::cout << "DEBUG: Treating as video input." << std::endl;
         opticalFlow = calculateOpticalFlow(videoPath);
    }
    
    auto& timestamps = opticalFlow.first;
    auto& visualFlowX = opticalFlow.second;
    
    if (timestamps.empty()) {
        result.message = "Could not extract optical flow from video.";
        return result;
    }
    
    auto gyroData = loadGyroData(gyroCSVPath);
    if (gyroData.empty()) {
        result.message = "Could not load gyro data.";
        return result;
    }
    
    // Sync Gyro Y (Yaw) to Visual Flow X (Pan)
    // Note: Assuming Gyro Y correlates to Flow X
    auto gyroYResampled = resampleGyro(timestamps, gyroData, 1);
    
    // Trim beginning (2 frames)
    if (visualFlowX.size() > 2) {
        visualFlowX.erase(visualFlowX.begin(), visualFlowX.begin() + 2);
        gyroYResampled.erase(gyroYResampled.begin(), gyroYResampled.begin() + 2);
    }
    

    
    auto visualFlowXNorm = normalizeVector(visualFlowX);
    auto gyroYNorm = normalizeVector(gyroYResampled);
    
    double corr = calculatePearsonCorrelation(visualFlowXNorm, gyroYNorm);
    
    result.score = std::abs(corr); // We care about magnitude
    result.success = true;
    result.duration_analyzed = timestamps.back() - timestamps.front();
    result.message = "Analysis complete. Correlation: " + std::to_string(corr);
    
    return result;
}
