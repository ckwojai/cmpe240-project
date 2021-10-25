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
  // Swtich pin as input
  GPIO:setup(switch_pin, GPIO::IN);

  // LED pin as output
  int led_state = GPIO::LOW; // LED pin set to low initially
  GPIO::setup(led_pin, GPIO::OUT, led_state;

  int prev_value = GPIO::input(switch_pin);
  while(!done) {
    int curr_value = GPIO::input(switch_pin); // get state of switch
    if (curr_value != prev_value) { // if state change, toggle the led
      led_state = led_state ? GPIO::LOW : GPIO::HIGH;
      GPIO::output(led_pin, led_state);
      prev_value = curr_value;
    }
  }
 
  GPIO::cleanup();
 
  return 0;
}
