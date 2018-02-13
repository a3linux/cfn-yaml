#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build snippets of AWS CloudFormation for Vim
# Copyright {2018} {Narrowbeam Limited}

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""

import sys
import os
import requests
from bs4 import BeautifulSoup
# import re


def get_cfn_res_list():
    """get_cfn_res_list

    :returns: CloudFormation Resource definition list

    """
    docurl = "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide"

    try:
        docpage = requests.get("%s/aws-template-resource-type-ref.html" %
                               docurl)
        htmldoc = docpage.content
    except Exception as e:
        print("Error when fetch AWS Document: %s!" % e)
        sys.exit(1)

    soup = BeautifulSoup(htmldoc, 'html.parser')

    # Selector based lookup - gets what we want and awstoc duplicates
    urllisttmp = soup.select('li a[href*="aws-"]')

    # Build a list of link description, url
    for url in urllisttmp:
        if 'class' not in url.attrs:
            yield (url.text, "%s/%s" % (docurl, url['href']))


def gen_cfn_snippets(urllist):
    """gen_cfn_snippets
    :urllist: CloudFormation Resource definition url list
    :returns: Snippets of CloudFormation Resources

    """
    for (pagelink, pageurl) in urllist:
        hotkey = ""
        snippet = ""
        pagelinklist = pagelink.split("::")
        hotkey = "cfn-" + pagelinklist[1]
        for i in range(2, len(pagelinklist)):
            hotkey = hotkey + "-" + pagelinklist[i]

        snippet = "snippet %s" % hotkey
        snippet = snippet + "\n#AWS-DOC " + pageurl

        try:
            page = requests.get(pageurl).content
            soup = BeautifulSoup(page, 'html.parser')
            fragment = soup.select_one('#YAML pre')
        except Exception as e:
            print(e)
        for tag in fragment:
            # Some source material has an extra \n that needs to be stripped
            snippetfilter = tag.text
            if not snippetfilter or not snippetfilter.strip():
                # skip blank tag(s), it might be the code function buttons
                continue
            if snippetfilter[0] == '\n':
                snippet = "%s\n%s" % (snippet, snippetfilter[1:])
            else:
                snippet = "%s\n%s" % (snippet, tag .text)
        yield (pagelinklist[1], hotkey, "%s\n%s" % (snippet, "endsnippet"))


# Create the folder for the snippets
BASE_DIR = "./cfn-yaml"
try:
    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)
except OSError:
    print("Error when prepare the destination folder")
    sys.exit(1)

for (name, hotkey, snippet) in gen_cfn_snippets(get_cfn_res_list()):
    try:
        path = os.path.join("./cfn-yaml", name)
        filepath = os.path.join(path, "%s.snippet" % hotkey)
        if not os.path.exists(path):
            os.mkdir(path)
        with open(filepath, 'w') as f:
            f.write(snippet)
    except Exception as e:
        print(e)
