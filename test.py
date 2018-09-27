#!/usr/bin/python
# -*- coding: utf-8 -*-

''' TikTokSpider 单元测试代码 '''

from unittest import TestCase


class TestIs_valid_id(TestCase):
    def test_is_valid_id(self):
        '''
        初步测试user_id格式是否正确
        后续添加更详细规则
        '''
        from dyspider import is_valid_id
        self.assertTrue(is_valid_id(100))
        self.assertTrue(is_valid_id(198372198))
        self.assertFalse(is_valid_id('a'))
        self.assertFalse(is_valid_id(''))
        self.assertFalse(is_valid_id('KASFJ'))
        self.assertFalse(is_valid_id(0))
        self.assertFalse(is_valid_id(None))


class TestGet_parser(TestCase):

    def setUp(self):
        from dyspider import parse_args
        self.args = parse_args(['--uid', '1234'])

    def test_get_parser(self):
        '''
        测试命令解析函数
        '''
        self.assertEqual(self.args.user_id, 1234)
        self.assertNotEqual(self.args.user_id, '1234')
        self.assertNotEqual(self.args.user_id, 123)


class TestGet_douyin_id(TestCase):

    def test_get_id_from_cmd(self):
        from dyspider import get_id_from_cmd
        _id = get_id_from_cmd(['--uid', '1234'])
        self.assertEqual(_id, 1234)
        self.assertNotEqual(_id, 123)

    def test_get_id_from_input(self):
        pass
