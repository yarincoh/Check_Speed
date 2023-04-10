import psutil
import speedtest
import time
import socket
import keyboard
import signal
import threading

# Set up variables to track network status and speed
last_status = None
last_speed = None
last_interface = None
last_report_time = 0

# Define a function to test the network speed and return the download speed in Mbps
def test_speed(interface_name):
    while True:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1000000
        return download_speed


# Define a function to output a report of network status and speed
def output_report():
    global last_status, last_speed, last_interface, last_report_time
    now = time.strftime("%Y-%m-%d %H:%M:%S")

    # Get the active network interface
    addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in addrs.items():
        for addr in interface_addresses:
            if addr.family == socket.AF_INET:
                ip_address = addr.address
                break

    # Print the network status and speed
    if last_status is not None:
        if not last_status and time.time() - last_report_time >= 30:
            print(f"{now}: Network disconnected")
        elif last_status and time.time() - last_report_time >= 30:
            print(f"{now}: Network reconnected")
    else:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: Network connected")

    if last_speed is not None and last_interface == interface_name:
        print(f"{now}: Network speed dropped to {test_speed(interface_name):.2f} Mbps" if test_speed(interface_name) < last_speed else f"{now}: Network speed stable at {test_speed(interface_name):.2f} Mbps")
    else:
        print(f"{now}: Network speed at {test_speed(interface_name):.2f} Mbps")
    last_status = psutil.net_if_stats()[interface_name].isup
    last_speed = test_speed(interface_name)
    last_interface = interface_name
    last_report_time = time.time()

# if ctrl+c is pressed the script stop
def signal_handler(sig, frame):
    print("Program terminated manually!")
    raise SystemExit

# Output a report non stop
while True:
    t = threading.Thread(target=test_speed, args=(last_interface,))
    t.daemon = True
    t.start()
    try:
        output_report()
    except KeyboardInterrupt: # if ctrl+c is pressed the script stop
        print("Program terminated manually!")
        raise SystemExit
    for i in range(6):  # Output the network speed every 15 seconds 
        try:
            network_speed = test_speed(last_interface)
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: Network speed: {network_speed:.2f} Mbps")
        except Exception as e:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: Error: {e}\nWe can't connect to the internet.")
            time.sleep(2)
        except KeyboardInterrupt: # if ctrl+c is pressed the script stop
            signal.signal(signal.SIGINT, signal_handler)
        time.sleep(3)
