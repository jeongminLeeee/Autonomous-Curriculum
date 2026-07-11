# ============================================================
# disaster.py
#
# 재난 상황 생성 모듈
#
# 기능
# ------------------------------------------------------------
# - 지진 붕괴 위험지역 생성
# - 위험지역 관리
# - 피해 확률 계산
# - 환자 생성
# - 위급도 결정
# ============================================================


import random
import math

from patient import Patient, Severity



# ============================================================
# 위험지역 클래스
# ============================================================

class HazardZone:


    def __init__(
        self,
        zone_id,
        x,
        y,
        radius
    ):

        # 위험지역 번호
        self.id = zone_id

        # 중심 좌표
        self.x = x
        self.y = y

        # 영향 반경
        self.radius = radius



    # --------------------------------------------------------
    # 거리 계산
    # --------------------------------------------------------

    def distance_to(
        self,
        x,
        y
    ):

        dx = self.x - x
        dy = self.y - y

        return math.sqrt(
            dx ** 2 +
            dy ** 2
        )



    # --------------------------------------------------------
    # 위험 단계
    # --------------------------------------------------------

    def get_damage_level(
        self,
        x,
        y
    ):

        distance = self.distance_to(
            x,
            y
        )


        ratio = distance / self.radius


        if ratio <= 0.3:
            return "HIGH"

        elif ratio <= 0.7:
            return "MEDIUM"

        else:
            return "LOW"





# ============================================================
# 재난 관리자 클래스
# ============================================================

class Disaster:



    def __init__(
        self,
        width,
        height,
        zone_count=3,
        seed=None
    ):


        self.width = width
        self.height = height


        # 실험 재현용
        if seed is not None:
            random.seed(seed)



        # 위험지역

        self.hazard_zones = []


        # 환자 목록

        self.patients = []



        self.create_hazard_zones(
            zone_count
        )



    # ========================================================
    # 위험지역 생성
    # ========================================================

    def create_hazard_zones(
        self,
        count
    ):


        attempts = 0


        while len(self.hazard_zones) < count:


            attempts += 1


            if attempts > 1000:
                break



            x = random.randint(
                100,
                self.width-100
            )

            y = random.randint(
                100,
                self.height-100
            )


            radius = random.randint(
                150,
                300
            )



            # 기존 위험지역과 너무 가까우면 재생성

            overlap = False


            for zone in self.hazard_zones:

                distance = math.sqrt(
                    (zone.x-x)**2 +
                    (zone.y-y)**2
                )


                if distance < (
                    zone.radius + radius
                ) * 0.5:

                    overlap = True
                    break



            if overlap:
                continue



            zone = HazardZone(
                len(self.hazard_zones)+1,
                x,
                y,
                radius
            )


            self.hazard_zones.append(
                zone
            )





    # ========================================================
    # 가장 가까운 위험지역 거리
    # ========================================================

    def nearest_hazard_distance(
        self,
        x,
        y
    ):


        result = float("inf")


        for zone in self.hazard_zones:

            distance = zone.distance_to(
                x,
                y
            )


            result = min(
                result,
                distance
            )


        return result





    # ========================================================
    # 환자 위치 생성
    #
    # 재난 상황:
    # 위험지역 주변에 피해자 집중
    # ========================================================

    def generate_position(self):


        # 70% 확률
        # 위험지역 주변 생성


        if random.random() < 0.7:


            zone = random.choice(
                self.hazard_zones
            )


            angle = random.uniform(
                0,
                math.pi*2
            )


            distance = random.uniform(
                0,
                zone.radius
            )


            x = (
                zone.x +
                math.cos(angle)
                *
                distance
            )


            y = (
                zone.y +
                math.sin(angle)
                *
                distance
            )


        else:


            x = random.randint(
                0,
                self.width
            )


            y = random.randint(
                0,
                self.height
            )



        # 지도 밖 방지

        x = max(
            0,
            min(
                self.width,
                x
            )
        )


        y = max(
            0,
            min(
                self.height,
                y
            )
        )


        return x, y





    # ========================================================
    # 위급도 결정
    # ========================================================

    def generate_severity(
        self,
        x,
        y
    ):


        distance = self.nearest_hazard_distance(
            x,
            y
        )



        # 가까움

        if distance < 100:


            r = random.random()


            if r < 0.6:
                return Severity.RED


            elif r < 0.9:
                return Severity.YELLOW


            else:
                return Severity.GREEN




        # 중간

        elif distance < 250:


            r = random.random()


            if r < 0.25:
                return Severity.RED


            elif r < 0.7:
                return Severity.YELLOW


            else:
                return Severity.GREEN




        # 멀리


        else:


            r = random.random()


            if r < 0.05:
                return Severity.RED


            elif r < 0.25:
                return Severity.YELLOW


            else:
                return Severity.GREEN





    # ========================================================
    # 환자 1명 생성
    # ========================================================

    def create_patient(
        self,
        patient_id
    ):


        x, y = self.generate_position()



        severity = self.generate_severity(
            x,
            y
        )



        patient = Patient(
            patient_id,
            x,
            y,
            severity
        )



        self.patients.append(
            patient
        )



        return patient





    # ========================================================
    # 여러 환자 생성
    # ========================================================

    def generate_patients(
        self,
        count
    ):


        result = []


        for i in range(count):

            patient = self.create_patient(
                i+1
            )

            result.append(
                patient
            )


        return result





    # ========================================================
    # 위험지역 정보 반환
    # ========================================================

    def get_hazard_data(self):


        data = []


        for zone in self.hazard_zones:


            data.append(
                {
                    "id": zone.id,
                    "x": zone.x,
                    "y": zone.y,
                    "radius": zone.radius
                }
            )


        return data





    # ========================================================
    # 초기화
    # ========================================================

    def reset(self):

        self.patients.clear()



    # ========================================================
    # 상태 출력
    # ========================================================

    def print_status(self):


        print("="*50)

        print("재난 시뮬레이션")

        print(
            f"위험지역 : {len(self.hazard_zones)}개"
        )

        print(
            f"생성 환자 : {len(self.patients)}명"
        )


        print("="*50)