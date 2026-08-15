#pragma once
#include <pybind11/pybind11.h>


namespace py = pybind11;

// Экспортируемая функция representate
py::object representate(py::object obj);
