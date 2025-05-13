from openvpnclient import OpenVPNClient
import subprocess
import time

# Path to your .ovpn configuration file
#ovpn_file = '/Users/abhisareen/Documents/PSU/temp/mitproject/LLM_Polilean/vpnconfigs/ipvanish-US-Seattle-sea-c01.ovpn'
ovpn_file = '/Users/abhisareen/Documents/PSU/temp/mitproject/LLM_Polilean/vpnconfigs/ipvanish-IN-Virtual-pnq-c01.ovpn'
#ovpn_file = '/Users/abhisareen/Documents/PSU/temp/mitproject/LLM_Polilean/vpnconfigs/ipvanish-CA-Montreal-yul-c03.ovpn'

def get_public_ip():
    """
    Get the public IP address using curl and ifconfig.me.
    """
    try:
        result = subprocess.run(
            ["curl", "-s", "ifconfig.me"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error fetching public IP: {e}")
        return None

# Initialize the OpenVPN client with the configuration file
vpn = OpenVPNClient(ovpn_file)

# Connect to the VPN
try:
    vpn.connect()
except:
    exit()
    print("Error, disconnecting")
    vpn.disconnect()
    vpn.connect()

print("VPN connection established.")

time.sleep(5)
# Check public IP address
print("Checking public IP address...")
vpn_ip = get_public_ip()
if vpn_ip:
    print(f"Current public IP: {vpn_ip}")
else:
    print("Failed to retrieve public IP address.")
# Your code to interact with the VPN goes here

# Disconnect from the VPN when done
#vpn.disconnect()
#print("VPN connection closed.")

