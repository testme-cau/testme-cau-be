package org.jdn.lab_w5

import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.jdn.lab_w5.ui.theme.Lab_w5Theme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            Lab_w5Theme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    StudentRegistrationScreen(
                        modifier = Modifier.padding(innerPadding)
                    )
                }
            }
        }
    }
}

enum class Plan {
    BASIC, STANDARD, EXPERT
}

@Composable
fun StudentRegistrationScreen(modifier: Modifier = Modifier) {
    var name by remember { mutableStateOf("") }
    var studentId by remember { mutableStateOf("") }
    var selectedPlan by remember { mutableStateOf(Plan.BASIC) }
    var notificationsEnabled by remember { mutableStateOf(false) }
    var termsAgreed by remember { mutableStateOf(false) }
    var showSummary by remember { mutableStateOf(false) }
    
    val context = LocalContext.current
    
    fun validate(): Pair<Boolean, String> {
        return when {
            name.isBlank() -> Pair(false, "Name cannot be empty")
            studentId.isBlank() -> Pair(false, "Student ID cannot be empty")
            !termsAgreed -> Pair(false, "You must agree to the terms")
            else -> Pair(true, "")
        }
    }
    
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Title
        Text(
            text = "Student Registration",
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold,
            modifier = Modifier
                .align(Alignment.Start)
                .padding(bottom = 8.dp)
        )

        HorizontalDivider(
            color = Color.Gray,
            thickness = 1.dp,
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 12.dp)
        )
        
        // Name Input
        OutlinedTextField(
            value = name,
            onValueChange = { 
                name = it
                showSummary = false
            },
            label = { Text("Name") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 8.dp)
        )
        
        // Student ID Input
        OutlinedTextField(
            value = studentId,
            onValueChange = { 
                studentId = it
                showSummary = false
            },
            label = { Text("Student ID") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 12.dp)
        )
        
        // Plan Selection
        Text(
            text = "Select Plan",
            fontSize = 16.sp,
            fontWeight = FontWeight.Medium,
            modifier = Modifier
                .align(Alignment.Start)
                .padding(bottom = 4.dp)
        )
        
        Column(modifier = Modifier.fillMaxWidth()) {
            Plan.values().forEach { plan ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 2.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    RadioButton(
                        selected = selectedPlan == plan,
                        onClick = { 
                            selectedPlan = plan
                            showSummary = false
                        }
                    )
                    Text(
                        text = plan.name.lowercase().replaceFirstChar { it.uppercase() },
                        modifier = Modifier.padding(start = 8.dp)
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(4.dp))
        
        // Notifications Switch
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 4.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Notifications: ${if (notificationsEnabled) "ON" else "OFF"}",
                fontSize = 16.sp
            )
            Switch(
                checked = notificationsEnabled,
                onCheckedChange = { 
                    notificationsEnabled = it
                    showSummary = false
                }
            )
        }
        
        Spacer(modifier = Modifier.height(4.dp))
        
        // Terms Checkbox
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 4.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Checkbox(
                checked = termsAgreed,
                onCheckedChange = { 
                    termsAgreed = it
                    showSummary = false
                }
            )
            Text(
                text = "I agree to the terms.",
                modifier = Modifier.padding(start = 8.dp)
            )
        }
        
        Spacer(modifier = Modifier.height(12.dp))
        
        // Action Buttons
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Button(
                onClick = {
                    val (isValid, errorMessage) = validate()
                    if (isValid) {
                        showSummary = true
                    } else {
                        Toast.makeText(context, errorMessage, Toast.LENGTH_SHORT).show()
                        showSummary = false
                    }
                },
                modifier = Modifier.weight(1f),
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.primary
                )
            ) {
                Text("Preview")
            }
            
            Button(
                onClick = {
                    val (isValid, errorMessage) = validate()
                    if (isValid) {
                        Toast.makeText(context, "Submitted", Toast.LENGTH_SHORT).show()
                    } else {
                        Toast.makeText(context, errorMessage, Toast.LENGTH_SHORT).show()
                    }
                },
                modifier = Modifier.weight(1f),
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.secondary
                )
            ) {
                Text("Submit")
            }
        }
        
        // Summary Card
        if (showSummary) {
            Spacer(modifier = Modifier.height(12.dp))
            
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFFF5F5F5)
                )
            ) {
                Column(
                    modifier = Modifier.padding(12.dp),
                    verticalArrangement = Arrangement.spacedBy(2.dp)
                ) {
                    Text(text = "Name: $name")
                    Text(text = "ID: $studentId")
                    Text(text = "Plan: ${selectedPlan.name.lowercase().replaceFirstChar { it.uppercase() }}")
                    Text(text = "Notifications: ${if (notificationsEnabled) "ON" else "OFF"}")
                    Text(text = "Agreed: $termsAgreed")
                }
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
fun StudentRegistrationPreview() {
    Lab_w5Theme {
        StudentRegistrationScreen()
    }
}