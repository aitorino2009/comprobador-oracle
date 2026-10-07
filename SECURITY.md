# Seguridad

- Nunca guardes una clave privada OCI, token de Telegram o credencial en el repositorio.
- Todos los secretos deben estar en **GitHub Actions Repository Secrets**.
- La clave privada OCI se escribe únicamente en el directorio temporal del runner y desaparece al terminar el job.
- El monitor solo consulta capacidad. No crea, destruye ni modifica instancias.
- El aviso de Telegram contiene únicamente información de infraestructura, sin datos de clientes.
- Si una credencial se expone accidentalmente, rótala antes de volver a ejecutar el workflow.
