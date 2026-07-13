# patient.py

from enum import Enum
import math


# -----------------------------
# 환자 상태
# -----------------------------
class PatientState(Enum):
    MOVING = "Moving"
    WAITING = "Waiting"
    TREATING = "Treating"
    DEAD = "Dead"
    FINISHED = "Finished"


# -----------------------------
# 위급도
# -----------------------------
class Severity(Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


# -----------------------------
# 환자 클래스
# -----------------------------
class Patient:

    def __init__(self, patient_id, x, y, severity):

        self.id = patient_id

        # 현재 위치
        self.x = x
        self.y = y

        # 위급도
        self.severity = severity

        # 현재 상태
        self.state = PatientState.MOVING

        # 목표 병원
        self.target_hospital = None

        # 현재 치료 중인 병원
        self.current_hospital = None

        # 생성 시간
        self.created_time = 0

        # 병원 도착 시간
        self.arrival_time = None

        # 치료 시작 시간
        self.start_treatment_time = None

        # 치료 종료 시간
        self.finish_time = None

        # 대기 시간
        self.waiting_time = 0

        # 사망 여부
        self.dead = False

        # 사망 위치
        self.death_x = None
        self.death_y = None

        # -----------------------------
        # 위급도별 설정
        # -----------------------------
        if severity == Severity.RED:
            self.move_speed = 0.5          # m/s
            self.treatment_time = 20 * 60  # 20분
            self.remaining_survival = 10 * 60  # 10분

        elif severity == Severity.YELLOW:
            self.move_speed = 1.0
            self.treatment_time = 10 * 60
            self.remaining_survival = 20 * 60

        else:
            self.move_speed = 1.4
            self.treatment_time = 5 * 60
            self.remaining_survival = math.inf

    # ----------------------------------
    # 목표 병원 설정
    # ----------------------------------
    def set_target(self, hospital):
        self.target_hospital = hospital

    # ----------------------------------
    # 목표 병원까지 거리
    # ----------------------------------
    def distance_to_target(self):

        if self.target_hospital is None:
            return None

        dx = self.target_hospital.x - self.x
        dy = self.target_hospital.y - self.y

        return math.sqrt(dx * dx + dy * dy)

    # ----------------------------------
    # 이동
    # ----------------------------------
    def move(self):

        if self.target_hospital is None:
            return

        if self.state != PatientState.MOVING:
            return

        dx = self.target_hospital.x - self.x
        dy = self.target_hospital.y - self.y

        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance == 0:
            self.state = PatientState.WAITING
            return

        step = min(self.move_speed, distance)

        self.x += dx / distance * step
        self.y += dy / distance * step

        if self.distance_to_target() <= 1:
            self.state = PatientState.WAITING

        print(
            f"Patient {self.id}: ({self.x:.6f}, {self.y:.6f})"
        )    

    # ----------------------------------
    # 생존 시간 감소
    # ----------------------------------
    def update_survival(self, dt):

        if self.state in (
                PatientState.DEAD,
                PatientState.FINISHED):
            return

        if self.severity == Severity.GREEN:
            return

        self.remaining_survival -= dt

        if self.remaining_survival <= 0:
            self.die()

    # ----------------------------------
    # 치료 시작
    # ----------------------------------
    def start_treatment(self, hospital=None):

        self.state = PatientState.TREATING

        if hospital is not None:
            self.current_hospital = hospital

    # ----------------------------------
    # 치료 진행
    # ----------------------------------
    def update_treatment(self, dt):

        if self.state != PatientState.TREATING:
            return

        self.treatment_time -= dt

        if self.treatment_time <= 0:
            self.finish()

    # ----------------------------------
    # 치료 완료
    # ----------------------------------
    def finish(self):

        self.state = PatientState.FINISHED

    # ----------------------------------
    # 사망
    # ----------------------------------
    def die(self):

        self.state = PatientState.DEAD
        self.dead = True

        self.death_x = self.x
        self.death_y = self.y

    # ----------------------------------
    # 문자열 출력
    # ----------------------------------
    def __str__(self):

        return (
            f"Patient("
            f"id={self.id}, "
            f"severity={self.severity.name}, "
            f"state={self.state.name})"
        )
