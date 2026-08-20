#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include "utils.hpp"


std::string representate(py::object obj) {
    static py::function py_representate = py::module_::import("slinn.utils").attr("representate");
    return py_representate(obj).attr("decode")().cast<std::string>();
}
