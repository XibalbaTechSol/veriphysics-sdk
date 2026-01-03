#include <jni.h>
#include <string>
#include "MotionVerifier.h"

extern "C" JNIEXPORT jstring JNICALL
Java_com_xibalbasolutions_veriphysics_MainActivity_verifyCapture(
        JNIEnv* env,
        jobject /* this */,
        jstring videoPath,
        jstring gyroPath) {
            
    const char* cVideoPath = env->GetStringUTFChars(videoPath, 0);
    const char* cGyroPath = env->GetStringUTFChars(gyroPath, 0);

    MotionVerifier verifier;
    VerificationResult result = verifier.verify(std::string(cVideoPath), std::string(cGyroPath));

    env->ReleaseStringUTFChars(videoPath, cVideoPath);
    env->ReleaseStringUTFChars(gyroPath, cGyroPath);

    std::string report = "Score: " + std::to_string(result.score) + 
                         " | " + (result.success ? "Success" : "Failed") + 
                         " | " + result.message;
                         
    return env->NewStringUTF(report.c_str());
}
