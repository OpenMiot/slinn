// src/my_module.cpp
#include <pybind11/pybind11.h>
#include "net/http/http_headers.hpp"
#include "utils.hpp"

namespace py = pybind11;


PYBIND11_MODULE(slinn_cxx, m) {
    py::enum_<HttpVersion>(m, "HttpVersion")
        .value("H09", HttpVersion::H09)
        .value("H1", HttpVersion::H1)
        .value("H11", HttpVersion::H11)
        .value("H2", HttpVersion::H2)
        .value("H3", HttpVersion::H3)
        .def_property_readonly("value", [](HttpVersion httpVersion) {
            return httpVersionToStdString(httpVersion);
        })
        .def("__str__", [](HttpVersion httpVersion) {
            return httpVersionToStdString(httpVersion);
        });
    
    py::enum_<HttpProtocol>(m, "HttpProtocol")
        .value("HTTP", HttpProtocol::HTTP)
        .value("HTTPS", HttpProtocol::HTTPS)
        .def_property_readonly("value", [](HttpProtocol httpProtocol) {
            return httpProtocolToStdString(httpProtocol);
        })
        .def("__str__", [](HttpProtocol httpProtocol) {
            return httpProtocolToStdString(httpProtocol);
        });

    py::class_<HttpHeaders>(m, "HttpHeaders")
        .def(py::init<HttpVersion, std::unordered_map<std::string, std::vector<py::object>>>(),
             py::arg("version") = HttpVersion::H11,
             py::arg("default_headers") = std::unordered_map<std::string, std::vector<py::object>>())
        .def_static("parse", &HttpHeaders::parse, py::return_value_policy::move)
        .def_readwrite("version", &HttpHeaders::version)
        .def_property_readonly("method", &HttpHeaders::method)
        .def_property_readonly("scheme", &HttpHeaders::scheme)
        .def_property_readonly("authority", &HttpHeaders::authority)
        .def_property_readonly("path", &HttpHeaders::path)
        .def_property_readonly("protocol", &HttpHeaders::protocol)
        .def_property_readonly("status", &HttpHeaders::status)
        .def("get", &HttpHeaders::get,
             py::arg("key"),
             py::arg("default_value") = py::none())
        .def("values", &HttpHeaders::values,
             py::arg("key"),
             py::arg("default_values") = std::vector<py::object>())
        .def("add", &HttpHeaders::add, py::return_value_policy::move)
        .def("add_many", &HttpHeaders::add_many, py::return_value_policy::move)
        .def("set", &HttpHeaders::set, py::return_value_policy::move)
        .def("delete", &HttpHeaders::del, py::return_value_policy::move)
        .def("pop", &HttpHeaders::pop,
             py::arg("key"),
             py::arg("index") = -1)
        .def("keys", &HttpHeaders::keys)
        .def("__contains__", &HttpHeaders::__contains__)
        .def("make", &HttpHeaders::make)
        .def("extend", &HttpHeaders::extend);
    
    m.def("representate", &representate);
}
