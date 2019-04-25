import json
import psycopg2
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

KPU_PILPRES_URL = 'https://pemilu2019.kpu.go.id/static/json/hhcw/ppwp'
conn_string = "dbname=ironman_db user=ironman_user password=ironman_pw host=localhost port=5432"

conn = psycopg2.connect(conn_string)
cur = conn.cursor()
cur.execute("SELECT * FROM suara_tps;")
data_all_tps = cur.fetchall()

for tps in data_all_tps:
    print(tps)
    is_valid = True
    error_type = 0
    remarks = "Valid"

    suara_tps_id = tps[0]
    province_id = tps[1]
    province_name = tps[2]
    city_id = tps[3]
    city_name = tps[4]
    kecamatan_id = tps[5]
    kecamatan_name = tps[6]
    kelurahan_id = tps[7]
    kelurahan_name = tps[8]
    tps_id = tps[9]
    tps_name = tps[10]
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
        is_valid = False
        error_type = 5
        remarks = "Data Suara Belum Tersedia"
        query = """UPDATE suara_tps SET is_valid = %s, error_type = %s, remarks = %s, raw_data = %s WHERE id = %s  """
        cur.execute(query, (is_valid, error_type, remarks,
                            json.dumps(data_tps), suara_tps_id))

        conn.commit()
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

    query = """UPDATE suara_tps SET is_valid = %s, error_type = %s, remarks = %s, raw_data = %s, total_pemilih_terdaftar = %s, total_pengguna_hak_pilih = %s, total_surat_suara_digunakan = %s, total_surat_suara_sah = %s, total_surat_suara_tidak_sah = %s, total_surat_suara_01 = %s, total_surat_suara_02 = %s WHERE id = %s  """
    cur.execute(query, (is_valid, error_type, remarks,
                        json.dumps(data_tps), total_pemilih_terdaftar, total_pengguna_hakpilih, total_seluruh_suara, total_suara_sah, total_suara_tidak_sah, total_suara_01, total_suara_02, suara_tps_id))

    conn.commit()


cur.close()
conn.close()
