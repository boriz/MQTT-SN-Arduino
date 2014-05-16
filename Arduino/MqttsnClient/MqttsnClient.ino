#include <stdint.h>
#include <stdbool.h>
#include <strings.h>
#include <mqttsn-messages.h>
#include <SoftwareSerial.h>
#include "config.h"

#define TOPIC_PUB "arduino/temp"
#define TOPIC_SUB "arduino/temp"

MQTTSN mqttsn;
uint16_t u16TopicPubID;
uint16_t u16TopicSubID;
uint8_t u8Counter;
SoftwareSerial DbgSer(10, 11); // RX, TX

uint8_t FrameBufferIn[API_FRAME_LEN];
uint8_t FrameBufferOut[API_FRAME_LEN];

void setup()
{
  DbgSer.begin(9600);
  Serial.begin(115200);
  
  ADMUX = 0xC8; // turn on internal reference, right-shift ADC buffer, ADC channel = internal temp sensor
  delay(100);  // wait a sec for the analog reference to stabilize
  
  u8Counter = 1;
  DbgSer.println("Setup done");   
}

 
void loop()
{ 
  // Check serila data
  CheckSerial();
  
  // ------- MQTT-SN publis logic -------
  // Busy?
  if (mqttsn.wait_for_response())
  {
    // Busy. exit
    return;
  }
  
  // Connected?
  if (!mqttsn.connected())
  {
    // Not connected - connect
    mqttsn.connect(0, 10, "test1758");  // Flags=0, Duration=10
    DbgSer.println("Connect sent");   
    return;
  }
  
  // Topic registered?
  uint8_t index;
  u16TopicPubID = mqttsn.find_topic_id(TOPIC_PUB, &index);
  if (u16TopicPubID == 0xffff)
  {
    // Topic is not registered yet
    mqttsn.register_topic(TOPIC_PUB);
    DbgSer.println("Reg top sent");    
    return;  
  }
   
  // Topic is alredy registered, publish
  char str[50];
  char temp[10];
  float t = averageTemperature();
  itoa(t, temp, 10);
  sprintf(str, "%s (%i)", temp, u8Counter);
  DbgSer.print("Top id:");      
  DbgSer.print(u16TopicPubID);    
  DbgSer.print("; Val:");      
  DbgSer.println(str);      
  mqttsn.publish(0, u16TopicPubID, str, strlen(str));  // Flags=0         
  u8Counter++;
  delay(2000);
  
  // ------- MQTT-SN subscribe logic -------
  u16TopicSubID = mqttsn.find_topic_id(TOPIC_SUB, &index);
  if (u16TopicSubID == 0xffff)
  {
    // Topic is not registered yet
    mqttsn.subscribe_by_name(0, TOPIC_SUB);  // Flags=0   
    DbgSer.println("Sub top sent");    
    return;  
  }
  delay(2000);  
}


// gwinfo message callback
void MQTTSN_gwinfo_handler(const msg_gwinfo* msg)
{
  // Got a gateway response
  // The frame is still in the buffer - parse it
  
  DbgSer.println("GW info hand"); 
}


void MQTTSN_publish_handler(const msg_publish* msg)
{
  DbgSer.println("Sub pub hand"); 
}


// Callback funciton to send serial data
void MQTTSN_serial_send(uint8_t* message_buffer, int length)
{
  // Assuming that our gateway is at address 0 (coordinator)
  int len = MB_FrameCreate (message_buffer, length, 0x0000, FrameBufferOut, sizeof(FrameBufferOut), false);
  if (len > 0)
  {
    Serial.write(FrameBufferOut, len);
    Serial.flush();
  }
}


// Serial event interrupt
void CheckSerial()
{
  if (Serial.available() > 0) 
  {
    // Wait till we got the whole packet or timeout
    long Start = millis();   
    int cnt =0;
    while (cnt < API_FRAME_LEN && (millis() - Start) < 100) 
    {
        while (Serial.available() > 0) 
        {
            FrameBufferIn[cnt++] = (uint8_t)Serial.read();
            
            // Reset timeout counter
            Start = millis();
        }
    }
    
    if (cnt == API_FRAME_LEN)
    {
      // Got the whole packet
      DbgSer.print("From ser:");  
      for (int i=0; i<cnt; i++)
      {        
        DbgSer.print (FrameBufferIn[i], HEX);
        DbgSer.print (" ");
      }
      DbgSer.println();   
  
      uint8_t pay[API_DATA_LEN];
      uint16_t src_addr;
      int pay_len = MB_FrameParse(FrameBufferIn, cnt, pay, sizeof(pay), &src_addr);
      if (pay_len > 0)
      {
        DbgSer.print("Ser payload:");  
        for (int i=0; i<pay_len; i++)
        {        
          DbgSer.print (pay[i], HEX);
          DbgSer.print (" ");
        }
        DbgSer.println(); 
        
        // Valid frame. Pare it
        mqttsn.parse_stream(pay, pay_len);
      }
    }
    else
    {
      // Timeout. 
      DbgSer.println("Chec ser timeout");  
    }
  }
}



// =================== Measure temperature =================== 
int readTemperature() 
{
  ADCSRA |= _BV(ADSC); // start the conversion
  while (bit_is_set(ADCSRA, ADSC)); // ADSC is cleared when the conversion finishes
  return (ADCL | (ADCH << 8)) - 342; // combine bytes & correct for temp offset (approximate)} 
}

float averageTemperature()
{
  readTemperature(); // discard first sample (never hurts to be safe)

  float averageTemp; // create a float to hold running average
  for (int i = 1; i < 1000; i++) // start at 1 so we dont divide by 0
    averageTemp += ((readTemperature() - averageTemp)/(float)i); // get next sample, calculate running average

  return averageTemp; // return average temperature reading
}
