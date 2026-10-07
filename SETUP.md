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

El monitor solo necesita consultar informes de capacidad Compute. Si usas tu usuario administrador actual, funcionará sin crear una política adicional.

Cuando el sistema esté funcionando, lo recomendable es crear un usuario técnico dedicado con permisos mínimos para `compute-capacity-reports`.

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

## 5. Probar todo

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

## Por qué 30 minutos y no 5 en este repositorio privado

GitHub redondea cada job privado al siguiente minuto facturable. Cada 5 minutos podría consumir unas 8.640 ejecuciones/minutos facturables al mes. GitHub Free incluye 2.000 minutos y GitHub Pro 3.000.

Cada 30 minutos son como máximo unas 1.440 ejecuciones al mes, dejando margen. Si se convierte este repositorio en **público**, los runners estándar de GitHub Actions dejan de consumir esa cuota y se puede bajar el cron a 5 minutos.
