package com.xibalbasolutions.veriphysics.sdk

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.SystemClock
import java.io.File
import java.io.FileWriter
import java.io.IOException

class SensorRecorder(private val context: Context) : SensorEventListener {

    private var sensorManager: SensorManager? = null
    private var gyroscope: Sensor? = null
    private var isRecording = false
    private var writer: FileWriter? = null
    private var outputFile: File? = null

    init {
        sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
        gyroscope = sensorManager?.getDefaultSensor(Sensor.TYPE_GYROSCOPE)
    }

    fun start(outputFile: File) {
        if (isRecording) return
        this.outputFile = outputFile
        
        try {
            writer = FileWriter(outputFile)
            // Write Header
            writer?.append("timestamp,x,y,z\n")
        } catch (e: IOException) {
            e.printStackTrace()
            return
        }

        isRecording = true
        // REGISTER LISTENER
        // SENSOR_DELAY_FASTEST is critical for high frequency capture needed for integration
        sensorManager?.registerListener(this, gyroscope, SensorManager.SENSOR_DELAY_FASTEST)
    }

    fun stop() {
        if (!isRecording) return
        isRecording = false
        sensorManager?.unregisterListener(this)
        
        try {
            writer?.flush()
            writer?.close()
        } catch (e: IOException) {
            e.printStackTrace()
        }
    }

    override fun onSensorChanged(event: SensorEvent?) {
        if (event == null || !isRecording) return
        
        if (event.sensor.type == Sensor.TYPE_GYROSCOPE) {
            val x = event.values[0]
            val y = event.values[1]
            val z = event.values[2]
            
            // Time in nanoseconds
            val timestamp = event.timestamp
            
            try {
                writer?.append("$timestamp,$x,$y,$z\n")
            } catch (e: IOException) {
                // Ignore drop
            }
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {
        // No-op
    }
}
