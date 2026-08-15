#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include "utils.hpp"


static py::object representate_str(py::handle obj) {
    // 1. Словарь
    if (py::isinstance<py::dict>(obj)) {
        py::dict result;
        for (auto item : obj.cast<py::dict>()) {
            // item.first и item.second - это py::handle
            result[item.first] = representate_str(item.second);
        }
        return result;
    }

    // 2. Список, кортеж, множество
    if (py::isinstance<py::list>(obj) || py::isinstance<py::tuple>(obj) || py::isinstance<py::set>(obj)) {
        py::list result;
        for (auto item : obj) {
            result.append(representate_str(item));
        }
        return result;
    }

    // 3. Базовые типы: str, int, float, bool
    if (py::isinstance<py::str>(obj) ||
        py::isinstance<py::int_>(obj) ||
        py::isinstance<py::float_>(obj) ||
        py::isinstance<py::bool_>(obj)) {
        return py::cast<py::object>(obj);; // py::handle неявно преобразуется в py::object? Лучше явно
        // Но если компилируется - оставляем. Если нет, используем py::object(obj)
    }

    // 4. bytes -> декодируем в str
    if (py::isinstance<py::bytes>(obj)) {
        return obj.attr("decode")();
    }

    // 5. enum.Enum
    try {
        py::module enum_module = py::module::import("enum");
        py::object enum_class = enum_module.attr("Enum");
        if (py::isinstance(obj, enum_class)) {
            return representate_str(obj.attr("value"));
        }
    } catch (...) {}

    // 6. Проверка переопределения __str__ или __repr__
    py::object type_obj = obj.attr("__class__");
    py::object object_class = py::module::import("builtins").attr("object");
    bool str_overridden = false, repr_overridden = false;
    try {
        py::object obj_str = type_obj.attr("__str__");
        py::object obj_repr = type_obj.attr("__repr__");
        py::object obj_str_default = object_class.attr("__str__");
        py::object obj_repr_default = object_class.attr("__repr__");
        str_overridden = (obj_str != obj_str_default);
        repr_overridden = (obj_repr != obj_repr_default);
    } catch (...) {}

    if (str_overridden || repr_overridden) {
        try {
            py::object repr_result = py::repr(obj);
            if (py::isinstance<py::str>(repr_result)) {
                return repr_result;
            }
        } catch (...) {}
    }

    // 7. Попытка использовать __dict__
    try {
        if (py::hasattr(obj, "__dict__")) {
            py::dict dict_attr = obj.attr("__dict__");
            py::dict result;
            for (auto item : dict_attr) {
                result[item.first] = representate_str(item.second);
            }
            return result;
        }
    } catch (...) {}

    // 8. Дефолтное представление
    std::string type_name = py::str(obj.attr("__class__").attr("__name__")).cast<std::string>();
    uintptr_t obj_id = reinterpret_cast<uintptr_t>(obj.ptr());
    std::string default_str = "<" + type_name + " object at " + std::to_string(obj_id) + ">";
    return py::str(default_str);
}

// Экспортируемая функция representate
py::object representate(py::object obj) {
    if (py::isinstance<py::bytes>(obj)) {
        return obj; // возвращаем как есть (py::handle -> py::object)
    }

    py::object result = representate_str(obj);

    if (py::isinstance<py::str>(result) ||
        py::isinstance<py::int_>(result) ||
        py::isinstance<py::float_>(result) ||
        py::isinstance<py::bool_>(result)) {
        return py::str(result).attr("encode")();
    }

    // Сериализация через orjson или json
    try {
        py::module orjson = py::module::import("orjson");
        return orjson.attr("dumps")(result);
    } catch (const py::error_already_set&) {
        py::module json = py::module::import("json");
        return json.attr("dumps")(result).attr("encode")();
    }
}
