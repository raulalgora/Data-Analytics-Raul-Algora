# CloudIA: Conectando necesidad y ayuda en tiempo real

<div align="center">
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/googlecloud/googlecloud-original.svg" height="60" alt="Google Cloud" />
  <img width="20" />
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" height="60" alt="Python" />
  <img width="20" />
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/terraform/terraform-original.svg" height="60" alt="Terraform" />
</div>

## 📌 Descripción del Proyecto

CloudIA es una solución tecnológica diseñada para abordar problemas críticos en la gestión de ayuda humanitaria durante situaciones de emergencia. El sistema utiliza la potencia de la nube y la inteligencia artificial para conectar eficientemente a personas que necesitan ayuda con voluntarios dispuestos a proporcionarla, todo en tiempo real.

### Desafíos Identificados

- **Descoordinación** entre entidades de ayuda y afectados
- **Retrasos en respuesta** a necesidades urgentes
- **Desconocimiento de necesidades** específicas en diferentes zonas
- **Ineficiencia en distribución** de recursos y voluntarios
- **Falta de actualización en tiempo real** de la situación

## 🎯 Objetivo

CloudIA tiene como objetivo principal crear un sistema automatizado de conexión entre personas que necesitan ayuda y voluntarios, utilizando IA y servicios en la nube para optimizar el proceso de asistencia y distribución de recursos en situaciones de emergencia.

## 🛠️ Tecnologías Utilizadas

<table>
  <tr>
    <td><b>Infraestructura Cloud</b></td>
    <td>
      • Google Cloud Platform (GCP)<br>
      • Cloud Run (Servicios serverless)<br>
      • Cloud Functions<br>
      • Pub/Sub (Mensajería en tiempo real)<br>
      • Dataflow (Procesamiento de datos en streaming)<br>
      • BigQuery (Análisis de datos)
    </td>
  </tr>
  <tr>
    <td><b>Frontend</b></td>
    <td>• Telegram API (Interfaz principal de usuario)</td>
  </tr>
  <tr>
    <td><b>Desarrollo</b></td>
    <td>
      • Python (Lógica de negocio)<br>
      • Terraform (Infraestructura como código)
    </td>
  </tr>
  <tr>
    <td><b>Inteligencia Artificial</b></td>
    <td>
      • GPT-4o (Procesamiento de lenguaje natural)<br>
      • ReAct (Toma de decisiones inteligentes)
    </td>
  </tr>
</table>

## 🏗️ Arquitectura de la Solución

CloudIA está estructurado en varios componentes interconectados:

### 1. Interfaz de Usuario
- Implementada a través de un bot de Telegram 
- Proporciona una experiencia accesible sin necesidad de instalar aplicaciones adicionales

### 2. Procesamiento de Datos
- **Fuentes de datos**: Recopilación de información estructurada
- **Lectura**: Procesamiento de mensajes entrantes para extraer datos clave
- **Matcheo**: Sistema inteligente de coincidencia basado en:
  - Tipo de necesidad
  - Ubicación geográfica
  - Necesidades específicas

### 3. Transformación de Datos
El flujo de datos sigue tres etapas principales:

```
[Lectura] ➡️ [Matcheo] ➡️ [Salida]
```

- **Lectura**: Captación y análisis de mensajes
- **Matcheo**: Algoritmo que empareja necesidades con recursos
- **Salida**: Generación de notificaciones y actualizaciones

### 4. Almacenamiento
- Tablas específicas para matches exitosos y fallidos
- Sistema optimizado para consultas en tiempo real
- Integración con BigQuery para análisis histórico

### 5. Infraestructura como Código
Todo el despliegue gestionado a través de Terraform, permitiendo:
- Reproducibilidad del entorno
- Control de versiones de la infraestructura
- Automatización del despliegue
- Componentes modulares:
  - Pub/Sub
  - Generadores de ayudantes/solicitantes
  - IA Agent
  - Telegram API
  - Cloud Functions

## 📊 Visualización y Resultados

El proyecto incluye paneles de visualización para:

- Monitoreo en tiempo real de necesidades y asistencia
- Análisis geográfico de afectados y voluntarios
- Estadísticas sobre tipos de necesidades más demandadas
- Seguimiento de la eficacia del sistema de matcheo
- Optimización continua basada en datos históricos

## 🔄 Flujo de Trabajo

1. Los usuarios envían necesidades o se registran como voluntarios vía Telegram
2. El sistema procesa los mensajes y extrae información clave
3. El motor de matcheo empareja solicitantes con voluntarios apropiados
4. Se notifica a ambas partes cuando se encuentra una coincidencia
5. Se almacena toda la información para análisis y mejora continua

## 💡 Innovación y Escalabilidad

CloudIA destaca por:

- **Análisis en tiempo real** que permite respuestas inmediatas
- **Transformaciones eficaces** que mejoran la velocidad del proceso
- **Optimización basada en datos** para futuras operaciones
- **Extrapolable** a cualquier situación de emergencia

---
<img width="1077" alt="Captura de pantalla 2025-03-31 a las 10 23 12" src="https://github.com/user-attachments/assets/23a01d29-946b-46ea-97b6-84243ffa4a26" />


