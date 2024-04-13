#!/usr/bin/env python3

if __name__ == '__main__':
    from config.Config import Config
    from tools.Runner import Runner

    _config = Config.instance()
    _runner = Runner(_config)

    _runner.start()
