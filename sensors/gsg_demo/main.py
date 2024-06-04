from quat_utils import quat_multiply
import numpy as np
from rk4_utils import rk4

# Definišemo početnu i krajnju brzinu rotacije
w0 = np.array([0.0, 0.1, 0.0])  # Početna brzina rotacije (u rad/s)
w1 = np.array([0.0, 0.2, 0.0])  # Krajnja brzina rotacije (u rad/s)
dt = 1.0  # Korak vremena (u sekundama)

# Predviđamo delta kvaternion koristeći RK4
delta_quat = rk4(w0, w1, dt)

# Početna orijentacija (neutralna)
start_orientation = np.array([1.0, 0.0, 0.0, 0.0])

# Primenjujemo delta kvaternion na početnu orijentaciju
end_orientation = quat_multiply(delta_quat, start_orientation)

# Prikazujemo rezultat
print("Početna orijentacija:", start_orientation)
print("Krajnja orijentacija:", end_orientation)

if __name__ == '__main__':
    pass