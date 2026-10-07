# Configuración

El código ya está preparado. Solo faltan **6 secrets** que no deben guardarse en Git.

## 1. Crear una API Key en Oracle Cloud

En Oracle Cloud:

1. Abre tu perfil.
2. Entra en **My profile / Mi perfil**.
3. Abre **API Keys / Claves de API**.
4. Pulsa **Add API Key / Agregar clave de API**.
5. Elige **Generate API Key Pair / Generar par de claves de API**.
6. Descarga la clave privada `.pem`.
7. Guarda también los valores que muestra Oracle en la vista previa de configuración:
   - `user`
   - `fingerprint`
   - `tenancy`
   - `region`

La región debe ser `eu-madrid-1`.

> La clave privada de API no es la clave SSH de la futura VM.

### Permisos OCI

El monitor solo necesita consultar informes de capacidad Compute y descubrir el Availability Domain de Madrid.

**Ruta rápida:** si generas la API Key en tu usuario administrador actual, funcionará sin crear políticas adicionales.

**Ruta recomendada de mínimo privilegio:** crea un usuario técnico, por ejemplo `oracle-capacity-monitor`, añádelo a un grupo del mismo nombre y crea una política con estas dos sentencias:

```
Allow group OracleCapacityMonitor to manage compute-capacity-reports in tenancy
Allow group OracleCapacityMonitor to inspect compartments in tenancy
```

La primera permite exclusivamente crear el informe puntual de capacidad; la segunda permite obtener el nombre interno del Availability Domain mediante `ListAvailabilityDomains`.

No necesita permisos para crear, borrar, arrancar o modificar instancias.

## 2. Crear el bot de Telegram

1. Abre **@BotFather** en Telegram.
2. Ejecuta `/newbot`.
3. Elige nombre y username.
4. Guarda el token que devuelve BotFather.
5. Abre el bot recién creado y envíale `/start`.

## 3. Añadir los secrets en GitHub

Repositorio:

`aitorino2009/comprobador-oracle`

Ve a:

**Settings → Secrets and variables → Actions → New repository secret**

Crea:

| Secret | Contenido |
|---|---|
| `OCI_TENANCY_OCID` | valor `tenancy` mostrado por Oracle |
| `OCI_USER_OCID` | valor `user` |
| `OCI_FINGERPRINT` | valor `fingerprint` |
| `OCI_PRIVATE_KEY` | contenido COMPLETO del archivo `.pem` |
| `TELEGRAM_BOT_TOKEN` | token entregado por BotFather |

Todavía falta `TELEGRAM_CHAT_ID`.

## 4. Obtener automáticamente TELEGRAM_CHAT_ID

Después de haber enviado `/start` al bot:

1. GitHub → **Actions**.
2. Abre **Obtener Telegram Chat ID**.
3. Pulsa **Run workflow**.
4. Abre la ejecución → **Detectar chat privado**.
5. En el log aparecerá:
   `TELEGRAM_CHAT_ID = 123456789`
6. Añade ese número como sexto secret:
   `TELEGRAM_CHAT_ID`.

## 5. Hacer público el repositorio

Este monitor no contiene credenciales ni datos privados. Para aprovechar GitHub Actions sin consumir la cuota mensual de minutos de un repositorio privado, cambia el repositorio a **Public**:

**Settings → General → Danger Zone → Change repository visibility → Make public**

Los **Repository Secrets siguen siendo secretos** y no se muestran al hacer público el repositorio.

Después de hacerlo, el workflow comprobará automáticamente la capacidad cada **5 minutos**.

## 6. Probar todo

1. GitHub → **Actions**.
2. Abre **Comprobar capacidad Oracle A1.Flex**.
3. Pulsa **Run workflow**.
4. Activa **Enviar también un mensaje de prueba a Telegram**.
5. Ejecuta.

Telegram debe recibir:

`✅ Prueba correcta: el monitor de Oracle A1.Flex está conectado a Telegram.`

La misma ejecución consultará también la capacidad real.

## Qué hace después

Cada 30 minutos consulta:

- región `eu-madrid-1`
- `VM.Standard.A1.Flex`
- 1 OCPU
- 6 GB RAM

Si Oracle cambia de no disponible a disponible, envía inmediatamente un único aviso a Telegram.

El Capacity Report **no reserva** la máquina. Cuando llegue el aviso hay que ejecutar el Apply cuanto antes.

## Frecuencia

El repositorio está preparado para ser **público**, por lo que el workflow comprueba la capacidad cada **5 minutos**.

Esto es importante en este caso porque el Capacity Report no reserva capacidad: cuando aparezca un hueco queremos enterarnos rápidamente.
