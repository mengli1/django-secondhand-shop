# 自注册定义的路径转换器
class ActiveConverter:
    regex = '[\w.-]+'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)

