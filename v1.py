"""
糯米橋永續之旅碳足跡計算器 - 主應用程式
基於 Streamlit 的多頁籤 Web 應用程式，專為南投國姓地區永續旅遊設計
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from functions import (
    NantouCarbonCalculator, 
    EcoRecommendationEngine,
    NantouTripCalculation,
    NantouTripValidator,
    get_route_info,
    load_preset_routes,
    load_transport_options,
    load_departure_cities,
    load_dining_options,
    load_coffee_options,
    format_nantou_trip_result
)

# 設定頁面配置
st.set_page_config(
    page_title="糯米橋永續之旅碳足跡計算器",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 載入自定義 CSS
def load_css():
    """載入南投自然風格的 CSS 樣式"""
    
    css = """
    <style>
    /* 導入字體 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap');
    
    /* 全域樣式 */
    .stApp {
        font-family: 'Noto Sans TC', sans-serif;
    }
    
    /* 主要容器 */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* 背景圖片設定 */
    .hero-background {
        background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url("app/static/nantou_bridge.png");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        min-height: 400px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 15px;
        margin-bottom: 30px;
        position: relative;
    }
    
    /* 首頁橫幅內容 */
    .hero-background {
        text-align: center;
        color: white;
        padding: 60px 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .hero-slogan {
        font-size: 1.3rem;
        margin-bottom: 30px;
        opacity: 0.95;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        line-height: 1.6;
    }
    
    /* Tab 樣式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0px 24px;
        background-color: transparent;
        border-radius: 8px;
        color: #495057;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #28a745 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 卡片樣式 */
    .info-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border-left: 5px solid #28a745;
    }
    
    .result-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border-left: 5px solid #007bff;
    }
    
    /* 環保建議卡片 */
    .eco-card {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #28a745;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* 樹木視覺化 */
    .tree-visual {
        text-align: center;
        padding: 25px;
        background: linear-gradient(135deg, #f0f8f0 0%, #e8f5e8 100%);
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .tree-icons {
        font-size: 2.5rem;
        margin: 15px 0;
        line-height: 1.2;
    }
    
    /* 路線卡片 */
    .route-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 15px 0;
        border-left: 4px solid #007bff;
        transition: transform 0.2s ease;
    }
    
    .route-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* 統計指標 */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    /* 數據來源說明 */
    .data-source {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        font-size: 0.9rem;
        color: #666;
        margin-top: 30px;
        border-top: 3px solid #dee2e6;
    }
    
    /* 按鈕樣式 */
    .stButton > button {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3);
    }
    
    /* 行動裝置適配 */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.2rem;
        }
        
        .hero-slogan {
            font-size: 1.1rem;
        }
        
        .info-card, .result-card {
            padding: 20px;
        }
        
        .hero-background {
            min-height: 300px;
        }
    }
    
    /* Streamlit 控制欄確保可見 */
    .stApp > header {
        background-color: transparent;
        z-index: 999;
    }
    
    /* 隱藏部分 Streamlit 預設元素 */
    #MainMenu {visibility: visible;}
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def main():
    """主應用程式函數"""
    
    # 載入樣式
    load_css()
    
    # 初始化 session state
    if 'calculation_result' not in st.session_state:
        st.session_state.calculation_result = None
    
    # 首頁橫幅
    render_hero_banner()
    
    # 建立 Tab 導航
    tab1, tab2, tab3, tab4 = st.tabs(["🧮 碳足跡計算", "🗺️ 旅遊路線", "📊 計算結果", "ℹ️ 關於我們"])
    
    with tab1:
        render_carbon_calculator_tab()
    
    with tab2:
        render_routes_tab()
    
    with tab3:
        render_results_tab()
    
    with tab4:
        render_about_tab()

def render_hero_banner():
    """渲染首頁橫幅"""
    st.markdown("""
    <div class="hero-background">
        <div class="hero-title">🌿 糯米橋永續之旅</div>
        <div class="hero-slogan">每一次的旅行，都是對地球的投票。<br>選擇一個更溫柔的方式，探索國姓之美。</div>
    </div>
    """, unsafe_allow_html=True)

