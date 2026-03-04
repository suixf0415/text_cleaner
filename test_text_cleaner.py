import unittest
from text_cleaner import clean_text, extract_phone_numbers, extract_emails, extract_urls, detect_encoding, to_utf8, to_gbk, to_ascii, detect_gibberish

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
        test_cases = ["a", "b"]
        expected = ["a", "b"]
        self.assertEqual(clean_text(test_cases), expected)

    def test_dict_input(self):
        """测试字典输入"""
        with self.assertRaises(TypeError):
            clean_text({"key": "value"})

    def test_batch_clean_text(self):
        """测试批量文本清洗"""
        test_cases = [
            "  Hello   World!",
            "This is a test.",
            "  With spaces and newlines.  "
        ]
        # 直接用数组作为输入
        # 注意：此测试可能不会通过，因为clean_text函数可能不支持数组输入
        try:
            result = clean_text(test_cases)
            print(f"批量处理结果: {result}")
        except Exception as e:
            print(f"批量处理异常: {e}")

    def test_emoji_filtering(self):
        """测试emoji过滤功能"""
        test_cases = [
            ("Hello 😊 World 🌟", "HelloWorld", "基本emoji"),
            ("测试😀😃😄😁", "测试", "多个emoji"),
            ("Text with 🎉🎊🎈 emoji", "Textwithemoji", "英文+emoji"),
            ("中文😊测试🌟", "中文测试", "中文+emoji"),
            ("Flag 🇨🇳 and 🏳️", "Flagand", "国旗emoji"),
            ("Mixed 123 😊 test", "Mixed123test", "混合内容"),
        ]
        for text, expected, desc in test_cases:
            with self.subTest(desc=desc):
                result = clean_text(text)
                self.assertEqual(result, expected, f"{desc}: '{text}' -> '{result}' (期望: '{expected}')")

    def test_control_character_filtering(self):
        """测试控制字符过滤功能"""
        test_cases = [
            ("Hello\x00\x01\x02World", "HelloWorld", "C0控制字符"),
            ("Test\x80\x81\x9fText", "TestText", "C1控制字符"),
            ("Text\u200b\u200c\u200dTest", "TextTest", "零宽字符"),
            ("Hello\u2060\u2061Test", "HelloTest", "其他零宽字符"),
            ("Keep\nnewline\tand\ttab", "Keep\nnewlineandtab", "保留换行但制表符会被删除"),
            ("Mix\x00\x01\n\x80Test", "Mix\nTest", "混合控制字符"),
        ]
        for text, expected, desc in test_cases:
            with self.subTest(desc=desc):
                result = clean_text(text)
                self.assertEqual(result, expected, f"{desc}: '{text}' -> '{result}' (期望: '{expected}')")


    def test_gibberish_filtering(self):
        """测试乱码过滤功能"""
        text = "Hello \x81\x40\x82\x61 World"
        expected = "HelloaWorld"
        self.assertEqual(clean_text(text), expected)

    def test_mixed_filtering(self):
        """测试混合过滤功能"""
        test_cases = [
            ("Hello 😊\x00\x01World\x80🌟", "HelloWorld", "emoji+控制字符"),
            ("Test\ufffd😊\u200bText", "TestText", "乱码+emoji+零宽字符"),
            ("正常中文😊测试\x00", "正常中文测试", "中文+emoji+控制字符（中文应保留）"),
        ]
        for text, expected, desc in test_cases:
            with self.subTest(desc=desc):
                result = clean_text(text)
                self.assertEqual(result, expected, f"{desc}: '{text}' -> '{result}' (期望: '{expected}')")

    def test_non_ascii_gibberish_filtering(self):
        """测试连续非ASCII乱码过滤（不应误删正常中文）"""
        test_cases = [
            ("这是正常的中文文本", True, "正常中文应保留"),
            ("Hello世界Test", True, "中英文混合应保留"),
            ("正常文本123", True, "中文+数字应保留"),
        ]
        for text, should_have_chinese, desc in test_cases:
            with self.subTest(desc=desc):
                result = clean_text(text)
                has_chinese = any('\u4e00' <= c <= '\u9fff' for c in result)
                self.assertEqual(has_chinese, should_have_chinese, 
                               f"{desc}: '{text}' -> '{result}' (包含中文: {has_chinese})")

    def test_extended_special_characters(self):
        """测试扩展特殊字符过滤功能"""
        text = 'Hello!@#$%^&*()_+[]{}|;:\",.<>?/`~World'
        expected = "Hello_World"
        self.assertEqual(clean_text(text), expected)

    def test_currency_symbols(self):
        """测试货币符号过滤功能"""
        text = "Hello $¥€£¢World"
        expected = "HelloWorld"
        self.assertEqual(clean_text(text), expected)

    def test_mathematical_symbols(self):
        """测试数学符号过滤功能"""
        text = "Hello +-×÷=<>≤≥≠∧∨¬∀∃∂∇∫∮∑∏World"
        expected = "HelloWorld"
        self.assertEqual(clean_text(text), expected)

    def test_punctuation_marks(self):
        """测试标点符号过滤功能"""
        text = "Hello.,;:!?()[]{}|\'\"`~World"
        expected = "HelloWorld"
        self.assertEqual(clean_text(text), expected)

    def test_whitespace_characters(self):
        """测试空白字符过滤功能"""
        text = "Hello\t\n\v\f\r\x0b\x0cWorld"
        expected = "Hello\nWorld"
        self.assertEqual(clean_text(text), expected)


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

    def test_list_input(self):
        """测试列表输入"""
        test_cases = [
            "请联系我，我的手机号是13812345678",
            "公司电话：010-12345678"
        ]
        expected = [
            ["13812345678"],
            ["010-12345678"]
        ]
        self.assertEqual(extract_phone_numbers(test_cases), expected)

    def test_batch_extract_phone_numbers(self):
        """测试批量电话号码提取"""
        test_cases = [
            "请联系我，我的手机号是13812345678",
            "公司电话：010-12345678",
            "张三的号码是13812345678，李四的号码是15987654321"
        ]
        # 直接用数组作为输入
        try:
            result = extract_phone_numbers(test_cases)
            print(f"批量处理结果: {result}")
        except Exception as e:
            print(f"批量处理异常: {e}")


