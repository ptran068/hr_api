from os.path import exists, abspath, dirname, join

import environ

env = environ.Env()

# Build paths inside the project like this: join(BASE_DIR, "directory")
BASE_DIR = dirname(dirname(dirname(__file__)))
# Ideally move env file should be outside the git repo
# i.e. BASE_DIR.parent.parent
env_file = join(dirname(BASE_DIR), "config.env")
if not exists(env_file):
    env_file = "/etc/company-api/config.env"

if exists(env_file):
    environ.Env.read_env(str(env_file))
