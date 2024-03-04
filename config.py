from starlette.config import Config
from starlette.datastructures import Secret

config = Config()
#<var_name on user_api.py>:<data_type> = config("<var name on Azure environment variables>",default="")
API_KEY: str = config("API_KEY",default="")