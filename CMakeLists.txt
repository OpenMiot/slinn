cmake_minimum_required(VERSION 3.15)
project(slinn_cxx LANGUAGES CXX)

# Найти Python и pybind11
set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)


# Создать модуль расширения из всех .cpp файлов в папке src
pybind11_add_module(
    slinn_cxx
    slinn_cxx/slinn_cxx.cpp
    slinn_cxx/utils.cpp
    slinn_cxx/net/http/http_headers.cpp
)

# Указать стандарт C++ (pybind11 требует как минимум C++11)\
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
target_compile_features(slinn_cxx PRIVATE cxx_std_23)
if (MINGW)
    target_link_options(slinn_cxx PRIVATE -static-libgcc -static-libstdc++ -static)
endif()
set_target_properties(slinn_cxx PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/slinn"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/slinn"
)

# Установить модуль в Python site-packages
#install(TARGETS slinn_cxx DESTINATION ${Python_SITELIB})
install(TARGETS slinn_cxx DESTINATION ".")

install(DIRECTORY dexir/ DESTINATION dexir
        PATTERN "*.pyc" EXCLUDE
        PATTERN "*.pyo" EXCLUDE)
install(DIRECTORY slinn/ DESTINATION slinn
        PATTERN "*.pyc" EXCLUDE
        PATTERN "*.pyo" EXCLUDE)