import network
import socket
import time
import ujson
import gc
import sys
from machine import Pin
import uselect

sys.path.append('/pico_traffic')
if 'gpt_client' in sys.modules:
    del sys.modules['gpt_client']
from gpt_client import GPTClient

#WIFI_SSID = "Galaxy A709AA7"
#WIFI_PASSWORD = "ehye1548"
WIFI_SSID = "iPhone"
WIFI_PASSWORD = "123456789"
OPENAI_API_KEY = ""
SERVER_PORT = 80

led = Pin("LED", Pin.OUT)
led.off()

# ==========================================
# === 交通號誌 GPIO 初始化 ===
# ==========================================
ns_red = Pin(0, Pin.OUT)
ns_yellow = Pin(1, Pin.OUT)
ns_green = Pin(2, Pin.OUT)

ew_red = Pin(3, Pin.OUT)
ew_yellow = Pin(4, Pin.OUT)
ew_green = Pin(5, Pin.OUT)

# 初始全紅
ns_red.on(); ns_yellow.off(); ns_green.off()
ew_red.on(); ew_yellow.off(); ew_green.off()

# ==========================================
# === 七段顯示器 GPIO 初始化 ===
# ==========================================
# 段 (Segments) A-G, DP: GP6-GP13
segment_pins = [6, 7, 8, 9, 10, 11, 12, 13]
segments = [Pin(p, Pin.OUT) for p in segment_pins]

# 位數 (Digits) 1-4: GP14-GP17
# 假設順序 [最左, 左中, 右中, 最右] -> 我們用 [2] 和 [3]
digit_pins = [14, 15, 16, 17]
digits = [Pin(p, Pin.OUT) for p in digit_pins]

# 數字字型 (共陰極: 1亮 0滅)
number_map = {
    '0': [1,1,1,1,1,1,0], '1': [0,1,1,0,0,0,0], '2': [1,1,0,1,1,0,1],
    '3': [1,1,1,1,0,0,1], '4': [0,1,1,0,0,1,1], '5': [1,0,1,1,0,1,1],
    '6': [1,0,1,1,1,1,1], '7': [1,1,1,0,0,0,0], '8': [1,1,1,1,1,1,1],
    '9': [1,1,1,1,0,1,1], ' ': [0,0,0,0,0,0,0]
}

# ==========================================
# === [Pico 2W 優化版] 顯示器控制函式 ===
# ==========================================

def clear_all_segments():
    """完全清除所有段和位數"""
    for d in digits:
        d.value(1)  # 共陰極：High = 關閉位數
    for s in segments:
        s.value(0)  # 關閉所有段 (段設為Low)

def display_digit(char, digit_index):
    """
    顯示單一數字到指定位數
    digit_index: 硬體位數索引 (2=十位, 3=個位)
    """
    # 1. 完全消隱
    clear_all_segments()
    time.sleep_us(200)  # 消隱穩定時間
    
    # 2. 設定段資料
    pattern = number_map.get(char, number_map[' '])
    for j in range(7):
        segments[j].value(pattern[j])
    
    # 3. 段資料穩定延遲
    time.sleep_us(100)
    
    # 4. 啟動該位數
    digits[digit_index].value(0)  # 共陰極：Low = 導通
    
    # 5. 顯示時間 (亮度)
    time.sleep_ms(4)
    
    # 6. 關閉該位數
    digits[digit_index].value(1)
    time.sleep_us(150)  # 位數間隔

def refresh_display(number_val):
    """改進的掃描顯示函數"""
    if number_val > 99: number_val = 99
    if number_val < 0: number_val = 0
    
    s_num = "{:02d}".format(number_val)
    
    # 依序顯示十位數和個位數
    # 請確認硬體接線：digits[2]是左邊(十位)，digits[3]是右邊(個位)
    display_digit(s_num[0], 2)  
    display_digit(s_num[1], 3)

def countdown_timer(wait_seconds, start_number):
    """倒數計時器 (含訊號中斷檢測)"""
    start_ticks = time.ticks_ms()
    target_ticks = wait_seconds * 1000
    last_second = -1
    
    while True:
        # ==========================================
        # ★ 新增：檢查是否有新連線 (非阻塞)
        # ==========================================
        # s 是你的全域 Socket 物件
        # select 參數為 0 代表「看一眼馬上走」，不會卡住
        r, w, e = uselect.select([s], [], [], 0)
        if r:
            print("⚡ 偵測到新訊號！強制中斷目前倒數...")
            # 拋出一個異常，這會像「緊急彈射椅」一樣
            # 直接炸開這層函式，跳回主迴圈的 except 區塊
            raise Exception("New Signal Interrupt")

        # ==========================================
        # 原本的倒數邏輯
        # ==========================================
        elapsed_ms = time.ticks_diff(time.ticks_ms(), start_ticks)
        if elapsed_ms >= target_ticks:
            break
            
        elapsed_sec = elapsed_ms // 1000
        current_display = start_number - elapsed_sec
        if current_display < 0: current_display = 0
        
        # 只在秒數變化時打印 (減少 lag)
        if elapsed_sec != last_second:
            print(f"Countdown: {current_display:02d}")
            last_second = elapsed_sec
        
        # 高速刷新顯示
        refresh_display(current_display)
    
    # 確保最後顯示正確數字
    end_display = start_number - wait_seconds
    if end_display < 0: end_display = 0
    
    # 穩定顯示結束畫面 300ms
    # (這裡如果要更完美，也可以加上同樣的 select 檢查)
    end_time = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), end_time) < 300:
        refresh_display(end_display)

