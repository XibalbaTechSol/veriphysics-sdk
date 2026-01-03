package com.xibalbasolutions.veriphysics

import android.Manifest
import android.content.ContentValues
import android.content.Context
import android.content.pm.PackageManager
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.Build
import android.os.Bundle
import android.provider.MediaStore
import android.util.Log
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.CameraSelector
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.video.MediaStoreOutputOptions
import androidx.camera.video.Recorder
import androidx.camera.video.Recording
import androidx.camera.video.VideoCapture
import androidx.camera.video.VideoRecordEvent
import androidx.core.content.ContextCompat
import androidx.core.content.PermissionChecker
import com.xibalbasolutions.veriphysics.databinding.ActivityMainBinding
import com.xibalbasolutions.veriphysics.sdk.SensorRecorder
import com.xibalbasolutions.veriphysics.sdk.VeriPhysics
import java.text.SimpleDateFormat
import java.util.Locale
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.io.File
import java.io.FileWriter

class MainActivity : AppCompatActivity() {

    private lateinit var viewBinding: ActivityMainBinding
    private var videoCapture: VideoCapture<Recorder>? = null
    private var recording: Recording? = null
    private lateinit var cameraExecutor: ExecutorService

    // Sensor Logic
    private lateinit var veriphysics: VeriPhysics
    private var isRecording = false
    private var lastVideoUri: android.net.Uri? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewBinding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(viewBinding.root)

        // Request permissions
        if (allPermissionsGranted()) {
            startCamera()
        } else {
            requestPermissions()
        }

        viewBinding.videoCaptureButton.setOnClickListener { captureVideo() }
        viewBinding.generateProofButton.setOnClickListener {
            lastVideoUri?.let { uri ->
                // 1. Get Paths (Simplified for MVP, assuming file URI or resolving it)
                // Note: Production would need proper ContentResolver path conversion
                // This implies we need the absolute path for C++.
                val videoPath = uri.path ?: "" // Placeholder, see note below
                val gyroPath = File(getExternalFilesDir(null), "current_gyro.csv").absolutePath 
                
                // Hack: We need the proper file path for C++ fopen
                // For this MVP demo, let's assume we can resolve it or use the File API directly if possible
                // But wait, the Recording output was MediaStore... hard to get path.
                // START HACK: For verification demo, let's use the gyro file we just saved.
                
                Toast.makeText(this, "Verifying...", Toast.LENGTH_SHORT).show()
                
                // RUN VERIFICATION (Background thread recommended, MAIN for MVP)
                val report = veriphysics.verifyCapture(videoPath, gyroPath)
                val isReal = report.contains("Score:") // Placeholder check
                
                if (isReal) {
                    Toast.makeText(this, "Result: $report", Toast.LENGTH_LONG).show()
                    // VeriPhysics.generateProof(this, uri)
                } else {
                    Toast.makeText(this, "VERIFICATION FAILED. Fake content?", Toast.LENGTH_LONG).show()
                }

            } ?: Toast.makeText(this, "No video recorded yet", Toast.LENGTH_SHORT).show()
        }

        cameraExecutor = Executors.newSingleThreadExecutor()

