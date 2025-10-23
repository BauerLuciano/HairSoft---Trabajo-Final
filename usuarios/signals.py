# usuarios/signals.py

from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import update_last_login
from django.dispatch import Signal # Se usa Signal para la desconexión

# 🛑 CORRECCIÓN: Desconectar directamente la función update_last_login de la señal user_logged_in
# No necesitamos importar 'disconnect_receiver'.
user_logged_in.disconnect(update_last_login, dispatch_uid='update_last_login')

# Para asegurarnos, también la desconectamos de la función update_last_login misma, si es posible:
# update_last_login.disconnect(dispatch_uid='update_last_login')