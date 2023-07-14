import os

import yaml
from dotenv import load_dotenv


def get_config():
    if os.environ.get('DOCKER_ENV'):
        load_dotenv()  # 从环境变量加载.dockerenv文件中的变量
        config_path = os.getenv('CONFIG_FILE_PATH')
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    else:
        # 如果不在Docker容器中，则读取根目录下的config.yaml文件
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        return config
