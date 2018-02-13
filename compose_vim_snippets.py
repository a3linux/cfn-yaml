#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compose the single Vim snippets plugin file
"""

import os
import sys

STARTFILE="cfn-Start.vim.snippet"
OUTPUTFILE="yaml_awscfn.snippets"

with open(STARTFILE, 'r') as f:
    snippets = f.readlines()

with open(OUTPUTFILE, 'w') as w:
    w.writelines(snippets)
    w.write('\n')
    for root, dirs, files in os.walk("./cfn-yaml"):
        for file in files:
            if file.endswith(".snippet"):
                with open(os.path.join(root, file), 'r') as f:
                    snippets = f.readlines()
                w.writelines(snippets)
                w.write('\n')
