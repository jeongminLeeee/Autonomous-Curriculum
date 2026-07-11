# ============================================================
# pmedian.py
#
# p-Median 알고리즘
#
# 기능
# ------------------------------------------------------------
# - 후보 의료시설 중 p개 선택
# - 환자 이동거리 최소화
# - 기존 재난 의료시설 배치 모델
#
# 특징
# ------------------------------------------------------------
# - 대기시간 고려 X
# - 병목 고려 X
# - 거리만 고려
# ============================================================


import math
import random



# ============================================================
# 거리 계산
# ============================================================

def distance(
    patient,
    hospital
):

    dx = patient.x - hospital.x
    dy = patient.y - hospital.y

    return math.sqrt(
        dx ** 2 +
        dy ** 2
    )



# ============================================================
# 총 이동거리 계산
# ============================================================

def calculate_total_distance(
    patients,
    hospitals
):

    total = 0


    for patient in patients:

        min_distance = float("inf")


        for hospital in hospitals:

            d = distance(
                patient,
                hospital
            )


            if d < min_distance:

                min_distance = d


        total += min_distance


    return total





# ============================================================
# 환자 병원 배정
# ============================================================

def assign_patients(
    patients,
    hospitals
):


    for patient in patients:


        nearest = None

        min_distance = float("inf")



        for hospital in hospitals:


            d = distance(
                patient,
                hospital
            )


            if d < min_distance:

                min_distance = d
                nearest = hospital



        patient.set_target(
            nearest
        )



    return patients





# ============================================================
# 초기 병원 선택
#
# Greedy 방식
#
# 실제 최적해는 MILP 등을 사용하지만
# 시뮬레이션에서는 계산량 때문에 사용
# ============================================================

def greedy_initial_selection(
    candidates,
    patients,
    p
):


    selected = []


    remaining = candidates.copy()



    for _ in range(p):


        best = None

        best_score = float("inf")



        for candidate in remaining:


            temp = selected + [candidate]


            score = calculate_total_distance(
                patients,
                temp
            )


            if score < best_score:

                best_score = score

                best = candidate



        selected.append(
            best
        )


        remaining.remove(
            best
        )



    return selected





# ============================================================
# p-Median 실행
# ============================================================

def solve_pmedian(
    patients,
    candidate_hospitals,
    p
):


    if p >= len(candidate_hospitals):

        return candidate_hospitals



    selected = greedy_initial_selection(
        candidate_hospitals,
        patients,
        p
    )



    assign_patients(
        patients,
        selected
    )



    return selected





# ============================================================
# 결과 출력
# ============================================================

def print_result(
    hospitals
):


    print("="*50)

    print("p-Median 결과")

    print(
        f"선택된 의료시설 : {len(hospitals)}개"
    )


    for hospital in hospitals:


        print(
            f"Hospital {hospital.id}"
            f" : ({hospital.x:.1f}, {hospital.y:.1f})"
        )


    print("="*50)





# ============================================================
# 테스트용 실행
# ============================================================

if __name__ == "__main__":


    print(
        "p-Median module test"
    )