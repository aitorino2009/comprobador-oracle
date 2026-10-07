# Comprobador Oracle A1.Flex

Monitor gratuito para detectar cuándo Oracle Cloud vuelve a tener capacidad para crear una **VM.Standard.A1.Flex de 1 OCPU y 6 GB de RAM** en **Spain Central (Madrid / eu-madrid-1)** y avisar por Telegram.

El monitor usa el **Compute Capacity Report oficial de OCI**. No crea, reserva ni modifica ninguna VM.

## Estado

- Región: `eu-madrid-1`
- Shape: `VM.Standard.A1.Flex`
- OCPU: `1`
- RAM: `6 GB`
- Frecuencia por defecto en repositorio privado: cada **30 minutos**, para mantenerse dentro de los minutos gratuitos de GitHub Actions incluso con GitHub Free.
- Aviso: Telegram, solo cuando cambia de no disponible a disponible.
- Ejecución manual: disponible desde GitHub Actions.

Consulta `SETUP.md` para completar las credenciales.
