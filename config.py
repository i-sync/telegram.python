#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

import json

with open('config.json', 'r') as f:
    config = json.load(f)
    #print(config)

Config = config