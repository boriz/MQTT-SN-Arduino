/*
mqttsn.h

The MIT License (MIT)

Copyright (C) 2014 John Donovan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

#ifndef __MQTTSN_H__
#define __MQTTSN_H__

//#define USE_RF12 1
#define USE_SERIAL 1

#define PROTOCOL_ID 0x01

#define FLAG_DUP 0x80
#define FLAG_QOS_0 0x00
#define FLAG_QOS_1 0x20
#define FLAG_QOS_2 0x40
#define FLAG_QOS_M1 0x60
#define FLAG_RETAIN 0x10
#define FLAG_WILL 0x08
#define FLAG_CLEAN 0x04
#define FLAG_TOPIC_NAME 0x00
#define FLAG_TOPIC_PREDEFINED_ID 0x01
#define FLAG_TOPIC_SHORT_NAME 0x02

#define QOS_MASK (FLAG_QOS_0 | FLAG_QOS_1 | FLAG_QOS_2 | FLAG_QOS_M1)
#define TOPIC_MASK (FLAG_TOPIC_NAME | FLAG_TOPIC_PREDEFINED_ID | FLAG_TOPIC_SHORT_NAME)

// Recommended values for timers and counters. All timers are in seconds.
#define T_ADV 960
#define N_ADV 3
#define T_SEARCH_GW 5
#define T_GW_INFO 5
#define T_WAIT 360
#define T_RETRY 15
#define N_RETRY 5

enum return_code_t {
    ACCEPTED,
    REJECTED_CONGESTION,
    REJECTED_INVALID_TOPIC_ID,
    REJECTED_NOT_SUPPORTED
};

enum message_type {
    ADVERTISE,
    SEARCHGW,
    GWINFO,
    CONNECT = 0x04,
    CONNACK,
    WILLTOPICREQ,
    WILLTOPIC,
    WILLMSGREQ,
    WILLMSG,
    REGISTER,
    REGACK,
    PUBLISH,
    PUBACK,
    PUBCOMP,
    PUBREC,
    PUBREL,
    SUBSCRIBE = 0x12,
    SUBACK,
    UNSUBSCRIBE,
    UNSUBACK,
    PINGREQ,
    PINGRESP,
    DISCONNECT,
    WILLTOPICUPD = 0x1a,
    WILLTOPICRESP,
    WILLMSGUPD,
    WILLMSGRESP
};

struct message_header {
    uint8_t length;
    uint8_t type;
};

struct msg_advertise : public message_header {
    uint8_t gw_id;
    uint16_t duration;
};

struct msg_searchgw : public message_header {
    uint8_t radius;
};

struct msg_gwinfo : public message_header {
    uint8_t gw_id;
    char gw_add[0];
};

struct msg_connect : public message_header {
    uint8_t flags;
    uint8_t protocol_id;
    uint16_t duration;
    char client_id[0];
};

struct msg_connack : public message_header {
    return_code_t return_code;
};

struct msg_willtopic : public message_header {
    uint8_t flags;
    char will_topic[0];
};

struct msg_willmsg : public message_header {
    char willmsg[0];
};

struct msg_register : public message_header {
    uint16_t topic_id;
    uint16_t message_id;
    char topic_name[0];
};

struct msg_regack : public message_header {
    uint16_t topic_id;
    uint16_t message_id;
    uint8_t return_code;
};

struct msg_publish : public message_header {
    uint8_t flags;
    uint16_t topic_id;
    uint16_t message_id;
    char data[0];
};

struct msg_puback : public message_header {
    uint16_t topic_id;
    uint16_t message_id;
    uint8_t return_code;
};

struct msg_pubqos2 : public message_header {
    uint16_t message_id;
};

struct msg_subscribe : public message_header {
    uint8_t flags;
    uint16_t message_id;
    union {
        char topic_name[0];
        uint16_t topic_id;
    };
};

struct msg_suback : public message_header {
    uint8_t flags;
    uint16_t topic_id;
    uint16_t message_id;
    uint8_t return_code;
};

struct msg_unsubscribe : public message_header {
    uint8_t flags;
    uint16_t message_id;
    union {
        char topic_name[0];
        uint16_t topic_id;
    };
};

struct msg_unsuback : public message_header {
    uint16_t message_id;
};

struct msg_pingreq : public message_header {
    char client_id[0];
};

struct msg_disconnect : public message_header {
    uint16_t duration;
};

struct msg_willtopicresp : public message_header {
    uint8_t return_code;
};

struct msg_willmsgresp : public message_header {
    uint8_t return_code;
};

#endif
