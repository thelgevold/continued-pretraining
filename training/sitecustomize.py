import importlib.util


_ORIGINAL_FIND_SPEC = importlib.util.find_spec
_DISABLED_MODULES = {
    "triton_kernels",
    "vllm.third_party.triton_kernels",
}


def _install_apport_hook() -> None:
    try:
        import apport_python_hook
    except ImportError:
        return
    apport_python_hook.install()


def _find_spec(module_name: str, package: str | None = None):
    if module_name in _DISABLED_MODULES:
        return None
    return _ORIGINAL_FIND_SPEC(module_name, package)


_install_apport_hook()
importlib.util.find_spec = _find_spec
