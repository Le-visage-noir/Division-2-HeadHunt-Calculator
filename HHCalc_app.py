import streamlit as st
import pandas as pd
from HeadHuntCalc_division2_Y8S1_TU27 import run_calculation
from HHCalc_code import decode_build_redirect, encode_build_v2

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
        st.write("計算結果已更新，請切換到該分頁查看")
    
    st.subheader("玩家設定")

    agent_watch = st.number_input("手錶等級 (僅區分 1000 以上及以下)", value=1000)

    agent_class = st.selectbox(
        "特化職業",
        ["精準射手 (爆頭傷害 15 %)", "爆破專家 (對掩體外傷害 5 %)", "其他"],
        index=0
    )
    
    st.subheader("武器")

    weapon = st.selectbox(
        "選擇武器",
        ["1886", "SR-1", "白色死神", "戰術.308"]
    )
    
    WEAPON_MOD_OPTIONS = {
        "SR-1": {
            "預設不開鏡 (爆頭傷害 + 10 %)": {"HSD": 10},
            " 8 倍鏡 (爆頭傷害 + 30 %)": {"HSD": 30},
            " 12 倍鏡 (爆頭傷害 + 35 %，裝彈速度 - 10 %)": {"HSD": 35},
            "精準射手特化鏡 (爆頭傷害 + 45 %，爆擊傷害 - 5 %)": {"HSD": 45},
            "其他": {}
        },
        "白色死神": {
            "預設不開鏡 (爆頭傷害 + 10 %)": {"HSD": 10},
            " 8 倍鏡 (爆頭傷害 + 30 %)": {"HSD": 30},
            " 12 倍鏡 (爆頭傷害 + 35 %，裝彈速度 - 10 %)": {"HSD": 35},
            "精準射手特化鏡 (爆頭傷害 + 45 %，爆擊傷害 - 5 %)": {"HSD": 45},
            "其他": {}
        },
        "戰術.308": {
            "預設不開鏡 (爆頭傷害 + 10 %)": {"HSD": 10},
            " 8 倍鏡 (爆頭傷害 + 30 %)": {"HSD": 30},
            " 12 倍鏡 (爆頭傷害 + 35 %，裝彈速度 - 10 %)": {"HSD": 35},
            "精準射手特化鏡 (爆頭傷害 + 45 %，爆擊傷害 - 5 %)": {"HSD": 45},
            "其他": {}
        },
        "1886": {}  # 無影響堅定獵頭傷害計算的模組
    }

    mod_options = WEAPON_MOD_OPTIONS.get(weapon, {})
    
    weapon_mod = None
    
    if len(mod_options) == 0:
        st.info("此武器無影響堅定獵頭傷害計算的模組")
    else:
        selected_mod = st.selectbox(
            "選擇瞄準具",
            list(mod_options.keys()),
            index=0
        )
        weapon_mod = mod_options[selected_mod]

    weapon_grade = st.number_input("武器專精等級", value=0)
    
    # =========================
    # 原型武器
    # =========================

    use_prototype = st.checkbox("啟用原型武器 (非原型武器預設數值為全滿)")
    prototype_stats = {}
    
    PROTOTYPE_SPEC = {
        "1886": {
            "WD_rifle": {"label": "步槍傷害", "min": 15.0, "max": 22.5},
            "DTTOOC": {"label": "對掩體外傷害", "min": 10, "max": 15}
        },
        "SR-1": {
            "WD_marksman": {"label": "射手步槍傷害", "min": 15.0, "max": 22.5},
            "HSD": {"label": "爆頭傷害", "min": 111.0, "max": 166.5},
            "DTTOOC": {"label": "對掩體外傷害", "min": 10, "max": 15}
        },
        "白色死神": {
            "WD_marksman": {"label": "射手步槍傷害", "min": 15.0, "max": 22.5},
            "HSD": {"label": "爆頭傷害", "min": 137.0, "max": 179.5},
            "DTTOOC": {"label": "對掩體外傷害", "min": 10, "max": 15}
        },
        "戰術.308": {
            "WD_marksman": {"label": "射手步槍傷害", "min": 15.0, "max": 22.5},
            "HSD": {"label": "爆頭傷害", "min": 111.0, "max": 166.5},
            "DTTOOC": {"label": "對掩體外傷害", "min": 10, "max": 15}
        }
    }
        
    spec = PROTOTYPE_SPEC.get(weapon, {})

    if not use_prototype:
        # 非原型武器 → 直接用 min
        for key, meta in spec.items():
            prototype_stats[key] = meta["min"]
    else:        
        for key, meta in spec.items():
            is_int = (key == "DTTOOC")
            val = st.slider(
                meta["label"],
                min_value=float(meta["min"]),
                max_value=float(meta["max"]),
                value=float(meta["max"]),   # 預設 max（最佳解）
                step=1.0 if is_int else 0.1,
                key=f"proto_{key}"
            )
            
            prototype_stats[key] = int(val) if is_int else round(val, 1)

    weapon_prototype = {
        "enabled": use_prototype,
        "stats": prototype_stats
    }
    
    st.subheader("裝備")

    equip_core = st.selectbox("裝備紅核心數量 (預設 15 %)", list(range(7)), index=6)

    equip_sub = st.selectbox("裝備爆頭詞條數量 (預設 10 %)", list(range(7)), index=6)

    mod1 = st.number_input("裝備模組 1 (爆頭傷害)", value=10.0)
    mod2 = st.number_input("裝備模組 2 (爆頭傷害)", value=10.0)
    mod3 = st.number_input("裝備模組 3 (爆頭傷害)", value=10.0)

    mods = [mod1, mod2, mod3]

    # =========================
    # 賽季加成
    # =========================
    st.subheader("賽季加成")

    Activate_Sesonal_Modifier = st.checkbox("啟用賽季加成 (beta)")

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
        st.write("計算結果已更新，請切換到該分頁查看")
    
    # =========================
    # 特殊條件
    # =========================
    st.subheader("特殊條件")

    Forcing_Chest_ChainKiller = st.checkbox("強制連環殺手")
    
    # =========================
    # 篩選條件
    # =========================
    st.subheader("傷害門檻")

    use_first = st.checkbox("第一擊門檻", value=False)
    first_min = st.number_input("第一擊門檻值 (預設單人英雄紫怪)", value=6360822)

    use_second = st.checkbox("第二擊門檻", value=False)
    second_min = st.number_input("第二擊門檻值 (預設單人傳奇金怪)", value=14752327)

    use_upper = st.checkbox("上限門檻", value=False)
    upper_min = st.number_input("上限門檻值 (預設四人傳奇金怪)", value=25172179)

    # =========================
    # 排序條件
    # =========================
    st.subheader("排序")

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
    "weapon_mod": weapon_mod,
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
                weapon_dmg = r["first_hit"] / (( 1 + stats.get("HSD")/100 )*( 1 + stats.get("TWD")/100 )*( 1 + stats.get("DTTOOC")/100 ))
                row.update({
                    "武器傷害": format_number(int(weapon_dmg)),
                    "爆頭傷害": f"{stats.get('HSD'):.1f}%",
                    "對掩體外傷害": f"{int(stats.get('DTTOOC'))}%"
                })
                
            table.append(row)

        df = pd.DataFrame(table)

        st.dataframe(df)
        
        if len(results) == 0:
            st.write("無符合傷害門檻之裝備組合，建議提高數值或調整修改器搭配、或是改用其他武器")

