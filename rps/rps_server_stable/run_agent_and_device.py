#!/usr/bin/env python
# encoding: utf-8

from module.run_agent_client import run_agent_client
from module.run_agent_device import run_agent_device
from module.run_device import run_device

if __name__ == '__main__':
    run_agent_client()
    run_agent_device()
    run_device()

