# ============================================================
# animation.py
#
# 재난 의료 시뮬레이션 애니메이션
#
# Part 1 / 2
# ------------------------------------------------------------
# - 애니메이션 클래스
# - 초기화
# - 지도 설정
# - 환자/병원 데이터 연결
# ============================================================


import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import osmnx as ox

from patient import PatientState



class SimulationAnimation:
    """
    재난 의료 시뮬레이션 시각화 클래스


    기능
    ----------------------------
    - 환자 위치 표시
    - 환자 상태별 색상 표시
    - 병원 위치 표시
    - 시간 흐름 표현
    """



    # ========================================================
    # 생성자
    # ========================================================

    def __init__(
        self,
        simulation
    ):


        # simulation 연결

        self.simulation = simulation



        # history 데이터

        self.history = (
            simulation.history
        )



        # 지도 이미지

        self.map_loader = None



        # matplotlib 설정

        self.fig, self.ax = (
            plt.subplots(
                figsize=(8,8)
            )
        )



        # 환자 표시 객체

        self.patient_scatter = None



        # 병원 표시 객체

        self.hospital_scatter = None



        # 시간 표시

        self.time_text = None



        # 병원 정보 표시

        self.info_text = None




    # ========================================================
    # 초기 화면 설정
    # ========================================================

    def setup(self):


        self.ax.clear()



        # -------------------------
        # 지도 표시
        # -------------------------

        self.map_loader = self.simulation.map_loader

        ox.plot_graph(
            self.map_loader.graph,
            ax=self.ax,
            node_size=0,
            edge_color="gray",
            edge_linewidth=0.5,
            bgcolor="white",
            show=False,
            close=False
        )



        # -------------------------
        # 축 설정
        # -------------------------

        self.ax.set_title(
            "Disaster Medical Simulation"
        )


        boundary = self.map_loader.get_boundary()

        self.ax.set_xlim(
            boundary["west"],
            boundary["east"]
        )

        self.ax.set_ylim(
            boundary["south"],
            boundary["north"]
        )



        # -------------------------
        # 병원 위치 초기 표시
        # -------------------------

        hospital_x = []

        hospital_y = []



        for hospital in self.simulation.hospitals:


            hospital_x.append(
                hospital.x
            )


            hospital_y.append(
                hospital.y
            )



        self.hospital_scatter = (

            self.ax.scatter(

                hospital_x,

                hospital_y,

                marker="^",

                s=150,

                label="Hospital"

            )

        )



        # -------------------------
        # 환자 초기 표시
        # -------------------------

        self.patient_scatter = (

            self.ax.scatter(

                [],

                [],

                s=30,

                c="red"

            )

        )



        # 시간 표시

        self.time_text = (

            self.ax.text(

                0.02,

                0.95,

                "",

                transform=self.ax.transAxes

            )

        )



        # 병원 상태 표시

        self.info_text = (

            self.ax.text(

                0.02,

                0.02,

                "",

                transform=self.ax.transAxes

            )

        )



        return (

            self.patient_scatter,

            self.hospital_scatter,

            self.time_text,

            self.info_text

        )



    # ========================================================
    # 환자 색상 결정
    # ========================================================

    def get_patient_color(
        self,
        severity,
        state
    ):


        # 사망

        if state == "Dead":

            return "black"



        # 중증

        if severity == "RED":

            return "red"



        # 중등도

        if severity == "YELLOW":

            return "yellow"



        # 경상

        return "green"



# ============================================================
# Part 2 / 2 에서 계속
# ============================================================
# ============================================================
# animation.py
#
# Part 2 / 2
# ------------------------------------------------------------
# - 프레임 업데이트
# - 애니메이션 실행
# - 저장 기능
# ============================================================



    # ========================================================
    # 프레임 업데이트
    # ========================================================

    def update(
        self,
        frame
    ):

        """
        특정 시간의 화면 갱신

        frame:
            history index
        """



        if frame >= len(self.history):

            return



        data = self.history[frame]



        # -------------------------
        # 환자 데이터
        # -------------------------

        x = []

        y = []

        colors = []



        for patient in data["patients"]:

            print(patient)
            x.append(
                patient["x"]
            )


            y.append(
                patient["y"]
            )



            colors.append(

                self.get_patient_color(

                    patient["severity"],

                    patient["state"]

                )

            )



        # 환자 위치 갱신
        
        print("환자 수:", len(x))
        print("x =", x[:5])
        print("y =", y[:5])


        self.patient_scatter.set_offsets(

            list(

                zip(

                    x,

                    y

                )

            )

        )



        self.patient_scatter.set_color(

            colors

        )



        # -------------------------
        # 시간 표시
        # -------------------------

        self.time_text.set_text(

            f"Time : {data['time']} sec"

        )



        # -------------------------
        # 병원 상태 표시
        # -------------------------

        info = "Hospital Status\n"



        for hospital in data["hospitals"]:


            info += (

                f"H{hospital['id']} "

                f"W:{hospital['waiting']} "

                f"T:{hospital['treating']}\n"

            )



        self.info_text.set_text(

            info

        )



        return (

            self.patient_scatter,
            self.hospital_scatter,
            self.time_text,
            self.info_text

        )




    # ========================================================
    # 애니메이션 실행
    # ========================================================

    def show(
        self,
        interval=100
    ):

        """
        화면 출력

        interval:
            프레임 간격(ms)
        """



        self.setup()



        self.animation = FuncAnimation(

            self.fig,

            self.update,

            frames=len(self.history),

            interval=interval,

            blit=False

        )



        plt.show()



        return self.animation




    # ========================================================
    # 영상 저장
    # ========================================================

    def save(
        self,
        filename="simulation.mp4",
        fps=10
    ):

        """
        애니메이션 저장

        """



        self.setup()



        animation = FuncAnimation(

            self.fig,

            self.update,

            frames=len(self.history),

            interval=100

        )



        animation.save(

            filename,

            fps=fps

        )



    # ========================================================
    # 이미지 한 장 저장
    # ========================================================

    def save_frame(
        self,
        frame,
        filename="frame.png"
    ):

        """
        특정 시간 상태 저장
        """



        self.setup()



        self.update(
            frame
        )



        self.fig.savefig(

            filename

        )



# ============================================================
# 테스트
# ============================================================


if __name__ == "__main__":


    print(
        "animation.py module test"
    )



# ============================================================
# End of animation.py
# ============================================================
