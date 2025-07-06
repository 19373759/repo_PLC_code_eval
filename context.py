class CommonContext:
    def __init__(self):
        # 私有属性：需求描述（string类型）
        self.requirement = ""
        
        # 私有属性：已知的数据结构（字典类型，可存储任意结构）
        self.data_structure = {}
        self.modules = {}
        self.title = ""

    def set_requirement(self, requirement: str) -> None:
        """设置需求描述"""
        if not isinstance(requirement, str):
            raise TypeError("需求描述必须是字符串类型")
        self.requirement = requirement

    def set_data_structure(self, data: dict) -> None:
        """设置数据结构"""
        if not isinstance(data, dict):
            raise TypeError("数据结构必须是字典类型")
        self.data_structure = data

    def __str__(self) -> str:
        """对象字符串表示"""
        return (f"DataStructureManager(\n"
                f"  requirement='{self.requirement}',\n"
                f"  data_structure={self.data_structure}\n"
                f")")