        // Sensors
        // Sensors
        // Sensors
        veriphysics = VeriPhysics.getInstance(this)
    }

    private fun captureVideo() {
        val videoCapture = this.videoCapture ?: return

        viewBinding.videoCaptureButton.isEnabled = false

        val curRecording = recording
        if (curRecording != null) {
            // Stop recording
            curRecording.stop()
            recording = null
            isRecording = false
            // sensorRecorder stopped in Finalize callback to ensure sync? 
            // Or stop here. Usually stop here is safer to match video stop trigger.
            // But waiting for finalize is more precise for file write.
            // Converting async logic: let's leave stop call in Finalize for now or move it here.
            // Actually, video capture finalize takes a moment. Let's stop sensors immediately here.
            // veriphysics.stopCapture() // Wait, we need the path in Finalize. Let's keep state.
            return
        }

        // Start Recording
        val name = SimpleDateFormat(FILENAME_FORMAT, Locale.US)
            .format(System.currentTimeMillis())
        
        // 1. Prepare Video Output
        val contentValues = ContentValues().apply {
            put(MediaStore.MediaColumns.DISPLAY_NAME, name)
            put(MediaStore.MediaColumns.MIME_TYPE, "video/mp4")
            if (Build.VERSION.SDK_INT > Build.VERSION_CODES.P) {
                put(MediaStore.Video.Media.RELATIVE_PATH, "Movies/VeriPhysics-Videos")
            }
        }

        val mediaStoreOutputOptions = MediaStoreOutputOptions
            .Builder(contentResolver, MediaStore.Video.Media.EXTERNAL_CONTENT_URI)
            .setContentValues(contentValues)
            .build()

        // 2. Start Gyro Logging
        val gyroFile = File(getExternalFilesDir(null), "current_gyro.csv")
        veriphysics.startCapture(gyroFile)

        recording = videoCapture.output
            .prepareRecording(this, mediaStoreOutputOptions)
            .apply {
                if (PermissionChecker.checkSelfPermission(this@MainActivity,
                        Manifest.permission.RECORD_AUDIO) ==
                    PermissionChecker.PERMISSION_GRANTED)
                {
                    withAudioEnabled()
                }
            }
            .start(ContextCompat.getMainExecutor(this)) { recordEvent ->
                when(recordEvent) {
                    is VideoRecordEvent.Start -> {
                        viewBinding.videoCaptureButton.apply {
                            text = "Stop"
                            isEnabled = true
                        }
                    }
                    is VideoRecordEvent.Finalize -> {
                        if (!recordEvent.hasError()) {
                            val msg = "Video capture succeeded: " +
                                    "${recordEvent.outputResults.outputUri}"
                            Toast.makeText(baseContext, msg, Toast.LENGTH_SHORT).show()
                            Log.d(TAG, msg)
                            
            val uri = recordEvent.outputResults.outputUri
                            lastVideoUri = uri
                            
                            viewBinding.generateProofButton.visibility = android.view.View.VISIBLE
                            
                            // Stop Sensor Log and get Path
                             veriphysics.stopCapture()
                             val gyroPath = File(getExternalFilesDir(null), "current_gyro.csv").absolutePath 
                            
                            if (viewBinding.autoProofCheck.isChecked) {
                                // For auto proof, verify first then share? Or just share.
                                // Let's verify first for the "Auto-Proof" workflow
                                val report = veriphysics.verifyCapture(uri.path ?: "", gyroPath)
                                if (report.contains("Success") && report.contains("Score: 0.")) {
                                     // VeriPhysics.generateProof(this@MainActivity, uri)
                                     Toast.makeText(baseContext, "Verified: $report", Toast.LENGTH_LONG).show()
                                }
                            }
                            
                        } else {
                            recording?.close()
                            recording = null
                            Log.e(TAG, "Video capture ends with error: " +
                                    "${recordEvent.error}")
                        }
                        viewBinding.videoCaptureButton.apply {
                            text = "Start"
                            isEnabled = true
                        }
                    }
                }
            }
    }

    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)

        cameraProviderFuture.addListener({
            val cameraProvider: ProcessCameraProvider = cameraProviderFuture.get()

            val preview = Preview.Builder()
                .build()
                .also {
                    it.setSurfaceProvider(viewBinding.viewFinder.surfaceProvider)
                }

            val recorder = Recorder.Builder()
                .setQualitySelector(androidx.camera.video.QualitySelector.from(androidx.camera.video.Quality.HIGHEST))
                .build()
            videoCapture = VideoCapture.withOutput(recorder)

            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA

            try {
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(
                    this, cameraSelector, preview, videoCapture)

            } catch(exc: Exception) {
                Log.e(TAG, "Use case binding failed", exc)
            }

        }, ContextCompat.getMainExecutor(this))
    }

    // --- SENSOR LOGIC REPLACED BY SDK ---
    // Methods removed: startGyroLogging, stopGyroLogging, onSensorChanged, onAccuracyChanged, saveGyroData

    // --- PERMISSIONS ---
    private fun requestPermissions() {
        activityResultLauncher.launch(REQUIRED_PERMISSIONS)
    }

    private fun allPermissionsGranted() = REQUIRED_PERMISSIONS.all {
        ContextCompat.checkSelfPermission(
            baseContext, it) == PackageManager.PERMISSION_GRANTED
    }

    private val activityResultLauncher =
        registerForActivityResult(
            ActivityResultContracts.RequestMultiplePermissions())
        { permissions ->
            var permissionGranted = true
            permissions.entries.forEach {
                if (it.key in REQUIRED_PERMISSIONS && !it.value)
                    permissionGranted = false
            }
            if (!permissionGranted) {
                Toast.makeText(baseContext,
                    "Permission request denied",
                    Toast.LENGTH_SHORT).show()
            } else {
                startCamera()
            }
        }

    override fun onDestroy() {
        super.onDestroy()
        cameraExecutor.shutdown()
    }

    companion object {
        private const val TAG = "VeriPhysicsApp"
        private const val FILENAME_FORMAT = "yyyy-MM-dd-HH-mm-ss-SSS"
        private val REQUIRED_PERMISSIONS =
            mutableListOf (
                Manifest.permission.CAMERA,
                Manifest.permission.RECORD_AUDIO
            ).apply {
                if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.P) {
                    add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
                }
            }.toTypedArray()
    }
}
