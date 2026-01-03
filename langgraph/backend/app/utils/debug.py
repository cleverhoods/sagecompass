import os

def maybe_attach_pycharm() -> None:
    """
    Attach the PyCharm debugger if host/port env vars are present.

    Side effects/state writes:
        Starts a remote debug session when configured.
    """
    host = os.getenv("PYCHARM_DEBUG_HOST")
    port = os.getenv("PYCHARM_DEBUG_PORT")
    if not host or not port:
        return

    import pydevd_pycharm
    pydevd_pycharm.settrace(host, port=int(port), suspend=False)
