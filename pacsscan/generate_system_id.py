def generate_system_id(mac_address):
    # Remove hyphens and convert to uppercase
    mac_address = mac_address.replace('-', '').lower()

    # Check if the input is valid
    if len(mac_address) != 12:
        return "Invalid input format"

    # Reorder the pairs based on the reverse pattern
    generated_system_id = mac_address[10:12] + mac_address[2:4] + "-" + mac_address[6:8] + mac_address[4:6] + mac_address[8:10] + "-" + mac_address[0:2]

    return generated_system_id
mac_address = "00-05-9A-3C-7A-00"
generated_system_id = generate_system_id(mac_address)
print("Original MAC:", mac_address)
print("Scrambled System ID:", generated_system_id)