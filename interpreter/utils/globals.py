# If on, interpreter will send signal if waiting for user input, so web app can act properly
# See: https://github.com/KalenskyyAlex/omni-com
def enable_API_mode():
    with open("config", "w") as f:
        f.write("API_MODE")

def is_API_mode_enabled():
    with open("config", "r") as f:
        if "API_MODE" in f.read():
            return True
        else:
            return False