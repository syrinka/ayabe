# -*- coding=utf-8 -*-
# library: jionlp
# author: dongrixinyu
# license: Apache License 2.0
# Email: dongrixinyu.89@163.com
# github: https://github.com/dongrixinyu/JioNLP
# description: Preprocessing & Parsing tool for Chinese NLP
# website: www.jionlp.com


"""
TODO:
    - 某些金额为 合计/共/共计、共合计、合计共、共约1000元 类型。
    - 某些金额为单价类型，
        - 100 元每节课
        - 每桶油 1700 美元
        - 289.02 日元/本
    - 金额模糊表达
        - 五六百美元
    - 货币标识符
        - ￥5600、$85、€¥£、85,000$

"""

import re

from .funcs import start_end
from .rule_pattern import MONEY_NUM_STRING, MONEY_NUM_MIDDLE_STRING
from .extractor import extract_parentheses, remove_parentheses


__all__ = ['MoneyParser']


class MoneyParser(object):
    """将各种金额形式转换成指定的形式。
    使用该函数将中文金额转换成易于计算的float形式，该函数可以转换如下金额格式。

    Args:
        money_string(str): 一个金额形式字符串。
        default_unit(str): 默认金额单位，默认是 ”元“（人民币），指当金额中未指明货币类型时的默认值。
        ret_format(str): 转换金额标准化的返回格式，包括 'str'|'detail' 两种，默认为 detail
            'str' 格式形如 “64000.00韩元”，
            'detail' 格式形如 “{'num': '64000.00', 'case': '韩元', 'definition': 'accurate'}”

    Returns:
        标准解析格式的金额（见下例）。

    Examples:
        >>> import jionlp as jio
        >>> money = "六十四万零一百四十三元一角七分"
        >>> print(jio.parse_money(money))

        # {'num': '640143.17元', 'definition': 'accurate', 'case': '元'}

    """
    def __init__(self):
        self.money_pattern_1 = None
        self._prepare()
        
    def _prepare(self):
        self.float_num_pattern = re.compile('\d+(\.)?\d*')
        self.punc_pattern = re.compile(MONEY_NUM_MIDDLE_STRING)
        self.bai_pattern = re.compile('百|佰')
        self.qian_pattern = re.compile('千|仟|k')
        self.wan_pattern = re.compile('万|萬|w')
        self.yi_pattern = re.compile('亿')

        # 检测货币金额数值是否符合要求，不符合要求将直接报错，必须为数值字符与单位字符，可包括 角、分等
        self.money_num_string_pattern = re.compile(MONEY_NUM_STRING)

        # 纯数字的金额
        self.money_pattern_1 = re.compile(r'^\d+(\.)?\d*$')
        # 前为数字，后为汉字的金额
        self.money_pattern_2 = re.compile(r'^\d+(\.)?\d*[十拾百佰k千仟w万萬亿兆]{1,2}$')

        self.multi_nums = {
            '分': 0.01, '角': 0.1, '毛': 0.1, '十': 10, '拾': 10, 
            '百': 100, '佰': 100, '千': 1000, '仟': 1000, 
            '万': 10000, '萬': 10000, '亿': 100000000}
        self.plus_nums = {
            '〇': 0, 'O': 0, '零': 0, '０': 0,
            '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
            '壹': 1, '贰': 2, '俩': 2, '叁': 3, '弎': 3, '仨': 3, '肆': 4, '伍': 5, '陆': 6, '柒': 7, '捌': 8, '玖': 9,
            '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
            '１': 0, '２': 2, '３': 3, '４': 4, '５': 5, '６': 6, '７': 7, '８': 8, '９': 9,
        }
        self.suffix_nums = {
            '百': 100, '佰': 100, '千': 1000, '仟': 1000, 'k': 1000,
            '万': 10000, '萬': 10000, 'w': 10000, '亿': 100000000,
            '十万': 100000, '拾万': 100000, '百万': 1000000, '佰万': 1000000,
            '仟万': 10000000, '千万': 10000000, '万万': 100000000, '萬萬': 100000000,
            '十亿': 1000000000, '拾亿': 1000000000, '百亿': 10000000000, '佰亿': 10000000000,
            '千亿': 100000000000, '仟亿': 100000000000, '万亿': 1000000000000, '萬亿': 1000000000000,
            '兆': 1000000000000}

        self.standard_format = '{:.2f}'
        self.type_error = 'the given money_string `{}` is illegal.'
        
    def turn_num_standard_format(self, num):
        """将数字形式转换成`std_fmt`形式。
        使用该函数将数字形式转换成 `std_fmt` 形式。

        Args:
            num(int|str|float): 一个数字，支持 int 或 str 格式。

        Returns:
            转换后`std_fmt`形式的 str 类型的数字。

        Examples:
            >>> print(self.turn_num_standard_format(30.5))

            # '30.50'

        """
        standard_num = None

        if type(num) is str:
            if self.money_pattern_1.match(num):
                standard_num = self.standard_format.format(float(num))

        elif type(num) is int or type(num) is float:
            standard_num = self.standard_format.format(num)

        # else:
        #     raise TypeError('the type of `num` {} is not in [str, int, float].'.format(num))
            
        return standard_num

    def turn_money_std_fmt_util1(self, money_string):
        """将中文金额形式转换成 float 形式。处理以 “千百十个” 为核心的金额字符串。

        使用该函数将中文金额转换成易于计算的 float 形式，注意该函数是 turn_money_std_fmt
        辅助函数，只能方便将一万这种转换，一千万无法转换。

        Args:
            money_string: 一个中文格式表示的金额。

        Returns:
            转换后 float 类型的数字。

        """

        rtn_std_num = 0.0
        if not money_string or type(money_string) is not str:
            return rtn_std_num

        # 对 `十、百、千` 开头数字进行规范化
        if money_string[0] in '十拾百佰千仟':
            money_string = '一' + money_string

        tmp_nums = list()
        for char in list(money_string):
            plus_num = self.plus_nums.get(char, 0)
            if plus_num != 0:
                tmp_nums.append(plus_num)

            multi_num = self.multi_nums.get(char, 1)
            if len(tmp_nums) >= 1:
                tmp_nums[-1] = tmp_nums[-1] * multi_num
                
        rtn_std_num = sum(tmp_nums)
        return rtn_std_num

    def turn_money_std_fmt_util2(self, money_string):
        """将中文金额形式转换成 float 形式。处理以 “万” 为核心的金额字符串

        使用该函数将中文金额转换成易于计算的 float 形式，注意该函数是 turn_money_std_fmt 的
        另一个辅助函数，与 turn_money_std_fmt_util1 搭配起来转换类似“1千万”数字。

        Args:
            money_string: 一个中文格式表示的金额。

        Returns:
            转换后 float 类型的数字。

        """
        if '万' in money_string or '萬' in money_string:
            if money_string[0] in '万萬':
                money_string = '一' + money_string

            seg_money_string = self.wan_pattern.split(money_string)
            if len(seg_money_string) == 2:
                prev, nxt = seg_money_string
                tmp_prev_num = self.turn_money_std_fmt_util1(prev)
                tmp_prev_num = tmp_prev_num * 10000
                tmp_nxt_num = self.turn_money_std_fmt_util1(nxt)
                rtn_std_num = tmp_prev_num + tmp_nxt_num
            else:
                raise ValueError(self.type_error.format(money_string))
        else:
            rtn_std_num = self.turn_money_std_fmt_util1(money_string)

        return rtn_std_num

    def turn_money_std_fmt_util3(self, money_string):
        """将中文金额形式转换成 float 形式。处理以 “亿” 为核心的金额字符串

        使用该函数将中文金额转换成易于计算的 float 形式，注意该函数是 turn_money_std_fmt 的
        另一个辅助函数，与 turn_money_std_fmt_util2 搭配起来转换类似“1千亿”数字。

        Args:
            money_string: 一个中文格式表示的金额。

        Returns:
            转换后 float 类型的数字。

        """
        if '亿' in money_string:
            if money_string.startswith('亿'):
                money_string = '一' + money_string

            seg_billion = self.yi_pattern.split(money_string)
            if len(seg_billion) == 2:
                prev, nxt = seg_billion
                prev_num = self.turn_money_std_fmt_util2(prev)
                nxt_num = self.turn_money_std_fmt_util2(nxt)
                rtn_std_num = prev_num * 100000000 + nxt_num

            else:
                raise ValueError(self.type_error.format(money_string))
        else:
            rtn_std_num = self.turn_money_std_fmt_util2(money_string)

        return rtn_std_num

    def _cleansing(self, money_string):
        # 去除其中的标点符号 ，,等
        money_string = self.punc_pattern.sub('', money_string)

        # 去除其中的括号，如 “50万元（含）以上”
        sub_parentheses = extract_parentheses(money_string, parentheses='()（）')
        if '含' in ''.join(sub_parentheses):
            money_string = remove_parentheses(money_string, parentheses='()（）')

        return money_string

    def __call__(self, money_string):
        """ 解析单个金额字符串，可由解析两个组成金额范围 """

        # 清洗字符串
        money_string = self._cleansing(money_string)

        if money_string == '':
            raise ValueError(self.type_error.format(money_string))

        # 若货币的金额字符串部分有误，则报错返回。
        if self.money_num_string_pattern.search(money_string) is None:
            raise ValueError(self.type_error.format(money_string))
            # pass

        if self.money_pattern_1.search(money_string):
            # 纯数字格式的金额，如 “549040.27”
            computed_money_num = float(money_string)

        elif self.money_pattern_2.search(money_string):
            # 前为数字，后为汉字的金额，如 “6000万”

            char_part = self.float_num_pattern.sub('', money_string)
            if char_part in self.suffix_nums:
                num_suffix = self.suffix_nums.get(char_part)
            else:
                raise ValueError(self.type_error.format(money_string))

            num_part = money_string.replace(char_part, '')
            if self.money_pattern_1.search(num_part):
                computed_money_num = float(num_part) * num_suffix
            else:
                raise ValueError(self.type_error.format(money_string))

        else:
            computed_money_num = self.turn_money_std_fmt_util3(money_string)

        # 金额标准化
        standard_money_num = self.turn_num_standard_format(computed_money_num)
        if standard_money_num is None:
            raise ValueError(self.type_error.format(money_string))

        return standard_money_num
