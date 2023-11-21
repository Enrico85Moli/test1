"""
//        ³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³
//        ³                                                           ³
//        ³                                                           ³
//        ³ - autore      : Enrico Molinari                           ³
//        ³ - data        : 08/11/2022                                ³
//        ³ - revisione   : 1.0                                       ³
//        ³ - descrizione : Centrafari-P10Linux                       ³
//        ³               :                                           ³
//        ³               :                                           ³
//        ³               :                                           ³
//        ³               :                                           ³
//        ³               :                                           ³
//        ³  Codice SW    : MW289-12                                  ³
//        ³               :                                           ³
//        ³  Hardware     : Raspberry con monitor 10 pollici (P10L)   ³
//        ³               :                                           ³
//        ³                                                           ³
//        ³                                                           ³
//        ³                                                           ³
//        ³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³
"""

import sys
import socket
import math
import cv2
import numpy as np
from array import *
import tkinter as tk
import os
from tkinter import *
import PIL
from PIL import ImageTk # -> TODO: sudo apt-get install python3-pil.imagetk
import PIL.ImageOps

SCRIPT_VERSION = "V2.8_14/11/2023"

WINDOW_SHIFT_X = 278
WINDOW_SHIFT_Y = 130
WINDOW_WIDTH = 630
WINDOW_HEIGHT = 320

WINDOW_HALF_WIDTH = 315
WINDOW_HALF_HEIGHT = 160
posiz_pattern_x = 0
posiz_pattern_y = 0

lumen_accumul = 0
luminanza = 0
lux_25m = 0
mm_panel_per_pixel = 0.1250
inclinazione_pixel_panel = 0
#
# centroXpx = WINDOW_HALF_WIDTH + (5.0 / mm_panel_per_pixel)
# centroYpx = WINDOW_HALF_HEIGHT + inclinazione_pixel_panel + (5.0 / mm_panel_per_pixel)
centroXpx = WINDOW_HALF_WIDTH + (8.0 / 0.1250)
centroYpx = WINDOW_HALF_HEIGHT + inclinazione_pixel_panel + (3.0 / 0.1250)

# Xpx_in = centroXpx - (3.0 / mm_panel_per_pixel)
# Xpx_fin = centroXpx + (3.0 / mm_panel_per_pixel)
# Ypx_in = centroYpx - (3.0 / mm_panel_per_pixel)
# Ypx_fin = centroYpx + (3.0 / mm_panel_per_pixel)

Xpx_in = centroXpx - (5.0 / 0.1250)
Xpx_fin = centroXpx + (5.0 / 0.1250)
Ypx_in = centroYpx - (1.0 / 0.1250)
Ypx_fin = centroYpx + (1.0 / 0.1250)

offset_glarelight_lux = 0
#
centroXpx_ABB = WINDOW_HALF_WIDTH
centroYpx_ABB = WINDOW_HALF_HEIGHT + inclinazione_pixel_panel
offset_ABBlight_lux = 0

# Xpx_in_ABB = centroXpx_ABB - (3.0 / mm_panel_per_pixel)
# Xpx_fin_ABB = centroXpx_ABB + (3.0 / mm_panel_per_pixel)
# Ypx_in_ABB = centroYpx_ABB - (3.0 / mm_panel_per_pixel)
# Ypx_fin_ABB = centroYpx_ABB + (3.0 / mm_panel_per_pixel)

Xpx_in_ABB = centroXpx_ABB - (3.0 / 0.1250)
Xpx_fin_ABB = centroXpx_ABB + (3.0 / 0.1250)
Ypx_in_ABB = centroYpx_ABB - (3.0 / 0.1250)
Ypx_fin_ABB = centroYpx_ABB + (3.0 / 0.1250)

#

pixels_tac1_tac2 = 10
lunghezza_tac = 5

numero_di_tacche_abbagl_offset_x = -3
numero_di_tacche_abbagl_offset_y = 6

argomenti_passati_script = ["nome_script", "tipo_faro"]
argomenti_passati_script[0] = sys.argv[0]
argomenti_passati_script[1] = sys.argv[1]

replica_da_Proteus = "" # replica_da_Proteus = str(0)
port = int(sys.argv[2]) if len(sys.argv) >= 3 else 28500

msg_cnt = 0
display_croce = 0
pattern = 0
request_start_config = 1

shift1 = (0, -200)
shift2 = (0, 200)
shift3 = (-200, 0)
shift4 = (200, 0)

punto1 = (0, 0)
punto2 = (0, 0)
punto3 = (0, 0)

tol = 10  # in pixels
tolV = 10  # in pixels
tolH = 10  # in pixels
Larghezza_filtro_gaussiano = 21  # in pixels

SL1 = (WINDOW_HALF_WIDTH - tolH, 0)
EL1 = (WINDOW_HALF_WIDTH - tolH, WINDOW_HEIGHT)

SL2 = (WINDOW_HALF_WIDTH + tolH, 0)
EL2 = (WINDOW_HALF_WIDTH + tolH, WINDOW_HEIGHT)

SL3 = (0, WINDOW_HALF_HEIGHT + inclinazione_pixel_panel - tolV)
EL3 = (WINDOW_WIDTH, WINDOW_HALF_HEIGHT + inclinazione_pixel_panel - tolV)

SL4 = (0, WINDOW_HALF_HEIGHT + inclinazione_pixel_panel + tolV)
EL4 = (WINDOW_WIDTH, WINDOW_HALF_HEIGHT + inclinazione_pixel_panel + tolV)

tx_A = 0 # abbagliante
ty_A = 0 # abbagliante
tx_N = 0 # anabbagliante
ty_N = 0 # anabbagliante
tx_F = 0 # fendinebbia
ty_F = 0 # fendinebbia

start_row = 0
end_row = 0
start_col = 0
end_col = 0

lin_dem_anabb_offset_x = -200
lin_dem_anabb_offset_y = 5
lin_dem_anabb_coeff_angol = 0.267949192

lux_su_lineaX_AtH = 200

img_color = np.zeros([WINDOW_HEIGHT, WINDOW_WIDTH, 3], dtype=np.uint8)  # h,w,()

def refresh_mm_panel_per_pix_stuff():
    global centroXpx, centroYpx, Xpx_in, Xpx_fin, Ypx_in, Ypx_fin, Xpx_in_ABB, Xpx_fin_ABB, Ypx_in_ABB, Ypx_fin_ABB
    # centroXpx = WINDOW_HALF_WIDTH + (5.0 / mm_panel_per_pixel)
    centroXpx = WINDOW_HALF_WIDTH + (8.0 / 0.1250)
    # centroYpx = (
    #     WINDOW_HALF_HEIGHT + inclinazione_pixel_panel + (5.0 / mm_panel_per_pixel)
    # )
    centroYpx = (
    WINDOW_HALF_HEIGHT + inclinazione_pixel_panel + (3.0 / 0.1250)
    )
    # Xpx_in = centroXpx - (3.0 / mm_panel_per_pixel)
    # Xpx_fin = centroXpx + (3.0 / mm_panel_per_pixel)
    # Ypx_in = centroYpx - (3.0 / mm_panel_per_pixel)
    # Ypx_fin = centroYpx + (3.0 / mm_panel_per_pixel)
    Xpx_in = centroXpx - (5.0 / 0.1250)
    Xpx_fin = centroXpx + (5.0 / 0.1250)
    Ypx_in = centroYpx - (1.0 / 0.1250)
    Ypx_fin = centroYpx + (1.0 / 0.1250)
    centroYpx_ABB = WINDOW_HALF_HEIGHT + inclinazione_pixel_panel
    # Xpx_in_ABB = centroXpx_ABB - (3.0 / mm_panel_per_pixel)
    # Xpx_fin_ABB = centroXpx_ABB + (3.0 / mm_panel_per_pixel)
    # Ypx_in_ABB = centroYpx_ABB - (3.0 / mm_panel_per_pixel)
    # Ypx_fin_ABB = centroYpx_ABB + (3.0 / mm_panel_per_pixel)
    Xpx_in_ABB = centroXpx_ABB - (3.0 / 0.1250)
    Xpx_fin_ABB = centroXpx_ABB + (3.0 / 0.1250)
    Ypx_in_ABB = centroYpx_ABB - (3.0 / 0.1250)
    Ypx_fin_ABB = centroYpx_ABB + (3.0 / 0.1250)


def somma_xy(coppia1, coppia2):
    return (coppia1[0] + coppia2[0], coppia1[1] + coppia2[1])

def calcola_punto1(max_lux_xy):
    return (max_lux_xy[0]+lin_dem_anabb_offset_x, max_lux_xy[1]+lin_dem_anabb_offset_y) # return (max_lux_xy[0]-100, max_lux_xy[1]+15)

