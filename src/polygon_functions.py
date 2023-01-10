# Polygon rotation
def rotate_points(shape_x, shape_y, x_ini, y_ini, x_fin, y_fin, angle):
    if angle == 90:
        x_inicial = x_ini
        y_inicial = y_fin

        x_final = x_fin
        y_final = y_ini

        x_inicial_rot = shape_x - 1 - y_inicial
        y_inicial_rot = x_inicial

        x_final_rot = shape_x - 1 - y_final
        y_final_rot = x_final

    elif angle == 180:
        x_inicial = x_fin
        y_inicial = y_fin

        x_final = x_ini
        y_final = y_ini

        x_inicial_rot = shape_x - 1 - x_inicial
        y_inicial_rot = shape_y - 1 - y_inicial

        x_final_rot = shape_x - 1 - x_final
        y_final_rot = shape_y - 1 - y_final

    elif angle == 270:
        x_inicial = x_fin
        y_inicial = y_ini

        x_final = x_ini
        y_final = y_fin

        x_inicial_rot = y_inicial
        y_inicial_rot = shape_y - 1 - x_inicial

        x_final_rot = y_final
        y_final_rot = shape_y - 1 - x_final

    else:
        x_inicial_rot = x_ini
        y_inicial_rot = y_ini
        x_final_rot = x_fin
        y_final_rot = y_fin

    return x_inicial_rot, y_inicial_rot, x_final_rot, y_final_rot
