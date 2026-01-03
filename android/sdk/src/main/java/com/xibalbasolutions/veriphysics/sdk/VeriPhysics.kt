package com.xibalbasolutions.veriphysics.sdk

import android.content.Context
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import java.io.IOException
import java.util.concurrent.TimeUnit

class VeriPhysics private constructor(private val context: Context) {

    private val sensorRecorder = SensorRecorder(context)
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(60, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .build()

    companion object {
        @Volatile
        private var INSTANCE: VeriPhysics? = null

        fun getInstance(context: Context): VeriPhysics {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: VeriPhysics(context.applicationContext).also { INSTANCE = it }
            }
        }
        
        init {
            System.loadLibrary("veriphysics_sdk")
        }
    }

    external fun verifyCapture(videoPath: String, gyroPath: String): String

    fun startCapture(gyroFile: File) {
        sensorRecorder.start(gyroFile)
    }

    fun stopCapture() {
        sensorRecorder.stop()
    }

    interface UploadCallback {
        fun onSuccess(responseJson: String)
        fun onError(error: String)
    }

    fun uploadBundle(
        apiUrl: String,
        apiKey: String,
        videoFile: File,
        gyroFile: File,
        callback: UploadCallback
    ) {
        val mediaTypeVideo = "video/mp4".toMediaTypeOrNull()
        val mediaTypeCsv = "text/csv".toMediaTypeOrNull()

        // 1. Sign Data
        val signature = signBundle(videoFile.absolutePath, gyroFile.absolutePath)

        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("video", videoFile.name, videoFile.asRequestBody(mediaTypeVideo))
            .addFormDataPart("gyro", gyroFile.name, gyroFile.asRequestBody(mediaTypeCsv))
            .build()

        val request = Request.Builder()
            .url("$apiUrl/verify")
            .header("x-api-key", apiKey)
            .header("x-signature", signature)
            .post(requestBody)
            .build()

        client.newCall(request).enqueue(object : okhttp3.Callback {
            override fun onFailure(call: okhttp3.Call, e: IOException) {
                callback.onError(e.message ?: "Unknown upload error")
            }

            override fun onResponse(call: okhttp3.Call, response: okhttp3.Response) {
                response.use {
                    if (!it.isSuccessful) {
                        callback.onError("Server Error: ${it.code} ${it.message}")
                    } else {
                        val body = it.body?.string() ?: "{}"
                        callback.onSuccess(body)
                    }
                }
            }
        })
    }
    
    private fun signBundle(videoPath: String, gyroPath: String): String {
        try {
            val ks = java.security.KeyStore.getInstance("AndroidKeyStore")
            ks.load(null)
            val alias = "VeriPhysicsKey"
            
            // Create Key if not exists (Lazy Load)
            if (!ks.containsAlias(alias)) {
                val kpg = android.security.keystore.KeyGenParameterSpec.Builder(
                    alias,
                    android.security.keystore.KeyProperties.PURPOSE_SIGN or android.security.keystore.KeyProperties.PURPOSE_VERIFY
                )
                    .setDigests(android.security.keystore.KeyProperties.DIGEST_SHA256)
                    .setSignaturePaddings(android.security.keystore.KeyProperties.SIGNATURE_PADDING_RSA_PKCS1)
                    .build()
                    
                val generator = java.security.KeyPairGenerator.getInstance(
                    android.security.keystore.KeyProperties.KEY_ALGORITHM_RSA, 
                    "AndroidKeyStore"
                )
                generator.initialize(kpg)
                generator.generateKeyPair()
            }
            
            // Sign Hash of files
            val entry = ks.getEntry(alias, null) as java.security.KeyStore.PrivateKeyEntry
            val signature = java.security.Signature.getInstance("SHA256withRSA")
            signature.initSign(entry.privateKey)
            
            // Update with partial bytes or paths
            signature.update(File(videoPath).readBytes()) 
            signature.update(File(gyroPath).readBytes())
            
            return android.util.Base64.encodeToString(signature.sign(), android.util.Base64.NO_WRAP)
        } catch (e: Exception) {
            e.printStackTrace()
            return "signature_failed"
        }
    }
}
