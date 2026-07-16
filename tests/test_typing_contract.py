"""Structural checks for the shipped native-extension stub."""

import ast
import inspect
from collections import defaultdict
from pathlib import Path

import Fortuna

STUB = Path(__file__).parents[1] / "src" / "Fortuna" / "_core.pyi"


def _functions(nodes):
    grouped = defaultdict(list)
    for node in nodes:
        if isinstance(node, ast.FunctionDef):
            grouped[node.name].append(node)
    return grouped


def _runtime_count_apis():
    return {
        name
        for name in Fortuna.__all__
        if name != "Generator"
        and callable(function := getattr(Fortuna, name, None))
        and "count" in inspect.signature(function).parameters
    }


def _assert_count_overloads(functions, expected):
    assert {name for name, definitions in functions.items() if len(definitions) == 3} == expected
    for name in expected:
        definitions = functions[name]
        assert all(
            [ast.unparse(decorator) for decorator in definition.decorator_list] == ["overload"]
            for definition in definitions
        )

        count_parameters = []
        for definition in definitions:
            position = [argument.arg for argument in definition.args.kwonlyargs].index("count")
            count_parameters.append(
                (
                    ast.unparse(definition.args.kwonlyargs[position].annotation),
                    definition.args.kw_defaults[position],
                )
            )
        assert count_parameters[0][0] == "None"
        assert isinstance(count_parameters[0][1], ast.Constant)
        assert count_parameters[0][1].value is None
        assert count_parameters[1:] == [("int", None), ("int | None", None)]

        scalar = ast.unparse(definitions[0].returns)
        assert ast.unparse(definitions[1].returns) == f"list[{scalar}]"
        assert ast.unparse(definitions[2].returns) == f"{scalar} | list[{scalar}]"


def test_every_count_api_has_precise_module_and_generator_overloads():
    module = ast.parse(STUB.read_text())
    expected = _runtime_count_apis()
    assert len(expected) == 45

    generator = next(
        node for node in module.body if isinstance(node, ast.ClassDef) and node.name == "Generator"
    )
    _assert_count_overloads(_functions(module.body), expected)
    _assert_count_overloads(_functions(generator.body), expected)


def test_native_stub_does_not_advertise_stub_only_runtime_bases():
    module = ast.parse(STUB.read_text())
    classes = {node.name for node in module.body if isinstance(node, ast.ClassDef)}
    assert classes == {"Generator"}
    assert not hasattr(Fortuna._core, "_CountAPI")
