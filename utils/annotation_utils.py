import json


def load_annotations(labels_fpath, resize_scale=1.0):
    with open(labels_fpath, encoding="utf-8") as json_file:
        json_arq = json.load(json_file)
    for idx in range(len(json_arq)):
        json_arq[idx]["region_shape_attributes"]["all_points_x"] = list(
            map(
                lambda c: c * resize_scale,
                json_arq[idx]["region_shape_attributes"]["all_points_x"],
            )
        )
        json_arq[idx]["region_shape_attributes"]["all_points_y"] = list(
            map(
                lambda c: c * resize_scale,
                json_arq[idx]["region_shape_attributes"]["all_points_y"],
            )
        )
    return json_arq
