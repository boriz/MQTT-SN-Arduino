#include <stdint.h>
#include <stdbool.h>
#include <strings.h>
#include "config.h"

#define API_DATA_PACKET  0x02
#define API_START_DELIMITER  0x7E
#define OPTION_CAST_MASK  0x40   //option unicast or broadcast MASK
#define OPTION_ACK_MASK  0x80   // option ACK or not MASK

uint8_t FrameID = 0;

// Create MeshBee frame (return frame lenght)
int MB_FrameCreate(uint8_t* data, int data_len, uint16_t dest_addr, uint8_t* frame, int frame_max_len, bool broadcast)
{
  // frame buffer is big enough?
  if ( frame_max_len < API_FRAME_LEN )
  {
    return -1;
  }
  
  // data is too long?
  // TODO: Split in multiple packets?
  if (data_len > API_DATA_LEN)
  {
    return -2;
  }
  
  // Frame buffer is fine. Clear it
  memset (frame, 0, frame_max_len); 
  
  // Header
  frame[0] = API_START_DELIMITER;  // Delimiter
  frame[1] = API_PAY_LEN;	   // Length of the payload
  frame[2] = API_DATA_PACKET;	   // API ID
  
  // Payload
  uint8_t cs = 0;  // CS=Sum of the payload
  cs += frame[3] = FrameID++;   // frame id  
  if (broadcast)
  {
    cs += frame[4] = OPTION_CAST_MASK; // option
  }
  cs += frame[5] = data_len; // data length
  
  // Data
  for (int i=0; i<data_len; i++)
  {
    cs += frame[6 + i] = data[i];    
  }
  cs += frame[6 + API_DATA_LEN] = (dest_addr >> 8) && 0xFF;  // Unicast address (16 bits)
  cs += frame[7 + API_DATA_LEN] = (dest_addr >> 0) && 0xFF;  // Unicast address (16 bits)
  frame[8 + API_DATA_LEN] = cs;
  
  return API_FRAME_LEN;
}


// Parse MeshBee frame (return data length)
int MB_FrameParse(uint8_t* frame, int frame_len, uint8_t* data, int data_max_len, uint16_t* src_addr)
{
  // got a full frame?
  if ( frame_len != API_FRAME_LEN )  
  {
    // TODO: May be a valid frame, keep reading?
    return -1;  
  }
  
  // Delimeter?
  if (frame[0] != API_START_DELIMITER)  // Delimiter
  {
    return -2;
  }
  
  // Payload length?
  if (frame[1] != API_PAY_LEN)  // Length of the payload
  {
    return -3;
  }
  
  // Right API ID?
  if (frame[2] != API_DATA_PACKET)  // API ID
  {
    return -4;
  }  
  
  // Payload
  int len;
  uint8_t cs = 0;  // CS=Sum of the payload
  cs += frame[3];   // frame id
  cs += frame[4];  // option
  
  // Enough space in the payload buffer?
  cs += len = frame[5];
  if (len > data_max_len)
  {
    return -5;
  }
  
  // Clear output buffer
  memset (data, 0, data_max_len);
  
  // Copy data to the buffer
  for (int i=0; i<API_DATA_LEN; i++)
  {
    if (i<len)
    {
      cs += data[i] = frame[6 + i];    
    }
    else
    {
      // Rest of the payload data (for checksum) 
      cs += frame[6 + i];
    }
  }
  *src_addr = (frame[6 + API_DATA_LEN] << 8) | frame[7 + API_DATA_LEN];  // Unicast address (16 bits)
  cs += frame[6 + API_DATA_LEN]; 
  cs += frame[7 + API_DATA_LEN];
  
  // Verify checksum
  if (cs != frame[8 + API_DATA_LEN])
  {
    return -6;
  }
  
  return len;
}