# ==========================================
# === 網路與主要邏輯 ===
# ==========================================

def blink(t=3, i=0.1):
    for _ in range(t):
        led.on(); time.sleep(i); led.off(); time.sleep(i)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print("Connecting:", WIFI_SSID)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    for x in range(20):
        if wlan.isconnected(): break
        led.toggle(); time.sleep(1)

if not wlan.isconnected():
    print("WiFi FAILED")
    while True: blink(5, 0.2); time.sleep(1)

ip = wlan.ifconfig()[0]
print("WiFi OK IP:", ip)
blink(3, 0.1)

print("Init GPT")
gpt = GPTClient(api_key=OPENAI_API_KEY)
print("GPT OK")
blink(2, 0.1)

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', SERVER_PORT))
s.listen(1)
print("==================================================")
print("  Smart Traffic System (Optimized Display)")
print("==================================================")
print("  Pico IP:", ip)
print("==================================================")

def send_json(c, d):
    b = ujson.dumps(d)
    r = "HTTP/1.1 200 OK\r\nContent-Type: application/json; charset=utf-8\r\nAccess-Control-Allow-Origin: *\r\nAccess-Control-Allow-Methods: GET, POST, OPTIONS\r\nAccess-Control-Allow-Headers: Content-Type\r\nContent-Length: " + str(len(b.encode('utf-8'))) + "\r\nConnection: close\r\n\r\n"
    c.send(r.encode('utf-8'))
    c.send(b.encode('utf-8'))

def update_hardware_lights(data):
    try:
        direction = data.get('direction', '')
        try:
            duration = int(data.get('duration', 10))
        except:
            duration = 10
            
        print(f"Control -> Dir: {direction}, Time: {duration}s")
        
        green_time = duration - 3
        if green_time < 0: green_time = 0

        # === 1. 綠燈狀態 ===
        if "north-south" in direction or "南北" in direction:
            ns_green.on(); ns_yellow.off(); ns_red.off()
            ew_green.off(); ew_yellow.off(); ew_red.on()
        elif "east-west" in direction or "東西" in direction:
            ew_green.on(); ew_yellow.off(); ew_red.off()
            ns_green.off(); ns_yellow.off(); ns_red.on()
        
        # 綠燈倒數
        if green_time > 0:
            countdown_timer(green_time, start_number=duration)

        # === 2. 黃燈狀態 ===
        print("YELLOW (Last 3s)")
        if "north-south" in direction or "南北" in direction:
            ns_green.off(); ns_yellow.on(); ns_red.off()
        elif "east-west" in direction or "東西" in direction:
            ew_green.off(); ew_yellow.on(); ew_red.off()

        # 黃燈倒數 (從 03 開始)
        countdown_timer(3, start_number=3)

        # === 3. 紅燈狀態 ===
        print("ALL RED")
        ns_red.on(); ns_yellow.off(); ns_green.off()
        ew_red.on(); ew_yellow.off(); ew_green.off()
        
        # 結束畫面 (顯示 00 並停留一下)
        end_time = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), end_time) < 1000: # 停留1秒
            refresh_display(0)

    except Exception as e:
        print("GPIO Error:", e)
        ns_red.on(); ns_yellow.off(); ns_green.off()
        ew_red.on(); ew_yellow.off(); ew_green.off()
        
while True:
    gc.collect()
    try:
        cl, addr = s.accept()
        cl.settimeout(30)
        
        req = cl.recv(2048).decode('utf-8')
        m = req.split(' ')[0]
        p = req.split(' ')[1] if ' ' in req else '/'

        if m == 'OPTIONS':
            cl.send("HTTP/1.1 200 OK\r\nAccess-Control-Allow-Origin: *\r\nAccess-Control-Allow-Methods: GET, POST, OPTIONS\r\nAccess-Control-Allow-Headers: Content-Type\r\nContent-Length: 0\r\n\r\n".encode())
            cl.close()
            continue

        if m == 'POST' and '/traffic' in p:
            bd = req[req.find('\r\n\r\n') + 4:]
            dt = ujson.loads(bd)
            print("Traffic:", dt)
            led.on()
            rs = gpt.get_traffic_decision(dt)
            send_json(cl, rs)
            cl.close()
            update_hardware_lights(rs)
            led.off()

        elif m == 'POST' and '/control' in p:
            bd = req[req.find('\r\n\r\n') + 4:]
            dt = ujson.loads(bd)
            print("Test:", dt)
            led.on()
            send_json(cl, {"status": "ok", "mode": "test"})
            cl.close()
            update_hardware_lights(dt)
            led.off()

        else:
            send_json(cl, {"status": "online", "ip": ip})
        
        try: cl.close()
        except: pass
            
    except Exception as e:
        print("Err:", e)
        led.off()
        try: cl.close()
        except: pass
