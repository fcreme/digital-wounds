cmake_minimum_required(VERSION 3.20)
project(digital_wounds VERSION 0.1.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# --- Find packages ---
find_package(SDL2 REQUIRED)
find_package(OpenGL REQUIRED)
find_package(assimp REQUIRED)

# --- Collect C++ sources ---
file(GLOB_RECURSE SOURCES src/*.cpp)

# --- GLAD (OpenGL loader) ---
set(GLAD_SRC ${CMAKE_SOURCE_DIR}/lib/glad/src/gl.c)

# --- Executable ---
add_executable(${PROJECT_NAME} ${SOURCES} ${GLAD_SRC})

# --- Include directories ---
target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_SOURCE_DIR}/src
    ${CMAKE_SOURCE_DIR}/lib
    ${CMAKE_SOURCE_DIR}/lib/glad/include
    ${SDL2_INCLUDE_DIRS}
)

# --- Link libraries ---
target_link_libraries(${PROJECT_NAME} PRIVATE
    ${SDL2_LIBRARIES}
    OpenGL::GL
    assimp::assimp
)

# --- Copy runtime DLLs to build directory (MSYS2 MinGW on Windows only) ---
if(WIN32)
    foreach(DLL_NAME SDL2.dll libassimp-6.dll libgcc_s_seh-1.dll libstdc++-6.dll libwinpthread-1.dll zlib1.dll libminizip-1.dll libbz2-1.dll)
        add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "C:/msys64/mingw64/bin/${DLL_NAME}"
                $<TARGET_FILE_DIR:${PROJECT_NAME}>
            COMMENT "Copying ${DLL_NAME} to build directory"
        )
    endforeach()
endif()

# --- Copy assets and props to build directory on every build ---
# A custom target (not POST_BUILD) so data-only edits reach the build
# even when the executable does not relink.
add_custom_target(copy_assets ALL
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${CMAKE_SOURCE_DIR}/assets
        $<TARGET_FILE_DIR:${PROJECT_NAME}>/assets
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${CMAKE_SOURCE_DIR}/props
        $<TARGET_FILE_DIR:${PROJECT_NAME}>/props
    COMMENT "Copying assets and props to build directory"
)
add_dependencies(${PROJECT_NAME} copy_assets)

# --- Scripted test driver (off in normal builds) ---
option(DW_TEST_DRIVER "Build the scripted test driver (--script)" OFF)
if(DW_TEST_DRIVER)
    target_compile_definitions(${PROJECT_NAME} PRIVATE DW_TEST_DRIVER)
endif()

# --- Unit tests (OpenGL-free sources only) ---
enable_testing()
add_executable(dw_tests
    tests/test_main.cpp
)
target_include_directories(dw_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/src
    ${CMAKE_SOURCE_DIR}/lib
    ${CMAKE_SOURCE_DIR}/tests
)
add_test(NAME dw_tests COMMAND dw_tests)

# --- Compiler warnings ---
if(MSVC)
    target_compile_options(${PROJECT_NAME} PRIVATE /W4)
else()
    target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra -Wpedantic)
endif()
if(NOT MSVC)
    target_compile_options(dw_tests PRIVATE -Wall -Wextra -Wpedantic)
endif()
