![logo_converter](https://user-images.githubusercontent.com/44529886/230175467-824c6bf0-6e18-4d51-be34-98ff16031840.png)


[   ![Licencia Junglebot](https://jungle-team.com/wp-content/uploads/2023/03/licence.png)
](https://github.com/jungla-team/junglebot/blob/master/LICENSE) [![chat telegram](https://jungle-team.com/wp-content/uploads/2023/03/telegram.png)
](https://t.me/joinchat/R_MzlCWf4Kahgb5G) [![donar a jungle](https://jungle-team.com/wp-content/uploads/2023/03/donate.png)
](https://paypal.me/jungleteam)

Hemos realizado un script python `junglem3utobouquet` ejecutable para receptores enigma2 que te genera un favorito enigma2 a partir de una lista en formato .m3u, el favorito lo crea con los service reference Satelite o Tdt asignados en un diccionario de busqueda de palabras clave similares creado en el archivo llamado `satellite_references.txt`

Como el codigo esta diseñado para canales Movistar+ asignar el service reference ya sea satelite o tdt, se recomienda utilizar un archivo .m3u solamente con canales españoles.

Si deseas obtener ayudas asi como prestarlas sobre este desarrollo, asi como con enigma2 en general, tenemos  [grupo de Telegram](https://t.me/joinchat/R_MzlCWf4Kahgb5Gp) . ¡Únete a nosotros!

Si deseas estar a la ultima sobre novedades desarrolladas por jungle team [canal de Telegram noticias](https://t.me/+myB-5lmtSZ1hZDlk) .

## [](jungleteam#instalando)Instalando

Puede instalar o actualizar `junglem3utobouquet` simplemente añadiendo los repositorios jungle-team y luego realizando instalacion:

$ wget http://tropical.jungle-team.online/script/jungle-feed.conf -P /etc/opkg/

$ opkg update

$ opkg install enigma2-plugin-extensions-junglem3utobouquet

## Ejecucion y Funcionamiento

`junglem3utobouquet` realiza las siguientes funciones tras su ejecucion:

1. Convierte cualquier archivo .m3u que hallamos introducido previamente en `/etc/jungle_converter_m3u` a favorito enigma2
2. Compara los nombres del canal del archivo .m3u con palabras clave del diccionario `/etc/jungle_converter_m3u/satellite_references.txt` y las coincidentes crea el canal en el favorito enigma2 con el service reference asignado a esa palabra clave, ademas en ese mismo archivo si se desea tambien se puede añadir un nombre de canal distinto al que le corresponderia segun el archivo .m3u por si queremos ponerlo de otra manera.
3. En caso que no le asignemos ninguno nombre extra se creara con el nombre que lleve en el archivo m3u, si no encuentra ninguna coincidencia entre palabra clave y nombre del canal se le asignara un service reference automaticamente correlativos.
4. El archivo `satellite_references.txt` ya viene parcheado con el service reference y palabras clave que parchearan la mayoria de canales, en el caso de faltar algun canal puede añadir mas palabras claves a dicho archivo.
5. De la ejecucion del script se creara un log en `/etc/jungle_converter_m3u` que mostrara que canales no han sido parcheados por si necesita como hemos mencionado añadir mas palabras claves para afinar.
6. Tras la ejecucion necesitara reiniciar enigma2 para que aparezca los nuevos favoritos en la lista canales.
7. para la comparacion elimina los espacios del nombre del canal y caracteres no alfanumericos, asi como acentos para una mejor comparacion.
8. Permite asignarle un numero de orden del canal

El formato del archivo `/etc/jungle_converter_m3u/satellite_references.txt` es simple lo podeis ver cuando lo abras con un editor de textos:

`accion-->1:0:19:7509:420:1:C00000:0:0:0:-->M+ ACCIÓN HD`


`comedia-->1:0:19:7857:41A:1:C00000:0:0:0:`

* accion= a la palabra clave para busqueda, las palabras que ponga aqui ponerlas sin espacios, por ejemplo podria ser tambien series2.


* 1:0:19:7509:420:1:C00000:0:0:0: = el service reference que se le asigna


* M+ ACCIÓN HD = nombre del canal que quieres que aparezca en el favorito enigma2 este es opcional si no lo pones tomara el nombre del canal del m3u.

Ademas permite asignar el numero de orden que tendra el canal en el favorito enigma2

`accion-->1:0:19:7509:420:1:C00000:0:0:0:-->M+ ACCIÓN HD-->17`

Los parametros nombre de canal y numero de orden son opcionales los podeis poner o no.
 

Para la ejecucion del script basta ejecutar por terminal el comando:

`python /etc/jungle_converter_m3u/junglem3utobouquet.py` 

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
