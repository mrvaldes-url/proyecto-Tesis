# Prototipo de Sistema de Gestión Documental

Este proyecto es un prototipo de un sistema de gestión documental basado en la nube, diseñado para optimizar el almacenamiento, búsqueda y recuperación de documentos digitales.

## Arquitectura

El sistema utiliza una arquitectura serverless en AWS, que incluye:

- **Almacenamiento:** Amazon S3 para los documentos originales.
- **Procesamiento:** AWS Lambda para orquestar el flujo de trabajo.
- **Extracción de Texto (OCR):** Amazon Textract.
- **Análisis de Texto:** Amazon Comprehend para clasificación y extracción de entidades.
- **Búsqueda:** Amazon OpenSearch para indexar y buscar documentos por su contenido y metadatos.
- **Frontend:** Una aplicación web simple para la carga y búsqueda de documentos.
- **API:** Amazon API Gateway para exponer la funcionalidad de búsqueda al frontend.
