//**********************************************************************`
//* This is an include file generated by Message Compiler.             *`
//*                                                                    *`
//* Copyright (c) Microsoft Corporation. All Rights Reserved.          *`
//**********************************************************************`
#pragma once
#include <wmistr.h>
#include <evntrace.h>
#include "evntprov.h"
//
//  Initial Defs
//
#if !defined(ETW_INLINE)
#define ETW_INLINE DECLSPEC_NOINLINE __inline
#endif

#if defined(__cplusplus)
extern "C" {
#endif

//
// Allow disabling of code generation
//
#ifndef MCGEN_DISABLE_PROVIDER_CODE_GENERATION
#if  !defined(McGenDebug)
#define McGenDebug(a,b)
#endif 


#if !defined(MCGEN_TRACE_CONTEXT_DEF)
#define MCGEN_TRACE_CONTEXT_DEF
typedef struct _MCGEN_TRACE_CONTEXT
{
    TRACEHANDLE            RegistrationHandle;
    TRACEHANDLE            Logger;
    ULONGLONG              MatchAnyKeyword;
    ULONGLONG              MatchAllKeyword;
    ULONG                  Flags;
    ULONG                  IsEnabled;
    UCHAR                  Level; 
    UCHAR                  Reserve;
    USHORT                 EnableBitsCount;
    PULONG                 EnableBitMask;
    const ULONGLONG*       EnableKeyWords;
    const UCHAR*           EnableLevel;
} MCGEN_TRACE_CONTEXT, *PMCGEN_TRACE_CONTEXT;
#endif

#if !defined(MCGEN_LEVEL_KEYWORD_ENABLED_DEF)
#define MCGEN_LEVEL_KEYWORD_ENABLED_DEF
FORCEINLINE
BOOLEAN
McGenLevelKeywordEnabled(
    _In_ PMCGEN_TRACE_CONTEXT EnableInfo,
    _In_ UCHAR Level,
    _In_ ULONGLONG Keyword
    )
{
    //
    // Check if the event Level is lower than the level at which
    // the channel is enabled.
    // If the event Level is 0 or the channel is enabled at level 0,
    // all levels are enabled.
    //

    if ((Level <= EnableInfo->Level) || // This also covers the case of Level == 0.
        (EnableInfo->Level == 0)) {

        //
        // Check if Keyword is enabled
        //

        if ((Keyword == (ULONGLONG)0) ||
            ((Keyword & EnableInfo->MatchAnyKeyword) &&
             ((Keyword & EnableInfo->MatchAllKeyword) == EnableInfo->MatchAllKeyword))) {
            return TRUE;
        }
    }

    return FALSE;

}
#endif

#if !defined(MCGEN_EVENT_ENABLED_DEF)
#define MCGEN_EVENT_ENABLED_DEF
FORCEINLINE
BOOLEAN
McGenEventEnabled(
    _In_ PMCGEN_TRACE_CONTEXT EnableInfo,
    _In_ PCEVENT_DESCRIPTOR EventDescriptor
    )
{

    return McGenLevelKeywordEnabled(EnableInfo, EventDescriptor->Level, EventDescriptor->Keyword);

}
#endif


//
// EnableCheckMacro
//
#ifndef MCGEN_ENABLE_CHECK
#define MCGEN_ENABLE_CHECK(Context, Descriptor) (Context.IsEnabled &&  McGenEventEnabled(&Context, &Descriptor))
#endif

#if !defined(MCGEN_CONTROL_CALLBACK)
#define MCGEN_CONTROL_CALLBACK

DECLSPEC_NOINLINE __inline
VOID
__stdcall
McGenControlCallbackV2(
    _In_ LPCGUID SourceId,
    _In_ ULONG ControlCode,
    _In_ UCHAR Level,
    _In_ ULONGLONG MatchAnyKeyword,
    _In_ ULONGLONG MatchAllKeyword,
    _In_opt_ PEVENT_FILTER_DESCRIPTOR FilterData,
    _Inout_opt_ PVOID CallbackContext
    )
/*++

Routine Description:

    This is the notification callback for Windows Vista and later.

Arguments:

    SourceId - The GUID that identifies the session that enabled the provider. 

    ControlCode - The parameter indicates whether the provider 
                  is being enabled or disabled.

    Level - The level at which the event is enabled.

    MatchAnyKeyword - The bitmask of keywords that the provider uses to 
                      determine the category of events that it writes.

    MatchAllKeyword - This bitmask additionally restricts the category 
                      of events that the provider writes. 

    FilterData - The provider-defined data.

    CallbackContext - The context of the callback that is defined when the provider 
                      called EtwRegister to register itself.

Remarks:

    ETW calls this function to notify provider of enable/disable

--*/
{
    PMCGEN_TRACE_CONTEXT Ctx = (PMCGEN_TRACE_CONTEXT)CallbackContext;
    ULONG Ix;
#ifndef MCGEN_PRIVATE_ENABLE_CALLBACK_V2
    UNREFERENCED_PARAMETER(SourceId);
    UNREFERENCED_PARAMETER(FilterData);
#endif

    if (Ctx == NULL) {
        return;
    }

    switch (ControlCode) {

        case EVENT_CONTROL_CODE_ENABLE_PROVIDER:
            Ctx->Level = Level;
            Ctx->MatchAnyKeyword = MatchAnyKeyword;
            Ctx->MatchAllKeyword = MatchAllKeyword;
            Ctx->IsEnabled = EVENT_CONTROL_CODE_ENABLE_PROVIDER;

            for (Ix = 0; Ix < Ctx->EnableBitsCount; Ix += 1) {
                if (McGenLevelKeywordEnabled(Ctx, Ctx->EnableLevel[Ix], Ctx->EnableKeyWords[Ix]) != FALSE) {
                    Ctx->EnableBitMask[Ix >> 5] |= (1 << (Ix % 32));
                } else {
                    Ctx->EnableBitMask[Ix >> 5] &= ~(1 << (Ix % 32));
                }
            }
            break;

        case EVENT_CONTROL_CODE_DISABLE_PROVIDER:
            Ctx->IsEnabled = EVENT_CONTROL_CODE_DISABLE_PROVIDER;
            Ctx->Level = 0;
            Ctx->MatchAnyKeyword = 0;
            Ctx->MatchAllKeyword = 0;
            if (Ctx->EnableBitsCount > 0) {
                RtlZeroMemory(Ctx->EnableBitMask, (((Ctx->EnableBitsCount - 1) / 32) + 1) * sizeof(ULONG));
            }
            break;
 
        default:
            break;
    }

#ifdef MCGEN_PRIVATE_ENABLE_CALLBACK_V2
    //
    // Call user defined callback
    //
    MCGEN_PRIVATE_ENABLE_CALLBACK_V2(
        SourceId,
        ControlCode,
        Level,
        MatchAnyKeyword,
        MatchAllKeyword,
        FilterData,
        CallbackContext
        );
#endif
   
    return;
}

#endif
#endif // MCGEN_DISABLE_PROVIDER_CODE_GENERATION
//+
// Provider Microsoft-ServiceBus Event Count 4
//+
EXTERN_C __declspec(selectany) const GUID MicrosoftServiceBus = {0x4ccaa233, 0x6675, 0x4ec5, {0xb3, 0xa6, 0x1a, 0xa6, 0x8b, 0x7c, 0x8a, 0xe9}};

//
// Channel
//
#define Debug 0x10
#define Operational 0x11

//
// Opcodes
//
#define _loginfo 0xa
#define _logerror 0xb
#define _logdebug 0xc
#define _loglasterror 0xd

//
// Tasks
//
#define Log 0x1
EXTERN_C __declspec(selectany) const GUID LogId = {0xf66f77b5, 0x170a, 0x41a5, {0x97, 0x04, 0xc0, 0xca, 0xea, 0xa3, 0x8f, 0x54}};
//
// Keyword
//
#define _kw_loginfo 0x1
#define _kw_logerror 0x2
#define _kw_logdebug 0x4
#define _kw_loglasterror 0x8

//
// Event Descriptors
//
EXTERN_C __declspec(selectany) const EVENT_DESCRIPTOR LogInfoEvent = {0x1, 0x0, 0x11, 0x4, 0xa, 0x1, 0x4000000000000001};
#define LogInfoEvent_value 0x1
EXTERN_C __declspec(selectany) const EVENT_DESCRIPTOR LogErrorEvent = {0x2, 0x0, 0x11, 0x2, 0xb, 0x1, 0x4000000000000002};
#define LogErrorEvent_value 0x2
EXTERN_C __declspec(selectany) const EVENT_DESCRIPTOR LogDebugEvent = {0x3, 0x0, 0x10, 0x4, 0xc, 0x1, 0x8000000000000004};
#define LogDebugEvent_value 0x3
EXTERN_C __declspec(selectany) const EVENT_DESCRIPTOR LogLastError = {0x4, 0x0, 0x11, 0x2, 0xd, 0x1, 0x4000000000000008};
#define LogLastError_value 0x4

//
// Note on Generate Code from Manifest for Windows Vista and above
//
//Structures :  are handled as a size and pointer pairs. The macro for the event will have an extra 
//parameter for the size in bytes of the structure. Make sure that your structures have no extra padding.
//
//Strings: There are several cases that can be described in the manifest. For array of variable length 
//strings, the generated code will take the count of characters for the whole array as an input parameter. 
//
//SID No support for array of SIDs, the macro will take a pointer to the SID and use appropriate 
//GetLengthSid function to get the length.
//

//
// Allow disabling of code generation
//
#ifndef MCGEN_DISABLE_PROVIDER_CODE_GENERATION

//
// Globals 
//


//
// Event Enablement Bits
//

EXTERN_C __declspec(selectany) DECLSPEC_CACHEALIGN ULONG Microsoft_ServiceBusEnableBits[1];
EXTERN_C __declspec(selectany) const ULONGLONG Microsoft_ServiceBusKeywords[4] = {0x4000000000000001, 0x4000000000000002, 0x8000000000000004, 0x4000000000000008};
EXTERN_C __declspec(selectany) const UCHAR Microsoft_ServiceBusLevels[4] = {4, 2, 4, 2};
EXTERN_C __declspec(selectany) MCGEN_TRACE_CONTEXT MicrosoftServiceBus_Context = {0, 0, 0, 0, 0, 0, 0, 0, 4, Microsoft_ServiceBusEnableBits, Microsoft_ServiceBusKeywords, Microsoft_ServiceBusLevels};

EXTERN_C __declspec(selectany) REGHANDLE Microsoft_ServiceBusHandle = (REGHANDLE)0;

#if !defined(McGenEventRegisterUnregister)
#define McGenEventRegisterUnregister
#pragma warning(push)
#pragma warning(disable:6103)
DECLSPEC_NOINLINE __inline
ULONG __stdcall
McGenEventRegister(
    _In_ LPCGUID ProviderId,
    _In_opt_ PENABLECALLBACK EnableCallback,
    _In_opt_ PVOID CallbackContext,
    _Inout_ PREGHANDLE RegHandle
    )
/*++

Routine Description:

    This function registers the provider with ETW USER mode.

Arguments:
    ProviderId - Provider ID to be register with ETW.

    EnableCallback - Callback to be used.

    CallbackContext - Context for this provider.

    RegHandle - Pointer to registration handle.

Remarks:

    If the handle != NULL will return ERROR_SUCCESS

--*/
{
    ULONG Error;


    if (*RegHandle) {
        //
        // already registered
        //
        return ERROR_SUCCESS;
    }

    Error = EventRegister( ProviderId, EnableCallback, CallbackContext, RegHandle); 

    return Error;
}
#pragma warning(pop)


DECLSPEC_NOINLINE __inline
ULONG __stdcall
McGenEventUnregister(_Inout_ PREGHANDLE RegHandle)
/*++

Routine Description:

    Unregister from ETW USER mode

Arguments:
            RegHandle this is the pointer to the provider context
Remarks:
            If provider has not been registered, RegHandle == NULL,
            return ERROR_SUCCESS
--*/
{
    ULONG Error;


    if(!(*RegHandle)) {
        //
        // Provider has not registerd
        //
        return ERROR_SUCCESS;
    }

    Error = EventUnregister(*RegHandle); 
    *RegHandle = (REGHANDLE)0;
    
    return Error;
}
#endif
//
// Register with ETW Vista +
//
#ifndef EventRegisterMicrosoft_ServiceBus
#define EventRegisterMicrosoft_ServiceBus() McGenEventRegister(&MicrosoftServiceBus, McGenControlCallbackV2, &MicrosoftServiceBus_Context, &Microsoft_ServiceBusHandle) 
#endif

//
// UnRegister with ETW
//
#ifndef EventUnregisterMicrosoft_ServiceBus
#define EventUnregisterMicrosoft_ServiceBus() McGenEventUnregister(&Microsoft_ServiceBusHandle) 
#endif

//
// Enablement check macro for LogInfoEvent
//

#define EventEnabledLogInfoEvent() ((Microsoft_ServiceBusEnableBits[0] & 0x00000001) != 0)

//
// Event Macro for LogInfoEvent
//
#define EventWriteLogInfoEvent(content)\
        EventEnabledLogInfoEvent() ?\
        Template_s(Microsoft_ServiceBusHandle, &LogInfoEvent, content)\
        : ERROR_SUCCESS\

//
// Enablement check macro for LogErrorEvent
//

#define EventEnabledLogErrorEvent() ((Microsoft_ServiceBusEnableBits[0] & 0x00000002) != 0)

//
// Event Macro for LogErrorEvent
//
#define EventWriteLogErrorEvent(content, file, time, function, line)\
        EventEnabledLogErrorEvent() ?\
        Template_ssysq(Microsoft_ServiceBusHandle, &LogErrorEvent, content, file, time, function, line)\
        : ERROR_SUCCESS\

//
// Enablement check macro for LogDebugEvent
//

#define EventEnabledLogDebugEvent() ((Microsoft_ServiceBusEnableBits[0] & 0x00000004) != 0)

//
// Event Macro for LogDebugEvent
//
#define EventWriteLogDebugEvent(content, file, time, function, line)\
        EventEnabledLogDebugEvent() ?\
        Template_ssysq(Microsoft_ServiceBusHandle, &LogDebugEvent, content, file, time, function, line)\
        : ERROR_SUCCESS\

//
// Enablement check macro for LogLastError
//

#define EventEnabledLogLastError() ((Microsoft_ServiceBusEnableBits[0] & 0x00000008) != 0)

//
// Event Macro for LogLastError
//
#define EventWriteLogLastError(content, file, time, function, line, getLastError)\
        EventEnabledLogLastError() ?\
        Template_ssysqs(Microsoft_ServiceBusHandle, &LogLastError, content, file, time, function, line, getLastError)\
        : ERROR_SUCCESS\

#endif // MCGEN_DISABLE_PROVIDER_CODE_GENERATION


//
// Allow Diasabling of code generation
//
#ifndef MCGEN_DISABLE_PROVIDER_CODE_GENERATION

//
// Template Functions 
//
//
//Template from manifest : _template_log_info
//
#ifndef Template_s_def
#define Template_s_def
ETW_INLINE
ULONG
Template_s(
    _In_ REGHANDLE RegHandle,
    _In_ PCEVENT_DESCRIPTOR Descriptor,
    _In_opt_ LPCSTR  _Arg0
    )
{
#define ARGUMENT_COUNT_s 1

    EVENT_DATA_DESCRIPTOR EventData[ARGUMENT_COUNT_s];

    EventDataDescCreate(&EventData[0], 
                        (_Arg0 != NULL) ? _Arg0 : "NULL",
                        (_Arg0 != NULL) ? (ULONG)((strlen(_Arg0) + 1) * sizeof(CHAR)) : (ULONG)sizeof("NULL"));

    return EventWrite(RegHandle, Descriptor, ARGUMENT_COUNT_s, EventData);
}
#endif

//
//Template from manifest : _template_log_error
//
#ifndef Template_ssysq_def
#define Template_ssysq_def
ETW_INLINE
ULONG
Template_ssysq(
    _In_ REGHANDLE RegHandle,
    _In_ PCEVENT_DESCRIPTOR Descriptor,
    _In_opt_ LPCSTR  _Arg0,
    _In_opt_ LPCSTR  _Arg1,
    _In_ const SYSTEMTIME*  _Arg2,
    _In_opt_ LPCSTR  _Arg3,
    _In_ const unsigned int  _Arg4
    )
{
#define ARGUMENT_COUNT_ssysq 5

    EVENT_DATA_DESCRIPTOR EventData[ARGUMENT_COUNT_ssysq];

    EventDataDescCreate(&EventData[0], 
                        (_Arg0 != NULL) ? _Arg0 : "NULL",
                        (_Arg0 != NULL) ? (ULONG)((strlen(_Arg0) + 1) * sizeof(CHAR)) : (ULONG)sizeof("NULL"));

    EventDataDescCreate(&EventData[1], 
                        (_Arg1 != NULL) ? _Arg1 : "NULL",
                        (_Arg1 != NULL) ? (ULONG)((strlen(_Arg1) + 1) * sizeof(CHAR)) : (ULONG)sizeof("NULL"));

    EventDataDescCreate(&EventData[2], _Arg2, sizeof(SYSTEMTIME)  );

    EventDataDescCreate(&EventData[3], 
                        (_Arg3 != NULL) ? _Arg3 : "NULL",
                        (_Arg3 != NULL) ? (ULONG)((strlen(_Arg3) + 1) * sizeof(CHAR)) : (ULONG)sizeof("NULL"));

    EventDataDescCreate(&EventData[4], &_Arg4, sizeof(const unsigned int)  );

    return EventWrite(RegHandle, Descriptor, ARGUMENT_COUNT_ssysq, EventData);
}
#endif

//
//Template from manifest : _template_log_last_error
//
#ifndef Template_ssysqs_def
#define Template_ssysqs_def
ETW_INLINE
ULONG
Template_ssysqs(
    _In_ REGHANDLE RegHandle,
    _In_ PCEVENT_DESCRIPTOR Descriptor,
    _In_opt_ LPCSTR  _Arg0,
    _In_opt_ LPCSTR  _Arg1,
    _In_ const SYSTEMTIME*  _Arg2,
    _In_opt_ LPCSTR  _Arg3,
    _In_ const unsigned int  _Arg4,
    _In_opt_ LPCSTR  _Arg5
    )
{
#define ARGUMENT_COUNT_ssysqs 6

    EVENT_DATA_DESCRIPTOR EventData[ARGUMENT_COUNT_ssysqs];

    EventDataDescCreate(&EventData[0], 
                        (_Arg0 != NULL) ? _Arg0 : "NULL",
                        (_Arg0 != NULL) ? (ULONG)((strlen(_Arg0) + 1) * sizeof(CHAR)) : (ULONG)sizeof("NULL"));

    EventDataDescCreate(&EventData[1], 
                        (_Arg1 != NULL) ? _Arg1 : "NULL",
                        (_Arg1 != NULL) ? (ULONG)((strlen(_Arg1) + 1) * sizeof(CHAR)) : (ULONG)sizeof("NULL"));

    EventDataDescCreate(&EventData[2], _Arg2, sizeof(SYSTEMTIME)  );

    EventDataDescCreate(&EventData[3], 
                        (_Arg3 != NULL) ? _Arg3 : "NULL",
                        (_Arg3 != NULL) ? (ULONG)((strlen(_Arg3) + 1) * sizeof(CHAR)) : (ULONG)sizeof("NULL"));

    EventDataDescCreate(&EventData[4], &_Arg4, sizeof(const unsigned int)  );

    EventDataDescCreate(&EventData[5], 
                        (_Arg5 != NULL) ? _Arg5 : "NULL",
                        (_Arg5 != NULL) ? (ULONG)((strlen(_Arg5) + 1) * sizeof(CHAR)) : (ULONG)sizeof("NULL"));

    return EventWrite(RegHandle, Descriptor, ARGUMENT_COUNT_ssysqs, EventData);
}
#endif

#endif // MCGEN_DISABLE_PROVIDER_CODE_GENERATION

#if defined(__cplusplus)
};
#endif

