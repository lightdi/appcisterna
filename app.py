from flask import Flask, render_template, jsonify
import threading
import paho.mqtt.client as mqtt

# ====== CONFIGURAÇÕES DO BROKER MQTT ======
MQTT_BROKER = "200.129.71.149"
MQTT_PORT = 1883
MQTT_USER = "iot"
MQTT_PASS = "123"
MQTT_TOPIC = "Sede/Cisterna1/Volume"

# ====== DIMENSÕES DA CISTERNA (em cm) ======
ALTURA = 230
LARGURA = 350
COMPRIMENTO = 360

# ====== CÁLCULO DO VOLUME TOTAL EM LITROS ======
VOLUME_TOTAL = (ALTURA * LARGURA * COMPRIMENTO) / 1000.0  # cm³ → litros

# ====== VARIÁVEL GLOBAL ======
estado_cisterna = {"volume": None, "porcentagem": None}

# ====== CALLBACKS MQTT ======
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado ao broker MQTT")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"❌ Falha na conexão (código {rc})")

def on_message(client, userdata, msg):
    try:
        valor_str = msg.payload.decode().strip()
        volume_litros = float(valor_str)
        porcentagem = (volume_litros / VOLUME_TOTAL) * 100
        estado_cisterna["volume"] = round(volume_litros, 2)
        estado_cisterna["porcentagem"] = round(porcentagem, 1)
        print(f"📩 Volume recebido: {volume_litros} L ({porcentagem:.1f}%)")
    except Exception as e:
        print("Erro ao processar mensagem:", e)

# ====== THREAD DO MQTT ======
def mqtt_thread():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

# ====== FLASK APP ======
app = Flask(__name__, static_url_path='/appcisterna')

@app.route("/")
def index():
    return render_template("index.html", volume_total=round(VOLUME_TOTAL, 2))

@app.route("/dados")
def get_dados():
    return jsonify(estado_cisterna)

# ===== Gunicorn Configuration =====
t = threading.Thread(target=mqtt_thread)
t.daemon = True
t.start()


# ====== MAIN ======
if __name__ == "__main__":
    t = threading.Thread(target=mqtt_thread)
    t.daemon = True
    t.start()

    app.run(host="0.0.0.0", port=5000, debug=True)
