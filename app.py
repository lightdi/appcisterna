from flask import Flask, render_template, jsonify
import threading
import paho.mqtt.client as mqtt

# ====== CONFIGURAÇÕES DO BROKER MQTT ======
MQTT_BROKER = "200.129.71.149"
MQTT_PORT = 1883
MQTT_USER = "iot"
MQTT_PASS = "123"
MQTT_TOPIC = "Sede/Cisterna1/Volume"

# ====== VARIÁVEL GLOBAL PARA O VOLUME ======
volume_atual = {"valor": None}

# ====== CALLBACKS MQTT ======
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado ao broker MQTT")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"❌ Falha na conexão (código {rc})")

def on_message(client, userdata, msg):
    try:
        valor = msg.payload.decode()
        print(f"📩 Volume recebido: {valor}")
        volume_atual["valor"] = valor
    except Exception as e:
        print("Erro ao decodificar mensagem:", e)

# ====== FUNÇÃO PARA EXECUTAR O CLIENTE MQTT EM THREAD ======
def mqtt_thread():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

# ====== INICIALIZAÇÃO DO FLASK ======
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/volume")
def get_volume():
    return jsonify(volume_atual)

# ====== MAIN ======
if __name__ == "__main__":
    t = threading.Thread(target=mqtt_thread)
    t.daemon = True
    t.start()

    app.run(host="0.0.0.0", port=5000, debug=True)
