import streamlit as st
import pandas as pd
from HeadHuntCalc_division2_Y8S1_TU27 import run_calculation

st.title("Division 2 堅定獵頭配裝計算器")
st.subheader("適用版本 Y8S1 / TU27")
st.caption("Author: Le-visage-noir")

if "run" not in st.session_state: # 各 tab 共通按鈕
    st.session_state.run = False

tab1, tab2, tab3 = st.tabs(["數值設定", "篩選條件", "計算結果"])
# =========================
# 分頁 1 數值設定
# =========================
with tab1:
    
    if st.button("開始計算", key="run_tab1"):
        st.session_state.run = True
    
    st.header("玩家設定")

    agent_watch = st.number_input("手錶等級 (僅區分 1000 以上及以下)", value=1000)

    agent_class = st.selectbox(
        "特化職業",
        ["精準射手 (爆頭傷害 15 %)", "爆破專家 (對掩體外傷害 5 %)", "其他"],
        index=0
    )

    weapon = st.selectbox(
        "武器",
        ["1886", "SR-1", "白色死神", "戰術.308"]
    )
    if weapon != "1886":
        st.write("目前預設不開鏡 (採用爆頭傷害 + 10 % 瞄準鏡)")

    weapon_grade = st.number_input("武器專精等級", value=0)

    equip_core = st.selectbox("裝備紅核心數量 (預設 15 %)", list(range(7)), index=6)

    equip_sub = st.selectbox("裝備爆頭詞條數量 (預設 10 %)", list(range(7)), index=6)

    st.subheader("裝備模組 (爆頭傷害)")
    mod1 = st.number_input("模組1", value=10.0)
    mod2 = st.number_input("模組2", value=10.0)
    mod3 = st.number_input("模組3", value=10.0)

    mods = [mod1, mod2, mod3]

    # =========================
    # 原形武器
    # =========================
    st.subheader("原形武器")

    use_prototype = st.checkbox("啟用原形武器")

    prototype_type = None
    if use_prototype:
        PROTOTYPE_OPTIONS = {
            "1886": {
                "步槍傷害": "WD_rifle",
                "對掩體外傷害": "DTTOOC"
            },
            "SR-1": {
                "射手步槍傷害": "WD_marksman",
                "爆頭傷害": "HSD",
                "對掩體外傷害": "DTTOOC"
            },
            "白色死神": {
                "射手步槍傷害": "WD_marksman",
                "爆頭傷害": "HSD",
                "對掩體外傷害": "DTTOOC"
            },
            "戰術.308": {
                "射手步槍傷害": "WD_marksman",
                "爆頭傷害": "HSD",
                "對掩體外傷害": "DTTOOC"
            }
        }
        # ⭐ 根據武器抓可選項目
        options_dict = PROTOTYPE_OPTIONS.get(weapon, {})
        
        display_options = list(options_dict.keys())
        
        selected_display = st.selectbox(
            "原形類型",
            display_options
        )

        # ⭐ 轉換成內部參數
        prototype_type = options_dict[selected_display]

    weapon_prototype = [use_prototype, prototype_type]

    # =========================
    # 賽季加成
    # =========================
    st.header("賽季加成")

    Activate_Sesonal_Modifier = st.checkbox("啟用賽季加成")

    season_bonus = {}

    if Activate_Sesonal_Modifier:
        season_hsd = st.number_input("爆頭傷害加成", value=0.0)
        season_awd = st.number_input("武器傷害加成", value=0.0)
        season_twd = st.number_input("總武器傷害加成", value=0.0)

        season_bonus = {
            "HSD": season_hsd,
            "AWD": season_awd,
            "TWD": season_twd
        }

with tab2:
    
    if st.button("開始計算", key="run_tab2"):
        st.session_state.run = True
    
    # =========================
    # 特殊條件
    # =========================
    st.header("特殊條件")

    Forcing_Chest_ChainKiller = st.checkbox("強制連環殺手")
    
    # =========================
    # 篩選條件
    # =========================
    st.header("傷害門檻")

    use_first = st.checkbox("第一擊門檻", value=False)
    first_min = st.number_input("第一擊門檻值 (預設單人英雄紫怪)", value=6360822)

    use_second = st.checkbox("第二擊門檻", value=False)
    second_min = st.number_input("第二擊門檻值 (預設單人英雄金怪)", value=14752327)

    use_upper = st.checkbox("上限門檻", value=False)
    upper_min = st.number_input("上限門檻值 (預設四人傳奇金怪)", value=25172179)

    # =========================
    # 排序條件
    # =========================
    st.header("排序")

    sort_key_display = st.selectbox(
        "排序依據",
        ["第一擊", "第二擊", "上限"],
        index=0
    )

    # 對應回你的 key
    sort_key_map = {
        "第一擊": "first_hit",
        "第二擊": "second_hit",
        "上限": "upper_limit"
    }

    sort_key = sort_key_map[sort_key_display]

    descending = st.checkbox("由大到小排序", value=True)

    top_n = st.selectbox("顯示數量", [10, 25, 50], index=0)

agent_config = {
    "agent_watch": agent_watch,
    "agent_class": agent_class,
    "weapon": weapon,
    "weapon_grade": weapon_grade,
    "equip_core": equip_core,
    "equip_sub": equip_sub,
    "mods": mods,
    "weapon_prototype": weapon_prototype
}

query_config = {
    "filter": {
        "first_hit": {"enabled": use_first, "min": first_min},
        "second_hit": {"enabled": use_second, "min": second_min},
        "upper_limit": {"enabled": use_upper, "min": upper_min}
    },
    "sort": {
        "key": sort_key,
        "descending": descending
    },
    "top_n": top_n
}

def format_number(x):
    return f"{x:,}"

def format_stats(stats, ndigits=1):
    formatted = {}
    for k, v in stats.items():
        if isinstance(v, float):
            formatted[k] = round(v, ndigits)
        else:
            formatted[k] = v
    return formatted

with tab3:

    if st.button("更新計算結果", key="run_tab3"):
        st.session_state.run = True
    
    show_stats = st.toggle("顯示結果中的詳細數值 (stats)", value=False)
    
    if st.session_state.run:
        
        valid_build_count, results = run_calculation(agent_config, query_config, Forcing_Chest_ChainKiller, Activate_Sesonal_Modifier, season_bonus, show_stats)
        st.write(f"合理組合數量: {valid_build_count}")
        
        table = []
        
        for r in results:
            row = {
                "排名": r["rank"],
                "裝備 (面具 / 背包 / 防彈衣 / 手套 / 槍套 / 護膝)": " / ".join(r["combo"]),
                "第一擊": format_number(r["first_hit"]),
                "上限": format_number(r["upper_limit"]),
                "前五擊": " / ".join([format_number(x) for x in r["first_5_hits"]])
            }
            
            if show_stats and "stats" in r:
                stats = format_stats(r["stats"])
                
                row.update({
                    "所有武器傷害": stats.get("AWD"),
                    "爆頭傷害": stats.get("HSD"),
                    "對掩體外傷害": stats.get("DTTOOC")
                })
                
            table.append(row)

        df = pd.DataFrame(table)

        st.dataframe(df)
        
        if len(results) == 0:
            st.write("無符合傷害門檻之裝備組合，建議提高數值或調整修改器搭配、或是改用其他武器")
    