import re
import unicodedata


# Emoji / pictograph patterns are intentionally broader than a single Unicode plane.
# This helps handle:
# - BMP emoji-like symbols (e.g. ☀, ✈, ❤)
# - variation selectors (FE0F) and keycap / tag sequences
# - ZWJ-based emoji sequences
_EMOJI_RE = re.compile(
    "["  # a single-codepoint coarse filter (we also strip joiners/selectors below)
    "\U0001F1E6-\U0001F1FF"  # flags (regional indicators)
    "\U0001F300-\U0001F5FF"  # misc symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F700-\U0001F77F"  # alchemical
    "\U0001F780-\U0001F7FF"  # geometric extended
    "\U0001F800-\U0001F8FF"  # arrows-C
    "\U0001F900-\U0001F9FF"  # supplemental symbols & pictographs
    "\U0001FA00-\U0001FAFF"  # symbols & pictographs extended-A
    "\U00002700-\U000027BF"  # dingbats
    "\U00002600-\U000026FF"  # misc symbols (BMP)
    "\U00002300-\U000023FF"  # misc technical (some are emoji-presented)
    "\U00002190-\U000021FF"  # arrows (some are emoji-presented)
    "\u24C2"                  # circled M (often emoji-presented)
    "\u25AA-\u25AB"            # small squares
    "\u25B6"                   # play
    "\u25C0"                   # reverse play
    "\u25FB-\u25FE"            # medium squares
    "\u2B00-\u2BFF"             # misc symbols & arrows
    "\u3030"                   # wavy dash
    "\u303D"                   # part alternation mark
    "\u3297"                   # circled ideograph congratulation
    "\u3299"                   # circled ideograph secret
    "\u00A9"                   # copyright
    "\u00AE"                   # registered
    "\u2122"                   # trademark
    "]",
    flags=re.UNICODE,
)

# Characters that frequently participate in emoji sequences but are not covered by plane-based ranges.
_EMOJI_SEQUENCE_PARTS_RE = re.compile(
    "[\u200d\uFE0E\uFE0F\u20E3]",  # ZWJ, variation selectors, keycap combiner
    flags=re.UNICODE,
)

# Typical mojibake markers when UTF-8 is decoded as Latin-1 / Windows-1252.
_MOJIBAKE_MARKERS_RE = re.compile(r"[ÃÂâ�]", flags=re.UNICODE)
# Runs of Latin-1 supplement chars (often show up as garbage when mis-decoded).
_LATIN1_RUN_RE = re.compile(r"[\u00A0-\u00FF]{3,}", flags=re.UNICODE)


def _strip_unicode_controls(text: str) -> str:
    """
    Remove Unicode control/format/surrogate/private/unassigned characters,
    but keep '\n' (newline) as a structural delimiter.
    """
    out = []
    for ch in text:
        if ch == "\n":
            out.append(ch)
            continue
        cat = unicodedata.category(ch)
        # Cc: control, Cf: format (includes many zero-width chars), Cs: surrogate, Co: private use, Cn: unassigned
        if cat[0] == "C":
            continue
        out.append(ch)
    return "".join(out)


def _strip_emoji(text: str) -> str:
    # First remove broad emoji-like codepoints, then remove sequence glue (ZWJ/VS/keycap combiner).
    text = _EMOJI_RE.sub("", text)
    text = _EMOJI_SEQUENCE_PARTS_RE.sub("", text)
    return text


def _strip_mojibake_runs(text: str) -> str:
    """
    Heuristic removal of obvious mojibake (garbled text) while avoiding deleting normal CJK.
    - Always remove the replacement character U+FFFD.
    - Remove Latin-1 runs when they contain typical mojibake markers (Ã, Â, â, �).
    """
    if not text:
        return text

    # Always drop explicit replacement characters.
    text = text.replace("\ufffd", "")

    def _maybe_drop(match: re.Match) -> str:
        chunk = match.group(0)
        return "" if _MOJIBAKE_MARKERS_RE.search(chunk) else chunk

    return _LATIN1_RUN_RE.sub(_maybe_drop, text)


def clean_text(text):
    """
    清洗文本，去除空格、回车符、特殊符号、emoji、乱码和控制字符，保留换行符
    :param text: 原始文本或文本列表
    :return: 清洗后的文本或文本列表
    """

    if isinstance(text, list):
        # 批量处理文本列表
        return [clean_text(item) for item in text]
    elif not isinstance(text, str):
        raise TypeError(f"Expected str or list, got {type(text).__name__}")
    # Normalize newlines: convert CRLF/CR to LF, but keep LF.
    cleaned = text.replace("\r\n", "\n").replace("\r", "")
    # Remove all ASCII spaces (existing behavior); keep '\n'.
    cleaned = cleaned.replace(" ", "")

    # Strip emoji/pictographs comprehensively (incl. BMP + sequences).
    cleaned = _strip_emoji(cleaned)
    # Strip Unicode control/format chars (incl. C0/C1, zero-width, etc.), but keep '\n'.
    cleaned = _strip_unicode_controls(cleaned)
    # Strip obvious mojibake runs and replacement chars.
    cleaned = _strip_mojibake_runs(cleaned)

    # Remove long repeats (potential garbage)
    cleaned = re.sub(r"(.)\1{3,}", "", cleaned)
    # Remove all special symbols (keep letters/digits/underscore + newline)
    cleaned = re.sub(r"[^\w\n]", "", cleaned)

    # Detect and handle remaining gibberish
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
    
    # 统计不可打印字符比例（把明显的替换字符也算进去）
    unprintable_count = sum(
        1 for c in text
        if (not c.isprintable() and c not in "\n\t\r") or c == "\ufffd"
    )
    
    # 简单判断：如果不可打印字符比例过高，或者非ASCII字符比例过高但不是有效的UTF-8
    if unprintable_count / total_count > 0.3:
        return True
    
    # 尝试用不同编码解码，看是否能得到有意义的文本
    try:
        # 尝试用UTF-8解码
        text.encode('utf-8').decode('utf-8')
    except:
        return True
    
    # 如果包含明显的 mojibake 标记且比例较高，也认为是乱码
    marker_count = sum(1 for c in text if c in "ÃÂâ�")
    if marker_count / total_count > 0.1 and total_count >= 10:
        return True

    return False


