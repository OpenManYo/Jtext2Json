# -*- coding: utf-8 -*-
# Copyright (c) 2017 Masahiko Hashimoto <hashimom@geeko.jp>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from collections import OrderedDict
import MeCab
import json
import jaconv

# ------------------------------
# Parserクラス
# Mecabで形態素解析を行うクラス
class Parser:
    def __init__(self):
        self.__tagger = MeCab.Tagger()
        self.__tagger.parse('')

    # annotate
    # Mecabで形態素解析を行いJSONへ変換する
    # str : 形態素解析を行うテキスト（1文単位）
    def annotate(self, str):
        __idx = 0
        __rcvIdx = [-1, -1]
        __rcvOfst = -1
        __firstFlg = 0
        jsonObj = OrderedDict()
        jsonObj["Body"] = str
        jsonObj["Phrase"] = []

        # 文節0番目初期化
        phrase = OrderedDict()
        phrase["Idx"] = __idx
        phrase["RcvIdx"] = __rcvIdx
        phrase["Tags"] = []

        __node = self.__tagger.parseToNode(str)
        while __node:
            # BOS/EOFなど文字数=0のものは処理を行わない
            if __node.length == 0:
                __node = __node.next
                continue

            # Mecabの結果featureを , 単位で分解
            __feature = __node.feature.strip().split(',')
            __tag = OrderedDict()
            __tag["Word"] = __node.surface
            # feature要素数チェック
            if 7 < len(__feature):
                __tag["Read"] = jaconv.kata2hira(__feature[7])
            else:
                # featureの要素が7個存在しない場合は恐らく未知語なのでsurfaceをそのまま使う
                __tag["Read"] = jaconv.kata2hira(__node.surface)
            __tag["PosID"] = __node.posid

            # 文節頭になりうる単語を抽出
            if (0 <= __node.posid <= 6) or \
                    (10 <= __node.posid <= 12) or \
                    (26 <= __node.posid <= 31) or \
                    (33 <= __node.posid <= 49) or \
                    (59 <= __node.posid <= 68):
                if __firstFlg != 0:
                    jsonObj["Phrase"].append(phrase)
                    __idx = __idx + 1
                    # 文節を再初期化
                    phrase = OrderedDict()
                    phrase["Idx"] = __idx
                    phrase["RcvIdx"] = __rcvIdx
                    phrase["Tags"] = []
                else:
                    __firstFlg = 1

            phrase["Tags"].append(__tag)

            __node = __node.next

        # 最後の文節を登録
        jsonObj["Phrase"].append(phrase)

        return jsonObj

# ------------------------------
# Main
#
if __name__ == "__main__":
    __loop = 1
    inFilename = 'test.txt'

    # Mecabパーサー初期化
    parse = Parser()

    for line in open(inFilename, 'r'):
        # 改行文字の削除
        line = line.replace('\n', '')

        # 「。」毎にパースを行う ※それ以外は未対応
        for context in line.replace("。", "。___").split("___"):
            if len(context) == 0:
                continue
            jsonObj = parse.annotate(context)

            # JSONへ変換
            outFilename = "%s_%08d.json" % (inFilename.split('.')[0], __loop)
            outFile = open(outFilename, 'w')
            outFile.write(json.dumps(jsonObj, ensure_ascii=False))
            outFile.close()

            __loop = __loop + 1

    print("Success!!")
