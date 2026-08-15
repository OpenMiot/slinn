#include "http_headers.hpp"
#include "../../utils.hpp"
#include <stdexcept>


#define WHITESPACE_CHARACTERS " \n\r\t\f\v"


std::string_view httpVersionToStdString(HttpVersion httpVersion) {
    switch (httpVersion) {
        case HttpVersion::H09: return "HTTP/0.9";
        case HttpVersion::H1:  return "HTTP/1.0";
        case HttpVersion::H11: return "HTTP/1.1";
        case HttpVersion::H2:  return "HTTP/2.0";
        case HttpVersion::H3:   return "HTTP/3.0";
    }
    return "unknown";
}

HttpVersion stdStringToHttpVersion(const std::string_view& str){
    if(str == "HTTP/0.9") return HttpVersion::H09;
    if(str == "HTTP/1.0") return HttpVersion::H1;
    if(str == "HTTP/1.1") return HttpVersion::H11;
    if(str == "HTTP/2.0") return HttpVersion::H2;
    if(str == "HTTP/3.0") return HttpVersion::H3;
    return HttpVersion::H11;
}

std::string_view httpProtocolToStdString(HttpProtocol httpProtocol) {
    switch (httpProtocol) {
        case HttpProtocol::HTTP: return "HTTP";
        case HttpProtocol::HTTPS:  return "HTTPS";
    }
    return "unknown";
}

HttpProtocol stdStringToHttpProtocol(const std::string_view& str){
    if(str == "HTTP") return HttpProtocol::HTTP;
    if(str == "HTTPS") return HttpProtocol::HTTPS;
    return HttpProtocol::HTTP;
}

std::string titleCase(std::string text) {
    bool new_word = true;
    for (char &c : text) {
        if (std::isspace(static_cast<unsigned char>(c))) {
            new_word = true;
        } else if (new_word) {
            c = std::toupper(static_cast<unsigned char>(c));
            new_word = false;
        } else {
            c = std::tolower(static_cast<unsigned char>(c));
        }
    }
    return text;
}

void toLowerCase(std::string& text){
    for (char &c : text) {
        c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    }
}

void toUpperCase(std::string& text){
    for (char &c : text) {
        c = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
    }
}

std::string join(const std::vector<std::string>& tokens, const std::string& delimeter){
    auto joined_view = tokens | std::views::join_with(delimeter);
    return std::string{joined_view.begin(), joined_view.end()};
}

std::vector<std::string> split(const std::string& str, const std::string& delimiter = " ") {
    std::vector<std::string> tokens;
    size_t start = 0;
    size_t end = str.find(delimiter);

    while (end != std::string::npos) {
        tokens.push_back(str.substr(start, end - start));
        start = end + delimiter.length();
        end = str.find(delimiter, start);
    }

    tokens.push_back(str.substr(start)); 
    return tokens;
}

template <typename T>
std::vector<T> slice(std::vector<T> vec, long long from, long long to){
    auto sliced_view = vec | std::views::drop(from) | std::views::take(to - 1);
    return std::vector<T>(sliced_view.begin(), sliced_view.end());
}

std::string_view lstrip(std::string_view s) {
    auto start = s.find_first_not_of(WHITESPACE_CHARACTERS);
    if (start == std::string_view::npos) {
        return "";
    }
    s.remove_prefix(start);
    return s;
}

std::string_view rstrip(std::string_view s) {
    auto end = s.find_last_not_of(WHITESPACE_CHARACTERS);
    if (end == std::string_view::npos) {
        return "";
    }
    s.remove_suffix(s.size() - 1 - end);
    return s;
}

std::string_view strip(std::string_view s) {
    return lstrip(rstrip(s));
}

template <typename K, typename V>
std::optional<V> get_optional(const std::unordered_map<K, V>& map, const K& key) {
    auto it = map.find(key);
    if (it != map.end()) {
        return it->second;
    }
    return std::nullopt;
}

std::string HttpHeaders::normalizeKey(std::string& key) const{
    if(key.starts_with(":")){
        toLowerCase(key);
    }else{
        key = titleCase(key);
    }
    key = strip(key);
    if(key == "Host") return ":authority";
    return key;
}

std::string HttpHeaders::normalizeValue(const py::object& value) const{
    return representate(value).attr("decode")().cast<std::string>();
}


HttpHeaders HttpHeaders::parse(const std::string& rawHttp){
    std::string_view http = rawHttp;

    size_t pos = http.find("\r\n");
    std::string_view _startLine = http.substr(0, pos);
    size_t methodPos =  _startLine.find(" ");
    size_t pathPos = _startLine.find(" ", methodPos + 1);

    HttpHeaders headers(
        stdStringToHttpVersion(_startLine.substr(pathPos, pos))
    );
    std::string _method = std::string(_startLine.substr(0, methodPos));
    toUpperCase(_method);
    headers._add(":method", _method);
    headers._add(":path", std::string(_startLine.substr(methodPos+1, pathPos-2)));

    size_t current_pos = pos + 2;
    while (current_pos < http.size()) {
        size_t next_line = http.find("\r\n", current_pos);
        if (next_line == std::string::npos) break;

        std::string_view line = http.substr(current_pos, next_line - current_pos);
        if (line.empty()) break;

        size_t colon_pos = line.find(':');
        if (colon_pos != std::string::npos) {
            std::string_view key = line.substr(0, colon_pos);
            std::string_view value = line.substr(colon_pos + 1);
            
            // Только здесь мы делаем одну аллокацию для ключа (если нужно)
            // или вообще работаем с view, если мы знаем, что ключ не изменится
            headers._add(std::string(strip(key)), std::string(strip(value)));
        }

        current_pos = next_line + 2;
    }

    return headers;
}

