# TW-2014 풍하중 1장 총칙
# Clause 1.1: 適用範圍
# Clause 1.2: 符號說明
# Clause 1.3: 專有名詞定義

class WindLoadChapter1:
    """
    處理風力計算總則，定義結構物分類與基本參數。
    """
    def __init__(self):
        self.building_types = {
            'enclosed': '封閉式建築物',
            'partially_enclosed': '部分封閉式建築物',
            'open': '開放式建築物'
        }
        self.structure_types = ['建築物', '地上獨立結構物']
        self.definitions = {
            'basic_design_wind_speed': '基本設計風速',
            'MWFRS': '主要風力抵抗系統',
            'components_cladding': '局部構件及外部被覆物',
            'opening': '開口',
            'design_wind_pressure': '設計風壓',
            'design_wind_force': '設計風力',
            'ordinary_building': '普通建築物',
            'flexible_building': '柔性建築物',
            'importance_factor': '用途係數',
            'effective_wind_area': '有效受風面積',
            'characteristic_area': '特徵面積'
        }

    def classify_building(self, opening_ratio):
        """
        根據開口比例分類建築物類型。
        :param opening_ratio: 開口面積佔外牆面積比例
        :return: 建築物類型字串
        """
        if opening_ratio < 0.05:
            return self.building_types['enclosed']
        elif opening_ratio < 0.3:
            return self.building_types['partially_enclosed']
        else:
            return self.building_types['open']

    def get_definition(self, term):
        """
        取得專有名詞定義。
        :param term: 專有名詞鍵值
        :return: 定義字串
        """
        return self.definitions.get(term, '未定義')