"""
def calcola_punto1(max_lux_xy):
    return (max_lux_xy[0]+0, max_lux_xy[1]+0) # return (max_lux_xy[0]-100, max_lux_xy[1]+15)
"""

def calcola_punto2(point1):
    if argomenti_passati_script[1] == "ANABBAGLIANTE" :
        return (
            point1[0] + WINDOW_HEIGHT, 
            (point1[1] - (int(WINDOW_HEIGHT * lin_dem_anabb_coeff_angol))), # return (point1[0]+altezza_frame, (point1[1]-(int(altezza_frame*0.267949192))))
        )
    elif argomenti_passati_script[1] == "FENDINEBBIA" :
        return (point1[0] + WINDOW_HEIGHT, point1[1])


def calcola_punto3(point1):
    return (point1[0] - WINDOW_HEIGHT, point1[1])


def refresh_tolerance_display():
    global SL1, EL1, SL2, EL2, SL3, EL3, SL4, EL4
    SL1 = (WINDOW_HALF_WIDTH - tolH, 0)
    EL1 = (WINDOW_HALF_WIDTH - tolH, WINDOW_HEIGHT)

    SL2 = (WINDOW_HALF_WIDTH + tolH, 0)
    EL2 = (WINDOW_HALF_WIDTH + tolH, WINDOW_HEIGHT)

    SL3 = (0, WINDOW_HALF_HEIGHT + inclinazione_pixel_panel - tolV)
    EL3 = (WINDOW_WIDTH, WINDOW_HALF_HEIGHT + inclinazione_pixel_panel - tolV)

    SL4 = (0, WINDOW_HALF_HEIGHT + inclinazione_pixel_panel + tolV)
    EL4 = (WINDOW_WIDTH, WINDOW_HALF_HEIGHT + inclinazione_pixel_panel + tolV)


def display_griglia_HV(frame):
    if argomenti_passati_script[1] != "FENDINEBBIA":
        cv2.line(frame, SL1, EL1, (0, 255, 255), 1)
        cv2.line(frame, SL2, EL2, (0, 255, 255), 1)
    cv2.line(frame, SL3, EL3, (0, 255, 255), 1)
    cv2.line(frame, SL4, EL4, (0, 255, 255), 1)


def display_griglia_HV2(sfondo):
    if argomenti_passati_script[1] != "FENDINEBBIA":
        cv2.line(sfondo, SL1, EL1, (0, 255, 255), 1)
        cv2.line(sfondo, SL2, EL2, (0, 255, 255), 1)
    cv2.line(sfondo, SL3, EL3, (0, 255, 255), 1)
    cv2.line(sfondo, SL4, EL4, (0, 255, 255), 1)


def display_griglia_HV3(img_color):
    if argomenti_passati_script[1] != "FENDINEBBIA":
        cv2.line(img_color, SL1, EL1, (0, 0, 0), 1)
        cv2.line(img_color, SL2, EL2, (0, 0, 0), 1)
    cv2.line(img_color, SL3, EL3, (0, 0, 0), 1)
    cv2.line(img_color, SL4, EL4, (0, 0, 0), 1)


