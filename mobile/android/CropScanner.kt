// android/app/src/main/java/ai/agrovision/scanner/CropScanner.kt
package ai.agrovision.scanner

import android.content.Context
import android.graphics.Bitmap
import org.tensorflow.lite.DataType
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.support.common.ops.NormalizeOp
import org.tensorflow.lite.support.image.ImageProcessor
import org.tensorflow.lite.support.image.TensorImage
import org.tensorflow.lite.support.image.ops.ResizeOp
import java.io.FileInputStream
import java.nio.channels.FileChannel

class CropScanner(context: Context) {
    private var interpreter: Interpreter

    init {
        // Enforce NNAPI GPU/NPU hardware acceleration delegates
        val options = Interpreter.Options().apply {
            setNumThreads(4)
            useNNAPI = true
        }
        interpreter = Interpreter(loadModelFile(context, "crop_disease_quant.tflite"), options)
    }

    private fun loadModelFile(context: Context, modelPath: String): java.nio.MappedByteBuffer {
        val fileDescriptor = context.assets.openFd(modelPath)
        val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
        val fileChannel = inputStream.channel
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, fileDescriptor.startOffset, fileDescriptor.declaredLength)
    }

    fun scanLeaf(bitmap: Bitmap): Pair<Int, Float> {
        // Preprocess Bitmap image to INT8 normalized format
        val imageProcessor = ImageProcessor.Builder()
            .add(ResizeOp(224, 224, ResizeOp.Method.BILINEAR))
            .add(NormalizeOp(floatArrayOf(123.675f, 116.28f, 103.53f), floatArrayOf(58.395f, 57.12f, 57.375f)))
            .build()
            
        val tensorImage = TensorImage(DataType.INT8)
        tensorImage.load(bitmap)
        val processedImage = imageProcessor.process(tensorImage)

        // Outputs tensor allocation (1, num_classes)
        val outputBuffer = Array(1) { ByteArray(4) } // Assuming 4 target classes
        
        interpreter.run(processedImage.buffer, outputBuffer)

        // Find highest class logit probability
        val result = outputBuffer[0]
        var maxIdx = 0
        var maxVal = -128.toByte()
        for (i in result.indices) {
            if (result[i] > maxVal) {
                maxVal = result[i]
                maxIdx = i
            }
        }
        // Dequantize logic: (value - zero_point) * scale
        val confidence = (maxVal.toFloat() + 128f) / 255.0f
        return Pair(maxIdx, confidence)
    }
}
