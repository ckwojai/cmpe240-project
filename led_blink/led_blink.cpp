// Handles input and output
#include <iostream>
 
// For delay function
#include <chrono> 
 
// Handles threads of program execution
#include <thread>
 
// Signal handling
#include <signal.h>
 
#include <JetsonGPIO.h>
 
// Pin Definitions
int led_pin = 7;
 
// Flag to determine when user wants to end program
bool done = false;
 
// Function called by Interrupt
void signalHandler (int s){
  done = true;
}
 
int main() {
 
  // When CTRL+C pressed, signalHandler will be called
  // to interrupt the programs execution
  signal(SIGINT, signalHandler);
 
  // Pin Definitions 
  GPIO::setmode(GPIO::BOARD);
 
  // LED pin gets set to high initially
  GPIO::setup(led_pin, GPIO::OUT, GPIO::HIGH);
 
  std::cout << "Press CTRL+C to stop the LED" << std::endl;
 
  int curr_value = GPIO::HIGH;
 
  // Blink LED every 0.5 seconds
  while(!done) {
 
    std::this_thread::sleep_for(std::chrono::milliseconds(500));
 
    curr_value = GPIO::HIGH;
 
    GPIO::output(led_pin, curr_value);
 
    std::cout << "LED is ON" << std::endl;
 
    std::this_thread::sleep_for(std::chrono::milliseconds(500));
 
    curr_value = GPIO::LOW;
 
    GPIO::output(led_pin, curr_value);
 
    std::cout << "LED is OFF" << std::endl;
  }
 
  GPIO::cleanup();
 
  return 0;
}
