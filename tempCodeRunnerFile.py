def get_config_path():
    username = getpass.getuser()
    config_dir = os.path.expanduser("~/.bsrnchat")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, f"config_{username}.toml")