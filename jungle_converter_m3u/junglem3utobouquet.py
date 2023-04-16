#Convertir m3u en favorito enigma2 by jungle-team en base a diccionario palabras clave.

import os
import re
import glob
import sys 
import requests
from urllib.parse import urlsplit, urlunsplit
import json

def load_config_from_json_file(file_path):
    with open(file_path, "r") as file:
        config = json.load(file)
    return config

config = load_config_from_json_file("/etc/jungle_converter_m3u/jungle_config.json")
ALLOWED_PREFIXES = config["ALLOWED_PREFIXES"]
PORT = config["PORT"]
USER = config["USER"]
PASSWORD = config["PASSWORD"]
OSCAM_ICAM = config["OSCAM_ICAM"]
OSCAM_ICAM_PORT = config["OSCAM_ICAM_PORT"]
USE_GROUP_TITLE = config["USE_GROUP_TITLE"]
PERMITIR_EXTENSION_VIDEO = config["ALLOW_VIDEO_EXTENSIONS"]
VIDEO_EXTENSIONS = tuple(config["VIDEO_TYPE"])
ALLOW_COUNTRIES = config["ALLOW_COUNTRIES"]
COUNTRIES = config["COUNTRIES"]
favorites_by_country = {country: [] for country in COUNTRIES.keys()}

def parse_m3u(file_path):
    tvg_ids = []
    with open(file_path, 'r') as file:
        lines = file.readlines()

        for line in lines:
            tvg_id = re.search(r'tvg-id="(.*?)"', line)
            if tvg_id:
                service_ref = tvg_id.group(1)
                modified_service_ref = re.sub(r'C00000', '21', service_ref)
                tvg_ids.append(modified_service_ref)
    return tvg_ids
                
def order_channels(channels_list):
    occupied_orders = []
    ordered_channels = []
    unordered_channels = []
    for channel in channels_list:
        if channel[0] is None:
            unordered_channels.append(channel)
        else:
            ordered_channels.append(channel)
            occupied_orders.append(channel[0])

    def get_free_order(occupied_orders):
        free_order = 1
        while True:
            if free_order not in occupied_orders:
                yield free_order
            free_order += 1

    free_order_gen = get_free_order(occupied_orders)
    for channel in unordered_channels:
        order = next(free_order_gen)
        ordered_channels.append((order, *channel[1:]))
    ordered_channels.sort(key=lambda x: x[0])
    return ordered_channels

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
    enigma2_file = open(os.path.splitext(output_file)[0] + ".tv", "w")
    satellite_reference = load_satellite_reference(satellite_reference_file)
    favorite_name = os.path.splitext(os.path.basename(input_file))[0]
    enigma2_file.write("#NAME {}\n".format(favorite_name))
    unique_id = 1
    channel_reference = None
    channels = []
    occupied_orders = []
    skip_channel = False
    is_video_channel = False
    tvg_ids = parse_m3u(input_file)
    channel_index = 0
    with open(input_file, "rb") as m3u_file:
        for raw_line in m3u_file:
            try:
                line = raw_line.decode('utf-8')
            except UnicodeDecodeError as e:
                write_to_log(log_path, f"Error de codificación: {e} - Línea omitida: {raw_line.strip()}")
                continue
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
                original_channel_name = channel_name
                group_title = re.search('group-title\s*=\s*["\'](.*?)["\']', line)
                if group_title:
                    group_title = group_title.group(1)
                    if USE_GROUP_TITLE:
                        prefix_allowed = any(group_title.startswith(prefix) for prefix in ALLOWED_PREFIXES)
                    else:
                        prefix_allowed = any(channel_name.startswith(prefix) for prefix in ALLOWED_PREFIXES)
                else:
                    prefix_allowed = any(channel_name.startswith(prefix) for prefix in ALLOWED_PREFIXES)
                if prefix_allowed and not is_video_channel:
                    original_channel_name = channel_name
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
            if line.startswith("http"):
                video_extensions = VIDEO_EXTENSIONS
                is_video_channel = line.strip().endswith(video_extensions)
                if not PERMITIR_EXTENSION_VIDEO and is_video_channel:
                    skip_channel = True
                    channel_reference = None
                    continue
                if channel_reference is not None and not skip_channel:
                    channel_url = line.strip()
                    parsed_url = urlsplit(channel_url)
                    if parsed_url.scheme == "https":
                        enigma2_url = urlunsplit(("https", parsed_url.netloc, parsed_url.path, parsed_url.query, parsed_url.fragment))
                    else:
                        enigma2_url = urlunsplit(("http", parsed_url.netloc, parsed_url.path, parsed_url.query, parsed_url.fragment))
                    if OSCAM_ICAM:
                        channel_reference = tvg_ids[channel_index]
                        enigma2_url = urlunsplit(("http", parsed_url.netloc, parsed_url.path, parsed_url.query, parsed_url.fragment))
                        parsed_url = urlsplit(enigma2_url)
                        enigma2_url = urlunsplit(("http", "127.0.0.1:" + str(OSCAM_ICAM_PORT), parsed_url.path, parsed_url.query, parsed_url.fragment))
                        enigma2_url = enigma2_url.replace(":", "%3a")
                        channel_index += 1
                    else:
                        enigma2_url = enigma2_url.replace(":", "%3a")
                    if USE_GROUP_TITLE:
                        readprefix= group_title
                    else:
                        readprefix= original_channel_name
                    if USE_GROUP_TITLE:
                        readprefix= group_title
                    else:
                        readprefix= original_channel_name
                    if ALLOW_COUNTRIES:
                        added_to_favorites = False
                        for country, prefixes in COUNTRIES.items():
                            if added_to_favorites:
                                break
                            for prefix in prefixes:
                                if readprefix.startswith(prefix):
                                    favorites_by_country[country].append((order, channel_reference, enigma2_url, channel_name))
                                    added_to_favorites = True
                                    break
                    else:
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
    if ordered_channels:
        max_order = max(ordered_channels, key=lambda x: x[0])[0]
    else:
        max_order = 0
    for i, channel in enumerate(unordered_channels, start=max_order + 1):
        ordered_channels.append((i, *channel[1:]))
    ordered_channels.sort(key=lambda x: x[0])
    for _, channel_reference, enigma2_url, channel_name in ordered_channels:
        enigma2_file.write("#SERVICE {}{}\n".format(channel_reference, enigma2_url))
        enigma2_file.write("#DESCRIPTION {}\n".format(channel_name))    
    enigma2_file.close()
    
