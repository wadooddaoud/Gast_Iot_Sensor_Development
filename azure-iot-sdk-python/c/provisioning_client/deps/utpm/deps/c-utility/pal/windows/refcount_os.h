// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

// This file gets included into refcount.h as a means of extending the behavior of
// atomic increment, decrement, and test.

// The first phase defines COUNT_TYPE
#ifndef REFCOUNT_OS_H__WINDOWS
#define REFCOUNT_OS_H__WINDOWS

#include "windows.h"
// The Windows atomic operations work on LONG
#define COUNT_TYPE LONG

/*if macro DEC_REF returns DEC_RETURN_ZERO that means the ref count has reached zero.*/
#define DEC_RETURN_ZERO (0)
#define INC_REF(type, var) InterlockedIncrement(&(((REFCOUNT_TYPE(type)*)var)->count))
#define DEC_REF(type, var) InterlockedDecrement(&(((REFCOUNT_TYPE(type)*)var)->count))

#endif // REFCOUNT_OS_H__WINDOWS
