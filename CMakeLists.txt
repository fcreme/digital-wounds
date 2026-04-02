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

# --- Copy runtime DLLs to build directory ---
foreach(DLL_NAME SDL2.dll libassimp-6.dll)
    add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "C:/msys64/mingw64/bin/${DLL_NAME}"
            $<TARGET_FILE_DIR:${PROJECT_NAME}>
        COMMENT "Copying ${DLL_NAME} to build directory"
    )
endforeach()

# --- Copy assets to build directory ---
add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${CMAKE_SOURCE_DIR}/assets
        $<TARGET_FILE_DIR:${PROJECT_NAME}>/assets
    COMMENT "Copying assets to build directory"
)

# --- Compiler warnings ---
if(MSVC)
    target_compile_options(${PROJECT_NAME} PRIVATE /W4)
else()
    target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra -Wpedantic)
endif()
