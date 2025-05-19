import streamlit as st

# 대표값 예시
food_c_n = 14.81
sludge_c_n = 6.1
pig_c_n = 16.0
cow_c_n = 20.0

food_pH = 4.2
sludge_pH = 7.63
pig_pH = 7.25
cow_pH = 7.25

st.title("🌿 바이오가스 혼합 설계 시뮬레이터")

st.write("지역/계절/기질 선택을 통해 혼합비에 따른 발효 안정성을 예측합니다.")

# 사용자 입력
location = st.text_input("지역 입력 (예: 춘천시, 청주시 등)")
season = st.selectbox("계절 선택", ["봄", "여름", "가을", "겨울"])

materials = st.multiselect("혼합 기질 선택", ["음식물 폐기물", "하수슬러지", "돈분", "우분"])
custom_ratio = st.text_input("혼합 비율 입력 (예: 음식물 60, 슬러지 40) / 미입력 시 자동 제안")

# 계산 버튼
if st.button("시뮬레이션 실행"):
    st.subheader("✅ 혼합 결과 예측")
    
    if not materials:
        st.warning("기질을 최소 2개 이상 선택해주세요!")
    else:
        # 혼합비 계산
        if custom_ratio:
            # 수동 입력값 처리
            try:
                parts = [float(x.strip()) for x in custom_ratio.split(",")]
                if len(parts) != len(materials):
                    st.error("혼합비 개수가 기질 선택 수와 맞지 않습니다!")
                else:
                    total = sum(parts)
                    ratios = [x / total for x in parts]
            except:
                st.error("혼합비 입력 형식이 잘못되었습니다. 예: 60, 40")
                ratios = None
        else:
            # 비율 미입력 → 자동 균등 배분
            ratios = [1 / len(materials)] * len(materials)

        if ratios:
            # 기질별 C/N, pH 매핑
            cn_map = {
                "음식물 폐기물": food_c_n,
                "하수슬러지": sludge_c_n,
                "돈분": pig_c_n,
                "우분": cow_c_n
            }
            ph_map = {
                "음식물 폐기물": food_pH,
                "하수슬러지": sludge_pH,
                "돈분": pig_pH,
                "우분": cow_pH
            }

            mix_cn = sum([ratios[i] * cn_map[materials[i]] for i in range(len(materials))])
            mix_pH = sum([ratios[i] * ph_map[materials[i]] for i in range(len(materials))])

            st.write(f"**혼합 C/N 비율:** {mix_cn:.2f}")
            st.write(f"**혼합 pH:** {mix_pH:.2f}")

            # 판정 메시지
            if mix_cn < 15:
                st.warning("C/N 비가 낮습니다 → 탄소원 보완 필요")
            elif mix_cn > 30:
                st.warning("C/N 비가 너무 높습니다 → 질소원 보완 필요")
            else:
                st.success("C/N 비 적정 범위입니다")

            if mix_pH < 6.5 or mix_pH > 8.5:
                st.warning("pH 범위가 불안정합니다 → 슬러지/알칼리제 조절 필요")
            else:
                st.success("pH 안정 범위입니다")

