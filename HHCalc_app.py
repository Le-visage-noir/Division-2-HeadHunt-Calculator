import streamlit as st
import pandas as pd
from HeadHuntCalc_division2_Y8S1_TU27 import run_calculation
from HHCalc_code import decode_build_redirect, encode_build_v2

st.title("Division 2 堅定獵頭配裝計算器")
st.subheader("適用版本 Y8S1 / TU27")
st.caption("Author: Le-visage-noir")

if "run" not in st.session_state: # 各 tab 共通按鈕
    st.session_state.run = False

# =========================
# 選項列表 (給 index 還原用)
# =========================
AGENT_CLASS_OPTIONS = ["精準射手 (爆頭傷害 15 %)", "爆破專家 (對掩體外傷害 5 %)", "其他"]
WEAPON_OPTIONS = ["1886", "SR-1", "白色死神", "戰術.308"]
 
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
    "1886": {}
}
 
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

def find_weapon_mod_index(weapon_name, weapon_mod_dict):
    options = WEAPON_MOD_OPTIONS.get(weapon_name, {})
    for i, (label, val) in enumerate(options.items()):
        if val == weapon_mod_dict:
            return i
    return 0

# =========================
# 核心設計：
#   Streamlit 規則：widget key 在「本次 rerun 尚未渲染前」可以直接寫入 session_state。
#   匯入流程：
#     1. 匯入時把所有值存入 _import_data，呼叫 st.rerun()
#     2. rerun 開頭（所有 widget 渲染前），偵測到 _import_data 就直接寫入 widget key
#     3. 接著正常渲染 widget，此時 session_state 已有正確值，widget 會顯示正確內容
# =========================
 
if "run" not in st.session_state:
    st.session_state.run = False
    
# 為 number_input 設定初始預設值（只在 key 不存在時才設定，不覆蓋匯入值）
_number_input_defaults = {
    "agent_watch": 1000,
    "weapon_grade": 0,
    "mod1": 10.0,
    "mod2": 10.0,
    "mod3": 10.0,
}
for _k, _v in _number_input_defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v
 
# 在所有 widget 渲染前，若有匯入資料則寫入 session_state
if "_import_data" in st.session_state:
    imp = st.session_state.pop("_import_data")
    weapon_for_import = imp.get("weapon", WEAPON_OPTIONS[0])
 
    # 直接寫入 widget key — 此時 widget 尚未建立，Streamlit 允許寫入
    st.session_state["agent_watch"]               = int(imp.get("agent_watch", 1000))
    st.session_state["agent_class"]               = imp.get("agent_class", AGENT_CLASS_OPTIONS[0])
    st.session_state["weapon"]                    = weapon_for_import
    st.session_state["weapon_grade"]              = int(imp.get("weapon_grade", 0))
    st.session_state["equip_core"]                = int(imp.get("equip_core", 6))
    st.session_state["equip_sub"]                 = int(imp.get("equip_sub", 6))
    st.session_state["mod1"]                      = float(imp.get("mod1", 10.0))
    st.session_state["mod2"]                      = float(imp.get("mod2", 10.0))
    st.session_state["mod3"]                      = float(imp.get("mod3", 10.0))
    st.session_state["use_prototype"]             = imp.get("use_prototype", False)
    st.session_state["Forcing_Chest_ChainKiller"] = imp.get("Forcing_Chest_ChainKiller", False)
    st.session_state["Activate_Sesonal_Modifier"] = imp.get("Activate_Sesonal_Modifier", False)
    st.session_state["season_hsd"]                = float(imp.get("season_hsd", 0.0))
    st.session_state["season_awd"]                = float(imp.get("season_awd", 0.0))
    st.session_state["season_twd"]                = float(imp.get("season_twd", 0.0))
    # selected_mod 需要換算成 label
    mod_options = WEAPON_MOD_OPTIONS.get(weapon_for_import, {})
    mod_index = find_weapon_mod_index(weapon_for_import, imp.get("weapon_mod", {}))
    mod_labels = list(mod_options.keys())
    if mod_labels:
        st.session_state["selected_mod"] = mod_labels[mod_index]
    # proto sliders
    proto_stats = imp.get("weapon_prototype_stats", {})
    for k, v in proto_stats.items():
        st.session_state[f"proto_{k}"] = float(v)
 
tab1, tab2, tab3 = st.tabs(["數值設定", "篩選條件", "計算結果"])

