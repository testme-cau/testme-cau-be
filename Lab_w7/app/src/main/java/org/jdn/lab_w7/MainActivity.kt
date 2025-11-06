package org.jdn.lab_w7

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.BatteryManager
import android.os.Bundle
import android.provider.MediaStore
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.jdn.lab_w7.ui.theme.Lab_w7Theme

class MainActivity : ComponentActivity() {

    private val requestPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) {
                openCamera()
            } else {
                Toast.makeText(this, "Camera permission denied",
                    Toast.LENGTH_SHORT).show()
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            Lab_w7Theme {
                Scaffold(
                    modifier = Modifier.fillMaxSize(),
                ) { innerPadding ->
                    MainScreen(
                        modifier = Modifier.padding(innerPadding),
                        onOpenCamera = {
                            requestPermissionLauncher.launch(Manifest.permission.CAMERA)
                        },
                        onSendBattery = {
                            val batteryLevel = getBatteryPercentage()
                            val intent = Intent(this, SecondActivity::class.java)
                            intent.putExtra("BATTERY_LEVEL", batteryLevel)
                            startActivity(intent)
                        },
                        getBatteryLevel = { getBatteryPercentage() }
                    )
                }
            }
        }
    }

    private fun getBatteryPercentage(): Int {
        val batteryManager = getSystemService(Context.BATTERY_SERVICE) as BatteryManager
        return batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
    }

    private fun openCamera() {
        val intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        try {
            startActivity(intent)
        } catch (e: Exception) {
            Toast.makeText(this, "No camera app found",
                Toast.LENGTH_SHORT).show()
        }
    }
}

@Composable
fun MainScreen(
    modifier: Modifier = Modifier,
    onOpenCamera: () -> Unit,
    onSendBattery: () -> Unit,
    getBatteryLevel: () -> Int
) {
    val batteryLevel = remember { mutableStateOf(getBatteryLevel()) }
    
    // Update battery level periodically
    LaunchedEffect(Unit) {
        batteryLevel.value = getBatteryLevel()
    }
    
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        horizontalAlignment = Alignment.Start
    ) {
        // Battery display at the top
        Text(
            text = "Battery: ${batteryLevel.value}%",
            fontSize = 20.sp,
            modifier = Modifier.padding(vertical = 16.dp)
        )
        
        // Buttons
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Button(
                onClick = onOpenCamera,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                shape = MaterialTheme.shapes.extraSmall,
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                )
            ) {
                Text(
                    "OPEN CAMERA",
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Button(
                onClick = onSendBattery,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                shape = MaterialTheme.shapes.extraSmall,
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                )
            ) {
                Text(
                    "SEND",
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
fun PreviewMainScreen() {
    Lab_w7Theme {
        MainScreen(
            onOpenCamera = {},
            onSendBattery = {},
            getBatteryLevel = { 100 }
        )
    }
}