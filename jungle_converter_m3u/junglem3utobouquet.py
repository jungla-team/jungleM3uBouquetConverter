# -*- coding: utf-8 -*-
#Convertir m3u en favorito enigma2 by jungle-team en base a diccionario palabras clave.

import os
import re
import glob
import sys 
import requests

ALLOWED_PREFIXES = ["ES-", "ES -", "ES:", "|ES|", "SP -", "SP-", "SP:"]

def write_to_log(log_path, message):
    with open(log_path, 'a') as log_file:
        log_file.write(message + '\n')

def remove_accents(text):
    accent_replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ü': 'u', 'Ü': 'U', 'ñ': 'n', 'Ñ': 'N'
    }
    for original, replacement in accent_replacements.items():
        text = text.replace(original, replacement)
    return text

def clean_channel_name(channel_name):
    cleaned_name = remove_accents(channel_name.lower())
    return re.sub(r'\W+', '', cleaned_name)
    
def is_valid_name(name):
    return bool(re.match(r'^[\w\s#]+$', name))

def load_satellite_reference(file_path):
    with open(file_path, "r") as file:
        data = {}
        for line in file.readlines():
            try:
                parts = line.strip().split("-->")
                if len(parts) == 4:
                    name, ref, display_name, order = parts
                    order = int(order)
                elif len(parts) == 3:
                    name, ref, display_name_or_order = parts
                    try:
                        order = int(display_name_or_order)
                        display_name = None
                    except ValueError:
                        display_name = display_name_or_order
                        order = None
                else:
                    name, ref = parts
                    display_name = None
                    order = None
                if is_valid_name(name):
                    data[clean_channel_name(name)] = (ref, display_name, order)
                else:
                    print(f"Subnormal, tienes error en la línea: {line.strip()}")
            except ValueError:
                print(f"Subnormal, tienes error en la línea: {line.strip()}")
        return data
        
def find_channel_with_keyword(channel_name, satellite_reference):
    cleaned_channel_name = clean_channel_name(channel_name)
    matched_keyword = None
    max_length = 0
    for keyword, ref in satellite_reference.items():
        cleaned_keyword = clean_channel_name(keyword)
        if cleaned_keyword in cleaned_channel_name and len(cleaned_keyword) > max_length:
            matched_keyword = keyword
            max_length = len(cleaned_keyword)
    return matched_keyword

def add_to_bouquets_tv(favorite_name):
    bouquets_tv_path = "/etc/enigma2/bouquets.tv"
    entry = '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.{}.tv" ORDER BY bouquet\n'.format(favorite_name)
    if not os.path.exists(bouquets_tv_path):
        with open(bouquets_tv_path, "w") as bouquets_tv_file:
            bouquets_tv_file.write(entry)
            bouquets_tv_file.write("\n")
    else:
        with open(bouquets_tv_path, "r") as bouquets_tv_file:
            lines = bouquets_tv_file.readlines()
        if lines and not lines[-1].strip():
            lines.pop()
        if entry not in lines:
            with open(bouquets_tv_path, "w") as bouquets_tv_file:
                for line in lines:
                    bouquets_tv_file.write(line)
                    if not line.strip():
                        break
                bouquets_tv_file.write(entry.strip())
                bouquets_tv_file.write("\n")
                bouquets_tv_file.writelines(lines[len(lines) - (len(lines) - lines.index(line)) + 1:])
        else:
            print("No se sobreescribe el nombre en bouquet.tv ya existe previamente")

