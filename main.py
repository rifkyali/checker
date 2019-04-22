import json
import requests
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

KPU_PILPRES_URL = 'https://pemilu2019.kpu.go.id/static/json/hhcw/ppwp'
data_all_tps = []

with open('sumut.json') as json_file:
    data_all_tps = json.load(json_file)

text_file = open("hasil_check_tps_sumut.txt", "w")

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
            res = requests.get(TPS_URL, verify=False)
            if not hasattr(res, 'status_code'):
                res = None

            if hasattr(res, 'status_code'):
                if res.status_code not in (200, 201):
                    res = None
        except:
            print('Unable to fetch data')
            time.sleep(2)
            pass

    data_tps = res.json()

    if "chart" not in data_tps:
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

    if len(remarks) > 0:
        print(catatan)
        text_file.write(catatan)
        text_file.write("\n")

    time.sleep(0.5)

text_file.close()
