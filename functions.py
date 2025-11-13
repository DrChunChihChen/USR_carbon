"""
南投永續之旅碳足跡計算器核心功能模組
包含南投國姓旅遊路線資料、碳足跡計算和環保建議生成等功能
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import json

# 台灣環境部官方碳排放係數
TAIWAN_EMISSION_FACTORS = {
    'transportation': {
        'car_petrol': 0.115,      # kg CO2e/km (自用小客車汽油)
        'motorcycle': 0.0951,     # kg CO2e/km (機車)
        'high_speed_rail': 0.032, # kg CO2e/km (高鐵)
        'train': 0.06,           # kg CO2e/km (台鐵)
        'bus': 0.04,             # kg CO2e/km (公車/客運)
    },
    'dining': {
        'local_meat': 3.0,        # kg CO2e/餐 (在地客家料理含肉類)
        'local_vegetarian': 1.0,  # kg CO2e/餐 (在地蔬食餐)
        'light_meal': 1.5,        # kg CO2e/餐 (輕食簡餐)
        'self_prepared': 0.5,     # kg CO2e/餐 (自備餐點)
    },
    'coffee': {
        'black_coffee': 0.1,      # kg CO2e/杯 (黑咖啡)
        'latte_cappuccino': 1.0,  # kg CO2e/杯 (拿鐵/卡布奇諾)
        'no_coffee': 0.0,         # kg CO2e/杯 (不喝咖啡)
    }
}

# 預設南投國姓旅遊路線資料
NANTOU_ROUTES = {
    'route_a': {
        'id': 'route_a',
        'name': '歷史遺產與咖啡鑑賞家之旅',
        'description': '探索國姓的歷史文化與咖啡產業，感受時光流轉中的人文風情',
        'internal_distance': 25,  # 路線內移動總公里數
        'walking_distance': 1.5,  # 步行距離 (公里)
        'estimated_duration': '一日遊 (8小時)',
        'attractions': [
            '糯米橋 - 百年石橋見證歷史',
            '松興飲食部 - 品嚐道地客家美食',
            '國姓驛站 - 咖啡文化體驗中心',
            '國姓咖啡莊園 - 高山咖啡品鑑'
        ],
        'highlights': [
            '深度了解國姓咖啡產業發展',
            '體驗客家文化與美食',
            '欣賞百年糯米橋建築工藝',
            '品嚐高品質台灣咖啡'
        ]
    },
    'route_b': {
        'id': 'route_b',
        'name': '探索心靈與絕景之道',
        'description': '尋找內心平靜與自然美景的完美結合，享受山林間的寧靜時光',
        'internal_distance': 30,
        'walking_distance': 2.5,  # 步行距離 (公里)
        'estimated_duration': '一日遊 (9小時)',
        'attractions': [
            '九份二山 - 地震紀念地與生態復育',
            '澀水森林步道 - 森林浴與芬多精',
            '國姓禪寺 - 心靈沉澱與冥想',
            '天空之橋觀景台 - 360度山景'
        ],
        'highlights': [
            '體驗森林療癒與自然教育',
            '學習災後重建與生態保育',
            '享受山林間的寧靜冥想',
            '俯瞰國姓鄉壯麗山景'
        ]
    },
    'route_c': {
        'id': 'route_c',
        'name': '闔家歡樂的季節恩賜冒險',
        'description': '適合全家大小的季節性體驗活動，創造美好的親子回憶',
        'internal_distance': 35,
        'walking_distance': 2.0,  # 步行距離 (公里)
        'estimated_duration': '一日遊 (10小時)',
        'attractions': [
            '國姓草莓園 - 季節限定採果樂',
            '親子農場體驗 - 餵食小動物',
            '國姓溫泉區 - 天然溫泉泡湯',
            '夜間生態導覽 - 觀察螢火蟲'
        ],
        'highlights': [
            '季節性農產品採收體驗',
            '親子互動與自然教育',
            '享受天然溫泉放鬆身心',
            '夜間生態觀察與環境教育'
        ]
    }
}

# 主要城市到南投國姓的距離資料
CITY_DISTANCES = {
    '台北': 220,    # 公里
    '新北': 210,
    '桃園': 200,
    '新竹': 150,
    '苗栗': 120,
    '台中': 80,
    '彰化': 100,
    '雲林': 140,
    '嘉義': 180,
    '台南': 280,
    '高雄': 350,
    '屏東': 380,
    '宜蘭': 160,
    '花蓮': 180,
    '台東': 320
}

# 交通工具選項
TRANSPORT_OPTIONS = {
    'car_petrol': {
        'name': '自用小客車 (汽油)',
        'emission_factor': 0.115,
        'description': '最常見的交通方式，適合家庭出遊'
    },
    'motorcycle': {
        'name': '機車',
        'emission_factor': 0.0951,
        'description': '機動性高，適合短程旅遊'
    },
    'bus': {
        'name': '大眾運輸 (客運/火車)',
        'emission_factor': 0.04,
        'description': '最環保的選擇，減少個人碳足跡'
    },
    'high_speed_rail': {
        'name': '高鐵',
        'emission_factor': 0.032,
        'description': '快速便捷，適合長程旅行'
    }
}

# 用餐選擇選項
DINING_OPTIONS = {
    'local_meat': {
        'name': '在地客家料理 (含肉類)',
        'emission_factor': 3.0,
        'description': '品嚐道地客家風味，體驗在地文化'
    },
    'local_vegetarian': {
        'name': '在地蔬食餐',
        'emission_factor': 1.0,
        'description': '健康環保，支持永續飲食'
    },
    'light_meal': {
        'name': '輕食簡餐 (咖啡館餐點)',
        'emission_factor': 1.5,
        'description': '簡單輕鬆，適合悠閒時光'
    },
    'self_prepared': {
        'name': '自備餐點',
        'emission_factor': 0.5,
        'description': '最環保的選擇，減少包裝廢棄物'
    }
}

# 咖啡選擇選項
COFFEE_OPTIONS = {
    'black_coffee': {
        'name': '品嚐黑咖啡 (手沖/義式)',
        'emission_factor': 0.1,
        'description': '品味國姓咖啡豆的純粹風味'
    },
    'latte_cappuccino': {
        'name': '選擇拿鐵/卡布奇諾 (含牛奶)',
        'emission_factor': 1.0,
        'description': '香濃奶香，經典咖啡體驗'
    },
    'no_coffee': {
        'name': '不喝咖啡',
        'emission_factor': 0.0,
        'description': '選擇其他在地飲品或茶類'
    }
}

@dataclass
class NantouTripCalculation:
    """南投旅程計算資料模型"""
    # 使用者輸入 - 基本資訊
    route_option: str  # 'route_a', 'route_b', 'route_c'
    traveler_count: int  # 1-10人或更多
    transport_mode: str  # 'car_petrol', 'motorcycle', 'bus', 'high_speed_rail'
    departure_city: str  # 出發城市
    
    # 使用者輸入 - 旅程細節
    dining_choice: str = 'local_meat'  # 用餐選擇
    coffee_choice: str = 'black_coffee'  # 咖啡選擇
    
    # 計算結果 - 交通
    intercity_distance: float = 0.0  # 城際距離 (km)
    route_distance: float = 0.0     # 路線內距離 (km)
    walking_distance: float = 0.0   # 步行距離 (km)
    total_distance: float = 0.0     # 總距離 (km)
    
    intercity_emissions: float = 0.0  # 城際碳排放 (kg CO2e)
    route_emissions: float = 0.0     # 路線內碳排放 (kg CO2e)
    
    # 計算結果 - 飲食
    dining_emissions: float = 0.0    # 飲食碳排放 (kg CO2e)
    coffee_emissions: float = 0.0    # 咖啡碳排放 (kg CO2e)
    
    # 計算結果 - 總計
    total_emissions: float = 0.0     # 總碳排放 (kg CO2e)
    per_person_emissions: float = 0.0 # 每人平均碳排放 (kg CO2e)
    
    # 減碳貢獻
    walking_carbon_saved: float = 0.0  # 步行減少的碳排放 (kg CO2e)
    
    # 比較和建議
    tree_equivalent: float = 0.0     # 相當於幾棵樹的CO2吸收量
    transport_alternatives: List[Dict] = None
    eco_recommendations: List[str] = None
    
    # 計算時間
    calculated_at: datetime = None

@dataclass
class TransportAlternative:
    """交通替代方案模型"""
    transport_mode: str      # 替代交通方式
    emissions_reduction: float  # 可減少的碳排放量 (kg CO2e)
    percentage_reduction: float # 減少百分比
    recommendation_text: str    # 建議文字

@dataclass
class RouteInfo:
    """路線資訊模型"""
    route_id: str           # 'route_a', 'route_b', 'route_c'
    name: str              # 路線名稱
    description: str       # 路線描述
    internal_distance: float # 路線內移動距離 (km)
    walking_distance: float # 步行距離 (km)
    attractions: List[str] # 主要景點列表
    estimated_duration: str # 預估遊覽時間
    highlights: List[str]  # 路線特色

class NantouCarbonCalculator:
    """南投永續之旅碳足跡計算引擎"""
    
    def __init__(self):
        self.emission_factors = TAIWAN_EMISSION_FACTORS
        self.route_distances = NANTOU_ROUTES
        self.city_distances = CITY_DISTANCES
    
    def calculate_intercity_emissions(self, departure_city: str, transport_mode: str, passengers: int) -> float:
        """計算城際交通碳排放 (出發城市到南投)"""
        
        # 獲取城際距離
        distance = self.city_distances.get(departure_city, 200)  # 預設200公里
        
        # 獲取排放係數
        emission_factor = self.emission_factors['transportation'][transport_mode]
        
        # 計算碳排放 (往返)
        return emission_factor * distance * 2 * passengers
    
    def calculate_route_emissions(self, route_option: str, transport_mode: str, passengers: int) -> float:
        """計算行程內交通碳排放 (預設路線內移動)"""
        
        # 獲取路線內距離
        route_data = self.route_distances.get(route_option, self.route_distances['route_a'])
        internal_distance = route_data['internal_distance']
        
        # 獲取排放係數
        emission_factor = self.emission_factors['transportation'][transport_mode]
        
        # 計算碳排放
        return emission_factor * internal_distance * passengers
    
    def calculate_dining_emissions(self, dining_choice: str, traveler_count: int) -> float:
        """計算飲食碳排放"""
        emission_factor = self.emission_factors['dining'][dining_choice]
        return emission_factor * traveler_count
    
    def calculate_coffee_emissions(self, coffee_choice: str, traveler_count: int) -> float:
        """計算咖啡碳排放"""
        emission_factor = self.emission_factors['coffee'][coffee_choice]
        return emission_factor * traveler_count
    
    def calculate_walking_carbon_saved(self, walking_distance: float, traveler_count: int) -> float:
        """計算步行減少的碳排放（相對於開車）"""
        car_emission_factor = self.emission_factors['transportation']['car_petrol']
        return car_emission_factor * walking_distance * traveler_count
    
    def calculate_total_emissions(self, trip_data: NantouTripCalculation) -> NantouTripCalculation:
        """計算總碳排放 = 城際 + 行程內 + 飲食 + 咖啡"""
        
        # 計算城際交通碳排放
        intercity_emissions = self.calculate_intercity_emissions(
            trip_data.departure_city,
            trip_data.transport_mode,
            trip_data.traveler_count
        )
        
        # 計算路線內交通碳排放
        route_emissions = self.calculate_route_emissions(
            trip_data.route_option,
            trip_data.transport_mode,
            trip_data.traveler_count
        )
        
        # 計算飲食碳排放
        dining_emissions = self.calculate_dining_emissions(
            trip_data.dining_choice,
            trip_data.traveler_count
        )
        
        # 計算咖啡碳排放
        coffee_emissions = self.calculate_coffee_emissions(
            trip_data.coffee_choice,
            trip_data.traveler_count
        )
        
        # 計算距離
        intercity_distance = self.city_distances.get(trip_data.departure_city, 200) * 2  # 往返
        route_distance = self.route_distances[trip_data.route_option]['internal_distance']
        walking_distance = self.route_distances[trip_data.route_option]['walking_distance']
        
        # 計算步行減碳貢獻
        walking_carbon_saved = self.calculate_walking_carbon_saved(walking_distance, trip_data.traveler_count)
        
        # 更新計算結果
        trip_data.intercity_distance = intercity_distance
        trip_data.route_distance = route_distance
        trip_data.walking_distance = walking_distance
        trip_data.total_distance = intercity_distance + route_distance
        
        trip_data.intercity_emissions = intercity_emissions
        trip_data.route_emissions = route_emissions
        trip_data.dining_emissions = dining_emissions
        trip_data.coffee_emissions = coffee_emissions
        trip_data.walking_carbon_saved = walking_carbon_saved
        
        trip_data.total_emissions = intercity_emissions + route_emissions + dining_emissions + coffee_emissions
        trip_data.per_person_emissions = trip_data.total_emissions / trip_data.traveler_count
        
        # 計算樹木等效
        trip_data.tree_equivalent = self.calculate_tree_equivalent(trip_data.total_emissions)
        
        # 設定計算時間
        trip_data.calculated_at = datetime.now()
        
        return trip_data
    
    def calculate_per_person_emissions(self, total_emissions: float, passenger_count: int) -> float:
        """計算每人平均碳足跡"""
        return total_emissions / passenger_count if passenger_count > 0 else 0.0
    
    def calculate_tree_equivalent(self, co2_amount: float) -> float:
        """計算相當於幾棵樹的CO2吸收量"""
        # 一棵成年樹每天約吸收 22kg CO2 / 365天 = 0.06kg CO2
        daily_absorption_per_tree = 0.06
        return co2_amount / daily_absorption_per_tree

class DistanceCalculator:
    """距離計算器"""
    
    def __init__(self):
        self.city_distances = CITY_DISTANCES
        self.nantou_location = (24.0, 120.9)  # 南投國姓概略座標
    
    def calculate_intercity_distance(self, departure_city: str) -> float:
        """計算出發城市到南投的距離"""
        return self.city_distances.get(departure_city, 200)  # 預設200公里
    
    def get_route_internal_distance(self, route_option: str) -> float:
        """獲取預設路線的內部移動距離"""
        route_data = NANTOU_ROUTES.get(route_option, NANTOU_ROUTES['route_a'])
        return route_data['internal_distance']

class EcoRecommendationEngine:
    """環保建議生成器"""
    
    def __init__(self):
        self.recommendation_templates = self.load_recommendation_templates()
    
    def generate_transport_alternatives(self, current_transport: str, total_emissions: float, trip_data: NantouTripCalculation) -> List[TransportAlternative]:
        """生成綠色交通替代建議"""
        alternatives = []
        
        # 計算不同交通方式的排放量
        calculator = NantouCarbonCalculator()
        
        for transport_mode, transport_info in TRANSPORT_OPTIONS.items():
            if transport_mode != current_transport:
                # 創建替代方案的計算資料
                alt_trip = NantouTripCalculation(
                    route_option=trip_data.route_option,
                    traveler_count=trip_data.traveler_count,
                    transport_mode=transport_mode,
                    departure_city=trip_data.departure_city
                )
                
                # 計算替代方案的排放量
                alt_trip = calculator.calculate_total_emissions(alt_trip)
                
                # 計算減少量
                emissions_reduction = total_emissions - alt_trip.total_emissions
                percentage_reduction = (emissions_reduction / total_emissions) * 100 if total_emissions > 0 else 0
                
                if emissions_reduction > 0:
                    recommendation_text = f"若改搭{transport_info['name']}，您這次的旅程能減少 {emissions_reduction:.1f} 公斤的碳排放！"
                    
                    alternatives.append(TransportAlternative(
                        transport_mode=transport_info['name'],
                        emissions_reduction=emissions_reduction,
                        percentage_reduction=percentage_reduction,
                        recommendation_text=recommendation_text
                    ))
        
        return alternatives
    
    def generate_sustainable_dining_tips(self) -> List[str]:
        """生成永續飲食建議"""
        return [
            "在品嚐客家美食時，選擇一道蔬食餐點，也能為地球減輕負擔。",
            "選擇當地當季的食材，減少食物運輸的碳足跡。",
            "支持使用有機農法的在地農產品，保護土壤與生態環境。"
        ]
    
    def generate_waste_reduction_tips(self) -> List[str]:
        """生成源頭減量建議"""
        return [
            "記得攜帶自己的環保杯與餐具，向一次性用品說不。",
            "自備購物袋，減少塑膠袋的使用。",
            "選擇可重複使用的水瓶，減少寶特瓶消費。"
        ]
    
    def generate_personalized_recommendations(self, trip_data: NantouTripCalculation) -> Dict[str, List[str]]:
        """生成個人化的環保建議"""
        recommendations = {
            'dining': [],
            'coffee': [],
            'transport': [],
            'general': []
        }
        
        # 根據飲食選擇給建議
        if trip_data.dining_choice == 'local_meat':
            recommendations['dining'].append(
                "您知道嗎？下次旅程若選擇在地蔬食，光是一餐就能減少約 2 公斤的碳排放，相當於少開車 17 公里喔！"
            )
        elif trip_data.dining_choice == 'local_vegetarian':
            recommendations['dining'].append(
                "太棒了！您選擇了蔬食餐點，為地球減少了大量碳排放。繼續保持這個環保習慣！"
            )
        elif trip_data.dining_choice == 'self_prepared':
            recommendations['dining'].append(
                "自備餐點是最環保的選擇！您不僅減少了碳排放，還避免了包裝廢棄物的產生。"
            )
        
        # 根據咖啡選擇給建議
        if trip_data.coffee_choice == 'latte_cappuccino':
            recommendations['coffee'].append(
                "國姓的黑咖啡風味絕佳！下次嘗試看看，不僅能品嚐到咖啡豆最純粹的風味，碳足跡也比拿鐵低了許多！"
            )
        elif trip_data.coffee_choice == 'black_coffee':
            recommendations['coffee'].append(
                "您選擇了黑咖啡，既能品味國姓咖啡豆的純粹風味，又是最環保的咖啡選擇！"
            )
        
        # 根據交通方式給建議
        if trip_data.transport_mode == 'bus':
            recommendations['transport'].append(
                "您選擇了最環保的旅行方式之一！感謝您為這趟旅程大幅降低了碳足跡。"
            )
        elif trip_data.transport_mode == 'car_petrol':
            recommendations['transport'].append(
                "下次旅行時，考慮與朋友共乘或選擇大眾運輸，可以大幅減少碳排放。"
            )
        
        # 一般建議
        if trip_data.per_person_emissions > 30:
            recommendations['general'].append(
                "您的碳足跡較高，建議考慮碳抵消方案來中和環境影響。"
            )
        else:
            recommendations['general'].append(
                "恭喜！您選擇了相對低碳的旅遊方式，為環境保護做出了貢獻。"
            )
        
        return recommendations
    
    def generate_eco_recommendations(self, trip_data: NantouTripCalculation) -> List[str]:
        """生成綜合環保建議（保持向後相容）"""
        personalized = self.generate_personalized_recommendations(trip_data)
        all_recommendations = []
        
        for category, recs in personalized.items():
            all_recommendations.extend(recs)
        
        return all_recommendations
    
    def load_recommendation_templates(self) -> Dict:
        """載入建議範本"""
        return {
            'low_carbon': "您的旅程碳足跡相對較低，繼續保持環保的旅遊習慣！",
            'medium_carbon': "透過一些簡單的改變，您可以進一步減少旅遊的環境影響。",
            'high_carbon': "建議考慮更環保的交通方式或碳抵消方案。"
        }

# 輔助函數
def get_route_info(route_id: str) -> RouteInfo:
    """獲取路線資訊"""
    route_data = NANTOU_ROUTES.get(route_id, NANTOU_ROUTES['route_a'])
    return RouteInfo(
        route_id=route_data['id'],
        name=route_data['name'],
        description=route_data['description'],
        internal_distance=route_data['internal_distance'],
        walking_distance=route_data['walking_distance'],
        attractions=route_data['attractions'],
        estimated_duration=route_data['estimated_duration'],
        highlights=route_data['highlights']
    )

def get_transport_options() -> Dict:
    """獲取交通工具選項"""
    return TRANSPORT_OPTIONS

def get_city_list() -> List[str]:
    """獲取城市列表"""
    return list(CITY_DISTANCES.keys())

def validate_trip_input(trip_data: dict) -> List[str]:
    """驗證旅程輸入資料"""
    errors = []
    
    if not trip_data.get('route_option'):
        errors.append("請選擇一個旅遊路線")
    
    traveler_count = trip_data.get('traveler_count', 0)
    if traveler_count <= 0 or traveler_count > 50:
        errors.append("旅遊人數必須在 1-50 人之間")
    
    if not trip_data.get('transport_mode'):
        errors.append("請選擇交通方式")
    
    if not trip_data.get('departure_city'):
        errors.append("請輸入出發城市")
    
    return errors

def format_nantou_trip_result(trip_data: NantouTripCalculation) -> Dict:
    """格式化南投旅程計算結果供顯示使用"""
    
    return {
        'total_co2_kg': round(trip_data.total_emissions, 2),
        'per_person_co2_kg': round(trip_data.per_person_emissions, 2),
        'intercity_co2_kg': round(trip_data.intercity_emissions, 2),
        'route_co2_kg': round(trip_data.route_emissions, 2),
        'dining_co2_kg': round(trip_data.dining_emissions, 2),
        'coffee_co2_kg': round(trip_data.coffee_emissions, 2),
        'walking_saved_kg': round(trip_data.walking_carbon_saved, 2),
        'intercity_percentage': round(
            (trip_data.intercity_emissions / trip_data.total_emissions) * 100, 1
        ) if trip_data.total_emissions > 0 else 0,
        'route_percentage': round(
            (trip_data.route_emissions / trip_data.total_emissions) * 100, 1
        ) if trip_data.total_emissions > 0 else 0,
        'dining_percentage': round(
            (trip_data.dining_emissions / trip_data.total_emissions) * 100, 1
        ) if trip_data.total_emissions > 0 else 0,
        'coffee_percentage': round(
            (trip_data.coffee_emissions / trip_data.total_emissions) * 100, 1
        ) if trip_data.total_emissions > 0 else 0,
        'tree_equivalent': round(trip_data.tree_equivalent, 1),
        'total_distance': round(trip_data.total_distance, 1),
        'intercity_distance': round(trip_data.intercity_distance, 1),
        'route_distance': round(trip_data.route_distance, 1),
        'walking_distance': round(trip_data.walking_distance, 1)
    }

# 輸入驗證類別
class NantouTripValidator:
    """南投旅程輸入驗證器"""
    
    @staticmethod
    def validate_trip_input(trip_data: dict) -> List[str]:
        """驗證旅程輸入資料"""
        errors = []
        
        if not trip_data.get('route_option'):
            errors.append("請選擇一個旅遊路線")
        
        traveler_count = trip_data.get('traveler_count', 0)
        if traveler_count <= 0 or traveler_count > 50:
            errors.append("旅遊人數必須在 1-50 人之間")
        
        if not trip_data.get('transport_mode'):
            errors.append("請選擇交通方式")
        
        if not trip_data.get('departure_city'):
            errors.append("請輸入出發城市")
        elif trip_data.get('departure_city') not in CITY_DISTANCES:
            errors.append("請選擇有效的出發城市")
        
        return errors
    
    @staticmethod
    def validate_route_option(route_option: str) -> bool:
        """驗證路線選項"""
        return route_option in NANTOU_ROUTES
    
    @staticmethod
    def validate_transport_mode(transport_mode: str) -> bool:
        """驗證交通方式"""
        return transport_mode in TRANSPORT_OPTIONS

# 資料載入函數
def load_preset_routes() -> Dict:
    """載入預設路線資料"""
    return NANTOU_ROUTES

def load_transport_options() -> Dict:
    """載入交通工具選項"""
    return TRANSPORT_OPTIONS

def load_departure_cities() -> List[str]:
    """載入出發城市列表"""
    return sorted(list(CITY_DISTANCES.keys()))

def load_dining_options() -> Dict:
    """載入用餐選擇選項"""
    return DINING_OPTIONS

def load_coffee_options() -> Dict:
    """載入咖啡選擇選項"""
    return COFFEE_OPTIONS

def load_taiwan_emission_factors() -> Dict:
    """載入台灣環境部碳排放係數"""
    return TAIWAN_EMISSION_FACTORS