def convert_m3u_to_enigma2(input_file, output_file, satellite_reference_file, log_path):
    m3u_file = open(input_file, "r")
    enigma2_file = open(os.path.splitext(output_file)[0] + ".tv", "w")
    satellite_reference = load_satellite_reference(satellite_reference_file)
    favorite_name = os.path.splitext(os.path.basename(input_file))[0]
    enigma2_file.write("#NAME {}\n".format(favorite_name))
    unique_id = 1
    channel_reference = None
    channels = []
    occupied_orders = []
    skip_channel = False
    for line in m3u_file:
        if line.startswith("#EXTINF:"):
            if skip_channel:
                skip_channel = False
                continue
            channel_name = re.search('tvg-name="(.*?)"', line)
            if channel_name:
                channel_name = channel_name.group(1)
            else:
                channel_name = re.search('tvg-id="(.*?)"', line)
                if channel_name:
                    channel_name = channel_name.group(1)
                else:
                    channel_name_match = re.search(',(.*)', line)
                    if channel_name_match:
                        channel_name = channel_name_match.group(1)
                    else:
                        print(f"Error: no se pudo extraer el nombre del canal de la línea: {line.strip()}")
                        continue
            prefix_allowed = any(channel_name.startswith(prefix) for prefix in ALLOWED_PREFIXES)
            if prefix_allowed:
                matching_channel_name = find_channel_with_keyword(channel_name, satellite_reference)
                if matching_channel_name:
                    channel_reference, channel_display_name, order = satellite_reference.get(matching_channel_name.lower())
                    if channel_display_name:
                        channel_name = channel_display_name
                    write_to_log(log_path, f"Parcheado: {channel_name}")

                    if order is not None:
                        occupied_orders.append(order)
                else:
                    channel_reference = "4097:0:1:{:X}:0:0:0:0:0:0:".format(unique_id)
                    unique_id += 1
                    order = None
                    write_to_log(log_path, f"No encontrado: {channel_name}")
            else:
                channel_reference = "4097:0:1:{:X}:0:0:0:0:0:0:".format(unique_id)
                unique_id += 1
                order = None
        elif line.startswith("http"):
            if line.strip().endswith(".mkv") or line.strip().endswith(".avi") or line.strip().endswith(".mp4"):
                skip_channel = True
                channel_reference = None
                continue
            if channel_reference is not None and not skip_channel:
                channel_url = line.strip()
                enigma2_url = "http%3a" + channel_url[5:].replace(":", "%3a")
                channels.append((order, channel_reference, enigma2_url, channel_name))
                channel_reference = None
            elif skip_channel:
                skip_channel = False

    def get_free_order():
        free_order = 1
        while True:
            if free_order not in occupied_orders:
                yield free_order
            free_order += 1
    free_order_gen = get_free_order()
    ordered_channels = []
    unordered_channels = []
    for channel in channels:
        if channel[0] is None:
            unordered_channels.append(channel)
        else:
            ordered_channels.append(channel)
    max_order = max(ordered_channels, key=lambda x: x[0])[0]
    for i, channel in enumerate(unordered_channels, start=max_order + 1):
        ordered_channels.append((i, *channel[1:]))
    ordered_channels.sort(key=lambda x: x[0])
    for _, channel_reference, enigma2_url, channel_name in ordered_channels:
        enigma2_file.write("#SERVICE {}{}\n".format(channel_reference,enigma2_url))
        enigma2_file.write("#DESCRIPTION {}\n".format(channel_name))
    m3u_file.close()
    enigma2_file.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        m3u_url = sys.argv[1]
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        response = requests.get(m3u_url, headers=headers)
        if response.status_code == 200:
            if len(sys.argv) > 2:
                output_filename = sys.argv[2]
                if not output_filename.endswith(".m3u"):
                    output_filename += ".m3u"
            else:
                output_filename = "temp.m3u"
            output_path = os.path.join("/etc/jungle_converter_m3u", output_filename)
            with open(output_path, "wb") as temp_m3u:
                temp_m3u.write(response.content)
            input_files = [output_path]
        else:
            print(f"No se pudo descargar el archivo m3u de {m3u_url}. Código de estado: {response.status_code}")
            sys.exit(1)
    else:
        input_files = glob.glob("/etc/jungle_converter_m3u/*.m3u")
        if not input_files:
            print("Vamos a ver, piensa, si no tienes ningun m3u en el directorio /etc/jungle_converter_m3u como quieres que funcione")
            sys.exit(1)
    output_dir = "/etc/enigma2"
    satellite_reference_file = "/etc/jungle_converter_m3u/satellite_references.txt"
    log_path = "/etc/jungle_converter_m3u/log.txt"
    for input_file in input_files:
        output_file = os.path.join(output_dir, "userbouquet." + os.path.splitext(os.path.basename(input_file))[0] + ".tv")
        favorite_name = os.path.splitext(os.path.basename(input_file))[0]
        convert_m3u_to_enigma2(input_file, output_file, satellite_reference_file, log_path)
        add_to_bouquets_tv(favorite_name)
            