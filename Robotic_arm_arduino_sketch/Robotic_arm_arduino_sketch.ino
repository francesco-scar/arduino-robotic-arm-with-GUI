/* More info at https://github.com/francesco-scar/arduino-robotic-arm-with-GUI */

#include <Servo.h>
#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
#include <EEPROM.h>

LiquidCrystal_I2C lcd(0x3f, 16, 2);


#define SERVO1 2
#define SERVO2 3
#define SERVO3 4
#define SERVO4 5
#define SERVO5 6
#define SERVO6 7

#define STEPS_PER_SECOND 50.0

int nOfSaved = 0;
float savedPositions[16][7] =  {{0, 0, 0, 0, 0, 0, 0},
                                {0, 0, 0, 0, 0, 0, 0},
                                {0, 0, 0, 0, 0, 0, 0},
                                {0, 0, 0, 0, 0, 0, 0},
                                {0, 0, 0, 0, 0, 0, 0},
                                {0, 0, 0, 0, 0, 0, 0},
                                {0, 0, 0, 0, 0, 0, 0},
                                {0, 0, 0, 0, 0, 0, 0},
                                {0, 0, 0, 0, 0, 0, 0},
                                {0, 0, 0, 0, 0, 0, 0},
                                {0, 0, 0, 0, 0, 0, 0},
                                {0, 0, 0, 0, 0, 0, 0},
                                {0, 0, 0, 0, 0, 0, 0},
                                {0, 0, 0, 0, 0, 0, 0},
                                {0, 0, 0, 0, 0, 0, 0},
                                {0, 0, 0, 0, 0, 0, 0}};

float tmpArray[7] = {0, 0, 0, 0, 0, 0, 0};
float currentJoint[6] = {0, 100, 90, 180, 160, 0};

String result = "";

bool serialReceived = false; 


Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;
Servo servo5;
Servo servo6;


  

void setup() {
  lcd.init();
  
  lcd.backlight();
  
  Serial.begin(9600);

  pinMode(13, OUTPUT);

  delay(2000);

  Serial.println(F("\n\nBasic arduino-based robotic arm controlled by a GUI running on the PC that send command to the board using serial comunication\n\nYou can find more info at https://github.com/francesco-scar/arduino-robotic-arm-with-GUI"));

  delay(1000);

  unsigned long millisInizio = millis();
  
  while (millis()-millisInizio <= 5000){
    Serial.println(F("Connecting to PC\nYou can find more info about this project at https://github.com/francesco-scar/arduino-robotic-arm-with-GUI"));
    delay(50);
  }
  
  servo2.attach(SERVO2);
  servo2.write(100);

  delay(300);
  servo3.attach(SERVO3);
  servo3.write(90);
  
  delay(500);
  servo6.attach(SERVO6);
  servo6.write(0);
  
  delay(200);
  servo5.attach(SERVO5);
  servo5.write(160);
  
  delay(500);
  servo4.attach(SERVO4);
  servo4.write(180);  
  
  delay(1000);
  servo1.attach(SERVO1);
  servo1.write(0);
  delay(1000);
}

void loop() {
  char c;
  if (Serial.available()){
    result = "";
    do {
      c = Serial.read();
      result += c;
      delay(10);
    } while(Serial.available() && c != '$');
    
    if (result[0] == '+'){
      serialReceived = true;
      loopSavedPositions();
    } else if (result[0] == '-'){
      serialReceived = true;
      nOfSaved--;
      EEPROM.write(0, nOfSaved);
    } else if (result[0] == '*') {
      serialReceived = true;
      loadFromEEPROM();
      loopSavedPositions();
    } else {
      if (!getValue(result, tmpArray)){
        serialReceived = true;
        moveSmoothManual(tmpArray);
        if (result[0] == '|'){
          for (int i = 0; i < 7; i++){
            savedPositions[nOfSaved][i] = tmpArray[i];
          }
          nOfSaved++;
          setToEEPROM(tmpArray);
          EEPROM.write(0, nOfSaved);
        }
      }
    }
  } else if (!serialReceived){
    if (millis() >= 60000){
      digitalWrite(13, HIGH);
      loadFromEEPROM();
      loopSavedPositions();
    }
  }
}



