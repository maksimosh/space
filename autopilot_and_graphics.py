import krpc
import time
import threading
import matplotlib.pyplot as plt


altitudes = []
speeds = []
timestamps = []
masses = []

conn = krpc.connect(name='Lunar Rover Autopilot')

# Получаем доступ к управляемому кораблю
vessel = conn.space_center.active_vessel

# Определяем высоты для отсоединения ступеней
stage1_separation_time = 121  # Время для отсоединения первой ступени
stage2_separation_time = 211.1  # Время для отсоединения второй ступени
stage3_separation_time = 240  # Время для отсоединения третьей ступени

# Запускаем двигатели
vessel.control.throttle = 1.0
vessel.control.activate_next_stage()  # Активация первой стадии


def rocket_autopilot():
    start_time = time.time()
    while time.time() - start_time < stage1_separation_time:
        time.sleep(1)
    # Отсоединение первой ступени
    vessel.control.throttle = 0  # Отключаем двигатели
    time.sleep(1)
    vessel.control.activate_next_stage()  # Отсоединение первой ступени
    print("Первая ступень отсоединена.")
    time.sleep(2)  # Ждем некоторое время для стабилизации
    vessel.control.throttle = 1.0  # Запускаем двигатели второй ступени

    time.sleep(1)

    # отсоединение второй ступени
    start_time = time.time()
    while time.time() - start_time < stage2_separation_time:
        time.sleep(1)
    # Отсоединение второй ступени
    vessel.control.throttle = 0  # Отключаем двигатели
    time.sleep(1)
    vessel.control.activate_next_stage()  # Отсоединение второй ступени
    print("Вторая ступень отсоединена.")
    time.sleep(2)  # Ждем некоторое время для стабилизации
    vessel.control.throttle = 1.0  # Запускаем двигатели третьей ступени

    # отсоединение третьей ступени
    start_time = time.time()
    while time.time() - start_time < stage3_separation_time:
        time.sleep(1)
    vessel.control.activate_next_stage()  # Отсоединение третьей ступени
    print("Третья ступень отсоединена.")


def plot_altitude():
    start_time = time.time()
    while time.time() - start_time < (stage1_separation_time + stage2_separation_time + stage3_separation_time) + 3:
        altitude = vessel.flight().surface_altitude  # Высота над уровнем моря
        altitudes.append(altitude)
        speed = vessel.flight(vessel.orbit.body.reference_frame).speed  # Скорость полета
        speeds.append(speed)
        mass = vessel.mass
        masses.append(mass)
        timestamps.append(time.time() - start_time)  # Время в секундах
        time.sleep(1)  # Сбор данных каждую секунду


altitudes = []
speeds = []
timestamps = []
masses = []


rocket_thread = threading.Thread(target=rocket_autopilot)
plot_thread = threading.Thread(target=plot_altitude)

rocket_thread.start()
plot_thread.start()

rocket_thread.join()
plot_thread.join()


# Построение графика высоты от времени
plt.figure(figsize=(10, 5))
plt.plot(timestamps, altitudes, label='Высота над уровнем моря', color='blue')
plt.title('Изменение высоты корабля во времени')
plt.xlabel('Время (секунды)')
plt.ylabel('Высота (метры)')
plt.legend()
plt.grid()

# Построение графика скорости от времени
plt.figure(figsize=(10, 5))
plt.plot(timestamps, speeds, label='Скорость ракеты', color='blue')
plt.title('Изменение скорости корабля во времени')
plt.xlabel('Время (секунды)')
plt.ylabel('Скорость (метры в секунду)')
plt.legend()
plt.grid()

# Построение графика массы от времени
plt.figure(figsize=(10, 5))
plt.plot(timestamps, masses, label='Масса ракеты', color='blue')
plt.title('Изменение массы корабля во времени')
plt.xlabel('Время (секунды)')
plt.ylabel('Масса (килограммы)')
plt.legend()
plt.grid()

# Построение графика высоты от скорости
plt.figure(figsize=(10, 5))
plt.plot(speeds, altitudes, label='Высота над уровнем моря', color='blue')
plt.title('Изменение высоты корабля от скорости')
plt.xlabel('Скорость (метры в секунду)')
plt.ylabel('Высота (метры)')
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()