#Copyright (c) Microsoft. All rights reserved.
#Licensed under the MIT license. See LICENSE file in the project root for full license information.

cmake_minimum_required(VERSION 2.8.11)

if (DEFINED AZURE_MQTT_BUILT)
    RETURN()
endif()

project(umqtt)

FILE(READ ${CMAKE_CURRENT_LIST_DIR}/version.txt UMQTT_VERSION)

set(GENERIC_LIB_VERSION ${UMQTT_VERSION})
string(SUBSTRING ${UMQTT_VERSION} 0 1 GENERIC_LIB_SOVERSION)

# Include the common build rules for the C SDK
include(deps/c-utility/configs/azure_iot_build_rules.cmake)

include(ExternalProject)

#the following variables are project-wide and can be used with cmake-gui
option(run_unittests "set run_unittests to ON to run unittests (default is OFF)" OFF)
option(run_e2e_tests "set run_e2e_tests to ON to run e2e tests (default is OFF)" OFF)
option(skip_samples "set skip_samples to ON to skip building samples (default is OFF)[if possible, they are always built]" OFF)
option(use_installed_dependencies "set use_installed_dependencies to ON to use installed packages instead of building dependencies from submodules" OFF)

if (${no_logging})
    add_definitions(-DNO_LOGGING)
endif ()

#do not add or build any tests of the dependencies
set(original_run_e2e_tests ${run_e2e_tests})
set(original_run_unittests ${run_unittests})

set(run_e2e_tests OFF)
set(run_unittests OFF)

include("dependencies.cmake")

if (${original_run_e2e_tests} OR ${original_run_unittests})
    set(SHARED_UTIL_REAL_TEST_FOLDER ${CMAKE_CURRENT_LIST_DIR}/deps/c-utility/tests/real_test_files CACHE INTERNAL "this is what needs to be included when doing test sources" FORCE)
    add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/deps/c-utility/testtools)
endif ()

set(use_cppunittest ON)
set_platform_files(${CMAKE_CURRENT_LIST_DIR}/deps/c-utility)

set(run_e2e_tests ${original_run_e2e_tests})
set(run_unittests ${original_run_unittests})

#these are the C source files
set(source_c_files
    ./src/mqtt_client.c
    ./src/mqtt_codec.c
    ./src/mqtt_message.c
)

#these are the C headers
set(source_h_files
    ./inc/azure_umqtt_c/mqtt_client.h
    ./inc/azure_umqtt_c/mqtt_codec.h
    ./inc/azure_umqtt_c/mqttconst.h
    ./inc/azure_umqtt_c/mqtt_message.h
)

#the following "set" statetement exports across the project a global variable called COMMON_INC_FOLDER that expands to whatever needs to included when using COMMON library
set(MQTT_INC_FOLDER ${CMAKE_CURRENT_LIST_DIR}/inc CACHE INTERNAL "this is what needs to be included if using sharedLib lib" FORCE)
set(MQTT_SRC_FOLDER ${CMAKE_CURRENT_LIST_DIR}/src CACHE INTERNAL "this is what needs to be included when doing include sources" FORCE)
include_directories(${MQTT_INC_FOLDER} ${SHARED_UTIL_INC_FOLDER})

get_directory_property(hasParent PARENT_DIRECTORY)
if (hasParent)
    set(AZURE_MQTT_BUILT "1C283849-1933-4197-B9AC" PARENT_SCOPE)
endif ()

if (${memory_trace})
    add_definitions(-DGB_MEASURE_MEMORY_FOR_THIS -DGB_DEBUG_ALLOC)
endif ()

#this is the product (a library)
add_library(umqtt ${source_c_files} ${source_h_files})
setTargetBuildProperties(umqtt)

set(SHARED_UTIL_ADAPTER_FOLDER "${CMAKE_CURRENT_LIST_DIR}/deps/c-utility/adapters")

set_platform_files(${CMAKE_CURRENT_LIST_DIR}/deps/c-utility)

target_link_libraries(umqtt aziotsharedutil)
if (NOT WIN32)
    set_target_properties(umqtt
        PROPERTIES
        VERSION ${GENERIC_LIB_VERSION}
        SOVERSION ${GENERIC_LIB_SOVERSION}
    )
endif ()

if (NOT ${ARCHITECTURE} STREQUAL "ARM")
    if (NOT ${skip_samples})
        add_subdirectory(samples)
    endif ()
endif ()

if (${run_unittests})
    include("dependencies-test.cmake")
    add_subdirectory(tests)
endif ()

# Set CMAKE_INSTALL_LIBDIR if not defined
include(GNUInstallDirs)

if (${use_installed_dependencies})
    # Install umqtt
    set(package_location "cmake")

    if(NOT DEFINED CMAKE_INSTALL_LIBDIR)
        set(CMAKE_INSTALL_LIBDIR "lib")
    endif()

    install(TARGETS umqtt EXPORT umqttTargets
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_LIBDIR}/../bin
        INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/azureiot
    )
    install(FILES ${source_h_files} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/azureiot/azure_umqtt_c)

    include(CMakePackageConfigHelpers)

    write_basic_package_version_file(
        "${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}/${PROJECT_NAME}ConfigVersion.cmake"
        VERSION ${UMQTT_VERSION}
        COMPATIBILITY SameMajorVersion
    )

    configure_file("configs/${PROJECT_NAME}Config.cmake"
        "${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}/${PROJECT_NAME}Config.cmake"
        COPYONLY
    )

    install(EXPORT umqttTargets
        FILE
            "${PROJECT_NAME}Targets.cmake"
        DESTINATION
            ${package_location}
    )

    install(
        FILES
            "configs/${PROJECT_NAME}Config.cmake"
            "${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}/${PROJECT_NAME}ConfigVersion.cmake"
        DESTINATION
            ${package_location}
    )
else ()
    set(install_staticlibs
        umqtt
    )
    install(FILES ${source_h_files}
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/azure_umqtt_c) 
    install(TARGETS ${install_staticlibs} 
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
endif ()