def refresh_bouquets():
    try:
        base_url = f'http://localhost:{PORT}/api/'
        requests.get(base_url + 'servicelistreload?mode=2', auth=(USER, PASSWORD))
        print("Lista de canales actualizada con éxito.")
    except Exception as e:
        print(f"Error al actualizar la lista de canales: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        m3u_url = sys.argv[1]
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        try:
            response = requests.get(m3u_url, headers=headers)
        except requests.exceptions.RequestException as e:
            print(f"No se pudo descargar el archivo m3u de {m3u_url}. seguramente url introducia no valida")
            sys.exit(1)
        if response.status_code == 200:
            if len(sys.argv) > 2:
                output_filename = sys.argv[2]
                if not output_filename.endswith(".m3u") and not output_filename.endswith(".m3u8"):
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
        input_files = glob.glob("/etc/jungle_converter_m3u/*.m3u") + glob.glob("/etc/jungle_converter_m3u/*.m3u8")
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
        if ALLOW_COUNTRIES:
            for country, favorites in favorites_by_country.items():
                country_favorite_name = f"{favorite_name}_{country}"
                country_output_file = os.path.join(output_dir, f"userbouquet.{country_favorite_name}.tv")
                with open(country_output_file, "w") as country_enigma2_file:
                    country_enigma2_file.write(f"#NAME {country_favorite_name}\n")
                    ordered_channels_by_country = order_channels(favorites)
                    for order, channel_reference, enigma2_url, channel_name in ordered_channels_by_country:
                        country_enigma2_file.write("#SERVICE {}{}\n".format(channel_reference, enigma2_url))
                        country_enigma2_file.write("#DESCRIPTION {}\n".format(channel_name))
                add_to_bouquets_tv(country_favorite_name)
        else:
            add_to_bouquets_tv(favorite_name)

    refresh_bouquets()
            