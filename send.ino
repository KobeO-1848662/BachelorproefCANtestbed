#include <SPI.h>
#include "mcp2515_can.h"

const int SPI_CS_PIN = 9; // Set CS pin
mcp2515_can CAN(SPI_CS_PIN);

void setup() {
    Serial.begin(115200);
    while (!Serial);

    while (CAN_OK != CAN.begin(CAN_500KBPS)) {
        Serial.println("CAN init fail, retry...");
        delay(100);
    }
    Serial.println("CAN init ok!");
}

void loop() {
    if (Serial.available() > 0) {
        String receivedData = Serial.readStringUntil('\n');
        receivedData.trim(); 

        byte canData[8]; 
        int dataLength = parseReceivedData(receivedData, canData);

        if (dataLength > 0) {
            unsigned long canId = 0x123;

            CAN.sendMsgBuf(canId, 0, dataLength, canData);
            Serial.println("Data sent to CAN bus.");
        } else {
            Serial.println("Invalid data received from Python.");
        }
    }
}

int parseReceivedData(const String &dataStr, byte *dataBuffer) {
    if (dataStr.length() % 2 != 0 || dataStr.length() > 16) {
        return 0; 
    }

    int dataLength = dataStr.length() / 2;
    for (int i = 0; i < dataLength; i++) {
        String byteStr = dataStr.substring(i * 2, i * 2 + 2);
        dataBuffer[i] = (byte)strtol(byteStr.c_str(), NULL, 16);
    }

    return dataLength;
}

