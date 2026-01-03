#include <iostream>
#include "MotionVerifier.h"

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cout << "Usage: ./vp_cli <video_path> <gyro_csv_path>" << std::endl;
        return 1;
    }
    
    std::string videoPath = argv[1];
    std::string gyroPath = argv[2];
    
    MotionVerifier verifier;
    VerificationResult result = verifier.verify(videoPath, gyroPath);
    
    if (result.success) {
        // Structured output (YAML-like) for easy parsing
        std::cout << "SUCCESS: " << result.message << std::endl;
        std::cout << "SCORE: " << result.score << std::endl;
        std::cout << "CAUSALITY_SCORE: " << result.causalityScore << std::endl;
        std::cout << "IS_HANDHELD: " << (result.isHandheld ? "true" : "false") << std::endl;
        std::cout << "TREMOR_ENERGY: " << result.tremorEnergy << std::endl;
        std::cout << "DURATION: " << result.duration_analyzed << "s" << std::endl;
        
        // Simple threshold
        if (result.score > 0.7) {
            std::cout << "VERDICT: REAL/CONSISTENT" << std::endl;
        } else {
            std::cout << "VERDICT: FAKE/INCONSISTENT" << std::endl;
        }
    } else {
        std::cerr << "FAILURE: " << result.message << std::endl;
        return 1;
    }
    
    return 0;
}
