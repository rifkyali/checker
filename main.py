import json
import requests
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

KPU_PILPRES_URL = 'https://pemilu2019.kpu.go.id/static/json/hhcw/ppwp'
data_all_tps = []

with open('data/aceh.json') as json_file:
    data_all_tps = json.load(json_file)

text_file = open("hasil_check_tps_aceh.txt", "w")
text_file.write("[\n")

for tps in data_all_tps:
    data_tps = {}
    remarks = []
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
            res = requests.get(TPS_URL, verify=False, timeout=10)
            if not hasattr(res, 'status_code'):
                res = None

            if hasattr(res, 'status_code'):
                if res.status_code not in (200, 201):
                    res = None
        except Exception as e:
            print(e)
            print('Unable to fetch data')
            time.sleep(2)
            pass

    data_tps = res.json()

    if "chart" not in data_tps:
        remarks.append(
            "Data Belum Tersedia")
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
            "remarks": remarks
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

    if (total_suara_01+total_suara_02) != total_suara_sah:
        remarks.append("Total Surat Suara Sah Tidak Sesuai")

    if (total_suara_sah+total_suara_tidak_sah) != total_seluruh_suara:
        remarks.append("Total Seluruh Surat Suara Tidak Sesuai")

    if total_seluruh_suara != total_pengguna_hakpilih:
        remarks.append(
            "Total Surat Suara Tidak Sesuai dengan Total Pengguna Hak Pilih")

    if total_pemilih_terdaftar < total_pengguna_hakpilih:
        remarks.append(
            "Total Pengguna Hak Pilih melebihi Total Pemilih Terdaftar")

    catatan = "{}|{}|{}|{}|{}|{}".format(
        province_name, city_name, kecamatan_name, kelurahan_name, tps_name, remarks)

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
        "remarks": remarks
    }
    text_file.write(json.dumps(data_ppwp_tps))
    text_file.write(",\n")

    print(data_ppwp_tps)
    time.sleep(0.5)

text_file.write("]")
text_file.close()