int getValue(String data, float *arrayResult) {
  int maxIndex = data.length()-1;
  int found = 0;
  String subStr = "";

  for(int i=0; i<=maxIndex; i++){
    if(data[i] == '|'){
        if (i != 0){
          arrayResult[found] = subStr.toInt();
          found++;
        }
        subStr = "";
    } else {
      subStr += data[i];
    }
  }


  if (found != 7){
    return 1;
  }

//  Serial.println(String(arrayResult[0])+" - "+String(arrayResult[1])+" - "+String(arrayResult[2])+" - "+String(arrayResult[3])+" - "+String(arrayResult[4])+" - "+String(arrayResult[5]));

  return 0;
}

void setServo (float *Array){
  servo1.write(Array[0]);
  servo2.write(Array[1]);
  servo3.write(Array[2]);
  servo4.write(Array[3]);
  servo5.write(Array[4]);
  servo6.write(Array[5]);

  for (int i = 0; i < 6; i++){
    currentJoint[i] = Array[i];
  }
}


void loadFromEEPROM () {
  nOfSaved = EEPROM.read(0);

  for (int addr = 0; addr < nOfSaved; addr++){
    for (int cell = 0; cell < 6; cell++){
      savedPositions[addr][cell] = EEPROM.read(addr*7+cell+1);
    }
    savedPositions[addr][6] = EEPROM.read(addr*7+6+1)*100;    // Sono salvate le centinaia di ms
  }
}


void setToEEPROM (float *Array){
  for (int i = 0; i < 6; i++){
    EEPROM.write((nOfSaved-1)*7+i+1, (char) Array[i]);
  }
  float f = Array[6]/100;
  EEPROM.write((nOfSaved-1)*7+6+1, (char) f);    // Sono salvate le centinaia di ms
}


void loopSavedPositions(){
  for (int saved = 0; saved < nOfSaved; saved++){

    moveSmooth(savedPositions[saved]);
    delay(100);
    
    if (saved == nOfSaved-1){     // Rendi infinito il for (se è l'ultimo ciclo torna a 0 (-1+1)) tranne nel caso nOfSaved==0
      saved = -1;
    }
  }
}


void moveSmooth (float *Array) {
  float stepPerFrame[6] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
  float nSteps = Array[6]*STEPS_PER_SECOND/1000.0;


  for (int i = 0; i < 6; i++){
    stepPerFrame[i] = (Array[i]-currentJoint[i])/nSteps;                  // Farà step intermedi prima della posizione finale
  }
  for (int frame = 0; frame < nSteps; frame++){
    for (int i = 0; i < 6; i++){
      tmpArray[i] = currentJoint[i]+stepPerFrame[i];
    }
    setServo(tmpArray);
    delay(1000/STEPS_PER_SECOND);
  }

  setServo(Array);
}

void moveSmoothManual (float *Array){
  float stepPerFrame = Array[6]/50.0;
  float localArray[6] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
  int arrived = 0;
  for (int i = 0; i < 6; i++){
    localArray[i] = Array[i];
  }
  while (arrived < 6){
    arrived = 0;
    for (int i = 0; i < 6; i++){
      if (abs(localArray[i]-currentJoint[i]) >= stepPerFrame){
        if (localArray[i]-currentJoint[i] > 0){
          tmpArray[i] = currentJoint[i] + stepPerFrame;
        } else {
          tmpArray[i] = currentJoint[i] - stepPerFrame;
        }
      } else {
        tmpArray[i] = localArray[i];
        arrived++;
      }
    }
    setServo(tmpArray);
    delay(10);
  }
  setServo(Array);
}