#define MSG_Microsoft_ServiceBus_MessagingStore_BlockStorage_keyword__loginfo_message 0x10000001L
#define MSG_Microsoft_ServiceBus_MessagingStore_BlockStorage_Keyword__logerror_message 0x10000002L
#define MSG_Microsoft_ServiceBus_MessagingStore_BlockStorage_Keyword__logdebug_message 0x10000003L
#define MSG_Microsoft_ServiceBus_Keyword__kw_loglasterror_message 0x10000004L
#define MSG_Microsoft_ServiceBus_MessagingStore_BlockStorage_opcode__loginfo_message 0x3000000AL
#define MSG_Microsoft_ServiceBus_MessagingStore_BlockStorage_opcode__logerror_message 0x3000000BL
#define MSG_Microsoft_ServiceBus_MessagingStore_BlockStorage_opcode__logdebug_message 0x3000000CL
#define MSG_level_Error                      0x50000002L
#define MSG_level_Informational              0x50000004L
#define MSG_Microsoft_ServiceBus_MessagingStore_BlockStorage_task_Log_message 0x70000001L
#define MSG_Microsoft_ServiceBus_MessagingStore_BlockStorage_channel_Debug_message 0x90000001L
#define MSG_Microsoft_ServiceBus_MessagingStore_BlockStorage_channel_Operational_message 0x90000002L
#define MSG_Microsoft_ServiceBus_MessagingStore_BlockStorage_event_1_message 0xB0000001L
#define MSG_Microsoft_ServiceBus_MessagingStore_BlockStorage_event_2_message 0xB0000002L
#define MSG_Microsoft_ServiceBus_MessagingStore_BlockStorage_event_3_message 0xB0000003L
#define MSG_Microsoft_ServiceBus_event_4_message 0xB0000004L
