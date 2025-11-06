package org.jdn.lab_w7

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.jdn.lab_w7.ui.theme.Lab_w7Theme

class SecondActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        // Receive battery percentage from MainActivity
        val batteryLevel = intent.getIntExtra("BATTERY_LEVEL", -1)
        
        setContent {
            Lab_w7Theme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    BatteryDisplayScreen(
                        batteryLevel = batteryLevel,
                        modifier = Modifier.padding(innerPadding)
                    )
                }
            }
        }
    }
}

@Composable
fun BatteryDisplayScreen(batteryLevel: Int, modifier: Modifier = Modifier) {
    Box(
        modifier = modifier.fillMaxSize(),
        contentAlignment = Alignment.TopStart
    ) {
        Text(
            text = if (batteryLevel != -1) {
                "Battery: $batteryLevel%"
            } else {
                "No battery data received"
            },
            fontSize = 24.sp
        )
    }
}

