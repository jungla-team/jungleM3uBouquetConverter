![logo_converter](https://user-images.githubusercontent.com/44529886/230175467-824c6bf0-6e18-4d51-be34-98ff16031840.png)


![python](https://user-images.githubusercontent.com/44529886/230740585-e3637e6c-9bac-472c-88b1-d249a1490e34.png)
[   ![Licencia Junglebot](https://jungle-team.com/wp-content/uploads/2023/03/licence.png)
](https://github.com/jungla-team/junglebot/blob/master/LICENSE) [![chat telegram](https://jungle-team.com/wp-content/uploads/2023/03/telegram.png)
](https://t.me/joinchat/R_MzlCWf4Kahgb5G) [![donar a jungle](https://jungle-team.com/wp-content/uploads/2023/03/donate.png)
](https://paypal.me/jungleteam)

Hemos realizado un script python `junglem3utobouquet` ejecutable para receptores enigma2 que te genera un favorito enigma2 a partir de una lista en formato .m3u, el favorito lo crea con los service reference Satelite o Tdt asignados en un diccionario de busqueda de palabras clave similares creado en el archivo llamado `satellite_references.txt`

El codigo esta diseñado para filtrar los canales de la plataforma movistar+ para poder obtener de los mismos Picon y EPG.

Si deseas obtener ayudas asi como prestarlas sobre este desarrollo, asi como con enigma2 en general, tenemos  [grupo de Telegram](https://t.me/joinchat/R_MzlCWf4Kahgb5Gp) . ¡Únete a nosotros!

Si deseas estar a la ultima sobre novedades desarrolladas por jungle team [canal de Telegram noticias](https://t.me/+myB-5lmtSZ1hZDlk) .

## [](jungleteam#instalando)Instalando

--> Puede instalar o actualizar `junglem3utobouquet` simplemente añadiendo los repositorios jungle-team y luego realizando instalacion:

```{code-block} bash
wget http://tropical.jungle-team.online/script/jungle-feed.conf -P /etc/opkg/
```
```{code-block} bash
opkg update
```
```{code-block} bash
opkg install enigma2-plugin-extensions-junglem3utobouquet
```
--> Si lo deseas tambien puedes descargarte el paquete ipk desde [Lanzamientos](https://github.com/jungla-team/jungleM3uBouquetConverter/releases), una vez descargado, introducirlo en el directorio `tmp`del receptor y ejecutar su instalacion:

## Ejecucion y Funcionamiento

`junglem3utobouquet` realiza las siguientes funciones tras su ejecucion:

1. Convierte cualquier archivo .m3u que hallamos introducido previamente en `/etc/jungle_converter_m3u` a favorito enigma2, tambien permite ejecutarlo introduciendo la url de descarga del m3u.
2. Compara los nombres del canal del archivo .m3u con palabras clave del diccionario `/etc/jungle_converter_m3u/satellite_references.txt` y las coincidentes crea el canal en el favorito enigma2 con el service reference asignado a esa palabra clave, ademas en ese mismo archivo si se desea tambien se puede añadir un nombre de canal distinto al que le corresponderia segun el archivo .m3u por si queremos ponerlo de otra manera, comparacion la realiza con los canales españoles, para ello el codigo esta realizado para buscar canales con los distintos prefijos de indentificacion de idioma del m3u.
3. En caso que no le asignemos ninguno nombre extra se creara con el nombre que lleve en el archivo m3u, si no encuentra ninguna coincidencia entre palabra clave y nombre del canal se le asignara un service reference automaticamente correlativos.
4. El archivo `satellite_references.txt` ya viene parcheado con el service reference y palabras clave que parchearan asi como el orden en la mayoria de canales, en el caso de faltar algun canal puede añadir mas palabras claves a dicho archivo.
5. De la ejecucion del script se creara un log en `/etc/jungle_converter_m3u` que mostrara que canales no han sido parcheados por si necesita como hemos mencionado añadir mas palabras claves para afinar.
6. Al finalizar refresca automaticamente la lista usando la api de webif
7. para la comparacion elimina los espacios del nombre del canal y caracteres no alfanumericos, asi como acentos para una mejor comparacion.
8. Permite asignarle un numero de orden del canal
9. Permite usar prefijos de idiomas configurables en archivo de configuracion para aunque los añada al favorito enigma2, pero no procese la comparacion de nombres con el archivo satellite_references.txt

El formato del archivo `/etc/jungle_converter_m3u/satellite_references.txt` es simple lo podeis ver cuando lo abras con un editor de textos:

`accion-->1:0:19:7509:420:1:C00000:0:0:0:-->M+ ACCIÓN HD`


`comedia-->1:0:19:7857:41A:1:C00000:0:0:0:`

* accion= a la palabra clave para busqueda, las palabras que ponga aqui ponerlas sin espacios, por ejemplo podria ser tambien series2.


* 1:0:19:7509:420:1:C00000:0:0:0: = el service reference que se le asigna


* M+ ACCIÓN HD = nombre del canal que quieres que aparezca en el favorito enigma2 este es opcional si no lo pones tomara el nombre del canal del m3u.

Ademas permite asignar el numero de orden que tendra el canal en el favorito enigma2

`accion-->1:0:19:7509:420:1:C00000:0:0:0:-->M+ ACCIÓN HD-->17`

Los parametros nombre de canal y numero de orden son opcionales los podeis poner o no.
 

Para la ejecucion del script podemos realizarlo de dos maneras:

* Si hemos introducido el archivo .m3u en el directorio `/etc/jungle_converter_m3u/` ejecutaremos:

```{code-block} bash
python /etc/jungle_converter_m3u/junglem3utobouquet.py
```

* Si deseamos realizar la conversion directamente con la url ejecutaremos:

```{code-block} bash
python /etc/jungle_converter_m3u/junglem3utobouquet.py "urldescarga" nombrequedeseemosquetengalalista
```
Para la configuracion del script se usa archivo `jungle_config.json` donde podemos configurar los datos de acceso a api de openwebif asi como los prefijos de idiomas que deseemos que se procesen con el satellite_references.txt

```{code-block} json
{
    "PORT": 80,
    "USER": "",
    "PASSWORD": "",
    "ALLOWED_PREFIXES": ["ES-", "ES -", "ES:", "|ES|", "SP -", "SP-", "SP:", "|SP|"]
}

```
--> Si no se tiene password se puede dejar como esta por defecto, si se tiene password pues se introduciria "root" "password que se tenga"


--> Los prefijos se usan para solo procesar en la comparacion los canales que tengan en su prefijo los que hay por defecto, esto viene bien para listas m3u de miles de canales, en los que les ponen un prefijo al canal, solo procesar con el satellite_references los que pongamos, y el resto los añadira al favorito enigma2 pero sin comparacion para añadir service reference. Si desearamos por que nuestra lista es muy corta y depurada y no tiene prefijos de idiomas, añadiriamos "" en ALLOWED_PREFIXES, ejemplo: "ALLOWED_PREFIXES": ["ES-", "ES -", "ES:", "|ES|", "SP -", "SP-", "SP:", "|SP|", ""]

## Obteniendo ayuda

Si los recursos mencionados anteriormente no responden a sus preguntas o dudas,  o te ha resultado muy complicado, tienes varias formas de obtener ayuda.

1.  Tenemos una comunidad donde se intenta que se ayudan unos a otros en nuestro [grupo de Telegram](https://t.me/joinchat/R_MzlCWf4Kahgb5G) . ¡Únete a nosotros! Hacer una pregunta aquí suele ser la forma más rápida de obtener respuesta y poder hablar directamente con los desarrolladores.
2.  Tambien puedes leer con detenimiento la [Guia avanzada de junglem3utobouquet](https://jungle-team.com/junglem3utobouquet-convertir-m3u-a-favorito-enigma2-con-epg-y-picon/) .

## contribuir

junglem3utobouquet esta desarrollado bajo codigo abierto, por lo que las contribuciones de todos los tamaños son bienvenidas para mejorar o ampliar las posibilidades de junglebot. También puede ayudar [informando errores o solicitudes de funciones a traves del grupo telegram](https://t.me/joinchat/R_MzlCWf4Kahgb5G) .

## [](jungleteam#donating)donando

De vez en cuando nos preguntan si aceptamos donaciones para apoyar el desarrollo. Si bien, mantener `junglebot`  es nuestro hobby y  pasatiempo, si tenemos un coste de mantenimiento de servidor de repositorios asi como [del blog enigma2](https://jungle-team.com/), por lo que si deseas colaborar en su mantenimiento sirvase de realizar [Donacion](https://paypal.me/jungleteam)

## [](jungleteam#license)Licencia

Puede copiar, distribuir y modificar el software siempre que las modificaciones se describan y se licencien de forma gratuita bajo [LGPL-3](https://www.gnu.org/licenses/lgpl-3.0.html) . Los trabajos derivados (incluidas las modificaciones o cualquier cosa vinculada estáticamente a la biblioteca) solo se pueden redistribuir bajo LGPL-3.
