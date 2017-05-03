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
        __jsonObj = OrderedDict()
        __jsonObj["Body"] = str
        __jsonObj["Tags"] = []

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
            __jsonObj["Tags"].append(__tag)
            __node = __node.next

        return(__jsonObj)

# ------------------------------
# Main
#
if __name__ == "__main__":
    inFilename = 'test.txt'
    outFilename = inFilename.split('.')[0] + '.json'

    # 出力ファイル作成
    outFile = open(outFilename, 'w')
    outFile.write("{\"File\": \"" + inFilename + "\",\n")
    outFile.write(" \"Context\": [ \n")

    # Mecabパーサー初期化
    parse = Parser()

    for line in open(inFilename, 'r'):
        # 改行文字の削除
        line = line.replace('\n', '')

        # 「。」毎にパースを行う ※それ以外は未対応
        for context in line.replace("。", "。_").split("_"):
            if len(context) == 0:
                continue
            jsonTmp = parse.annotate(context)

            # JSONへ変換
            jsonString = json.dumps(jsonTmp, ensure_ascii=False)
            outFile.write("  " + jsonString + ",\n")

    outFile.write("  ]\n")
    outFile.write("}\n")
    outFile.close()

    print("Success!!")
