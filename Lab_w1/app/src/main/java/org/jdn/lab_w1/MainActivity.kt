package org.jdn.lab_w1

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import org.jdn.lab_w1.ui.theme.Lab_w1Theme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            Lab_w1Theme {
                // A surface container using the 'background' color from the theme
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    Greeting("Seongmin Choi")
                }
            }
        }
    }
}

@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    Column(
        modifier = Modifier.fillMaxSize(),                 // 전체 화면 채우기
        verticalArrangement = Arrangement.Center,          // 세로 방향 가운데
        horizontalAlignment = Alignment.CenterHorizontally // 가로 방향 가운데
    ) {
        Text(text = "Hello, $name!")
        Text(text = "Student ID: 20203876")
        Text(text = "Date: 2025-09-11")
    }
}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    Lab_w1Theme {
        Greeting("Android")
    }
}