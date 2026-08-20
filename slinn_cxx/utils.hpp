#pragma once
#include <pybind11/pybind11.h>


namespace py = pybind11;

// Экспортируемая функция representate
std::string representate(py::object obj);
