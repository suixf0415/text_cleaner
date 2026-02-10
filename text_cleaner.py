def clean_text(text):
    """
    清洗文本，去除空格、回车符和特殊符号，保留换行符
    :param text: 原始文本或文本列表
    :return: 清洗后的文本或文本列表
    """
    import re

    if isinstance(text, list):
        # 批量处理文本列表
        return [clean_text(item) for item in text]
    elif not isinstance(text, str):
        raise TypeError(f"Expected str or list, got {type(text).__name__}")
    # 去除所有空格
    cleaned = text.replace(" ", "")
    # 去除所有回车符
    cleaned = cleaned.replace("\r", "")
    # 去除所有特殊符号（只保留字母、数字和换行符）
    cleaned = re.sub(r"[^\w\n]", "", cleaned)
    return cleaned


def extract_phone_numbers(text):
    """
    从文本中提取电话号码
    支持格式：
    - 11位手机号（如：13812345678）
    - 带横杠的座机号（如：010-12345678）
    - 不带横杠的座机号（如：02187654321）
    - 带空格的手机号（如：138 1234 5678）
    - 带国际区号的手机号（如：+86 138 1234 5678 或 +86-159-8765-4321）
    - 带括号的座机号（如：(010)12345678）
    - 带分机号的座机号（如：010-12345678-8001）
    :param text: 原始文本或文本列表
    :return: 电话号码列表或电话号码列表的列表
    """
    import re

    if isinstance(text, list):
        # 批量处理文本列表
        return [extract_phone_numbers(item) for item in text]
    elif not isinstance(text, str):
        raise TypeError(f"Expected str or list, got {type(text).__name__}")

    phone_numbers = []

    # 定义多种电话号码格式的正则表达式
    patterns = [
        r"\+86\s?\d{3}\s?\d{4}\s?\d{4}",  # 带国际区号和空格的手机号：+86 138 1234 5678
        r"\+86-\d{3}-\d{4}-\d{4}",         # 带国际区号和横杠的手机号：+86-159-8765-4321
        r"1\d{2}\s\d{4}\s\d{4}",          # 带空格的手机号：138 1234 5678
        r"0\d{2,3}-\d{7,8}-\d{1,4}",        # 带分机号的座机号：010-12345678-8001
        r"0\d{2,3}-\d{7,8}",                # 带横杠的座机号：010-12345678 或 0571-12345678
        r"\(0\d{2,3}\)\d{7,8}",             # 带括号的座机号：(010)12345678
        r"0\d{9,10}",                         # 不带横杠的座机号：02187654321
        r"1\d{10}"                            # 普通手机号：13812345678
    ]

    # 用于记录已匹配的位置，避免重复匹配
    matched_positions = set()

    for pattern in patterns:
        for match in re.finditer(pattern, text):
            start, end = match.span()
            # 检查是否与已匹配的位置重叠
            if not any(start < pos_end and end > pos_start for pos_start, pos_end in matched_positions):
                phone_numbers.append((start, match.group()))
                matched_positions.add((start, end))

    # 验证电话号码有效性并过滤
    def is_valid_phone(phone):
        # 移除非数字字符（保留国际区号和分隔符）
        digits = re.sub(r"[^\d+]", "", phone)
        
        # 检查长度
        if len(digits) < 11 or len(digits) > 15:
            return False
        
        # 检查手机号号段
        if phone.startswith("1") and len(re.sub(r"\D", "", phone)) == 11:
            # 中国大陆手机号号段
            valid_prefixes = ["13", "14", "15", "16", "17", "18", "19"]
            return any(phone.startswith(prefix) for prefix in valid_prefixes)
        
        # 其他格式的电话号码（座机、带国际区号等）
        return True

    # 按出现位置排序并返回有效电话号码
    phone_numbers.sort(key=lambda x: x[0])
    valid_phones = [phone for _, phone in phone_numbers if is_valid_phone(phone)]
    return valid_phones


def extract_emails(text):
    """
    从文本中提取邮箱地址
    :param text: 原始文本或文本列表
    :return: 邮箱地址列表或邮箱地址列表的列表
    """
    import re

    if isinstance(text, list):
        # 批量处理文本列表
        return [extract_emails(item) for item in text]
    elif not isinstance(text, str):
        raise TypeError(f"Expected str or list, got {type(text).__name__}")

    # 邮箱正则表达式
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    
    # 查找所有匹配的邮箱
    emails = re.findall(email_pattern, text)
    return emails


def extract_urls(text):
    """
    从文本中提取URL地址
    :param text: 原始文本或文本列表
    :return: URL地址列表或URL地址列表的列表
    """
    import re

    if isinstance(text, list):
        # 批量处理文本列表
        return [extract_urls(item) for item in text]
    elif not isinstance(text, str):
        raise TypeError(f"Expected str or list, got {type(text).__name__}")

    # URL正则表达式
    url_pattern = r"https?://[\w\-]+(\.[\w\-]+)+([\w\-.,@?^=%&:/~+#]*[\w\-@?^=%&/~+#])?"
    
    # 查找所有匹配的URL
    urls = []
    for match in re.finditer(url_pattern, text):
        urls.append(match.group())
    
    return urls


if __name__ == "__main__":
    # 测试示例
    test_text = "  Hello   World!\nThis is a test.\r\n  With spaces and newlines.  "
    print("原始文本:")
    print(test_text)
    print("\n清洗后:")
    print(clean_text(test_text))
