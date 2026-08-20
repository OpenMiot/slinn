#pragma once
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>
#include <string_view>

namespace py = pybind11;


enum HttpVersion { H09, H1, H11, H2, H3 };

std::string_view httpVersionToStdString(HttpVersion httpVersion);

HttpVersion stdStringToHttpVersion(const std::string_view& str);

enum HttpProtocol { HTTP, HTTPS };

std::string_view httpProtocolToStdString(HttpProtocol httpProtocol);

HttpProtocol stdStringToHttpProtocol(const std::string_view& str);

class HttpHeaders{
protected:
    std::string normalizeKey(std::string& key) const;
    std::string normalizeValue(const py::object& value) const;
public:
    static HttpHeaders parse(const std::string& rawHttp);

    HttpVersion version;
    std::unordered_map<std::string, std::vector<std::string>> _data;

    HttpHeaders(
        HttpVersion version = HttpVersion::H11,
        std::unordered_map<std::string, std::vector<py::object>> default_headers = {}
    );

    std::optional<std::string> method() const;
    std::optional<std::string> scheme() const;
    std::optional<std::string> authority() const;
    std::optional<std::string> path() const;
    std::optional<HttpProtocol> protocol() const;
    std::optional<std::string> status() const;

    std::string get(std::string key, const py::object& default_value = py::none()) const;
    std::vector<std::string> values(std::string key, const std::vector<py::object>& default_values = {}) const;
    HttpHeaders add(std::string key, const py::object& value);
    HttpHeaders add_many(std::unordered_map<std::string, std::vector<py::object>> headers);
    HttpHeaders set_many(std::unordered_map<std::string, std::vector<py::object>> headers);
    void _add(std::string key, const std::string& value);
    HttpHeaders set(std::string key, const py::object& value);
    HttpHeaders del(std::string key);
    std::string pop(std::string key, py::ssize_t index = -1);
    std::vector<std::string> keys() const;
    bool __contains__(std::string key) const;
    py::bytes make() const;
    
    HttpHeaders extend(const HttpHeaders& headers);
    HttpHeaders merge(const HttpHeaders& headers);

    std::string __request_str__() const;
};