def display_scala_graduata_frame(frame):  # Orange / #FFA500 RGB
    cv2.line(frame, (20, 60), (620, 60), (0, 165, 255), 1)  # Line H1
    cv2.line(
        frame,
        (WINDOW_HALF_WIDTH, 60),
        (WINDOW_HALF_WIDTH, 60 + lunghezza_tac),
        (0, 165, 255),
        1,
    )  # tacchetta centrale
    for tac in range(1, 29, 1):
        cv2.line(
            frame,
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 60),
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 60 + lunghezza_tac),
            (0, 165, 255),
            1,
        )  # tacchette
        cv2.line(
            frame,
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 60),
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 60 + lunghezza_tac),
            (0, 165, 255),
            1,
        )  # tacchette

    cv2.line(frame, (20, 260), (620, 260), (0, 165, 255), 1)  # Line H2
    cv2.line(
        frame,
        (WINDOW_HALF_WIDTH, 260),
        (WINDOW_HALF_WIDTH, 260 - lunghezza_tac),
        (0, 165, 255),
        1,
    )  # tacchetta centrale
    for tac in range(1, 29, 1):
        cv2.line(
            frame,
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 260),
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 260 - lunghezza_tac),
            (0, 165, 255),
            1,
        )  # tacchette
        cv2.line(
            frame,
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 260),
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 260 - lunghezza_tac),
            (0, 165, 255),
            1,
        )  # tacchette

    cv2.line(
        frame, (20, 60), (20, 260), (0, 165, 255), 1
    )  # Line V1 - cv2.line(frame, (20,60), (20,420), (0,165,255), 1)
    cv2.line(
        frame,
        (20, WINDOW_HALF_HEIGHT),
        (20 + lunghezza_tac, WINDOW_HALF_HEIGHT),
        (0, 165, 255),
        1,
    )  # tacchetta centrale
    for tac in range(1, 9, 1):  # for tac in range( 1, 17, 1 ):
        cv2.line(
            frame,
            (20, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (20 + lunghezza_tac, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (0, 165, 255),
            1,
        )  # tacchette
        cv2.line(
            frame,
            (20, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (20 + lunghezza_tac, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (0, 165, 255),
            1,
        )  # tacchette

    cv2.line(
        frame, (620, 60), (620, 260), (0, 165, 255), 1
    )  # Line V2 - cv2.line(frame, (620,60), (620,420), (0,165,255), 1)
    cv2.line(
        frame,
        (620, WINDOW_HALF_HEIGHT),
        (620 - lunghezza_tac, WINDOW_HALF_HEIGHT),
        (0, 165, 255),
        1,
    )  # tacchetta centrale
    for tac in range(1, 9, 1):  # for tac in range( 1, 17, 1 ):
        cv2.line(
            frame,
            (620, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (620 - lunghezza_tac, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (0, 165, 255),
            1,
        )  # tacchette
        cv2.line(
            frame,
            (620, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (620 - lunghezza_tac, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (0, 165, 255),
            1,
        )  # tacchette


def display_scala_graduata_sfondo(sfondo):
    cv2.line(sfondo, (20, 60), (620, 60), (0, 165, 255), 1)  # Line H1
    cv2.line(
        sfondo,
        (WINDOW_HALF_WIDTH, 60),
        (WINDOW_HALF_WIDTH, 60 + lunghezza_tac),
        (0, 165, 255),
        1,
    )  # tacchetta centrale
    for tac in range(1, 29, 1):
        cv2.line(
            sfondo,
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 60),
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 60 + lunghezza_tac),
            (0, 165, 255),
            1,
        )  # tacchette
        cv2.line(
            sfondo,
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 60),
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 60 + lunghezza_tac),
            (0, 165, 255),
            1,
        )  # tacchette

    cv2.line(sfondo, (20, 260), (620, 260), (0, 165, 255), 1)  # Line H2
    cv2.line(
        sfondo,
        (WINDOW_HALF_WIDTH, 260),
        (WINDOW_HALF_WIDTH, 260 - lunghezza_tac),
        (0, 165, 255),
        1,
    )  # tacchetta centrale
    for tac in range(1, 29, 1):
        cv2.line(
            sfondo,
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 260),
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 260 - lunghezza_tac),
            (0, 165, 255),
            1,
        )  # tacchette
        cv2.line(
            sfondo,
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 260),
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 260 - lunghezza_tac),
            (0, 165, 255),
            1,
        )  # tacchette

    cv2.line(sfondo, (20, 60), (20, 260), (0, 165, 255), 1)  # Line V1
    cv2.line(
        sfondo,
        (20, WINDOW_HALF_HEIGHT),
        (20 + lunghezza_tac, WINDOW_HALF_HEIGHT),
        (0, 165, 255),
        1,
    )  # tacchetta centrale
    for tac in range(1, 9, 1):
        cv2.line(
            sfondo,
            (20, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (20 + lunghezza_tac, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (0, 165, 255),
            1,
        )  # tacchette
        cv2.line(
            sfondo,
            (20, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (20 + lunghezza_tac, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (0, 165, 255),
            1,
        )  # tacchette

    cv2.line(sfondo, (620, 60), (620, 260), (0, 165, 255), 1)  # Line V2
    cv2.line(
        sfondo,
        (620, WINDOW_HALF_HEIGHT),
        (620 - lunghezza_tac, WINDOW_HALF_HEIGHT),
        (0, 165, 255),
        1,
    )  # tacchetta centrale
    for tac in range(1, 9, 1):
        cv2.line(
            sfondo,
            (620, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (620 - lunghezza_tac, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (0, 165, 255),
            1,
        )  # tacchette
        cv2.line(
            sfondo,
            (620, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (620 - lunghezza_tac, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (0, 165, 255),
            1,
        )  # tacchette


def display_scala_graduata_thermal(img_color):
    cv2.line(img_color, (20, 60), (620, 60), (0, 0, 0), 1)  # Line H1
    cv2.line(
        img_color,
        (WINDOW_HALF_WIDTH, 60),
        (WINDOW_HALF_WIDTH, 60 + lunghezza_tac),
        (0, 0, 0),
        1,
    )  # tacchetta centrale
    for tac in range(1, 29, 1):
        cv2.line(
            img_color,
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 60),
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 60 + lunghezza_tac),
            (0, 0, 0),
            1,
        )  # tacchette
        cv2.line(
            img_color,
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 60),
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 60 + lunghezza_tac),
            (0, 0, 0),
            1,
        )  # tacchette

    cv2.line(img_color, (20, 260), (620, 260), (0, 0, 0), 1)  # Line H2
    cv2.line(
        img_color,
        (WINDOW_HALF_WIDTH, 260),
        (WINDOW_HALF_WIDTH, 260 - lunghezza_tac),
        (0, 0, 0),
        1,
    )  # tacchetta centrale
    for tac in range(1, 29, 1):
        cv2.line(
            img_color,
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 260),
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 260 - lunghezza_tac),
            (0, 0, 0),
            1,
        )  # tacchette
        cv2.line(
            img_color,
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 260),
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 260 - lunghezza_tac),
            (0, 0, 0),
            1,
        )  # tacchette

    cv2.line(img_color, (20, 60), (20, 260), (0, 0, 0), 1)  # Line V1
    cv2.line(
        img_color,
        (20, WINDOW_HALF_HEIGHT),
        (20 + lunghezza_tac, WINDOW_HALF_HEIGHT),
        (0, 0, 0),
        1,
    )  # tacchetta centrale
    for tac in range(1, 9, 1):
        cv2.line(
            img_color,
            (20, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (20 + lunghezza_tac, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (0, 0, 0),
            1,
        )  # tacchette
        cv2.line(
            img_color,
            (20, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (20 + lunghezza_tac, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (0, 0, 0),
            1,
        )  # tacchette

    cv2.line(img_color, (620, 60), (620, 260), (0, 0, 0), 1)  # Line V2
    cv2.line(
        img_color,
        (620, WINDOW_HALF_HEIGHT),
        (620 - lunghezza_tac, WINDOW_HALF_HEIGHT),
        (0, 0, 0),
        1,
    )  # tacchetta centrale
    for tac in range(1, 9, 1):
        cv2.line(
            img_color,
            (620, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (620 - lunghezza_tac, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (0, 0, 0),
            1,
        )  # tacchette
        cv2.line(
            img_color,
            (620, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (620 - lunghezza_tac, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (0, 0, 0),
            1,
        )  # tacchette


def chiudi_programma(video, *args):
    print("Chiusura programma in corso...")
    video.release()
    sys.exit(0) # https://www.geeksforgeeks.org/python-exit-commands-quit-exit-sys-exit-and-os-_exit/

def zoom(img, zoom_factor=2):
    return cv2.resize(img, None, fx=zoom_factor, fy=zoom_factor)


def punto_anab_cr( gray_image, len_window_y, punto1_y, pos_x ):

    y_demark = punto1_y

    if ((punto1_y-len_window_y)<0):
        min_y = 0
    else:
        min_y = punto1_y-len_window_y

    if ((punto1_y+len_window_y)>319):
        Max_y = 319
    else:
        Max_y = punto1_y+len_window_y
    
    num_pixels = Max_y - min_y
    lux_media_su_lineaY = 0

    for pxY in range( min_y , Max_y , 1 ):
        lux_media_su_lineaY = lux_media_su_lineaY + gray_image[pxY][pos_x] # [y][x]
        
    lux_media_su_lineaY = lux_media_su_lineaY/num_pixels
    distanza_lux_abs_min = 1000000  

    for pxY in range( min_y , Max_y , 1 ):
        if( abs(gray_image[pxY][pos_x]-lux_media_su_lineaY)<distanza_lux_abs_min ):
            distanza_lux_abs_min = abs(gray_image[pxY][pos_x]-lux_media_su_lineaY)
            y_demark = pxY
    
    # cv2.line(frame, (pos_x-10, y_demark ), ( pos_x+10, y_demark ), (0, 0, 255), 2)
    # cv2.line(frame, ( pos_x, y_demark-10 ), ( pos_x, y_demark+10 ), (0, 0, 255), 2)

    return (pos_x, y_demark)


def punto_anab_cr_MAX_Derivata( gray_image, len_window_y, punto1_y, pos_x ):

    y_demark = punto1_y

    if ((punto1_y-len_window_y)<0):
        min_y = 0
    else:
        min_y = punto1_y-len_window_y

    if ((punto1_y+len_window_y)>310):
        Max_y = 310
    else:
        Max_y = punto1_y+len_window_y
    
    deriv_max = 0

    for pxY in range( min_y , Max_y , 8 ):
        if( gray_image[pxY+8][pos_x]-gray_image[pxY][pos_x]>deriv_max ):
            deriv_max = gray_image[pxY+8][pos_x]-gray_image[pxY][pos_x]
            y_demark = pxY

    return (pos_x, y_demark)


def punto_Abb_up( gray_image, pos_x ):

    min_y = 80
    Max_y = 310
    y_demark = 160
    passo = 3

    lux_su_lineaY = 0

    for pxY in range( min_y , Max_y , passo ):
        if( gray_image[pxY][pos_x] > lux_su_lineaY ):
            lux_su_lineaY = gray_image[pxY][pos_x] 
        else:
            y_demark = pxY - passo
            break
        
    return (pos_x, y_demark)


def punto_Abb_dwn( gray_image, pos_x ):

    min_y = 310
    Max_y = 80
    y_demark = 160
    passo = -3

    lux_su_lineaY = 0

    for pxY in range( min_y , Max_y , passo ):
        if( gray_image[pxY][pos_x] > lux_su_lineaY ):
            lux_su_lineaY = gray_image[pxY][pos_x] 
        else:
            y_demark = pxY - passo
            break
        
    return (pos_x, y_demark)

"""

def punto_Abb_up_ORIZ( gray_image, pos_y ):

    min_x = 100
    Max_x = 610
    x_demark = 320
    passo = 3

    lux_su_lineaX = 0

    for pxX in range( min_x , Max_x , passo ):
        if( gray_image[pos_y][pxX] > lux_su_lineaX ):
            lux_su_lineaX = gray_image[pos_y][pxX] 
        else:
            x_demark = pxX - passo
            break
        
    return (x_demark, pos_y)


def punto_Abb_dwn_ORIZ( gray_image, pos_y ):

    min_x = 610
    Max_x = 100
    x_demark = 320
    passo = -3

    lux_su_lineaX = 0

    for pxX in range( min_x , Max_x , passo ):
        if( gray_image[pos_y][pxX] > lux_su_lineaX ):
            lux_su_lineaX = gray_image[pos_y][pxX] 
        else:
            x_demark = pxX - passo
            break
        
    return (x_demark, pos_y)

"""

def punto_Abb_up_ORIZ( gray_image, pos_y ):

    global lux_su_lineaX_AtH

    min_x = 30
    Max_x = 610
    x_demark = 320
    passo = 3

    for pxX in range( min_x , Max_x , passo ):
        if( gray_image[pos_y][pxX] >= lux_su_lineaX_AtH ):
            x_demark = pxX
        
    return (x_demark, pos_y)


def punto_Abb_dwn_ORIZ( gray_image, pos_y ):

    global lux_su_lineaX_AtH

    min_x = 610
    Max_x = 30
    x_demark = 320
    passo = -3

    for pxX in range( min_x , Max_x , passo ):
        if( gray_image[pos_y][pxX] >= lux_su_lineaX_AtH ):
            x_demark = pxX
        
    return (x_demark, pos_y)



if __name__ == "__main__":
    # TODO 02/08/2023 - Attenzione a tenere l'indice fisso della telecamera
    # perche' potrebbe cambiare
    video = cv2.VideoCapture(0)

    root = tk.Tk()
    root.overrideredirect(True) # remove the title bar and other default window formatting, Ive noticed this also removes the ability to full screen windows, drag edges to resize, and other native window management methods
    root.geometry(
        "{}x{}+{}+{}".format(
            WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_SHIFT_X, WINDOW_SHIFT_Y
        )
    )
    root.resizable(False, False)
    lmain = tk.Label(root)
    lmain.pack() # https://python-course.eu/tkinter/labels-in-tkinter.php
    # Decommentare se si vuole che cliccando sull'immagine lo script venga
    # chiuso (importare partial dalla libreria functools)
    # lmain.bind("<Button-1>", partial(chiudi_programma, video))

    # Exit if video not opened.
    # TODO 02/08/2023 - Fare in modo che se non si riesce ad aprire la telecamera
    # questo venga comunicato all'applicazione proteus in modo che possa mostrare
    # un messaggio di errore per l'utente
    if not video.isOpened():
        print("Could not open video")
        sys.exit(1)


    def show_frame():
        # TODO 02/08/2023 - Rimuovere l'utilizzo di 'global'
        global request_start_config, msg_cnt, posiz_pattern_x, posiz_pattern_y, lux_25m
        global tx_A, ty_A, tx_F, ty_F, tx_N, ty_N, pattern, translation_matrix
        global Larghezza_filtro_gaussiano, Larghezza_filtro_gaussiano, tolH, tolV
        global inclinazione_pixel_panel, display_croce, img_color, sfondo, mm_panel_per_pixel
        global punto1, punto2, punto3
        global start_row, end_row, start_col, end_col, numero_di_tacche_abbagl_offset_x, numero_di_tacche_abbagl_offset_y, lin_dem_anabb_offset_x, lin_dem_anabb_offset_y, lin_dem_anabb_coeff_angol   
        global sfondo_tmp, inverted_sfondo
        global lux_su_lineaX_AtH
        
        client_socket = socket.socket()
        client_socket.connect(("localhost", port))

        if request_start_config == 1:
            msg = "start_cfg %s " % SCRIPT_VERSION
        else:
            msg_cnt = msg_cnt + 1
            msg = "XYL %d %d %f " % (posiz_pattern_x, posiz_pattern_y, lux_25m)


        client_socket.send(msg.encode())                              # send message
        replica_da_Proteus = client_socket.recv(1024).decode("UTF-8") # receive response = socket.recv is a blocking call - The return value is a bytes object representing the data received

        if request_start_config == 1:
            request_start_config = 0
            if (argomenti_passati_script[1] == "ASK-VERS-PY") and (
                replica_da_Proteus[0:5] == "EXIT!"
            ):
                sys.exit()
            elif replica_da_Proteus[0:5] == "CFG->":
                if replica_da_Proteus[5] == "0":  # analog
                    pattern = 0
                elif replica_da_Proteus[5] == "1":  # digital
                    pattern = 1
                elif replica_da_Proteus[5] == "2":  # thermal
                    pattern = 2
                # ----------------------------------
                if replica_da_Proteus[6] == "0":
                    display_croce = 0
                elif replica_da_Proteus[6] == "1":
                    display_croce = 1
            else:
                pattern = 0
                display_croce = 0
            # ----------------------------------------------------- // tol
            if replica_da_Proteus[7:10] == "TOV":
                tolV = int(replica_da_Proteus[10:13])  # in pixels
                refresh_tolerance_display()
            else:
                tolV = 10  # in pixels
            # -----------------------------------------------------
            if replica_da_Proteus[13:16] == "mpx":  # mm_panel_per_pix
                mm_panel_per_pixel = float(replica_da_Proteus[16:24])
                refresh_mm_panel_per_pix_stuff()
            else:
                mm_panel_per_pixel = 0.1250
            # -----------------------------------------------------
            if replica_da_Proteus[24:27] == "inc":
                inclinazione_pixel_panel = int(replica_da_Proteus[27:31])
                refresh_tolerance_display()
                refresh_mm_panel_per_pix_stuff()
            else:
                inclinazione_pixel_panel = 0
            # -----------------------------------------------------
            if replica_da_Proteus[31:34] == "TOH":
                tolH = int(replica_da_Proteus[34:37])  # in pixels
                refresh_tolerance_display()
            else:
                tolH = 10  # in pixels
            # -----------------------------------------------------
            if replica_da_Proteus[37:40] == "GSF":
                Larghezza_filtro_gaussiano = int(replica_da_Proteus[40:43])  # in pixels
            else:
                Larghezza_filtro_gaussiano = 21  # in pixels
            # -----------------------------------------------------
            if replica_da_Proteus[43:46] == "TAX":  # abbagliante X
                tx_A = int(replica_da_Proteus[46:51])  # in pixels
            else:
                tx_A = 0  # in pixels
            # -----------------------------------------------------
            if replica_da_Proteus[51:54] == "TAY":  # abbagliante Y
                ty_A = int(replica_da_Proteus[54:59])  # in pixels
            else:
                ty_A = 0  # in pixels

            if replica_da_Proteus[59:62] == "TNX":  # anabbagliante X
                tx_N = int(replica_da_Proteus[62:67])  # in pixels
            else:
                tx_N = 0  # in pixels
            # -----------------------------------------------------
            if replica_da_Proteus[67:70] == "TNY":  # anabbagliante Y
                ty_N = int(replica_da_Proteus[70:75])  # in pixels
            else:
                ty_N = 0  # in pixels
            if replica_da_Proteus[75:78] == "TFX":  # fendinebbia X
                tx_F = int(replica_da_Proteus[78:83])  # in pixels
            else:
                tx_F = 0  # in pixels
            # -----------------------------------------------------
            if replica_da_Proteus[83:86] == "TFY":  # fendinebbia Y
                ty_F = int(replica_da_Proteus[86:91])  # in pixels
            else:
                ty_F = 0  # in pixels
            #-----------------------------------------------------
            if( replica_da_Proteus[91:94] == 'CRI' ):   # Cropping riga iniziale  
                start_row = int(replica_da_Proteus[94:97])   # in pixels
            else:
                start_row = 0                                # in pixels
            #-----------------------------------------------------
            if( replica_da_Proteus[97:100] == 'CRF' ):  # Cropping riga finale 
                end_row = int(replica_da_Proteus[100:103]) # in pixels
            else:
                end_row = 319                                # in pixels 
            #-----------------------------------------------------                             
            if( replica_da_Proteus[103:106] == 'CCI' ): # Cropping colonna iniziale 
                start_col = int(replica_da_Proteus[106:109]) # in pixels
            else:
                start_col = 0                                # in pixels
            #-----------------------------------------------------
            if( replica_da_Proteus[109:112] == 'CCF' ): # Cropping colonna finale 
                end_col = int(replica_da_Proteus[112:115]) # in pixels
            else:
                end_col = 629                                # in pixels
            #-----------------------------------------------------    
            if( replica_da_Proteus[115:118] == 'tax' ):  
                numero_di_tacche_abbagl_offset_x = int(replica_da_Proteus[118:121]) # in pixels (-3)
            else:
                numero_di_tacche_abbagl_offset_x = -3                               # in pixels
            #-----------------------------------------------------
            if( replica_da_Proteus[121:124] == 'tay' ):  
                numero_di_tacche_abbagl_offset_y = int(replica_da_Proteus[124:127]) # in pixels (+6)
            else:
                numero_di_tacche_abbagl_offset_y = 6                                # in pixels
            #-----------------------------------------------------
            if( replica_da_Proteus[127:130] == 'Lnx' ):  
                lin_dem_anabb_offset_x = int(replica_da_Proteus[130:135])      # in pixels
            else:
                lin_dem_anabb_offset_x = -200                                  # in pixels   
            #-----------------------------------------------------
            if( replica_da_Proteus[135:138] == 'Lny' ):  
                lin_dem_anabb_offset_y = int(replica_da_Proteus[138:143])      # in pixels
            else:
                lin_dem_anabb_offset_y = 5                                     # in pixels     
            #-----------------------------------------------------
            if( replica_da_Proteus[143:146] == 'AtH' ):  
                lux_su_lineaX_AtH = int(replica_da_Proteus[146:149])           # 0 - 255
            else:
                lux_su_lineaX_AtH = 200                                        # 0 - 255 
            #-----------------------------------------------------
            if( replica_da_Proteus[149:152] == 'Lnm' ):  
                lin_dem_anabb_coeff_angol = float(replica_da_Proteus[152:163]) # in pixels
            else:
                lin_dem_anabb_coeff_angol = 0.267949192                        # in pixels 
            #-----------------------------------------------------

        else:

            if replica_da_Proteus[0:13] == "inclinazione*":
                inclinazione_pixel_panel = int(replica_da_Proteus[13:17])      # in pixels
                refresh_tolerance_display()
                refresh_mm_panel_per_pix_stuff()
            elif replica_da_Proteus == "croce_ON":
                display_croce = 1
            elif replica_da_Proteus == "croce_OFF":
                display_croce = 0
            elif replica_da_Proteus == "pattern_analog":
                pattern = 0
            elif replica_da_Proteus == "pattern_digital":
                pattern = 1
            elif replica_da_Proteus == "pattern_thermal":
                pattern = 2

        if pattern == 1:  # pattern_digital
            if argomenti_passati_script[1] == "ANABBAGLIANTE":
                sfondo_tmp = cv2.imread("/home/pi/Applications/topauto_anabb.bmp")
                sfondo = cv2.cvtColor(sfondo_tmp, cv2.COLOR_BGR2RGB)
            elif argomenti_passati_script[1] == "ABBAGLIANTE":
                sfondo_tmp = cv2.imread("/home/pi/Applications/topauto_abb.bmp")
                sfondo = cv2.cvtColor(sfondo_tmp, cv2.COLOR_BGR2RGB)
            elif argomenti_passati_script[1] == "FENDINEBBIA":
                sfondo_tmp = cv2.imread("/home/pi/Applications/topauto_fend.bmp")
                sfondo = cv2.cvtColor(sfondo_tmp, cv2.COLOR_BGR2RGB)
            display_griglia_HV2(sfondo)

        ok, frame_originale = video.read()

        # Creiamo la matrice di traslazione a seconda se abbiamo abbagliante, anabbagliante o fendinebbia
        if argomenti_passati_script[1] == "ABBAGLIANTE":
            translation_matrix = np.array(
                [[1, 0, tx_A], [0, 1, ty_A]], dtype=np.float32
            )
        elif argomenti_passati_script[1] == "ANABBAGLIANTE":
            translation_matrix = np.array(
                [[1, 0, tx_N], [0, 1, ty_N]], dtype=np.float32
            )
        elif argomenti_passati_script[1] == "FENDINEBBIA":
            translation_matrix = np.array(
                [[1, 0, tx_F], [0, 1, ty_F]], dtype=np.float32
            )
        else :
            translation_matrix = np.array(
                [[1, 0, 0], [0, 1, 0]], dtype=np.float32
            )

        fr_resized = cv2.resize(
            frame_originale, (WINDOW_WIDTH, WINDOW_HEIGHT), interpolation=cv2.INTER_AREA
        )

        if argomenti_passati_script[1] in ["ANABBAGLIANTE", "FENDINEBBIA"]:
            frame_zom = zoom(fr_resized, 2.000)
        elif argomenti_passati_script[1] == "ABBAGLIANTE":
            frame_zom = zoom(fr_resized, 2.500) # 2.500

        # apply the translation to the image
        frame = cv2.warpAffine(
            src=frame_zom,
            M=translation_matrix,
            dsize=(WINDOW_WIDTH, WINDOW_HEIGHT),
        )

        blurred = cv2.GaussianBlur(
            frame, (Larghezza_filtro_gaussiano, Larghezza_filtro_gaussiano), 0 # (51, 51) # (7, 7)
        )

        gray_image = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        (minVal, maxVal, minLoc, maxLoc_tuple) = cv2.minMaxLoc(gray_image)

        if pattern == 2:  # pattern_thermal
            img_color = cv2.applyColorMap(gray_image, cv2.COLORMAP_HSV) # COLORMAP_RAINBOW, COLORMAP_JET

        if argomenti_passati_script[1] in ["ANABBAGLIANTE", "FENDINEBBIA"]: # if (( argomenti_passati_script[1] == "ANABBAGLIANTE" ) or ( argomenti_passati_script[1] == "FENDINEBBIA" )) :
            lumen_accumul = 0

            # punto 75R per la normativa: anabbaglianti ALOGENI per la norma italiana e per le ISO 10604
            for y in range(int(Ypx_in), int(Ypx_fin), 1):
                for x in range(int(Xpx_in), int(Xpx_fin), 1):
                    B = blurred[y][x][0] / 10.0
                    G = blurred[y][x][1] / 10.0
                    R = blurred[y][x][2] / 10.0
                    lumen_pixel = (0.2126 * R) + (0.7152 * G) + (0.0722 * B)  # Standard
                    lumen_accumul = lumen_accumul + lumen_pixel

            luminanza = lumen_accumul
            lux_25m = (
                200 * (math.exp(luminanza / (718746 - 3.578 * luminanza)) - 1)
            ) + offset_glarelight_lux

        elif argomenti_passati_script[1] == "ABBAGLIANTE":
            lumen_accumul = 0

            # punto 75R per la normativa: anabbaglianti ALOGENI per la norma italiana e per le ISO 10604
            for y in range(int(Ypx_in_ABB), int(Ypx_fin_ABB), 1):
                for x in range(int(Xpx_in_ABB), int(Xpx_fin_ABB), 1):
                    B = blurred[y][x][0] / 10.0
                    G = blurred[y][x][1] / 10.0
                    R = blurred[y][x][2] / 10.0
                    lumen_pixel = (0.2126 * R) + (0.7152 * G) + (0.0722 * B)  # Standard
                    lumen_accumul = lumen_accumul + lumen_pixel

            luminanza = lumen_accumul
            lux_25m = (
                1000 * (math.exp(luminanza / (718746 - 3.578 * luminanza)) - 1)
            ) + offset_ABBlight_lux

        maxLoc_list = list(maxLoc_tuple)

        """
        if argomenti_passati_script[1] == "ABBAGLIANTE":
            # aggiusto le cose in modo che il pallino blu (punto di massima intensitÃ  ottica) sia abbastanza al
            # centro del globulo del pattern ottico dell'abbagliante
            maxLoc_list[0] = maxLoc_list[0] + pixels_tac1_tac2 * numero_di_tacche_abbagl_offset_x # -3
            maxLoc_list[1] = maxLoc_list[1] + pixels_tac1_tac2 * numero_di_tacche_abbagl_offset_y # +6
        """

        maxLoc = tuple(maxLoc_list)


        # pallino blu - punto di massima intensità ottica
        if display_croce == 1:
            if pattern == 0:  # pattern_analog
                cv2.circle(frame, maxLoc, 5, (255, 0, 0), 4)
            elif pattern == 1:  # pattern_digital
                cv2.circle(sfondo, maxLoc, 5, (255, 255, 255), 4)
            elif pattern == 2:  # pattern_thermal
                cv2.circle(img_color, maxLoc, 5, (0, 255, 255), 4)

        if argomenti_passati_script[1] in ["ANABBAGLIANTE", "FENDINEBBIA"]: # if (( argomenti_passati_script[1] == "ANABBAGLIANTE" ) or ( argomenti_passati_script[1] == "FENDINEBBIA" )) :
            if display_croce == 1:
                if pattern == 0:  # pattern_analog
                    cv2.line(
                        frame,
                        somma_xy(maxLoc, shift1),
                        somma_xy(maxLoc, shift2),
                        (255, 0, 0),
                        1,
                    )  # croce blu
                    cv2.line(
                        frame,
                        somma_xy(maxLoc, shift3),
                        somma_xy(maxLoc, shift4),
                        (255, 0, 0),
                        1,
                    )  # croce blu
                elif pattern == 1:  # pattern_digital
                    cv2.line(
                        sfondo,
                        somma_xy(maxLoc, shift1),
                        somma_xy(maxLoc, shift2),
                        (255, 255, 255),
                        1,
                    )  # croce blu
                    cv2.line(
                        sfondo,
                        somma_xy(maxLoc, shift3),
                        somma_xy(maxLoc, shift4),
                        (255, 255, 255),
                        1,
                    )  # croce blu
                elif pattern == 2:  # pattern_thermal
                    cv2.line(
                        img_color,
                        somma_xy(maxLoc, shift1),
                        somma_xy(maxLoc, shift2),
                        (0, 255, 255),
                        1,
                    )  # croce blu
                    cv2.line(
                        img_color,
                        somma_xy(maxLoc, shift3),
                        somma_xy(maxLoc, shift4),
                        (0, 255, 255),
                        1,
                    )  # croce blu

            if argomenti_passati_script[1] == "ANABBAGLIANTE":
                cv2.rectangle(
                    frame,
                    (int(Xpx_in), int(Ypx_in)),
                    (int(Xpx_fin), int(Ypx_fin)),
                    (0, 255, 255),
                    2,
                )  # <- qui dentro ci ho raccolto la luce (luminanza)


            #--------------------------------------------------------------------------------
            #--------------------------------------------------------------------------------
            #--------------------------------------------------------------------------------
            #--------------------------------------------------------------------------------

            punto1_tmp = calcola_punto1(maxLoc)

            Status_Points_CR = [0,0,0,0,0,0,0]
            len_window_y = 60
            punto1_x = punto1_tmp[0]
            punto1_y = punto1_tmp[1]            
            #--------------------------------------------------------------------------------

            if( argomenti_passati_script[1] == "ANABBAGLIANTE" ):

                if( punto1_x>=int(WINDOW_HALF_WIDTH/4) ):
                    Point1_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH/4) )  
                    Status_Points_CR[0] = 0
                else:
                    Point1_CR = punto_anab_cr( gray_image, len_window_y, punto1_y-( (int)(((float)(int(WINDOW_HALF_WIDTH/4)-punto1_x))*lin_dem_anabb_coeff_angol) ), int(WINDOW_HALF_WIDTH/4) )
                    Status_Points_CR[0] = 1
                ###
                if( punto1_x>=int(WINDOW_HALF_WIDTH/2) ):
                    Point2_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH/2) ) 
                    Status_Points_CR[1] = 0 
                else:
                    Point2_CR = punto_anab_cr( gray_image, len_window_y, punto1_y-( (int)(((float)(int(WINDOW_HALF_WIDTH/2)-punto1_x))*lin_dem_anabb_coeff_angol) ), int(WINDOW_HALF_WIDTH/2) )
                    Status_Points_CR[1] = 1
                ###
                if( punto1_x>=int(WINDOW_HALF_WIDTH*(3/4)) ):
                    Point3_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH*(3/4)) )
                    Status_Points_CR[2] = 0  
                else:
                    Point3_CR = punto_anab_cr( gray_image, len_window_y, punto1_y-( (int)(((float)(int(WINDOW_HALF_WIDTH*(3/4))-punto1_x))*lin_dem_anabb_coeff_angol) ), int(WINDOW_HALF_WIDTH*(3/4)) )
                    Status_Points_CR[2] = 1 
                ###
                if( punto1_x>=int(WINDOW_HALF_WIDTH) ):
                    Point4_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH) )  
                    Status_Points_CR[3] = 0
                else:
                    Point4_CR = punto_anab_cr( gray_image, len_window_y, punto1_y-( (int)(((float)(int(WINDOW_HALF_WIDTH)-punto1_x))*lin_dem_anabb_coeff_angol) ), int(WINDOW_HALF_WIDTH) ) 
                    Status_Points_CR[3] = 1
                ###
                if( punto1_x>=WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) ):
                    Point5_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) )  
                    Status_Points_CR[4] = 0
                else:
                    Point5_CR = punto_anab_cr( gray_image, len_window_y, punto1_y-( (int)(((float)(( WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) )-punto1_x))*lin_dem_anabb_coeff_angol) ), WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) )
                    Status_Points_CR[4] = 1
                ###
                if( punto1_x>=WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) ):
                    Point6_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) )  
                    Status_Points_CR[5] = 0
                else:
                    Point6_CR = punto_anab_cr( gray_image, len_window_y, punto1_y-( (int)(((float)(( WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) )-punto1_x))*lin_dem_anabb_coeff_angol) ), WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) )
                    Status_Points_CR[5] = 1
                ###            
                if( punto1_x>=WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH*(3/4)) ):
                    Point7_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH*(3/4)) ) 
                    Status_Points_CR[6] = 0 
                else:
                    Point7_CR = punto_anab_cr( gray_image, len_window_y, punto1_y-( (int)(((float)(( WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH*(3/4)) )-punto1_x))*lin_dem_anabb_coeff_angol) ), WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH*(3/4)) )           
                    Status_Points_CR[6] = 1
                ###

                num_punt = 1
                pos_y_pnt = Point1_CR[1] # [y]

                array_posizY = [ Point1_CR[1], Point2_CR[1], Point3_CR[1], Point4_CR[1], Point5_CR[1], Point6_CR[1], Point7_CR[1] ] # [y]
                # array_posizX = [ Point1_CR[0], Point2_CR[0], Point3_CR[0], Point4_CR[0], Point5_CR[0], Point6_CR[0], Point7_CR[0] ] # [x]

                for p in range( 1, 6+1, 1):
                    if( Status_Points_CR[p] == 0 ):
                        num_punt = num_punt + 1
                        pos_y_pnt = pos_y_pnt + array_posizY[p]
                    else:
                        punto1 = ( punto1_x, int((float(pos_y_pnt))/((float(num_punt)))) )
                        # punto1 = ( array_posizX[p-1], int((float(pos_y_pnt))/((float(num_punt)))) )
                        # punto1[0] = array_posizX[p-1] # [x]
                        break

                # punto1[1] = int((float(pos_y_pnt))/((float(num_punt)))) # [y]

            
            elif( argomenti_passati_script[1] == "FENDINEBBIA" ):

                Point1_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH/4) )
                Point2_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH/2) )
                Point3_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH*(3/4)) )
                Point4_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH) )
                Point5_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) )
                Point6_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) )
                Point7_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH*(3/4)) ) 

                num_punt = 1
                pos_y_pnt = Point1_CR[1] # [y]

                array_posizY = [ Point1_CR[1], Point2_CR[1], Point3_CR[1], Point4_CR[1], Point5_CR[1], Point6_CR[1], Point7_CR[1] ] # [y]

                for p in range( 1, 6+1, 1):
                    num_punt = num_punt + 1
                    pos_y_pnt = pos_y_pnt + array_posizY[p]

                punto1 = ( punto1_x, int((float(pos_y_pnt))/((float(num_punt)))) )
                # punto1[0] = punto1_x # [x]
                # punto1[1] = int((float(pos_y_pnt))/((float(num_punt)))) # [y]



            #--------------------------------------------------------------------------------
            #--------------------------------------------------------------------------------
            #--------------------------------------------------------------------------------
            #--------------------------------------------------------------------------------


            # punto1 = calcola_punto1(maxLoc)
            # punto2 = calcola_punto2(punto1)
            # punto3 = calcola_punto3(punto1)

            posiz_pattern_x = punto1[0]
            posiz_pattern_y = punto1[1]
                
            if ( argomenti_passati_script[1] == "ANABBAGLIANTE" ) : # tol
                valutazione_vero_falso1 = ( (punto1[0]<(WINDOW_HALF_WIDTH+tolH)) and (punto1[0]>(WINDOW_HALF_WIDTH-tolH)) ) and ( (punto1[1]<(WINDOW_HALF_HEIGHT+inclinazione_pixel_panel+tolV)) and (punto1[1]>(WINDOW_HALF_HEIGHT+inclinazione_pixel_panel-tolV)) ) 
            elif ( argomenti_passati_script[1] == "FENDINEBBIA" ) :
                valutazione_vero_falso1 = ( (punto1[1]<(WINDOW_HALF_HEIGHT+inclinazione_pixel_panel+tolV)) and (punto1[1]>(WINDOW_HALF_HEIGHT+inclinazione_pixel_panel-tolV)) )

            if valutazione_vero_falso1:
                if pattern == 0:  # pattern_analog
                    # ANALOGICO
                    # linea di demarcazione DENTRO la tolleranza
                    cv2.line(frame, ( 0, Point1_CR[1] ), ( Point1_CR[0], Point1_CR[1] ), (0, 255, 0), 4)
                    cv2.line(frame, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (0, 255, 0), 4)
                    cv2.line(frame, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (0, 255, 0), 4)
                    cv2.line(frame, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (0, 255, 0), 4)
                    cv2.line(frame, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (0, 255, 0), 4)
                    cv2.line(frame, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (0, 255, 0), 4)
                    cv2.line(frame, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (0, 255, 0), 4)
                    cv2.line(frame, ( Point7_CR[0], Point7_CR[1] ), ( 630, Point7_CR[1] ), (0, 255, 0), 4)
                    # cv2.putText(frame, "ANABBAGLIANTE CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,255,0), 2)
                elif pattern == 1:  # pattern_digital
                    # DIGITALE
                    # linea di demarcazione DENTRO la tolleranza
                    cv2.line(sfondo, ( 0, Point1_CR[1] ), ( Point1_CR[0], Point1_CR[1] ), (0, 255, 0), 4)
                    cv2.line(sfondo, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (0, 255, 0), 4)
                    cv2.line(sfondo, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (0, 255, 0), 4)
                    cv2.line(sfondo, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (0, 255, 0), 4)
                    cv2.line(sfondo, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (0, 255, 0), 4)
                    cv2.line(sfondo, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (0, 255, 0), 4)
                    cv2.line(sfondo, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (0, 255, 0), 4)
                    cv2.line(sfondo, ( Point7_CR[0], Point7_CR[1] ), ( 630, Point7_CR[1] ), (0, 255, 0), 4)
                    # cv2.putText(sfondo, "ANABBAGLIANTE CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,255,0), 2)
                elif pattern == 2:  # pattern_thermal
                    # TERMICO
                    # linea di demarcazione DENTRO la tolleranza
                    cv2.line(img_color, ( 0, Point1_CR[1] ), ( Point1_CR[0], Point1_CR[1] ), (0, 255, 0), 4)
                    cv2.line(img_color, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (0, 255, 0), 4)
                    cv2.line(img_color, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (0, 255, 0), 4)
                    cv2.line(img_color, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (0, 255, 0), 4)
                    cv2.line(img_color, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (0, 255, 0), 4)
                    cv2.line(img_color, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (0, 255, 0), 4)
                    cv2.line(img_color, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (0, 255, 0), 4)
                    cv2.line(img_color, ( Point7_CR[0], Point7_CR[1] ), ( 630, Point7_CR[1] ), (0, 255, 0), 4)
                    # cv2.putText(img_color, "ANABBAGLIANTE CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,255,0), 2)

            else:
                if pattern == 0:  # pattern_analog
                    # ANALOGICO
                    # linea di demarcazione FUORI la tolleranza
                    cv2.line(frame, ( 0, Point1_CR[1] ), ( Point1_CR[0], Point1_CR[1] ), (255, 0, 0), 4)
                    cv2.line(frame, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (255, 0, 0), 4)
                    cv2.line(frame, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (255, 0, 0), 4)
                    cv2.line(frame, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (255, 0, 0), 4)
                    cv2.line(frame, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (255, 0, 0), 4)
                    cv2.line(frame, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (255, 0, 0), 4)
                    cv2.line(frame, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (255, 0, 0), 4)
                    cv2.line(frame, ( Point7_CR[0], Point7_CR[1] ), ( 630, Point7_CR[1] ), (255, 0, 0), 4)
                    # cv2.putText(frame, "ANABBAGLIANTE NON CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,0,255), 2)
                elif pattern == 1:  # pattern_digital
                    # DIGITALE
                    # linea di demarcazione FUORI la tolleranza
                    cv2.line(sfondo, ( 0, Point1_CR[1] ), ( Point1_CR[0], Point1_CR[1] ), (255, 0, 0), 4)
                    cv2.line(sfondo, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (255, 0, 0), 4)
                    cv2.line(sfondo, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (255, 0, 0), 4)
                    cv2.line(sfondo, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (255, 0, 0), 4)
                    cv2.line(sfondo, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (255, 0, 0), 4)
                    cv2.line(sfondo, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (255, 0, 0), 4)
                    cv2.line(sfondo, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (255, 0, 0), 4)
                    cv2.line(sfondo, ( Point7_CR[0], Point7_CR[1] ), ( 630, Point7_CR[1] ), (255, 0, 0), 4)
                    # cv2.putText(sfondo, "ANABBAGLIANTE NON CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,0,255), 2)
                elif pattern == 2:  # pattern_thermal
                    # TERMICO
                    # linea di demarcazione FUORI la tolleranza
                    cv2.line(img_color, ( 0, Point1_CR[1] ), ( Point1_CR[0], Point1_CR[1] ), (255, 0, 0), 4)
                    cv2.line(img_color, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (255, 0, 0), 4)
                    cv2.line(img_color, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (255, 0, 0), 4)
                    cv2.line(img_color, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (255, 0, 0), 4)
                    cv2.line(img_color, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (255, 0, 0), 4)
                    cv2.line(img_color, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (255, 0, 0), 4)
                    cv2.line(img_color, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (255, 0, 0), 4)
                    cv2.line(img_color, ( Point7_CR[0], Point7_CR[1] ), ( 630, Point7_CR[1] ), (255, 0, 0), 4)
                    # cv2.putText(img_color, "ANABBAGLIANTE NON CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,0,255), 2)

        elif argomenti_passati_script[1] == "ABBAGLIANTE":

            cv2.rectangle(
                frame,
                (int(Xpx_in_ABB), int(Ypx_in_ABB)),
                (int(Xpx_fin_ABB), int(Ypx_fin_ABB)),
                (0, 255, 255),
                2,
            )  # <- qui dentro ci ho raccolto la luce (luminanza)


            Point1_ABB_up_CR = punto_Abb_up( gray_image, int(WINDOW_HALF_WIDTH/2) )
            Point1_ABB_down_CR = punto_Abb_dwn( gray_image, int(WINDOW_HALF_WIDTH/2) )
            Point1_ABB_media_CR = ( int((Point1_ABB_up_CR[0]+Point1_ABB_down_CR[0])/2) , int((Point1_ABB_up_CR[1]+Point1_ABB_down_CR[1])/2) )

            Point2_ABB_up_CR = punto_Abb_up( gray_image, int(WINDOW_HALF_WIDTH*(3/4)) )
            Point2_ABB_down_CR = punto_Abb_dwn( gray_image, int(WINDOW_HALF_WIDTH*(3/4)) )
            Point2_ABB_media_CR = ( int((Point2_ABB_up_CR[0]+Point2_ABB_down_CR[0])/2) , int((Point2_ABB_up_CR[1]+Point2_ABB_down_CR[1])/2) )

            Point3_ABB_up_CR = punto_Abb_up( gray_image, WINDOW_HALF_WIDTH )
            Point3_ABB_down_CR = punto_Abb_dwn( gray_image, WINDOW_HALF_WIDTH )
            Point3_ABB_media_CR = ( int((Point3_ABB_up_CR[0]+Point3_ABB_down_CR[0])/2) , int((Point3_ABB_up_CR[1]+Point3_ABB_down_CR[1])/2) )

            Point4_ABB_up_CR = punto_Abb_up( gray_image, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) )
            Point4_ABB_down_CR = punto_Abb_dwn( gray_image, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) )
            Point4_ABB_media_CR = ( int((Point4_ABB_up_CR[0]+Point4_ABB_down_CR[0])/2) , int((Point4_ABB_up_CR[1]+Point4_ABB_down_CR[1])/2) )

            Point5_ABB_up_CR = punto_Abb_up( gray_image, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) )
            Point5_ABB_down_CR = punto_Abb_dwn( gray_image, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) )
            Point5_ABB_media_CR = ( int((Point5_ABB_up_CR[0]+Point5_ABB_down_CR[0])/2) , int((Point5_ABB_up_CR[1]+Point5_ABB_down_CR[1])/2) )

            posiz_pattern_y = int(( Point1_ABB_media_CR[1] + Point2_ABB_media_CR[1] + Point3_ABB_media_CR[1] + Point4_ABB_media_CR[1] + Point5_ABB_media_CR[1] )/5)




            Point1_ABB_up_Hh = punto_Abb_up_ORIZ( gray_image, int(WINDOW_HALF_HEIGHT/2) )
            Point1_ABB_down_Hh = punto_Abb_dwn_ORIZ( gray_image, int(WINDOW_HALF_HEIGHT/2) )
            Point1_ABB_media_Hh = ( int((Point1_ABB_up_Hh[0]+Point1_ABB_down_Hh[0])/2) , int((Point1_ABB_up_Hh[1]+Point1_ABB_down_Hh[1])/2) )

            Point2_ABB_up_Hh = punto_Abb_up_ORIZ( gray_image, int(WINDOW_HALF_HEIGHT*(3/4)) )
            Point2_ABB_down_Hh = punto_Abb_dwn_ORIZ( gray_image, int(WINDOW_HALF_HEIGHT*(3/4)) )
            Point2_ABB_media_Hh = ( int((Point2_ABB_up_Hh[0]+Point2_ABB_down_Hh[0])/2) , int((Point2_ABB_up_Hh[1]+Point2_ABB_down_Hh[1])/2) )

            Point3_ABB_up_Hh = punto_Abb_up_ORIZ( gray_image, WINDOW_HALF_HEIGHT )
            Point3_ABB_down_Hh = punto_Abb_dwn_ORIZ( gray_image, WINDOW_HALF_HEIGHT )
            Point3_ABB_media_Hh = ( int((Point3_ABB_up_Hh[0]+Point3_ABB_down_Hh[0])/2) , int((Point3_ABB_up_Hh[1]+Point3_ABB_down_Hh[1])/2) )

            Point4_ABB_up_Hh = punto_Abb_up_ORIZ( gray_image, WINDOW_HALF_HEIGHT+int(WINDOW_HALF_HEIGHT/4) )
            Point4_ABB_down_Hh = punto_Abb_dwn_ORIZ( gray_image, WINDOW_HALF_HEIGHT+int(WINDOW_HALF_HEIGHT/4) )
            Point4_ABB_media_Hh = ( int((Point4_ABB_up_Hh[0]+Point4_ABB_down_Hh[0])/2) , int((Point4_ABB_up_Hh[1]+Point4_ABB_down_Hh[1])/2) )

            Point5_ABB_up_Hh = punto_Abb_up_ORIZ( gray_image, WINDOW_HALF_HEIGHT+int(WINDOW_HALF_HEIGHT/2) )
            Point5_ABB_down_Hh = punto_Abb_dwn_ORIZ( gray_image, WINDOW_HALF_HEIGHT+int(WINDOW_HALF_HEIGHT/2) )
            Point5_ABB_media_Hh = ( int((Point5_ABB_up_Hh[0]+Point5_ABB_down_Hh[0])/2) , int((Point5_ABB_up_Hh[1]+Point5_ABB_down_Hh[1])/2) )







            cv2.line(frame, (Point1_ABB_up_Hh[0]-10, Point1_ABB_up_Hh[1] ), ( Point1_ABB_up_Hh[0]+10, Point1_ABB_up_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point1_ABB_up_Hh[0], Point1_ABB_up_Hh[1]-10 ), ( Point1_ABB_up_Hh[0], Point1_ABB_up_Hh[1]+10 ), (0, 0, 255), 3)    
            cv2.line(frame, (Point1_ABB_down_Hh[0]-10, Point1_ABB_down_Hh[1] ), ( Point1_ABB_down_Hh[0]+10, Point1_ABB_down_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point1_ABB_down_Hh[0], Point1_ABB_down_Hh[1]-10 ), ( Point1_ABB_down_Hh[0], Point1_ABB_down_Hh[1]+10 ), (0, 0, 255), 3)

            cv2.line(frame, (Point2_ABB_up_Hh[0]-10, Point2_ABB_up_Hh[1] ), ( Point2_ABB_up_Hh[0]+10, Point2_ABB_up_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point2_ABB_up_Hh[0], Point2_ABB_up_Hh[1]-10 ), ( Point2_ABB_up_Hh[0], Point2_ABB_up_Hh[1]+10 ), (0, 0, 255), 3)    
            cv2.line(frame, (Point2_ABB_down_Hh[0]-10, Point2_ABB_down_Hh[1] ), ( Point2_ABB_down_Hh[0]+10, Point2_ABB_down_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point2_ABB_down_Hh[0], Point2_ABB_down_Hh[1]-10 ), ( Point2_ABB_down_Hh[0], Point2_ABB_down_Hh[1]+10 ), (0, 0, 255), 3)

            cv2.line(frame, (Point3_ABB_up_Hh[0]-10, Point3_ABB_up_Hh[1] ), ( Point3_ABB_up_Hh[0]+10, Point3_ABB_up_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point3_ABB_up_Hh[0], Point3_ABB_up_Hh[1]-10 ), ( Point3_ABB_up_Hh[0], Point3_ABB_up_Hh[1]+10 ), (0, 0, 255), 3)    
            cv2.line(frame, (Point3_ABB_down_Hh[0]-10, Point3_ABB_down_Hh[1] ), ( Point3_ABB_down_Hh[0]+10, Point3_ABB_down_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point3_ABB_down_Hh[0], Point3_ABB_down_Hh[1]-10 ), ( Point3_ABB_down_Hh[0], Point3_ABB_down_Hh[1]+10 ), (0, 0, 255), 3)

            cv2.line(frame, (Point4_ABB_up_Hh[0]-10, Point4_ABB_up_Hh[1] ), ( Point4_ABB_up_Hh[0]+10, Point4_ABB_up_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point4_ABB_up_Hh[0], Point4_ABB_up_Hh[1]-10 ), ( Point4_ABB_up_Hh[0], Point4_ABB_up_Hh[1]+10 ), (0, 0, 255), 3)    
            cv2.line(frame, (Point4_ABB_down_Hh[0]-10, Point4_ABB_down_Hh[1] ), ( Point4_ABB_down_Hh[0]+10, Point4_ABB_down_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point4_ABB_down_Hh[0], Point4_ABB_down_Hh[1]-10 ), ( Point4_ABB_down_Hh[0], Point4_ABB_down_Hh[1]+10 ), (0, 0, 255), 3)
            
            cv2.line(frame, (Point5_ABB_up_Hh[0]-10, Point5_ABB_up_Hh[1] ), ( Point5_ABB_up_Hh[0]+10, Point5_ABB_up_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point5_ABB_up_Hh[0], Point5_ABB_up_Hh[1]-10 ), ( Point5_ABB_up_Hh[0], Point5_ABB_up_Hh[1]+10 ), (0, 0, 255), 3)    
            cv2.line(frame, (Point5_ABB_down_Hh[0]-10, Point5_ABB_down_Hh[1] ), ( Point5_ABB_down_Hh[0]+10, Point5_ABB_down_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point5_ABB_down_Hh[0], Point5_ABB_down_Hh[1]-10 ), ( Point5_ABB_down_Hh[0], Point5_ABB_down_Hh[1]+10 ), (0, 0, 255), 3)







            posiz_pattern_x = int(( Point1_ABB_media_Hh[0] + Point2_ABB_media_Hh[0] + Point3_ABB_media_Hh[0] + Point4_ABB_media_Hh[0] + Point5_ABB_media_Hh[0] )/5)


            # posiz_pattern_x = maxLoc[0]
            # posiz_pattern_y = maxLoc[1]

            # tol

            if (
                (posiz_pattern_x < (WINDOW_HALF_WIDTH + tolH))
                and (posiz_pattern_x > (WINDOW_HALF_WIDTH - tolH))
            ) and (
                (posiz_pattern_y < (WINDOW_HALF_HEIGHT + inclinazione_pixel_panel + tolV))
                and (posiz_pattern_y > (WINDOW_HALF_HEIGHT + inclinazione_pixel_panel - tolV))
            ):
                if pattern == 0:  # pattern_analog
                    # ANALOGICO
                    # linea di demarcazione DENTRO la tolleranza
                    cv2.line(
                        frame,
                        (5, posiz_pattern_y),
                        (625, posiz_pattern_y),
                        (0, 255, 0),
                        2,
                    )  
                    cv2.line(
                        frame,
                        (posiz_pattern_x, 5),
                        (posiz_pattern_x, 315),
                        (0, 255, 0),
                        2,
                    )  
                    # cv2.putText(frame, "ABBAGLIANTE CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,255,0), 2)
                elif pattern == 1:  # pattern_digital
                    # DIGITALE
                    # linea di demarcazione DENTRO la tolleranza
                    cv2.line(
                        sfondo,
                        (5, posiz_pattern_y),
                        (625, posiz_pattern_y),
                        (0, 255, 0),
                        4,
                    )
                    cv2.line(
                        sfondo,
                        (posiz_pattern_x, 5),
                        (posiz_pattern_x, 315),
                        (0, 255, 0),
                        2,
                    ) 
                    # cv2.putText(sfondo, "ABBAGLIANTE CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,255,0), 2)
                elif pattern == 2:  # pattern_thermal
                    # TERMICO
                    # linea di demarcazione DENTRO la tolleranza
                    cv2.line(
                        img_color,
                        (5, posiz_pattern_y),
                        (625, posiz_pattern_y),
                        (0, 255, 0),
                        4,
                    )
                    cv2.line(
                        img_color,
                        (posiz_pattern_x, 5),
                        (posiz_pattern_x, 315),
                        (0, 255, 0),
                        2,
                    ) 
                    # cv2.putText(img_color, "ABBAGLIANTE CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,255,0), 2)

            else:
                if pattern == 0:  # pattern_analog
                    # ANALOGICO
                    # linea di demarcazione FUORI la tolleranza
                    cv2.line(
                        frame,
                        (5, posiz_pattern_y),
                        (625, posiz_pattern_y),
                        (255, 0, 0),
                        2,
                    ) 
                    cv2.line(
                        frame,
                        (posiz_pattern_x, 5),
                        (posiz_pattern_x, 315),
                        (255, 0, 0),
                        2,
                    )  
                    # cv2.putText(frame, "ABBAGLIANTE NON CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,0,255), 2)
                elif pattern == 1:  # pattern_digital
                    # DIGITALE
                    # linea di demarcazione FUORI la tolleranza
                    cv2.line(
                        sfondo,
                        (5, posiz_pattern_y),
                        (625, posiz_pattern_y),
                        (255, 0, 0),
                        4,
                    )
                    cv2.line(
                        sfondo,
                        (posiz_pattern_x, 5),
                        (posiz_pattern_x, 315),
                        (255, 0, 0),
                        2,
                    )  
                    # cv2.putText(sfondo, "ABBAGLIANTE NON CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,0,255), 2)
                elif pattern == 2:  # pattern_thermal
                    # TERMICO
                    # linea di demarcazione FUORI la tolleranza
                    cv2.line(
                        img_color,
                        (5, posiz_pattern_y),
                        (625, posiz_pattern_y),
                        (255, 0, 0), # (255, 255, 255)
                        4,
                    )
                    cv2.line(
                        img_color,
                        (posiz_pattern_x, 5),
                        (posiz_pattern_x, 315),
                        (255, 0, 0),
                        2,
                    )  
                    # cv2.putText(img_color, "ABBAGLIANTE NON CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,0,255), 2)

        if pattern == 0:  # pattern_analog
            display_griglia_HV(frame)
        elif pattern == 2:  # pattern_thermal
            display_griglia_HV3(img_color)

        if pattern == 0:  # pattern_analog
            display_scala_graduata_frame(frame)
            frame_to_show = frame
        elif pattern == 1:  # pattern_digital
            display_scala_graduata_sfondo(sfondo)
            frame_to_show = sfondo
        elif pattern == 2:  # pattern_thermal
            display_scala_graduata_thermal(img_color)
            frame_to_show = img_color

        img = PIL.Image.fromarray(frame_to_show)
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
        lmain.after(100, show_frame) # ogni 100ms itera a loop il corpo di "show_frame"

    show_frame()
    root.mainloop()

    chiudi_programma(video)
