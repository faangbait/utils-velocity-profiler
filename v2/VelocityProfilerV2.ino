// Clockwise and counter-clockwise definitions.
// Depending on how you wired your motors, you may need to swap.
#define FORWARD  1
#define BACKWARD 0

// Motor definitions to make life easier:
#define MOTOR_A 0
#define MOTOR_B 1

// Pin Assignments //
//Default pins:
#define DIRA 2 // Direction control for motor A
#define PWMA 3  // PWM control (speed) for motor A
#define DIRB 4 // Direction control for motor B
#define PWMB 11 // PWM control (speed) for motor B
#define STOP 5  // Define pin #2 as input
#define REVERSE 6 // Define pin #4 as input

int SPEED = 255; //Adjust motor speed here           
int DURATION = 2000; //Test point duration in ms


void setup()
{
  pinMode(STOP, INPUT);
  pinMode(REVERSE, INPUT);
  digitalWrite(REVERSE, LOW);
  digitalWrite(STOP,LOW);
  setupArdumoto(); // Set all pins as outputs
  Serial.begin(115200);
}

void loop()
{

  //Drive to next point
  while ((digitalRead(STOP) == HIGH) && (digitalRead(REVERSE) == HIGH))
  {
    driveArdumoto(MOTOR_A,FORWARD,SPEED); 
    driveArdumoto(MOTOR_B,FORWARD,SPEED);
    Serial.print("G"); // Added in V2
  }


  //Stop and take reading, then drive off block
  while ((digitalRead(STOP) == LOW) && (digitalRead(REVERSE) == HIGH))
  {
    //Actively brake the car
    driveArdumoto(MOTOR_A,BACKWARD,SPEED);
    driveArdumoto(MOTOR_B,BACKWARD,SPEED);
    delay(50);                                    //Adjust this if braking sucks
    stopArdumoto(MOTOR_A);
    stopArdumoto(MOTOR_B);

    //Take data point
    Serial.print('S'); // Changed from X in V2
    delay(DURATION);                                 //Data point duration
    driveArdumoto(MOTOR_A,FORWARD,SPEED);
    driveArdumoto(MOTOR_B,FORWARD,SPEED);
    delay(1500);                                  //Make sure to clear block
  }

  
 // if (digitalRead(REVERSE) == LOW)
 // {
 //   Serial.print("Y");                            //Send serial command to iterate the test
 //   delay(100);                                   //Debounce delay
 // }

  
  //Drive back to beginning
  while (digitalRead(REVERSE) == LOW)
  {
    driveArdumoto(MOTOR_A,BACKWARD,SPEED);
    driveArdumoto(MOTOR_B,BACKWARD,SPEED); 
      Serial.print("R"); // Changed from Y in V2
  }
}


// driveArdumoto drives 'motor' in 'dir' direction at 'spd' speed
void driveArdumoto(byte motor, byte dir, byte spd)
{
  if (motor == MOTOR_A)
  {
    digitalWrite(DIRA, dir);
    analogWrite(PWMA, spd);
  }
  else if (motor == MOTOR_B)
  {
    digitalWrite(DIRB, dir);
    analogWrite(PWMB, spd);
  }  
}

// stopArdumoto makes a motor stop
void stopArdumoto(byte motor)
{
  driveArdumoto(motor, 0, 0);
}

// setupArdumoto initialize all pins
void setupArdumoto()
{
  // All pins should be setup as outputs:
  pinMode(PWMA, OUTPUT);
  pinMode(PWMB, OUTPUT);
  pinMode(DIRA, OUTPUT);
  pinMode(DIRB, OUTPUT);

  // Initialize all pins as low:
  digitalWrite(PWMA, LOW);
  digitalWrite(PWMB, LOW);
  digitalWrite(DIRA, LOW);
  digitalWrite(DIRB, LOW);
}

