import json
import requests
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

KPU_WILAYAH_URL = 'https://pemilu2019.kpu.go.id/static/json/wilayah'
KPU_PILPRES_URL = 'https://pemilu2019.kpu.go.id/static/json/hhcw/ppwp'
data_all_tps = []
data_provinces = {}

res = requests.get(KPU_WILAYAH_URL+'/0.json', verify=False, timeout=2)
data_provinces = res.json()
for key_province in data_provinces:
    data_cities = {}
    province_data = data_provinces[key_province]
    province_id = key_province
    province_name = province_data.get('nama')
    province_file = "data tps/{}.json".format(province_name.lower())

    with open(province_file) as json_file:
        data_all_tps = json.load(json_file)

    result_file = "suara_{}.txt".format(province_name.lower())
    text_file = open(result_file, "w")
    text_file.write("[\n")

    for tps in data_all_tps:
        data_tps = {}
        is_valid = True
        error_type = 0
        remarks = "Valid"

        province_id = tps.get('id_provinsi')
        province_name = tps.get('nama_provinsi')
        city_id = tps.get('id_kota')
        city_name = tps.get('nama_kota')
        kecamatan_id = tps.get('id_kecamatan')
        kecamatan_name = tps.get('nama_kecamatan')
        kelurahan_id = tps.get('id_kelurahan')
        kelurahan_name = tps.get('nama_kelurahan')
        tps_id = tps.get('id_tps')
        tps_name = tps.get('nama_tps')
        TPS_URL = "{}/{}/{}/{}/{}/{}.json".format(
            KPU_PILPRES_URL, province_id, city_id, kecamatan_id, kelurahan_id, tps_id)

        res = None
        while res is None:
            try:
                res = requests.get(TPS_URL, verify=False, timeout=2)
                if not hasattr(res, 'status_code'):
                    res = None

                if hasattr(res, 'status_code'):
                    if res.status_code not in (200, 201):
                        res = None
            except Exception as e:
                print(e)
                print('Unable to fetch data suara tps')
                pass

        data_tps = res.json()

        if "chart" not in data_tps:
            data_ppwp_tps = {
                "id_provinsi": province_id,
                "nama_provinsi": province_name,
                "id_kota": city_id,
                "nama_kota": city_name,
                "id_kecamatan": kecamatan_id,
                "nama_kecamatan": kecamatan_name,
                "id_kelurahan": kelurahan_id,
                "nama_kelurahan": kelurahan_name,
                "id_tps": tps_id,
                "nama_tps": tps_name,
                "data": data_tps,
                "is_valid": False,
                "error_type": 5,
                "remarks": "Data Suara Belum Tersedia"
            }
            text_file.write(json.dumps(data_ppwp_tps))
            text_file.write(",\n")

            print(data_ppwp_tps)
            continue

        total_suara_01 = data_tps.get('chart').get('21')
        total_suara_02 = data_tps.get('chart').get('22')
        total_pemilih_terdaftar = data_tps.get('pemilih_j')
        total_pengguna_hakpilih = data_tps.get('pengguna_j')
        total_suara_sah = data_tps.get('suara_sah')
        total_suara_tidak_sah = data_tps.get('suara_tidak_sah')
        total_seluruh_suara = data_tps.get('suara_total')

        if total_pemilih_terdaftar < total_pengguna_hakpilih:
            remarks = "Total Pengguna Hak Pilih Melebihi Total Pemilih Terdaftar"
            error_type = 1
            is_valid = False

        if total_seluruh_suara != total_pengguna_hakpilih:
            remarks = "Total Seluruh Surat Suara Yang Digunakan Tidak Sesuai Dengan Total Pengguna Hak Pilih"
            error_type = 2
            is_valid = False

        if (total_suara_sah+total_suara_tidak_sah) != total_seluruh_suara:
            remarks = "Total Seluruh Surat Suara Yang Digunakan Tidak Sesuai Dengan Total Suara Sah Dan Tidak Sah"
            error_type = 3
            is_valid = False

        if (total_suara_01+total_suara_02) != total_suara_sah:
            remarks = "Total Surat Suara Sah Tidak Sesuai Dengan Total Suara Sah 01 Dan Total Suara Sah 02"
            error_type = 4
            is_valid = False

        data_ppwp_tps = {
            "id_provinsi": province_id,
            "nama_provinsi": province_name,
            "id_kota": city_id,
            "nama_kota": city_name,
            "id_kecamatan": kecamatan_id,
            "nama_kecamatan": kecamatan_name,
            "id_kelurahan": kelurahan_id,
            "nama_kelurahan": kelurahan_name,
            "id_tps": tps_id,
            "nama_tps": tps_name,
            "data": data_tps,
            "is_valid": is_valid,
            "error_type": error_type,
            "remarks": remarks
        }
        text_file.write(json.dumps(data_ppwp_tps))
        text_file.write(",\n")

        print(data_ppwp_tps)

    text_file.write("]")
    text_file.close()
