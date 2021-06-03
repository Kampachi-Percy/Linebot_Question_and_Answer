import requests
import json
import re

import deepl_config # auth_keyが入った設定ファイル

def translator(text) -> str:
    # deepl_apiを使うための各種パラメータ
    params = {"auth_key": deepl_config.auth_key, "text": ""}

    # ひらがな・カタカナが1文字以上含まれていれば日本語とみなす
    p = re.compile("[\u3041-\u30FF]+")
    if p.search(text):
        params["source_lang"] = "JA"
        params["target_lang"] = "EN"
    else:
        params["source_lang"] = "EN"
        params["target_lang"] = "JA"

    text_list = text.split("\n")
    results = []

    print(text_list)

    for i, line in enumerate(text_list, 1):
        params["text"] = line
        r = requests.post("https://api-free.deepl.com/v2/translate", params=params)
        res = json.loads(r.text)
        result = res["translations"][0]["text"]

        results.append(result)

    reply = "\n".join(results)

    return reply