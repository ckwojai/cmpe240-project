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
int switch_pin = 11;
 
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
  // Swtich pin as input
  GPIO:setup(switch_pin, GPIO::IN);
 
  int prev_value = GPIO::input(switch_pin);
  int led_state = GPIO::LOW;
  GPIO::output(led_pin, led_state);
  // Blink LED every 0.5 seconds
  while(!done) {
    int curr_value = GPIO::input(switch_pin);
    if (curr_value != prev_value) {
      led_state = led_state ? GPIO::LOW : GPIO::HIGH;
      GPIO::output(led_pin, led_state);
      prev_value = curr_value;
    }
  }
 
  GPIO::cleanup();
 
  return 0;
}
