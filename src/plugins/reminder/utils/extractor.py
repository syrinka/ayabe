# -*- coding=utf-8 -*-
# library: jionlp
# author: dongrixinyu
# license: Apache License 2.0
# Email: dongrixinyu.89@163.com
# github: https://github.com/dongrixinyu/JioNLP
# description: Preprocessing tool for Chinese NLP
# website: http://www.jionlp.com


import re

from .rule_pattern import *


__all__ = ['Extractor']


class Extractor(object):
    """ 规则抽取器 """
    def __init__(self):
        self.extract_parentheses_pattern = None
        self.remove_parentheses_pattern = None
        self.parentheses_pattern = PARENTHESES_PATTERN
        self.parentheses_dict = None

    def extract_parentheses(self, text, parentheses=PARENTHESES_PATTERN, detail=False):
        """ 提取文本中的括号及括号内内容，当有括号嵌套时，提取每一对
        成对的括号的内容

        Args:
            text(str): 字符串文本
            parentheses: 要删除的括号类型，格式为:
                '左括号1右括号1左括号2右括号2...'，必须为成对的括号如'{}()[]'，
                默认为self.parentheses
            detail: 是否打印括号内容位置信息

        Returns:
            list: [
                    {
                        'context'(str): 'the context between parentheses',
                        'offset'(tuple): 'the location of extracted text'
                    },  # 当 detail 为 True 时
                    'the context between parentheses',  # 当 detail 为 False 时
                    ...
                ]

        """
        if self.extract_parentheses_pattern is None or self.parentheses_pattern != parentheses:
            self.parentheses_pattern = parentheses

            extract_pattern = '[' + re.escape(self.parentheses_pattern) + ']'
            extract_pattern = re.compile(extract_pattern)
            
            p_length = len(self.parentheses_pattern)

            parentheses_dict = dict()
            for i in range(0, p_length, 2):
                value = self.parentheses_pattern[i]
                key = self.parentheses_pattern[i + 1]
                parentheses_dict.update({key: value})
            
            self.parentheses_dict = parentheses_dict
            self.extract_parentheses_pattern = extract_pattern

        content_list = list()
        parentheses_list = list()
        idx_list = list()
        finditer = self.extract_parentheses_pattern.finditer(text)
        for i in finditer:
            idx = i.start()
            parentheses = text[idx]

            if parentheses in self.parentheses_dict.keys():
                if len(parentheses_list) > 0:
                    if parentheses_list[-1] == self.parentheses_dict[parentheses]:
                        parentheses_list.pop()
                        if detail:
                            start_idx = idx_list.pop()
                            end_idx = idx + 1
                            content_list.append(
                                {'content': text[start_idx: end_idx],
                                 'offset': (start_idx, end_idx)})
                        else:
                            content_list.append(text[idx_list.pop(): idx + 1])
            else:
                parentheses_list.append(parentheses)
                idx_list.append(idx)
                
        return content_list

    def remove_parentheses(self, text, parentheses=PARENTHESES_PATTERN):
        """ 删除文本中的括号及括号内内容

        Args:
            text(str): 字符串文本
            parentheses: 要删除的括号类型，格式为:
                '左括号1右括号1左括号2右括号2...'，必须为成对的括号如'{}()[]'，
                默认为self.parentheses

        Returns:
            str: 删除括号及括号中内容后的文本

        """
        if self.remove_parentheses_pattern is None or self.parentheses_pattern != parentheses:
            self.parentheses_pattern = parentheses

            p_length = len(self.parentheses_pattern)
            remove_pattern_list = list()
            remove_pattern_format = '{left}[^{left}{right}]*{right}'
            
            for i in range(0, p_length, 2):
                left = re.escape(self.parentheses_pattern[i])
                right = re.escape(self.parentheses_pattern[i + 1])
                remove_pattern_list.append(
                    remove_pattern_format.format(left=left, right=right))
                
            remove_pattern = '|'.join(remove_pattern_list)
            remove_pattern = re.compile(remove_pattern)

            self.remove_parentheses_pattern = remove_pattern

        length = len(text)
        while True:
            text = self.remove_parentheses_pattern.sub('', text)
            if len(text) == length:
                return text
            length = len(text)


extractor = Extractor()
extract_parentheses = extractor.extract_parentheses
remove_parentheses = extractor.remove_parentheses