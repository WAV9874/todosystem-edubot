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