# Operación

## Comprobación manual inmediata

GitHub → **Actions** → **Comprobar capacidad Oracle A1.Flex** → **Run workflow**.

No es necesario activar el mensaje de prueba salvo que estés verificando Telegram.

## Estados

El archivo `state.json` solo cambia cuando cambia el estado real:

- `UNKNOWN`: todavía no se ha hecho una consulta válida.
- `UNAVAILABLE`: Oracle devuelve `OUT_OF_HOST_CAPACITY`.
- `AVAILABLE`: existe capacidad reportada para al menos una VM de 1 OCPU / 6 GB.
- `ERROR`: la consulta falló o Oracle devolvió un estado que no debe interpretarse como simple falta de capacidad.

Los cambios de estado los realiza únicamente GitHub Actions.

## Cuando llegue el aviso

El Compute Capacity Report es una fotografía puntual y **no reserva** capacidad.

Entra cuanto antes en:

**Oracle Cloud → Resource Manager → pila guardada → Apply**

Si el Apply vuelve a fallar por `Out of host capacity`, no hay que cambiar la configuración. El monitor se rearmará cuando vuelva a detectar una transición de no disponible a disponible.

## Frecuencia

Mientras el repositorio sea privado, se comprueba a los minutos 07 y 37 de cada hora. Esto limita el consumo máximo teórico a unas 1.440 ejecuciones facturables al mes.

Si el repositorio pasa a ser público, puede cambiarse el cron a:

```yaml
- cron: "*/5 * * * *"
```

Los runners estándar de GitHub Actions en repositorios públicos no consumen la cuota mensual de minutos.

## Parar el monitor

Cuando la VM haya sido creada:

1. GitHub → **Actions**.
2. Abre **Comprobar capacidad Oracle A1.Flex**.
3. Menú de los tres puntos → **Disable workflow**.

También puedes eliminar el bloque `schedule` si quieres conservar únicamente la comprobación manual.

## Rotación de credenciales

Si una clave OCI o token de Telegram se expone:

1. Revoca primero la credencial en Oracle/Telegram.
2. Genera una nueva.
3. Sustituye el Repository Secret correspondiente.
4. Ejecuta manualmente el workflow con el mensaje de prueba.
