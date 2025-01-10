import krpc
import time
import threading
import matplotlib.pyplot as plt
import math


conn = krpc.connect(name='Proton-K Autopilot')

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
    while time.time() - start_time < stage1_separation_time + stage2_separation_time + stage3_separation_time + 6:
        altitude = vessel.flight().surface_altitude  # Высота над уровнем моря
        altitudes.append(altitude)
        speed = vessel.flight(vessel.orbit.body.reference_frame).speed  # Скорость полета
        speeds.append(speed)
        mass = vessel.mass
        masses.append(mass)
        timestamps.append(time.time() - start_time)  # Время в секундах
        time.sleep(1)  # Сбор данных каждую секунду


my = []
r = 8.31 #универсальная газовая постоянная
y = 1.22 #показатель адиабаты газа
ts = 3500 #температура газа в камере сгорания (в Кельвинах)
mmrv = 23.5 * 0.001 #молярная масса рабочего вещ-ва
mm1 = 30600
mm2 = 11000
mm3 = 3500
m1 = 428300 / 121
m2 = 157300 / 211.1
m3 = 43062 / 240
m0 = 705000
m = 705000 #начальнаяч масса ракеты в кг
g = 9.8 #ускорение свободного падения постоянное 
v = math.sqrt(((2 * y) / (y - 1)) * ((r * ts) / mmrv)) #скорость вытекания
sm = 38.5 #площадь миделевого сечения 38.5
pl = 1.225 #плотность воздуха на текущей высоте
c = 0.2
v_i = []
s_i = []
t_r = 578 #время за которое хотим узнать высоту ракеты
tr = 572 #время работы всех двигателей
tp = 0
if t_r > tr:
    tp = tr
else:
    tp = t_r
v_i.append(0.0)
s_i.append(0.0)
for t in range(0, tp):
    if t <= 121:
        mt = m1
    elif t <= (211.1 + 121):
        mt = m2
    else:
        mt = m3
    vi1 = v_i[-1]
    si1 = s_i[-1]
    if si1 <= 1000.0:
        pl = 1.112
    elif si1 <= 2000.0:
        pl = 1.007
    elif si1 <= 3000.0:
        pl = 0.909
    elif si1 <= 5000.0:
        pl = 0.736
    elif si1 <= 8000.0:
        pl = 0.526
    elif si1 <= 10000.0:
        pl = 0.414
    elif si1 <= 15000.0:
        pl = 0.195
    elif si1 <= 20000.0:
        pl = 0.089
    else:
        pl = 0.0
    if si1 > 100000.0:
        pl = 0.0
    m = m - mt
    if t == 122:
        m = m - mm1
    elif t == (332):
        m = m - mm2
    elif t == 571:
        m = m - mm3
    else:
        pass
    p = mt * v #текущая тяга двигателя
    x = c * ((pl * vi1 ** 2) / 2) * sm
    dv = ((p - x - m * g) / m)
    vi = vi1 + dv
    si = si1 + vi1
    if si < si1:
        break
    v_i.append(vi)
    s_i.append(si)
    my.append(m)

if t_r > tr:
    for t in range(tr + 1, t_r):
        vi1 = v_i[-1]
        si1 = s_i[-1]
        x = c * ((pl * vi1 ** 2) / 2) * sm
        dv = (((-x) - m * g) / m)
        vi = vi1 + dv
        si = si1 + vi1
        if si < si1:
            break
        v_i.append(vi)
        s_i.append(si)



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


s_i = s_i[:len(timestamps)]
v_i = v_i[:len(timestamps)]
my = my[:len(timestamps)]

# Построение графика высоты от времени
plt.figure(figsize=(10, 5))
plt.plot(timestamps, altitudes, label='Высота над уровнем моря', color='green')
plt.plot(timestamps, s_i, label='Высота над уровнем моря', color='blue')
plt.title('Изменение высоты корабля во времени')
plt.xlabel('Время (секунды)')
plt.ylabel('Высота (метры)')
plt.legend()
plt.grid()

# Построение графика скорости от времени
plt.figure(figsize=(10, 5))
plt.plot(timestamps, speeds, label='Скорость ракеты', color='green')
plt.plot(timestamps, v_i, label='Скорость ракеты', color='blue')
plt.title('Изменение скорости корабля во времени')
plt.xlabel('Время (секунды)')
plt.ylabel('Скорость (метры в секунду)')
plt.legend()
plt.grid()

# Построение графика массы от времени
plt.figure(figsize=(10, 5))
plt.plot(timestamps, masses, label='Масса ракеты', color='green')
plt.plot(timestamps, my, label='Масса ракеты', color='blue')
plt.title('Изменение массы корабля во времени')
plt.xlabel('Время (секунды)')
plt.ylabel('Масса (килограммы)')
plt.legend()
plt.grid()

# Построение графика высоты от скорости
plt.figure(figsize=(10, 5))
plt.plot(speeds, altitudes, label='Высота над уровнем моря', color='green')
plt.plot(speeds, s_i, label='Высота над уровнем моря', color='blue')
plt.title('Изменение высоты корабля от скорости')
plt.xlabel('Скорость (метры в секунду)')
plt.ylabel('Высота (метры)')
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()
