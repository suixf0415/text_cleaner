# 文本清洗工具

一个简单的文本清洗工具，用于去除文本中的空格和换行符。

## 功能

- 去除文本中的所有空格
- 去除文本中的所有换行符（\n）
- 去除文本中的所有回车符（\r）

## 使用方法

### 直接运行测试

```bash
python text_cleaner.py
```

### 在其他项目中导入使用

```python
from text_cleaner import clean_text

text = "  Hello   World!\nThis is a test.  "
cleaned_text = clean_text(text)
print(cleaned_text)  # 输出: HelloWorld!Thisisatest.
```

## 函数说明

### `clean_text(text)`

- **参数**: `text` - 原始文本字符串
- **返回值**: 清洗后的文本字符串
- **功能**: 去除文本中的所有空格、换行符和回车符

## 示例

```python
# 输入
text = "  Hello   World!\nThis is a test.\r\n  With spaces and newlines.  "

# 输出
"HelloWorld!Thisisatest.Withspacesandnewlines."
```