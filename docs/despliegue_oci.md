# Despliegue en Oracle Cloud Infrastructure - TodoSystem EduBot

Este documento describe el plan de despliegue del agente inteligente **TodoSystem EduBot** en **Oracle Cloud Infrastructure (OCI)**.

El despliegue en OCI es un requisito del Challenge Alura Agente - ONE AI For Tech. El objetivo es ejecutar el agente en la nube y dejar evidencia de su funcionamiento mediante capturas o video.

---

## 1. Objetivo del despliegue

El objetivo del despliegue es publicar la aplicacion web de TodoSystem EduBot para que pueda ejecutarse fuera del entorno local.

La aplicacion sera desplegada inicialmente usando una instancia de **OCI Compute**, donde se instalaran las dependencias necesarias para ejecutar el proyecto con Python y Streamlit.

---

## 2. Servicio OCI seleccionado

Para esta primera version del proyecto se utilizara el siguiente servicio de Oracle Cloud Infrastructure:

```text
OCI Compute
```

Este servicio permite crear una maquina virtual en la nube para instalar y ejecutar la aplicacion.

La aplicacion se ejecutara con Streamlit en el puerto:

```text
8501
```

---

## 3. Requisitos previos

Antes de realizar el despliegue en OCI se requiere:

- Tener una cuenta activa en Oracle Cloud Infrastructure.
- Tener acceso a una instancia de OCI Compute.
- Tener instalado Git en la instancia.
- Tener instalado Python 3.
- Tener instalado pip.
- Clonar el repositorio publico del proyecto desde GitHub.
- Instalar las dependencias del archivo `requirements.txt`.
- Permitir el acceso al puerto `8501` para ejecutar Streamlit.

---

## 4. Preparacion de la instancia OCI Compute

Una vez creada la instancia de OCI Compute, se debe ingresar por SSH y preparar el entorno de ejecucion.

Los comandos generales para una instancia Linux son:

```bash
sudo apt update
sudo apt install git python3 python3-pip python3-venv -y
```

Estos comandos permiten instalar las herramientas necesarias para ejecutar el proyecto:

- Git para clonar el repositorio.
- Python 3 para ejecutar la aplicacion.
- pip para instalar dependencias.
- venv para crear un entorno virtual.

---

## 5. Clonar el repositorio del proyecto

Despues de preparar la instancia, se debe clonar el repositorio publico del proyecto desde GitHub.

Comando:

```bash
git clone https://github.com/WAV9874/todosystem-edubot.git
```

Luego se ingresa a la carpeta del proyecto:

```bash
cd todosystem-edubot
```

Con esto, el codigo fuente del agente queda disponible dentro de la instancia de OCI Compute.

---

## 6. Crear entorno virtual e instalar dependencias

Dentro de la carpeta del proyecto se recomienda crear un entorno virtual de Python.

Comandos:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Luego se instalan las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

El archivo `requirements.txt` contiene las librerias necesarias para ejecutar TodoSystem EduBot, entre ellas Streamlit, Pandas, PyPDF, ChromaDB y Sentence Transformers.

---

## 7. Ejecutar la aplicacion con Streamlit

Despues de instalar las dependencias, se puede ejecutar la aplicacion web con Streamlit.

Comando:

```bash
python3 -m streamlit run app/main.py --server.port 8501 --server.address 0.0.0.0
```

El parametro `--server.port 8501` indica que la aplicacion se ejecutara en el puerto 8501.

El parametro `--server.address 0.0.0.0` permite que la aplicacion pueda ser accedida desde fuera de la instancia, usando la direccion publica de la maquina virtual.

---

## 8. Acceder a la aplicacion desde el navegador

Cuando la aplicacion este ejecutandose en OCI, se podra acceder desde un navegador usando la IP publica de la instancia y el puerto 8501.

Formato de acceso:

```text
http://IP_PUBLICA_DE_LA_INSTANCIA:8501
```

Ejemplo:

```text
http://123.45.67.89:8501
```

La IP publica real sera tomada desde el panel de Oracle Cloud Infrastructure, en la informacion de la instancia Compute.

Para que este acceso funcione, el puerto `8501` debe estar permitido en las reglas de red de OCI.

---

## 9. Configuracion de red en OCI

Para que la aplicacion pueda abrirse desde internet, se debe permitir el trafico hacia el puerto `8501`.

En OCI se debe revisar la configuracion de red asociada a la instancia Compute, por ejemplo:

- Virtual Cloud Network.
- Subnet.
- Security List o Network Security Group.
- Regla de entrada para el puerto `8501`.

La regla de entrada debe permitir conexiones TCP hacia el puerto usado por Streamlit.

Configuracion general esperada:

```text
Protocolo: TCP
Puerto destino: 8501
Origen: 0.0.0.0/0
```

Esta configuracion permite acceder a la aplicacion desde el navegador usando la IP publica de la instancia.

Nota: en un entorno real de produccion se recomienda restringir el origen por seguridad, pero para este proyecto academico se permite el acceso publico con fines de demostracion.

---

## 10. Evidencias del despliegue

Para demostrar que el agente fue desplegado correctamente en Oracle Cloud Infrastructure, se deben registrar evidencias visuales del proceso.

Evidencias recomendadas:

- Captura de la instancia Compute creada en OCI.
- Captura de la IP publica de la instancia.
- Captura de la terminal conectada por SSH.
- Captura del repositorio clonado dentro de la instancia.
- Captura de la instalacion de dependencias.
- Captura de la aplicacion ejecutandose con Streamlit.
- Captura del navegador accediendo a la aplicacion desde la IP publica.
- Captura del agente respondiendo una pregunta desde OCI.
- Video corto mostrando la aplicacion funcionando en la nube.

Las imagenes principales se guardaran en la carpeta:

```text
assets/
```

Nombres sugeridos para las evidencias:

```text
assets/oci_compute.png
assets/oci_terminal.png
assets/oci_streamlit_running.png
assets/oci_app_funcionando.png
```

Estas evidencias seran usadas en el archivo `README.md` para demostrar el cumplimiento del requisito de despliegue en la nube.