def render_carbon_calculator_tab():
    """渲染碳足跡計算 Tab"""
    
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("🧮 碳足跡計算器")
    st.write("請輸入您的旅程資訊，我們將為您計算這次南投國姓之旅的碳足跡。")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 載入資料
    routes = load_preset_routes()
    transport_options = load_transport_options()
    cities = load_departure_cities()
    dining_options = load_dining_options()
    coffee_options = load_coffee_options()
    
    # 建立表單
    with st.form("trip_form"):
        # 第1步：旅程基本設定
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.subheader("📋 第1步：旅程基本設定")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 路線選擇
            route_options = [(k, v['name']) for k, v in routes.items()]
            selected_route = st.selectbox(
                "🗺️ 選擇您的國姓印象",
                options=[k for k, v in route_options],
                format_func=lambda x: next(v for k, v in route_options if k == x),
                index=0
            )
            
            # 旅遊人數
            traveler_count = st.number_input(
                "👥 旅遊人數",
                min_value=1,
                max_value=50,
                value=2,
                help="請輸入參與此次旅程的總人數"
            )
        
        with col2:
            # 交通工具選擇
            transport_options_list = [(k, v['name']) for k, v in transport_options.items()]
            selected_transport = st.selectbox(
                "🚙 選擇交通工具",
                options=[k for k, v in transport_options_list],
                format_func=lambda x: next(v for k, v in transport_options_list if k == x),
                index=0  # 預設為自用小客車
            )
            
            # 出發城市
            departure_city = st.selectbox(
                "🏙️ 您的出發城市",
                options=cities,
                index=cities.index('台北') if '台北' in cities else 0,
                help="選擇您出發前往南投的城市"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 第2步：旅程細節描繪
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.subheader("🍽️ 第2步：旅程細節描繪")
        st.write("這些細節選擇將大幅影響您的碳足跡計算結果。")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 用餐選擇
            dining_options_list = [(k, v['name']) for k, v in dining_options.items()]
            selected_dining = st.selectbox(
                "🥘 用餐選擇 (午餐)",
                options=[k for k, v in dining_options_list],
                format_func=lambda x: next(v for k, v in dining_options_list if k == x),
                index=0,
                help="不同的飲食選擇有著巨大的碳排差異"
            )
            
            # 顯示用餐選擇的描述
            if selected_dining in dining_options:
                st.info(f"💡 {dining_options[selected_dining]['description']}")
        
        with col2:
            # 咖啡選擇
            coffee_options_list = [(k, v['name']) for k, v in coffee_options.items()]
            selected_coffee = st.selectbox(
                "☕ 咖啡品味",
                options=[k for k, v in coffee_options_list],
                format_func=lambda x: next(v for k, v in coffee_options_list if k == x),
                index=0,
                help="國姓是咖啡之鄉，品嚐咖啡是行程重點"
            )
            
            # 顯示咖啡選擇的描述
            if selected_coffee in coffee_options:
                st.info(f"💡 {coffee_options[selected_coffee]['description']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 旅人足跡預覽
        if 'selected_route' in locals():
            route_info = get_route_info(selected_route)
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.subheader("👣 旅人足跡 (步行估算)")
            walking_distance = route_info.walking_distance
            st.success(f"🚶‍♀️ 您選擇的{route_info.name}，我們預估您將步行約 {walking_distance} 公里探索景點。這段路程，您為地球減少了碳排放！")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 計算按鈕
        submitted = st.form_submit_button("🧮 開始計算您的永續影響力", type="primary")
        
        # 在計算按鈕下方添加糯米橋圖片
        try:
            st.image("images/nantou_bridge_footer.png", use_container_width=True)
        except FileNotFoundError:
            pass  # 如果圖片不存在就略過
        
        if submitted:
            # 驗證輸入
            trip_data = {
                'route_option': selected_route,
                'traveler_count': traveler_count,
                'transport_mode': selected_transport,
                'departure_city': departure_city,
                'dining_choice': selected_dining,
                'coffee_choice': selected_coffee
            }
            
            errors = NantouTripValidator.validate_trip_input(trip_data)
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # 執行計算
                calculate_carbon_footprint(trip_data)
                st.success("✅ 計算完成！請切換到「計算結果」頁籤查看您的永續影響力報告。")

def render_routes_tab():
    """渲染旅遊路線 Tab"""
    
    st.subheader("🗺️ 南投國姓旅遊路線")
    st.write("探索三條精心設計的國姓旅遊路線，每條路線都有獨特的魅力和體驗。")
    
    routes = load_preset_routes()
    
    for route_id, route_data in routes.items():
        st.markdown('<div class="route-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"📍 {route_data['name']}")
            st.write(f"**路線描述：** {route_data['description']}")
            st.write(f"**預估時間：** {route_data['estimated_duration']}")
            st.write(f"**行程距離：** {route_data['internal_distance']} 公里")
            st.write(f"**步行距離：** {route_data['walking_distance']} 公里")
            
            st.write("**主要景點：**")
            for attraction in route_data['attractions']:
                st.write(f"• {attraction}")
        
        with col2:
            st.write("**路線特色：**")
            for highlight in route_data['highlights']:
                st.write(f"✨ {highlight}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")

def render_results_tab():
    """渲染計算結果 Tab"""
    
    if st.session_state.calculation_result:
        render_calculation_results()
        render_eco_recommendations()
    else:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.subheader("📊 計算結果")
        st.info("🔍 尚未進行碳足跡計算。請先到「碳足跡計算」頁籤輸入您的旅程資訊。")
        st.markdown('</div>', unsafe_allow_html=True)

def render_about_tab():
    """渲染關於我們 Tab"""
    
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("ℹ️ 關於南投永續之旅")
    
    st.write("""
    ### 🌿 我們的理念
    
    「每一次的旅行，都是對地球的投票。」我們相信旅遊不僅是探索美景，更是一種對環境負責的生活態度。
    
    ### 🎯 計算器目標
    
    - **提升環保意識**：讓旅客了解自己的碳足跡
    - **推廣低碳旅遊**：提供具體的環保建議
    - **支持在地發展**：促進南投國姓的永續觀光
    - **教育與行動**：將環保理念轉化為實際行動
    
    ### 📊 數據來源
    
    本計算器使用的碳排放係數來自：
    - 台灣環境部「生活碳足跡計算器」
    - 交通部運輸研究所相關數據
    - 國際能源署 (IEA) 碳排放標準
    
    ### 🌱 永續旅遊建議
    
    - **選擇低碳交通**：優先考慮大眾運輸工具
    - **支持在地業者**：選擇環保認證的住宿和餐廳
    - **減少廢棄物**：攜帶環保用品，實踐源頭減量
    - **尊重自然**：遵循無痕山林原則
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 數據來源說明
    render_data_source_footer()

def calculate_carbon_footprint(trip_data):
    """計算碳足跡"""
    try:
        # 創建計算物件
        trip_calculation = NantouTripCalculation(
            route_option=trip_data['route_option'],
            traveler_count=trip_data['traveler_count'],
            transport_mode=trip_data['transport_mode'],
            departure_city=trip_data['departure_city'],
            dining_choice=trip_data.get('dining_choice', 'local_meat'),
            coffee_choice=trip_data.get('coffee_choice', 'black_coffee')
        )
        
        # 執行計算
        calculator = NantouCarbonCalculator()
        result = calculator.calculate_total_emissions(trip_calculation)
        
        # 儲存結果到 session state
        st.session_state.calculation_result = result
        
    except Exception as e:
        st.error(f"計算過程中發生錯誤：{str(e)}")

def render_calculation_results():
    """渲染計算結果"""
    result = st.session_state.calculation_result
    formatted_result = format_nantou_trip_result(result)
    
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.subheader("📊 您的永續影響力報告")
    
    # 核心數據顯示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="總碳足跡",
            value=f"{formatted_result['total_co2_kg']} kg",
            help="此次旅程的總二氧化碳排放量"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="每人平均",
            value=f"{formatted_result['per_person_co2_kg']} kg",
            help="平均每人的碳排放量"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="步行距離",
            value=f"{formatted_result['walking_distance']} km",
            help="您在此次旅程中的步行距離"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="樹木等效",
            value=f"{formatted_result['tree_equivalent']} 棵",
            help="相當於幾棵樹一天的CO2吸收量"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 減碳貢獻亮點區塊
    render_carbon_saving_highlight(formatted_result)
    
    # 樹木視覺化
    render_tree_visualization(formatted_result['tree_equivalent'])
    
    # 圖表區域
    col1, col2 = st.columns(2)
    
    with col1:
        # 碳足跡結構分析圖表
        render_detailed_emission_breakdown_chart(result)
    
    with col2:
        # 交通方式比較圖表
        render_transport_comparison_chart(result)

def render_tree_visualization(tree_equivalent):
    """渲染樹木等效視覺化"""
    tree_count = int(tree_equivalent)
    
    st.markdown(f"""
    <div class="tree-visual">
        <h4>🌳 環境影響等效</h4>
        <p>您的旅程碳足跡相當於 <strong>{tree_equivalent}</strong> 棵樹一天的CO2吸收量</p>
        <div class="tree-icons">
            {'🌳' * min(tree_count, 10)}
            {f' +{tree_count-10}棵' if tree_count > 10 else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_carbon_saving_highlight(formatted_result):
    """渲染減碳貢獻亮點區塊"""
    
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("🌟 您的減碳貢獻")
    
    walking_saved = formatted_result['walking_saved_kg']
    walking_distance = formatted_result['walking_distance']
    
    if walking_saved > 0:
        st.success(f"""
        🚶‍♀️ **恭喜您！** 透過步行 {walking_distance} 公里，您成功避免了約 **{walking_saved} kg** 的二氧化碳排放。
        
        💚 這就是步行的力量！相當於少開車 {round(walking_distance, 1)} 公里的環保效益。
        """)
    else:
        st.info("🌱 雖然這次旅程沒有步行，但您的環保意識已經是很好的開始！")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_detailed_emission_breakdown_chart(result):
    """渲染詳細的碳足跡結構分析圓餅圖"""
    
    # 準備資料
    labels = ['城際交通', '路線內交通', '飲食', '咖啡']
    values = [
        result.intercity_emissions, 
        result.route_emissions,
        result.dining_emissions,
        result.coffee_emissions
    ]
    colors = ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    # 創建圓餅圖
    fig = px.pie(
        values=values,
        names=labels,
        title='碳足跡結構分析',
        color_discrete_sequence=colors
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    
    st.plotly_chart(fig, width='stretch')

def render_emission_breakdown_chart(result):
    """渲染碳足跡分解圓餅圖（保持向後相容）"""
    render_detailed_emission_breakdown_chart(result)

def render_transport_comparison_chart(result):
    """渲染交通方式比較長條圖"""
    
    # 生成替代方案
    eco_engine = EcoRecommendationEngine()
    alternatives = eco_engine.generate_transport_alternatives(
        result.transport_mode, 
        result.total_emissions, 
        result
    )
    
    if alternatives:
        # 準備資料
        transport_modes = ['您的選擇'] + [alt.transport_mode for alt in alternatives]
        emissions = [result.total_emissions] + [result.total_emissions - alt.emissions_reduction for alt in alternatives]
        colors = ['#dc3545'] + ['#28a745'] * len(alternatives)
        
        # 創建長條圖
        fig = px.bar(
            x=transport_modes,
            y=emissions,
            title='不同交通方式碳排放比較',
            labels={'y': 'CO2排放量 (kg)', 'x': '交通方式'},
            color=transport_modes,
            color_discrete_sequence=colors
        )
        
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, width='stretch')

def render_eco_recommendations():
    """渲染個人化環保建議"""
    result = st.session_state.calculation_result
    
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("🌱 您的下一步綠色行動")
    st.write("根據您的選擇，我們為您量身打造以下環保建議：")
    
    # 生成個人化建議
    eco_engine = EcoRecommendationEngine()
    personalized_recs = eco_engine.generate_personalized_recommendations(result)
    
    # 顯示個人化建議
    if personalized_recs['dining']:
        st.write("**🍽️ 飲食建議**")
        for rec in personalized_recs['dining']:
            st.markdown(f'<div class="eco-card">🥗 {rec}</div>', unsafe_allow_html=True)
    
    if personalized_recs['coffee']:
        st.write("**☕ 咖啡建議**")
        for rec in personalized_recs['coffee']:
            st.markdown(f'<div class="eco-card">☕ {rec}</div>', unsafe_allow_html=True)
    
    if personalized_recs['transport']:
        st.write("**🚌 交通建議**")
        for rec in personalized_recs['transport']:
            st.markdown(f'<div class="eco-card">🚌 {rec}</div>', unsafe_allow_html=True)
    
    # 交通替代建議
    alternatives = eco_engine.generate_transport_alternatives(
        result.transport_mode, 
        result.total_emissions, 
        result
    )
    
    if alternatives:
        st.write("**🔄 交通替代方案**")
        for alt in alternatives[:2]:  # 只顯示前兩個建議
            st.markdown(f'<div class="eco-card">💡 {alt.recommendation_text}</div>', unsafe_allow_html=True)
    
    # 一般環保建議
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🥬 永續飲食提醒**")
        dining_tips = eco_engine.generate_sustainable_dining_tips()
        for tip in dining_tips[:1]:
            st.markdown(f'<div class="eco-card">🍃 {tip}</div>', unsafe_allow_html=True)
    
    with col2:
        st.write("**♻️ 源頭減量提醒**")
        waste_tips = eco_engine.generate_waste_reduction_tips()
        for tip in waste_tips[:1]:
            st.markdown(f'<div class="eco-card">🌍 {tip}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_data_source_footer():
    """渲染數據來源說明"""
    st.markdown('<div class="data-source">', unsafe_allow_html=True)
    
    st.subheader("📋 數據來源與計算假設")
    
    st.write("**碳排放係數來源：**")
    st.write("• 交通工具：台灣環境部「生活碳足跡計算器」")
    st.write("• 飲食碳排：蔬食餐約 1kg CO2e，肉食餐約 3kg CO2e 之平均值")
    st.write("• 咖啡碳排：基於國際咖啡組織及乳製品生產碳排數據")
    
    st.write("**計算方法：**")
    st.write("• 步行減碳效益以替代同等距離之小客車碳排計算")
    st.write("• 樹木等效基於成年樹每日約吸收 0.06kg CO2 計算")
    st.write("• 所有數據旨在提供旅程規劃之參考")
    
    st.write("**免責聲明：**")
    st.write("計算結果僅供參考，實際碳排放量可能因個人行為、車輛效能、路況、食材來源等因素而有所差異。我們致力於推廣永續旅遊，邀請您一同為地球環境盡一份心力。")
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
