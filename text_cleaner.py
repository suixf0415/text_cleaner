def clean_text(text):
    """
    清洗文本，去除空格、回车符和特殊符号，保留换行符
    :param text: 原始文本
    :return: 清洗后的文本
    """
    import re

    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")
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
    :param text: 原始文本
    :return: 电话号码列表
    """
    import re

    phone_numbers = []

    # 定义多种电话号码格式的正则表达式
    patterns = [
        r"1\d{2}\s\d{4}\s\d{4}",  # 带空格的手机号：138 1234 5678
        r"0\d{2,3}-\d{7,8}",       # 带横杠的座机号：010-12345678 或 0571-12345678
        r"0\d{9,10}",              # 不带横杠的座机号：02187654321
        r"1\d{10}"                 # 普通手机号：13812345678
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

    # 按出现位置排序并返回
    phone_numbers.sort(key=lambda x: x[0])
    return [phone for _, phone in phone_numbers]


if __name__ == "__main__":
    # 测试示例
    test_text = "  Hello   World!\nThis is a test.\r\n  With spaces and newlines.  "
    print("原始文本:")
    print(test_text)
    print("\n清洗后:")
    print(clean_text(test_text))
