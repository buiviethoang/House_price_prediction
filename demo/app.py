import re
from flask import Flask, request
from flask_cors import CORS, cross_origin
from tensorflow.python.keras.backend import arange

from data_function import DataFunction
from models.data import Data
import numpy as np
import joblib
from tensorflow.keras.models import load_model

app = Flask(__name__)
CORS(app)


@app.route("/get-data")
@cross_origin()
def get_data():
    data_func = DataFunction()

    return {
        "is_dinning_room": [
            ["True", data_func.get_mean_if("price", "is_dinning_room", "True")],
            ["False", data_func.get_mean_if("price", "is_dinning_room", "False")],
        ],
        "is_kitchen": [
            ["True", data_func.get_mean_if("price", "is_kitchen", "True")],
            ["False", data_func.get_mean_if("price", "is_kitchen", "False")],
        ],
        "is_terrace": [
            ["True", data_func.get_mean_if("price", "is_terrace", "True")],
            ["False", data_func.get_mean_if("price", "is_terrace", "False")],
        ],
        "is_car_park": [
            ["True", data_func.get_mean_if("price", "is_car_park", "True")],
            ["False", data_func.get_mean_if("price", "is_car_park", "False")],
        ],
        "type": [
            ["Nhà mặt tiền", data_func.get_mean_if("price", "type", "Nhà mặt tiền")],
            ["Nhà trong hẻm", data_func.get_mean_if("price", "type", "Nhà trong hẻm")],
        ],
        "city": [
            ["Hà Nội", data_func.get_mean_if("price", "city", "Hà Nội")],
            ["Hồ Chí Minh", data_func.get_mean_if("price", "city", "Hồ Chí Minh")],
        ],
        "district": [
            ["Ngoại thành", data_func.get_mean_if("price", "district", "Ngoại thành")],
            ["Nội thành", data_func.get_mean_if("price", "district", "Nội thành")],
        ],
        "bedroom_number": data_func.get_mean_group_by("price", "bedroom_number"),
        "floor_number": data_func.get_mean_group_by("price", "floor_number"),
        "area": [
            ["20-30", data_func.get_mean_if_range("price", "area", 20, 30)],
            ["30-40", data_func.get_mean_if_range("price", "area", 30, 40)],
            ["40-50", data_func.get_mean_if_range("price", "area", 40, 50)],
            ["50-60", data_func.get_mean_if_range("price", "area", 50, 60)],
            ["60-70", data_func.get_mean_if_range("price", "area", 60, 70)],
            ["70-80", data_func.get_mean_if_range("price", "area", 70, 80)],
            ["80-90", data_func.get_mean_if_range("price", "area", 80, 90)],
            ["90-100", data_func.get_mean_if_range("price", "area", 90, 100)],
            ["100-200", data_func.get_mean_if_range("price", "area", 100, 200)],
        ],
    }


@app.route("/predict")
@cross_origin()
def home():
    try:
        area = request.args.get("area", type=float)
        floor_number = request.args.get("floor_number", type=int)
        bedroom_number = request.args.get("bedroom_number", type=int)
        is_dinning_room = request.args.get("is_dinning_room", type=int)
        is_kitchen = request.args.get("is_kitchen", type=int)
        is_terrace = request.args.get("is_terrace", type=int)
        is_car_park = request.args.get("is_car_park", type=int)
        rtype = request.args.get("type", type=int)
        direction = request.args.get("direction", type=str)
        street_in_front_of_house = request.args.get(
            "street_in_front_of_house", type=float
        )
        width = request.args.get("width", type=float)
        city = request.args.get("city", type=int)
        district = request.args.get("district", type=int)
        option = request.args.get("option", type=int)
    except:
        return {"price": 0}

    price = predict(
        area,
        floor_number,
        bedroom_number,
        is_dinning_room,
        is_kitchen,
        is_terrace,
        is_car_park,
        rtype,
        direction,
        street_in_front_of_house,
        width,
        city,
        district,
        option,
    )

    return {"price": price}


def predict(
    area,
    floor_number,
    bedroom_number,
    is_dinning_room,
    is_kitchen,
    is_terrace,
    is_car_park,
    rtype,
    direction,
    street_in_front_of_house,
    width,
    city,
    district,
    option,
):

    inp_dim = 21
    inp = np.zeros(inp_dim)

    inp[0] = np.log(np.float(area) + 1)  # area
    inp[1] = np.log(float(floor_number) + 1)  # floor number
    inp[2] = np.log(float(bedroom_number) + 1)  # bedroom number
    inp[3] = is_dinning_room  # is dinning room
    inp[4] = is_kitchen  # is kitchen
    inp[5] = is_terrace  # is terrace
    inp[6] = is_car_park  # is car park
    inp[7] = rtype  # type
    inp[8] = np.log(float(street_in_front_of_house) + 1)  # street in front of house
    inp[9] = np.log(float(width) + 1)  # width
    inp[10] = city  # city
    inp[11] = district  # district

    if direction == "Bắc":
        inp[12] = 1
    elif direction == "Nam":
        inp[13] = 1
    elif direction == "None":
        inp[14] = 1
    elif direction == "Tây":
        inp[15] = 1
    elif direction == "Tây Bắc":
        inp[16] = 1
    elif direction == "Tây Nam":
        inp[17] = 1
    elif direction == "Đông":
        inp[18] = 1
    elif direction == "Đông Bắc":
        inp[19] = 1
    elif direction == "Đông Nam":
        inp[20] = 1

    model = 0
    if option == 0:
        model = load_model("../src/Model/mlp.h5")
    else:
        model = joblib.load("../src/Model/xgboost.pkl")

    inp = np.reshape(inp, (1, inp_dim))
    pred = model.predict(inp)

    pred = pred.flatten()
    pred = np.round(pred[0], 2)
    pred = str(pred)

    return pred


if __name__ == "__main__":
    app.run(debug=True)
