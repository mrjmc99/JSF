from django.shortcuts import render


def unscramble_mac(scrambled_mac):
    # Remove hyphens and convert to uppercase
    scrambled_mac = scrambled_mac.replace('-', '').replace(':', '').upper()

    # Check if the input is valid
    if len(scrambled_mac) != 12:
        return "Invalid input format"

    # Reorder the pairs based on the pattern
    unscrambled_mac = scrambled_mac[10:12] + scrambled_mac[2:4] + scrambled_mac[6:8] + scrambled_mac[4:6] + scrambled_mac[8:10] + scrambled_mac[0:2]

    # Insert hyphens to format the unscrambled MAC address
    unscrambled_mac = '-'.join([unscrambled_mac[i:i+2] for i in range(0, 12, 2)])

    return unscrambled_mac


def generate_system_id(mac_address):
    # Remove hyphens and convert to uppercase
    mac_address = mac_address.replace('-', '').replace(':', '').lower()

    # Check if the input is valid
    if len(mac_address) != 12:
        return "Invalid input format"

    # Reorder the pairs based on the reverse pattern
    generated_system_id = mac_address[10:12] + mac_address[2:4] + "-" + mac_address[6:8] + mac_address[4:6] + mac_address[8:10] + "-" + mac_address[0:2]

    return generated_system_id


def unscramble_mac_view(request):
    scrambled_mac = request.POST.get('scrambled_mac', '')
    unscrambled_mac = unscramble_mac(scrambled_mac)

    mac_address = request.GET.get('mac_address', '')
    generated_system_id = generate_system_id(mac_address)

    return render(request, 'conversion_results.html', {
        'scrambled_mac': scrambled_mac,
        'unscrambled_mac': unscrambled_mac,
        'mac_address': mac_address,
        'generated_system_id': generated_system_id,
    })
