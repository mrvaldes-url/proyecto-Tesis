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

## Instalación

### Prerrequisitos
- Una cuenta de AWS con permisos para crear roles de IAM, S3, Lambda, API Gateway y OpenSearch.
- AWS CLI configurado en su máquina local.
- Python 3.8 o superior.
- Pip (manejador de paquetes de Python).

### Backend
1.  Navegue al directorio del backend:
    ```bash
    cd backend
    ```
2.  Instale las dependencias de Python:
    ```bash
    pip install -r requirements.txt
    ```

### Frontend
El frontend no requiere instalación. Es una aplicación estática de HTML, CSS y JavaScript que se puede abrir directamente en un navegador web.

## Ejecución y Uso del Prototipo

Este prototipo requiere el despliegue de varios servicios en AWS. A continuación se describe el proceso a alto nivel.

### 1. Despliegue de la Infraestructura en AWS

Deberá crear los siguientes recursos en su cuenta de AWS:

1.  **Amazon S3 Bucket:** Un bucket para almacenar los documentos cargados.
2.  **Amazon OpenSearch Domain:** Un dominio de OpenSearch para indexar los documentos. Asegúrese de que sea accesible desde las funciones Lambda (por ejemplo, desplegándolo dentro de una VPC con los endpoints correspondientes).
3.  **Roles de IAM:** Roles con los permisos necesarios para que las funciones Lambda puedan acceder a S3, Textract, Comprehend y OpenSearch.
4.  **Funciones Lambda:**
    -   `document_processor`: Despliegue el código de `backend/document_processor.py`. Configure un trigger de S3 para que se ejecute cuando se creen nuevos objetos en el bucket de carga.
    -   `generate_presigned_url`: Despliegue el código de `backend/generate_presigned_url.py`.
    -   `search_handler`: Despliegue el código de `backend/search_handler.py`.
5.  **Amazon API Gateway:**
    -   Cree una API REST.
    -   Cree un recurso para la generación de URLs pre-firmadas (ej. `/generate-presigned-url`) con un método `POST` que se integre con la Lambda `generate_presigned_url`.
    -   Cree un recurso para la búsqueda (ej. `/search`) con un método `GET` que se integre con la Lambda `search_handler`.
    -   Habilite CORS en ambos endpoints para permitir las solicitudes desde el navegador.

### 2. Configuración de Variables de Entorno

Configure las siguientes variables de entorno en sus funciones Lambda:

-   **Para `document_processor`:**
    -   `OPENSEARCH_HOST`: El endpoint de su dominio de OpenSearch (sin `https://`).
    -   `OPENSEARCH_INDEX`: El nombre del índice que desea usar (ej. `documents`).
-   **Para `generate_presigned_url`:**
    -   `UPLOAD_BUCKET`: El nombre de su bucket de S3.
-   **Para `search_handler`:**
    -   `OPENSEARCH_HOST`: El mismo endpoint de su dominio de OpenSearch.
    -   `OPENSEARCH_INDEX`: El mismo nombre del índice.

### 3. Configuración del Frontend

1.  Abra el archivo `frontend/script.js`.
2.  Reemplace las URLs de marcador de posición con las URLs reales de su API Gateway:
    ```javascript
    // Reemplace ... con las URLs de su despliegue
    const API_GENERATE_URL = 'https://<API-ID>.execute-api.<REGION>.amazonaws.com/prod/generate-presigned-url';
    const API_SEARCH_URL = 'https://<API-ID>.execute-api.<REGION>.amazonaws.com/prod/search';
    ```

### 4. Uso del Prototipo

1.  Abra el archivo `frontend/index.html` en su navegador web.
2.  **Para cargar un documento:**
    -   Haga clic en "Choose File" y seleccione un archivo de imagen (JPG, PNG).
    -   Haga clic en "Cargar y Procesar". El archivo se subirá a S3 y se iniciará el pipeline de procesamiento.
3.  **Para buscar documentos:**
    -   Escriba un término de búsqueda en el campo "Buscar por contenido...".
    -   Haga clic en "Buscar". Los resultados aparecerán debajo, con el texto coincidente resaltado.
