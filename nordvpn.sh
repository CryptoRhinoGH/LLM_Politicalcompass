#!/usr/bin/env zsh

# ------------- Utility Functions ----------------

function print_error { printf '%b' "\e[31m${1}\e[0m\n" >&2 }
function print_green { printf '%b' "\e[32m${1}\e[0m\n" 2>&1 }
function check_command { command -v "$1" &>/dev/null }
function public_ip { printf '%b' "$(curl -s ipinfo.io)\n" }

# ------------- DNS Settings --------------------

VPN_DNS_1="8.8.8.8"
VPN_DNS_2="1.1.1.1"
INTERFACE="Wi-Fi"
DNS_BACKUP_FILE="$HOME/.original_dns_servers"

function flush_dns {
    sudo dscacheutil -flushcache
    sudo killall -HUP mDNSResponder
}

function backup_dns {
    print_green "Backing up current DNS settings..."
    networksetup -getdnsservers "$INTERFACE" > "$DNS_BACKUP_FILE"
}

function restore_dns {
    if [[ -f "$DNS_BACKUP_FILE" ]]; then
        local servers
        servers=$(cat "$DNS_BACKUP_FILE")
        if [[ "$servers" == "There aren't any DNS Servers set on $INTERFACE." ]]; then
            sudo networksetup -setdnsservers "$INTERFACE" empty
        else
            sudo networksetup -setdnsservers "$INTERFACE" $=servers
        fi
        rm "$DNS_BACKUP_FILE"
    else
        print_error "No DNS backup found — skipping restore."
    fi
    flush_dns
}

function set_vpn_dns {
    print_green "Setting VPN DNS to $VPN_DNS_1 and $VPN_DNS_2"
    sudo networksetup -setdnsservers "$INTERFACE" "$VPN_DNS_1" "$VPN_DNS_2"
    flush_dns
}

# ------------- VPN Connect/Disconnect -----------

function connect_nordvpn {
    local cred_file_path="$1"
    local ovpn_config_path="$2"

    if [[ -z "$cred_file_path" || -z "$ovpn_config_path" ]]; then
        print_error "Usage: nordvpn <cred_file_path> <ovpn_config_path>"
        return 1
    fi

    disconnect_nordvpn &>/dev/null

    check_command openvpn || { print_error 'openvpn not found. install it with `brew install openvpn`'; return 1; }
    [ -f "$cred_file_path" ] || { print_error "Credential file not found at $cred_file_path"; return 1; }
    [ -f "$ovpn_config_path" ] || { print_error "OVPN config file not found at $ovpn_config_path"; return 1; }

    backup_dns

    sudo openvpn --config "$ovpn_config_path" --auth-user-pass "$cred_file_path" --daemon &>/dev/null

    # Give OpenVPN time to initialize
    sleep 3

    # Check if OpenVPN is actually running
    if pgrep -f "openvpn --config $ovpn_config_path" > /dev/null; then
        print_green "Connected using config: $ovpn_config_path"
        set_vpn_dns
        print_green "$(public_ip)"
        return 0
    else
        print_error "Failed to connect using config: $ovpn_config_path (OpenVPN not running)"
        restore_dns
        return 1
    fi
}

function disconnect_nordvpn {
    check_command pkill || { print_error 'pkill not found. install it with `brew install proctools`'; return 1; }
    sudo pkill openvpn &>/dev/null \
        && { restore_dns; print_green 'NordVPN is disconnected'; return 0; } \
        || { print_error 'NordVPN was not disconnected (might not be running)'; return 1; }
}

# ------------- CLI Entry Point ------------------

if [[ "$1" == "disconnect" ]]; then
    disconnect_nordvpn
elif [[ "$1" == "check_ip" ]]; then
    public_ip
else
    connect_nordvpn "$1" "$2"
fi

