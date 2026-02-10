import unittest
from text_cleaner import clean_text

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

if __name__ == '__main__':
    unittest.main()