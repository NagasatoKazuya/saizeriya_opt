import pandas as pd
import numpy as np
import cvxpy as cp
import streamlit as st

st.header("サイゼリヤメニューのPFC組み合わせ最適化アプリ")

menu = pd.read_excel("saizeriya.xlsx")
menu = menu.dropna()
menu.reset_index(drop=True, inplace=True)
menu.index += 1

price = np.array(menu["price"])
kcal = np.array(menu["kcal"])
protein = np.array(menu["P"])
fat = np.array(menu["F"])
carbo = np.array(menu["C"])

condition_dict = {
    "金額": price,
    "カロリー": kcal,
    "タンパク質": protein,
    "脂質": fat,
    "炭水化物": carbo,
}


x = cp.Variable(len(menu), boolean=True)

opt_list = st.radio(
    "どれを最適化する？", ["金額", "カロリー", "タンパク質", "脂質", "炭水化物"]
)
opt_condition = st.radio("上記項目をどうする？", ["最大化", "最小化"])
if opt_condition == "最大化":
    objective = cp.Maximize(condition_dict[opt_list] @ x)
else:
    objective = cp.Minimize(condition_dict[opt_list] @ x)

constraints = []


st.write("条件を指定する項目は？")
if st.checkbox("金額"):
    min_price, max_price = st.slider(
        label="金額(円)の範囲は？",
        min_value=0,
        max_value=3000,
        value=(0, 1000),
    )
    constraints += [max_price >= price @ x]
    constraints += [min_price <= price @ x]

if st.checkbox("カロリー"):
    min_kcal, max_kcal = st.slider(
        label="カロリー(kcal)の範囲は？",
        min_value=0,
        max_value=2000,
        value=(500, 1000),
    )
    constraints += [max_kcal >= kcal @ x]
    constraints += [min_kcal <= kcal @ x]

if st.checkbox("タンパク質"):
    min_P, max_P = st.slider(
        label="タンパク質(g)の範囲は？",
        min_value=0,
        max_value=200,
        value=(0, 50),
    )
    constraints += [max_P >= protein @ x]
    constraints += [min_P <= protein @ x]

if st.checkbox("脂質"):
    min_F, max_F = st.slider(
        label="脂質(g)の範囲は？",
        min_value=0,
        max_value=200,
        value=(0, 50),
    )
    constraints += [max_F >= fat @ x]
    constraints += [min_F <= fat @ x]

if st.checkbox("炭水化物"):
    min_C, max_C = st.slider(
        label="炭水化物(g)の範囲は？",
        min_value=0,
        max_value=200,
        value=(0, 50),
    )
    constraints += [max_C >= carbo @ x]
    constraints += [min_C <= carbo @ x]

if st.button("最適化する"):
    prob = cp.Problem(objective, constraints)
    prob.solve(solver=cp.ECOS_BB)
    result = []
    for i in range(len(x.value)):
        if x.value[i] >= 0.5:
            result.append(1)
        else:
            result.append(0)
    result = np.array(result)
    # result = x.value.astype(int)

    # st.write("status :", prob.status)
    st.write("金額 :", price @ result, "yen")
    st.write("カロリー :", kcal @ result, "kcal")
    st.write("{}の最適値".format(opt_list), round(prob.value, 1), "g")
    st.write("メニュー :", menu[result == 1][["name", "price", "kcal", "P", "F", "C"]])