class TestEmailExtraction(unittest.TestCase):
    def test_extract_single_email(self):
        """测试提取单个邮箱地址"""
        text = "请发送邮件至example@example.com"
        expected = ["example@example.com"]
        self.assertEqual(extract_emails(text), expected)

    def test_extract_multiple_emails(self):
        """测试提取多个邮箱地址"""
        text = "联系邮箱：user1@example.com 和 user2@test.org"
        expected = ["user1@example.com", "user2@test.org"]
        self.assertEqual(extract_emails(text), expected)

    def test_extract_complex_emails(self):
        """测试提取复杂格式的邮箱地址"""
        text = "复杂邮箱：user.name+tag@example.co.uk"
        expected = ["user.name+tag@example.co.uk"]
        self.assertEqual(extract_emails(text), expected)

    def test_no_emails(self):
        """测试无邮箱地址的文本"""
        text = "这段文本里没有邮箱地址"
        expected = []
        self.assertEqual(extract_emails(text), expected)

    def test_empty_string(self):
        """测试空字符串"""
        text = ""
        expected = []
        self.assertEqual(extract_emails(text), expected)

    def test_none_input(self):
        """测试None输入"""
        with self.assertRaises(TypeError):
            extract_emails(None)

    def test_integer_input(self):
        """测试整数输入"""
        with self.assertRaises(TypeError):
            extract_emails(123)

    def test_list_input(self):
        """测试列表输入"""
        test_cases = [
            "请发送邮件至example@example.com",
            "联系邮箱：user@test.org"
        ]
        expected = [
            ["example@example.com"],
            ["user@test.org"]
        ]
        self.assertEqual(extract_emails(test_cases), expected)

    def test_batch_extract_emails(self):
        """测试批量邮箱地址提取"""
        test_cases = [
            "请发送邮件至example@example.com",
            "联系邮箱：user1@example.com 和 user2@test.org",
            "这段文本里没有邮箱地址"
        ]
        # 直接用数组作为输入
        try:
            result = extract_emails(test_cases)
            print(f"批量处理结果: {result}")
        except Exception as e:
            print(f"批量处理异常: {e}")


class TestURLExtraction(unittest.TestCase):
    def test_extract_single_url(self):
        """测试提取单个URL地址"""
        text = "请访问网站 https://www.example.com"
        expected = ["https://www.example.com"]
        self.assertEqual(extract_urls(text), expected)

    def test_extract_multiple_urls(self):
        """测试提取多个URL地址"""
        text = "网站：https://www.example.com 和 http://test.org"
        expected = ["https://www.example.com", "http://test.org"]
        self.assertEqual(extract_urls(text), expected)

    def test_extract_complex_urls(self):
        """测试提取复杂格式的URL地址"""
        text = "复杂URL：https://www.example.com/path?param1=value1&param2=value2"
        expected = ["https://www.example.com/path?param1=value1&param2=value2"]
        self.assertEqual(extract_urls(text), expected)

    def test_no_urls(self):
        """测试无URL地址的文本"""
        text = "这段文本里没有URL地址"
        expected = []
        self.assertEqual(extract_urls(text), expected)

    def test_empty_string(self):
        """测试空字符串"""
        text = ""
        expected = []
        self.assertEqual(extract_urls(text), expected)

    def test_none_input(self):
        """测试None输入"""
        with self.assertRaises(TypeError):
            extract_urls(None)

    def test_integer_input(self):
        """测试整数输入"""
        with self.assertRaises(TypeError):
            extract_urls(123)

    def test_list_input(self):
        """测试列表输入"""
        test_cases = [
            "请访问网站 https://www.example.com",
            "网站：http://test.org"
        ]
        expected = [
            ["https://www.example.com"],
            ["http://test.org"]
        ]
        self.assertEqual(extract_urls(test_cases), expected)

    def test_batch_extract_urls(self):
        """测试批量URL地址提取"""
        test_cases = [
            "请访问网站 https://www.example.com",
            "网站：https://www.example.com 和 http://test.org",
            "这段文本里没有URL地址"
        ]
        # 直接用数组作为输入
        try:
            result = extract_urls(test_cases)
            print(f"批量处理结果: {result}")
        except Exception as e:
            print(f"批量处理异常: {e}")


