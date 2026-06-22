# TW-2014 風力設計基準 第1章 總則
# Clause 1.1 適用範圍
# Clause 1.2 符號說明
# Clause 1.3 專有名詞定義

class WindLoadChapter1:
    """
    第1章總則：定義結構類型與基本參數
    """
    def __init__(self):
        self.structure_types = ['enclosed', 'partially_enclosed', 'open']
        self.symbols = {
            'V': '基本設計風速 (m/s)',
            'p': '設計風壓 (kN/m²)',
            'F': '設計風力 (kN)',
            'C': '用途係數',
            'A': '有效受風面積 (m²)',
            'A_feature': '特徵面積 (m²)'
        }
        self.definitions = {
            'basic_design_wind_speed': '基本設計風速',
            'main_wind_force_resisting_system': '主要風力抵抗系統',
            'components_and_cladding': '局部構件及外部被覆物',
            'open_building': '開放式建築物',
            'partially_enclosed_building': '部分封閉式建築物',
            'enclosed_building': '封閉式建築物',
            'opening': '開口',
            'design_wind_pressure': '設計風壓',
            'design_wind_force': '設計風力',
            'ordinary_building': '普通建築物',
            'flexible_building': '柔性建築物',
            'importance_factor': '用途係數',
            'effective_wind_area': '有效受風面積',
            'characteristic_area': '特徵面積'
        }

    def get_structure_type(self, type_str):
        """根據輸入字串返回結構類型"""
        if type_str in self.structure_types:
            return type_str
        else:
            raise ValueError(f"不支援的結構類型: {type_str}")

    def get_symbol_meaning(self, symbol):
        """返回符號的意義"""
        return self.symbols.get(symbol, "未知符號")

    def get_definition(self, term):
        """返回專有名詞定義"""
        return self.definitions.get(term, "未知術語")