with st.sidebar:
    st.title("匯出參數")
    if st.button("儲存計算參數分享碼 (beta)"):
        code = encode_build_v2(
            agent_config,
            query_config,
            Forcing_Chest_ChainKiller,
            Activate_Sesonal_Modifier,
            season_bonus    
        )
        st.session_state.share_code = code
        if "share_code" in st.session_state:
            code = st.session_state.share_code
            st.code(code)
    
    st.title("匯入參數")
    import_from_code = st.text_input("請貼上分享碼 (beta)")
    if st.button("載入分享碼"):
        try:
            ac, qc, fck, season_on, sb = decode_build_redirect(import_from_code)
            # 將參數暫時 update 到 st.session_state 而不是直接放進正式參數
            st.session_state.update({
                "agent_watch": ac["agent_watch"],
                "agent_class": ac["agent_class"],
                "weapon": ac["weapon"],
                "weapon_grade": ac["weapon_grade"],
                "equip_core": ac["equip_core"],
                "equip_sub": ac["equip_sub"],
                "mods": ac["mods"],
                "weapon_mod": ac.get("weapon_mod", {}),
                "weapon_prototype": ac["weapon_prototype"],
                "Forcing_Chest_ChainKiller": fck,
                "season_bonus": sb
            })

            st.session_state.import_success = True
            st.rerun()
            
        except Exception as e:
            st.session_state.import_error = str(e)
            st.rerun()
    
    if st.session_state.get("import_success"):
        st.success("載入成功")
        st.caption("(後台已儲存參數、自動更新參數功能正在開發中)")
        # st.write(st.session_state)
        st.session_state.import_success = False
        
    if st.session_state.get("import_error"):
        st.error("分享碼錯誤")
        st.session_state.import_error = None