def clean_text(text):
    """
    清洗文本，去除空格、回车符和特殊符号，保留换行符
    :param text: 原始文本
    :return: 清洗后的文本
    """
    import re
    # 去除所有空格
    cleaned = text.replace(' ', '')
    # 去除所有回车符
    cleaned = cleaned.replace('\r', '')
    # 去除所有特殊符号（只保留字母、数字和换行符）
    cleaned = re.sub(r'[^\w\n]', '', cleaned)
    return cleaned

if __name__ == "__main__":
    # 测试示例
    test_text = "  Hello   World!\nThis is a test.\r\n  With spaces and newlines.  "
    print("原始文本:")
    print(test_text)
    print("\n清洗后:")
    print(clean_text(test_text))