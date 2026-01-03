#ifndef MOTION_VERIFIER_H
#define MOTION_VERIFIER_H

#include <vector>
#include <string>
#include <opencv2/opencv.hpp>

struct GyroSample {
    double timestamp; // seconds
    double x, y, z;
};

struct VerificationResult {
    double score; // 0.0 to 1.0 (Pearson correlation magnitude)
    double causalityScore; // 0.0 to 100.0 (Normalized Truth Score)
    bool isHandheld; // True if physiological tremor (8-12Hz) is detected
    double tremorEnergy; // Energy in the 8-12Hz band
    double duration_analyzed;
    bool success;
    std::string message;
};

class MotionVerifier {
public:
    MotionVerifier();
    ~MotionVerifier();

    /**
     * Verify consistency between a video file and a gyroscope CSV.
     * @param videoPath Path to mp4 video
     * @param gyroCSVPath Path to CSV (timestamp, x, y, z)
     */
    VerificationResult verify(const std::string& videoPath, const std::string& gyroCSVPath);

private:
    std::vector<GyroSample> loadGyroData(const std::string& path);
    
    // Calculates dense optical flow and returns a signal of average flow (X, Y) per frame
    // Returns pair of vectors: <Time, FlowX> (focusing on X for now)
    std::pair<std::vector<double>, std::vector<double>> calculateOpticalFlow(const std::string& videoPath);
    
    // Resamples gyro data to match video timestamps
    std::vector<double> resampleGyro(
        const std::vector<double>& targetTimestamps, 
        const std::vector<GyroSample>& gyroData, 
        int axisIndex // 0=x, 1=y, 2=z
    );

    double calculatePearsonCorrelation(const std::vector<double>& x, const std::vector<double>& y);
    std::vector<double> normalizeVector(const std::vector<double>& v);
    std::pair<std::vector<double>, std::vector<double>> loadFlowCSV(const std::string& path);
    
    // Analyzes gyro magnitude for 8-12Hz physiological tremor
    // Returns pair<bool isHandheld, double energy>
    std::pair<bool, double> analyzeTremor(const std::vector<GyroSample>& gyroData);
};

#endif // MOTION_VERIFIER_H
