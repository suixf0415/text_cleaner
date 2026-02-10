import unittest
from text_cleaner import clean_text, extract_phone_numbers


class TestTextCleaner(unittest.TestCase):
    def test_basic_cleaning(self):
        """测试基本清洗功能"""
        text = "  Hello   World!\nThis is a test.  "
        expected = "HelloWorld\nThisisatest"
        self.assertEqual(clean_text(text), expected)

    def test_empty_string(self):
        """测试空字符串"""
        text = ""
        expected = ""
        self.assertEqual(clean_text(text), expected)

    def test_only_spaces(self):
        """测试只有空格的字符串"""
        text = "     "
        expected = ""
        self.assertEqual(clean_text(text), expected)

    def test_only_newlines(self):
        """测试只有换行符的字符串"""
        text = "\n\n\n"
        expected = "\n\n\n"
        self.assertEqual(clean_text(text), expected)

    def test_only_carriage_returns(self):
        """测试只有回车符的字符串"""
        text = "\r\r\r"
        expected = ""
        self.assertEqual(clean_text(text), expected)

    def test_mixed_whitespace(self):
        """测试混合空白字符的字符串"""
        text = " \n \r \n "
        expected = "\n\n"
        self.assertEqual(clean_text(text), expected)

    def test_multiple_spaces(self):
        """测试连续多个空格"""
        text = "Hello   World   Test"
        expected = "HelloWorldTest"
        self.assertEqual(clean_text(text), expected)

    def test_leading_trailing_spaces(self):
        """测试开头和结尾的空格"""
        text = "   Hello World   "
        expected = "HelloWorld"
        self.assertEqual(clean_text(text), expected)

    def test_newline_combinations(self):
        """测试不同类型的换行符组合"""
        text = "Hello\nWorld\r\nTest\rEnd"
        expected = "Hello\nWorld\nTestEnd"
        self.assertEqual(clean_text(text), expected)

    def test_no_whitespace(self):
        """测试不含空白字符的文本"""
        text = "HelloWorld123!@#"
        expected = "HelloWorld123"
        self.assertEqual(clean_text(text), expected)

    def test_complex_mix(self):
        """测试复杂混合场景"""
        text = "  Start\n  Middle   \r\n  End  "
        expected = "Start\nMiddle\nEnd"
        self.assertEqual(clean_text(text), expected)

    def test_special_characters(self):
        """测试特殊符号去除功能"""
        text = "Hello!@#$World%^&*Test()"
        expected = "HelloWorldTest"
        self.assertEqual(clean_text(text), expected)

    def test_mixed_special_chars_and_whitespace(self):
        """测试特殊符号和空白字符的混合场景"""
        text = "  Hello!\n@World#\r$Test%  "
        expected = "Hello\nWorldTest"
        self.assertEqual(clean_text(text), expected)

    def test_none_input(self):
        """测试None输入"""
        with self.assertRaises(TypeError):
            clean_text(None)

    def test_integer_input(self):
        """测试整数输入"""
        with self.assertRaises(TypeError):
            clean_text(123)

    def test_list_input(self):
        """测试列表输入"""
        with self.assertRaises(TypeError):
            clean_text(["a", "b"])

    def test_dict_input(self):
        """测试字典输入"""
        with self.assertRaises(TypeError):
            clean_text({"key": "value"})


class TestPhoneNumberExtraction(unittest.TestCase):
    def test_extract_single_mobile_number(self):
        """测试提取单个手机号码"""
        text = "请联系我，我的手机号是13812345678"
        expected = ["13812345678"]
        self.assertEqual(extract_phone_numbers(text), expected)

    def test_extract_multiple_mobile_numbers(self):
        """测试提取多个手机号码"""
        text = "张三的号码是13812345678，李四的号码是15987654321"
        expected = ["13812345678", "15987654321"]
        self.assertEqual(extract_phone_numbers(text), expected)

    def test_extract_landline_with_hyphen(self):
        """测试提取带横杠的座机号码"""
        text = "公司电话：010-12345678"
        expected = ["010-12345678"]
        self.assertEqual(extract_phone_numbers(text), expected)

    def test_extract_landline_without_hyphen(self):
        """测试提取不带横杠的座机号码"""
        text = "联系电话：02187654321"
        expected = ["02187654321"]
        self.assertEqual(extract_phone_numbers(text), expected)

    def test_extract_phone_with_spaces(self):
        """测试提取带空格的电话号码"""
        text = "手机：138 1234 5678"
        expected = ["138 1234 5678"]
        self.assertEqual(extract_phone_numbers(text), expected)

    def test_extract_phone_with_country_code(self):
        """测试提取带国际区号的电话号码"""
        text = "国际号码：+86 138 1234 5678"
        expected = ["+86 138 1234 5678"]
        self.assertEqual(extract_phone_numbers(text), expected)

    def test_extract_phone_with_parentheses(self):
        """测试提取带括号的电话号码"""
        text = "电话：(010)12345678"
        expected = ["(010)12345678"]
        self.assertEqual(extract_phone_numbers(text), expected)

    def test_extract_mixed_formats(self):
        """测试提取混合格式的电话号码"""
        text = "手机13812345678，座机010-12345678，国际+86-159-8765-4321"
        expected = ["13812345678", "010-12345678", "+86-159-8765-4321"]
        self.assertEqual(extract_phone_numbers(text), expected)

    def test_no_phone_numbers(self):
        """测试无电话号码的文本"""
        text = "这段文本里没有电话号码，只有一些数字123和456"
        expected = []
        self.assertEqual(extract_phone_numbers(text), expected)

    def test_empty_string(self):
        """测试空字符串"""
        text = ""
        expected = []
        self.assertEqual(extract_phone_numbers(text), expected)

    def test_invalid_phone_numbers(self):
        """测试过滤无效的电话号码（位数不对）"""
        text = "这些不是电话：123, 12345, 123456789012345"
        expected = []
        self.assertEqual(extract_phone_numbers(text), expected)

    def test_phone_at_start_and_end(self):
        """测试开头和结尾的电话号码"""
        text = "13812345678是开头，结尾是15987654321"
        expected = ["13812345678", "15987654321"]
        self.assertEqual(extract_phone_numbers(text), expected)

    def test_phone_with_extension(self):
        """测试带分机号的电话"""
        text = "总机：010-12345678-8001"
        expected = ["010-12345678-8001"]
        self.assertEqual(extract_phone_numbers(text), expected)

    def test_none_input(self):
        """测试None输入"""
        with self.assertRaises(TypeError):
            extract_phone_numbers(None)

    def test_integer_input(self):
        """测试整数输入"""
        with self.assertRaises(TypeError):
            extract_phone_numbers(123)


if __name__ == "__main__":
    unittest.main()
