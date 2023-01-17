import sys
from . import chirp

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("Must have one parameter (mode)")

    mode = sys.argv[1]

    if mode == "boot":
        chirp.chirp_boot()
    elif mode == "shutdown":
        chirp.chirp_shutdown()
    elif mode == "monitor":
        pass # TODO: Call main loop
    else:
        raise ValueError(f"Unknown mode {repr(mode)}")
