

// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

#ifndef AMQP_DEFINITIONS_MESSAGE_ID_UUID_H
#define AMQP_DEFINITIONS_MESSAGE_ID_UUID_H


#ifdef __cplusplus
#include <cstdint>
extern "C" {
#else
#include <stdint.h>
#include <stdbool.h>
#endif

#include "azure_uamqp_c/amqpvalue.h"
#include "azure_c_shared_utility/umock_c_prod.h"


    typedef uuid message_id_uuid;

    MOCKABLE_FUNCTION(, AMQP_VALUE, amqpvalue_create_message_id_uuid, message_id_uuid, value);


    #define amqpvalue_get_message_id_uuid amqpvalue_get_uuid



#ifdef __cplusplus
}
#endif

#endif /* AMQP_DEFINITIONS_MESSAGE_ID_UUID_H */