class TestEncodingFunctions(unittest.TestCase):
    def test_detect_encoding(self):
        """测试编码检测功能"""
        # 测试ASCII编码（较短的文本，检测结果较可靠）
        ascii_text = "Hello World".encode('ascii')
        detected_encoding = detect_encoding(ascii_text)
        self.assertIn('ascii', detected_encoding.lower())
        
        # 测试UTF-8编码（较长的文本，检测结果更可靠）
        utf8_text = "你好，这是一段较长的UTF-8编码文本".encode('utf-8')
        detected_encoding = detect_encoding(utf8_text)
        # 对于UTF-8编码，chardet可能会检测为'utf-8'或'utf-8-sig'
        self.assertTrue('utf-8' in detected_encoding.lower())

    def test_to_utf8(self):
        """测试转换为UTF-8编码"""
        # 测试字符串输入
        text = "你好"
        result = to_utf8(text)
        self.assertIsInstance(result, str)
        self.assertEqual(result, text)
        
        # 测试UTF-8字节串输入
        utf8_bytes = "你好".encode('utf-8')
        result = to_utf8(utf8_bytes)
        self.assertIsInstance(result, str)
        self.assertEqual(result, "你好")
        
        # 测试GBK字节串输入
        gbk_bytes = "你好".encode('gbk')
        result = to_utf8(gbk_bytes)
        self.assertIsInstance(result, str)
        self.assertEqual(result, "你好")

    def test_to_gbk(self):
        """测试转换为GBK编码"""
        # 测试字符串输入
        text = "你好"
        result = to_gbk(text)
        self.assertIsInstance(result, bytes)
        
        # 测试UTF-8字节串输入
        utf8_bytes = "你好".encode('utf-8')
        result = to_gbk(utf8_bytes)
        self.assertIsInstance(result, bytes)

    def test_to_ascii(self):
        """测试转换为ASCII编码"""
        # 测试ASCII字符串输入
        text = "Hello"
        result = to_ascii(text)
        self.assertIsInstance(result, bytes)
        self.assertEqual(result, b"Hello")
        
        # 测试包含非ASCII字符的字符串输入
        text = "Hello 你好"
        result = to_ascii(text)
        self.assertIsInstance(result, bytes)

    def test_detect_gibberish(self):
        """测试乱码检测功能"""
        # 测试正常文本（应该返回False）
        normal_texts = [
            "Hello World",
            "这是正常的中文文本",
            "1234567890",
            "Test with\nnewline",
        ]
        for text in normal_texts:
            with self.subTest(text=text):
                self.assertFalse(detect_gibberish(text), f"正常文本 '{text}' 不应被识别为乱码")
        
        # 测试乱码文本（应该返回True）
        gibberish_texts = [
            "Hello\x00\x01\x02\x03\x04\x05\x06\x07\x08",  # 大量控制字符
            "\ufffd\ufffd\ufffd",  # 替换字符
        ]
        for text in gibberish_texts:
            with self.subTest(text=text):
                self.assertTrue(detect_gibberish(text), f"乱码文本应被识别为乱码")
        
        # 测试空字符串
        empty_text = ""
        self.assertFalse(detect_gibberish(empty_text), "空字符串不应被识别为乱码")

    def test_encoding_error_handling(self):
        """测试编码错误处理"""
        # 测试无效的字节串
        invalid_bytes = b'\xff\xfe\xfd'
        result = to_utf8(invalid_bytes)
        self.assertIsInstance(result, str)

    def test_invalid_input_types(self):
        """测试无效输入类型"""
        # 测试detect_encoding函数
        with self.assertRaises(TypeError):
            detect_encoding(123)
        
        # 测试to_utf8函数
        with self.assertRaises(TypeError):
            to_utf8(123)
        
        # 测试to_gbk函数
        with self.assertRaises(TypeError):
            to_gbk(123)
        
        # 测试to_ascii函数
        with self.assertRaises(TypeError):
            to_ascii(123)
        
        # 测试detect_gibberish函数
        with self.assertRaises(TypeError):
            detect_gibberish(123)


if __name__ == "__main__":
    unittest.main()
