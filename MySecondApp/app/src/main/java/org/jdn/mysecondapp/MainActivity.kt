package org.jdn.mysecondapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import org.jdn.mysecondapp.ui.theme.MySecondAppTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MySecondAppTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    Greeting(
                        name = "Android",
                        modifier = Modifier.padding(innerPadding)
                    )
                }
            }
        }
    }
}

/**
 * Data class to represent a student with name, ID, and GPA.
 */
data class Student(val name: String, val id: String, val gpa: Double) {
    override fun toString(): String {
        return "Name: $name, ID: $id, GPA: $gpa"
    }
}

private fun List<Student>.toNumberedText(): String =
    if (isEmpty()) "No students." else
        mapIndexed { idx, s -> "${idx + 1}. $s" }
            .joinToString("\n")

@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    var inputName by remember { mutableStateOf("") }
    var inputID by remember { mutableStateOf("") }
    var inputGPA by remember { mutableStateOf("") }
    var outputText by remember { mutableStateOf("") }
    var students by remember { mutableStateOf(listOf<Student>()) }

    Column(
        modifier = modifier.padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        OutlinedTextField(
            value = inputName,
            onValueChange = { inputName = it },
            label = { Text("Name") },
            modifier = Modifier.fillMaxWidth()
        )

        OutlinedTextField(
            value = inputID,
            onValueChange = { inputID = it },
            label = { Text("ID") },
            modifier = Modifier.fillMaxWidth()
        )

        OutlinedTextField(
            value = inputGPA,
            onValueChange = { inputGPA = it },
            label = { Text("GPA") },
            modifier = Modifier.fillMaxWidth()
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Button(
                onClick = {
                    if (inputName.isNotBlank() && inputID.isNotBlank() && inputGPA.toDoubleOrNull() != null) {
                        val student = Student(inputName, inputID, inputGPA.toDouble())
                        students = students + student
                        outputText = "Added: $student"
                        inputName = ""
                        inputID = ""
                        inputGPA = ""
                    } else {
                        outputText = "Please enter valid Name, ID, and GPA."
                    }
                },
                modifier = Modifier.weight(1f)
            ) {
                Text("Input")
            }

            Button(
                onClick = {
                    outputText = students.toNumberedText()
                },
                modifier = Modifier.weight(1f)
            ) {
                Text("Output")
            }
        }

        if (outputText.isNotEmpty()) {
            Text(outputText, style = MaterialTheme.typography.bodyLarge)
        }
    }
}