HttpHeaders::HttpHeaders(
    HttpVersion version, std::unordered_map<std::string, std::vector<py::object>> default_headers
){
    this->version = version;
    for (const auto& [key, values] : default_headers){
        for(const auto& value : values){
            add(key, value);
        }
    }
}

std::optional<std::string> HttpHeaders::method() const{
    return get(":method");
}
std::optional<std::string> HttpHeaders::scheme() const{
    return get(":scheme");
}
std::optional<std::string> HttpHeaders::authority() const{
    return get(":authority");
}
std::optional<std::string> HttpHeaders::path() const{
    return get(":path");
}
std::optional<HttpProtocol> HttpHeaders::protocol() const{
    if (__contains__(":protocol")) return stdStringToHttpProtocol(std::string(get(":protocol")));
    return std::nullopt;
}
std::optional<std::string> HttpHeaders::status() const{
    return get(":status");
}

std::string HttpHeaders::get(std::string key, const py::object& default_value) const{
    std::vector<std::string> _values = values(key, std::vector<py::object>{default_value});
    if(!_values.size()) return normalizeValue(default_value);
    return _values[0];
}
std::vector<std::string> HttpHeaders::values(std::string key, const std::vector<py::object>& default_values) const{
    std::vector<std::string> normalized_default_vaules;
    for(auto value : default_values){
        normalized_default_vaules.push_back(normalizeValue(value));
    }
    return get_optional(_data, normalizeKey(key)).value_or(normalized_default_vaules);
}

HttpHeaders HttpHeaders::add(std::string key, const py::object& value){
    _add(key, normalizeValue(value));
    return *this;
}
HttpHeaders HttpHeaders::add_many(std::unordered_map<std::string, std::vector<py::object>> headers){
    for(const auto& [_key, values] : headers){
        std::string key = _key;
        key = normalizeKey(key);
        std::vector<std::string> normalized_default_vaules;
        for(auto value : values){
            normalized_default_vaules.push_back(normalizeValue(value));
        }
        if(__contains__(key)){
            std::vector<std::string>& _values = _data[key];
            _values.reserve(_values.size() + normalized_default_vaules.size());
            _values.insert(_values.end(), normalized_default_vaules.begin(), normalized_default_vaules.end());
        }else{
            _data[key] = normalized_default_vaules;
        }
    }
    return *this;
}
void HttpHeaders::_add(std::string key, const std::string& value){
    key = normalizeKey(key);
    if(__contains__(key)){
        _data[key].push_back(value);
    }else{
        _data[key] = std::vector<std::string>{value};
    }
}
HttpHeaders HttpHeaders::set(std::string key, const py::object& value){
    _data[normalizeKey(key)] = std::vector<std::string>{normalizeValue(value)};
    return *this;
}
HttpHeaders HttpHeaders::del(std::string key){
    _data.erase(key);
    return *this;
}
std::string HttpHeaders::pop(std::string key, py::ssize_t index){
    std::string back = _data[key].back();
    _data[key].pop_back();
    return back;
}
std::vector<std::string> HttpHeaders::keys() const{
    std::vector<std::string> _keys;
    _keys.reserve(_data.size());

    for (const auto& [key, value] : _data) {
        _keys.push_back(key);
    }
    return _keys;
}
bool HttpHeaders::__contains__(std::string key) const{
    return _data.contains(key);
}
py::bytes HttpHeaders::make() const{
    if(!status()) throw std::runtime_error("pseudo header :status is not provided");
    std::string http = std::string(httpVersionToStdString(version)) + " " + std::string(*status()) + "\r\n";
    for (const auto& [key, values] : _data) {
        if(key.starts_with(":")) continue;
        for(const auto& value : values){
            http.append(std::string(key) + ": " + std::string(value) + "\r\n");
        }
    }
    http.append("\r\n");
    std::string_view view(http);
    return py::bytes(view.data(), view.size());
}


HttpHeaders HttpHeaders::extend(const HttpHeaders& headers){
    for (const auto& [key, values] : headers._data){
        auto [it, inserted] = _data.try_emplace(key, values);
        if(!inserted){
            std::vector<std::string>& _values = _data[key];
            _values.reserve(_values.size() + values.size());
            _values.insert(_values.end(), values.begin(), values.end());
        }
    }
    return *this;
}


std::string HttpHeaders::__request_str__() const{

}