# =========================
# 分頁 1 數值設定
# =========================
with tab1:
    
    if st.button("開始計算", key="run_tab1"):
        st.session_state.run = True
        st.write("計算結果已更新，請切換到該分頁查看")
 
    st.subheader("玩家設定")
 
    agent_watch = st.number_input(
        "手錶等級 (僅區分 1000 以上及以下)",
        step=1,
        key="agent_watch"
    )
 
    agent_class = st.selectbox(
        "特化職業", AGENT_CLASS_OPTIONS,
        key="agent_class"
    )
 
    st.subheader("武器")
 
    weapon = st.selectbox(
        "選擇武器", WEAPON_OPTIONS,
        key="weapon"
    )
 
    mod_options = WEAPON_MOD_OPTIONS.get(weapon, {})
    weapon_mod = None
 
    if len(mod_options) == 0:
        st.info("此武器無影響堅定獵頭傷害計算的模組")
    else:
        selected_mod = st.selectbox(
            "選擇瞄準具", list(mod_options.keys()),
            key="selected_mod"
        )
        weapon_mod = mod_options[selected_mod]
 
    weapon_grade = st.number_input(
        "武器專精等級",
        step=1,
        key="weapon_grade"
    )
    
    # =========================
    # 原型武器
    # =========================

    use_prototype = st.checkbox(
        "啟用原型武器 (非原型武器預設數值為全滿)",
        key="use_prototype"
    )
    prototype_stats = {}
    spec = PROTOTYPE_SPEC.get(weapon, {})
 
    if not use_prototype:
        for k, meta in spec.items():
            prototype_stats[k] = meta["min"]
    else:
        for k, meta in spec.items():
            is_int = (k == "DTTOOC")
            default_val = float(st.session_state.get(f"proto_{k}", meta["max"]))
            val = st.slider(
                meta["label"],
                min_value=float(meta["min"]),
                max_value=float(meta["max"]),
                value=default_val,
                step=1.0 if is_int else 0.1,
                key=f"proto_{k}"
            )
            prototype_stats[k] = int(val) if is_int else round(val, 1)
 
    weapon_prototype = {"enabled": use_prototype, "stats": prototype_stats}
 
    weapon_prototype = {"enabled": use_prototype, "stats": prototype_stats}

    st.subheader("裝備")
 
    equip_core = st.selectbox(
        "裝備紅核心數量 (預設 15 %)", list(range(7)),
        key="equip_core"
    )
    equip_sub = st.selectbox(
        "裝備爆頭詞條數量 (預設 10 %)", list(range(7)),
        key="equip_sub"
    )
 
    mod1 = st.number_input("裝備模組 1 (爆頭傷害)", key="mod1")
    mod2 = st.number_input("裝備模組 2 (爆頭傷害)", key="mod2")
    mod3 = st.number_input("裝備模組 3 (爆頭傷害)", key="mod3")
    mods = [mod1, mod2, mod3]

    # =========================
    # 賽季加成
    # =========================
    st.subheader("賽季加成")
 
    Activate_Sesonal_Modifier = st.checkbox(
        "啟用賽季加成 (beta)",
        key="Activate_Sesonal_Modifier"
    )
    season_bonus = {}
 
    if Activate_Sesonal_Modifier:
        season_hsd = st.number_input("爆頭傷害加成", key="season_hsd")
        season_awd = st.number_input("武器傷害加成", key="season_awd")
        season_twd = st.number_input("總武器傷害加成", key="season_twd")
        season_bonus = {"HSD": season_hsd, "AWD": season_awd, "TWD": season_twd}

with tab2:
    
    if st.button("開始計算", key="run_tab2"):
        st.session_state.run = True
        st.write("計算結果已更新，請切換到該分頁查看")
    
    # =========================
    # 特殊條件
    # =========================
    st.subheader("特殊條件")
    Forcing_Chest_ChainKiller = st.checkbox(
        "強制連環殺手",
        key="Forcing_Chest_ChainKiller"
    )
    
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
    sort_key_display = st.selectbox("排序依據", ["第一擊", "第二擊", "上限"], index=0)
    sort_key_map = {"第一擊": "first_hit", "第二擊": "second_hit", "上限": "upper_limit"}
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
        "first_hit":   {"enabled": use_first,  "min": first_min},
        "second_hit":  {"enabled": use_second, "min": second_min},
        "upper_limit": {"enabled": use_upper,  "min": upper_min}
    },
    "sort": {"key": sort_key, "descending": descending},
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
            agent_config, query_config,
            Forcing_Chest_ChainKiller, Activate_Sesonal_Modifier,
            season_bonus
        )
        st.session_state.share_code = code
 
    if "share_code" in st.session_state:
        st.code(st.session_state.share_code)
 
    st.title("匯入參數")
    import_from_code = st.text_input("請貼上分享碼 (beta)")
    if st.button("載入分享碼"):
        try:
            ac, qc, fck, season_on, sb = decode_build_redirect(import_from_code)
            mods  = ac.get("mods", [10.0, 10.0, 10.0])
            proto = ac.get("weapon_prototype", {})
 
            # 把所有值打包進 _import_data，rerun 後在腳本頂部寫入 session_state
            st.session_state["_import_data"] = {
                "agent_watch":            int(ac["agent_watch"]),
                "agent_class":            ac["agent_class"],
                "weapon":                 ac["weapon"],
                "weapon_grade":           int(ac["weapon_grade"]),
                "equip_core":             int(ac["equip_core"]),
                "equip_sub":              int(ac["equip_sub"]),
                "mod1":                   float(mods[0]),
                "mod2":                   float(mods[1]),
                "mod3":                   float(mods[2]),
                "use_prototype":          proto.get("enabled", False),
                "Forcing_Chest_ChainKiller": fck,
                "Activate_Sesonal_Modifier": season_on,
                "season_hsd":             float(sb.get("HSD", 0.0)),
                "season_awd":             float(sb.get("AWD", 0.0)),
                "season_twd":             float(sb.get("TWD", 0.0)),
                "weapon_mod":             ac.get("weapon_mod", {}),
                "weapon_prototype_stats": proto.get("stats", {}),
            }
            st.session_state.import_success = True
            st.rerun()
 
        except Exception as e:
            import traceback
            st.session_state.import_error = f"{e}\n{traceback.format_exc()}"
            st.rerun()
 
    if st.session_state.get("import_success"):
        st.success("載入成功")
        st.caption("(後台已儲存參數、自動更新參數功能正在開發中)")
        st.session_state.import_success = False
 
    if st.session_state.get("import_error"):
        st.error("分享碼錯誤")
        st.code(st.session_state.import_error)
        st.session_state.import_error = None