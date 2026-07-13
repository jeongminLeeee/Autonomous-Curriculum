# ============================================================
# pmedian.py
#
# p-Median + 병목 고려 알고리즘
#
# 기능
# ------------------------------------------------------------
# - 후보 의료시설 중 p개 선택
# - 환자 이동거리 최소화
# - 병원 수용량 고려
# - 예상 대기시간 고려
# - 병목 발생 방지
# ============================================================


import math



# ============================================================
# 거리 계산
# ============================================================

def distance(patient, hospital):

    dx = patient.x - hospital.x
    dy = patient.y - hospital.y

    return math.sqrt(
        dx ** 2 +
        dy ** 2
    )



# ============================================================
# 병원별 환자 배정
# ============================================================

def assign_patients(
    patients,
    hospitals
):


    hospital_patients = {
        h.id: []
        for h in hospitals
    }


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


        hospital_patients[
            nearest.id
        ].append(
            patient
        )


    return hospital_patients




# ============================================================
# 병목 비용 계산
#
# 환자수 / 처리능력
#
# 1 이하 : 정상
# 1 초과 : 병목
# ============================================================

def calculate_congestion_cost(
    hospital,
    assigned_patients
):


    patients = len(
        assigned_patients
    )


    capacity = getattr(
        hospital,
        "capacity",
        10
    )


    ratio = patients / capacity



    if ratio <= 1:

        return ratio



    else:

        # 초과하면 급격히 증가

        return ratio ** 2




# ============================================================
# 예상 대기시간 계산
#
# M/M/1 형태 단순 모델
#
# 대기시간 =
# 환자수 / 처리속도
# ============================================================

def calculate_waiting_time(
    hospital,
    assigned_patients
):


    patients = len(
        assigned_patients
    )


    service_rate = getattr(
        hospital,
        "service_rate",
        1
    )


    return patients / service_rate




# ============================================================
# 새로운 목적함수
#
# 거리 + 대기 + 병목
# ============================================================

def calculate_total_cost(
    patients,
    hospitals,
    alpha=5,
    beta=20
):


    assignments = assign_patients(
        patients,
        hospitals
    )


    total_distance = 0

    congestion = 0

    waiting = 0



    for patient in patients:


        total_distance += min(
            distance(
                patient,
                h
            )
            for h in hospitals
        )



    for hospital in hospitals:


        assigned = assignments[
            hospital.id
        ]


        congestion += calculate_congestion_cost(
            hospital,
            assigned
        )


        waiting += calculate_waiting_time(
            hospital,
            assigned
        )



    return (
        total_distance
        +
        alpha * waiting
        +
        beta * congestion
    )




# ============================================================
# Greedy 초기 선택
#
# 병목 포함
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


            temp = selected + [
                candidate
            ]


            score = calculate_total_cost(
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

    print(
        "병목 고려 p-Median 결과"
    )


    print(
        f"선택 의료시설 : {len(hospitals)}개"
    )



    for hospital in hospitals:


        print(
            f"Hospital {hospital.id}"
            f" : ({hospital.x:.1f}, {hospital.y:.1f})"
        )


    print("="*50)



# ============================================================
# 테스트
# ============================================================

if __name__ == "__main__":

    print(
        "p-Median + Congestion module test"
    )
