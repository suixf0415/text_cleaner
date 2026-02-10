def clean_text(text):
    """
    清洗文本，去除空格、回车符、特殊符号、emoji、乱码和控制字符，保留换行符
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
    # 去除emoji表情
    cleaned = re.sub(r'[\U00010000-\U0010ffff]', '', cleaned, flags=re.UNICODE)
    # 去除控制字符（除了换行符）
    cleaned = re.sub(r'[\x00-\x09\x0b\x0c\x0e-\x1f\x7f]', '', cleaned)
    # 去除乱码字符（包括连续的非ASCII字符和无效字符）
    cleaned = re.sub(r'[\x80-\xff]+', '', cleaned)
    # 去除连续的相同字符（可能是乱码）
    cleaned = re.sub(r'(.)\1{3,}', '', cleaned)
    # 去除所有特殊符号（只保留字母、数字和换行符）
    cleaned = re.sub(r"[^\w\n]", "", cleaned)
    # 检测并处理乱码
    if detect_gibberish(cleaned):
        # 如果是乱码，尝试用不同编码解码
        try:
            cleaned = cleaned.encode('utf-8', errors='replace').decode('utf-8')
            # 再次去除特殊符号
            cleaned = re.sub(r"[^\w\n]", "", cleaned)
        except:
            pass
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


def detect_encoding(data):
    """
    检测数据的编码
    :param data: 字节串
    :return: 编码名称
    """
    import chardet
    
    if not isinstance(data, bytes):
        raise TypeError(f"Expected bytes, got {type(data).__name__}")
    
    result = chardet.detect(data)
    return result['encoding']


def to_utf8(data):
    """
    转换为UTF-8编码
    :param data: 字符串或字节串
    :return: UTF-8字符串
    """
    if isinstance(data, str):
        return data
    elif isinstance(data, bytes):
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return data.decode('gbk')
            except UnicodeDecodeError:
                return data.decode('utf-8', errors='replace')
    else:
        raise TypeError(f"Expected str or bytes, got {type(data).__name__}")


def to_gbk(data):
    """
    转换为GBK编码
    :param data: 字符串或字节串
    :return: GBK字节串
    """
    if isinstance(data, str):
        return data.encode('gbk', errors='replace')
    elif isinstance(data, bytes):
        try:
            return data.decode('utf-8').encode('gbk', errors='replace')
        except UnicodeDecodeError:
            try:
                return data.decode('gbk').encode('gbk', errors='replace')
            except UnicodeDecodeError:
                return data
    else:
        raise TypeError(f"Expected str or bytes, got {type(data).__name__}")


def to_ascii(data):
    """
    转换为ASCII编码
    :param data: 字符串或字节串
    :return: ASCII字节串
    """
    if isinstance(data, str):
        return data.encode('ascii', errors='replace')
    elif isinstance(data, bytes):
        try:
            return data.decode('utf-8').encode('ascii', errors='replace')
        except UnicodeDecodeError:
            try:
                return data.decode('gbk').encode('ascii', errors='replace')
            except UnicodeDecodeError:
                return data
    else:
        raise TypeError(f"Expected str or bytes, got {type(data).__name__}")


def detect_gibberish(text):
    """
    检测乱码
    :param text: 字符串
    :return: 是否为乱码
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")
    
    if not text:
        return False
    
    # 统计非ASCII字符比例
    non_ascii_count = sum(1 for c in text if ord(c) > 127)
    total_count = len(text)
    
    # 统计不可打印字符比例
    unprintable_count = sum(1 for c in text if not c.isprintable() and c not in '\n\t\r')
    
    # 简单判断：如果不可打印字符比例过高，或者非ASCII字符比例过高但不是有效的UTF-8
    if unprintable_count / total_count > 0.3:
        return True
    
    # 尝试用不同编码解码，看是否能得到有意义的文本
    try:
        # 尝试用UTF-8解码
        text.encode('utf-8').decode('utf-8')
    except:
        return True
    
    return False


