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

## Despliegue y Ejecución (CloudFormation)

La forma más sencilla de desplegar toda la infraestructura necesaria es utilizando el script de AWS CloudFormation incluido en el repositorio.

### 1. Despliegue de la Infraestructura

1.  Asegúrese de tener sus credenciales de AWS configuradas localmente y de haber cumplido con los [Prerrequisitos](#prerrequisitos).
2.  Abra su terminal y navegue a la raíz de este repositorio.
3.  Ejecute el siguiente comando para desplegar la pila de CloudFormation. Puede cambiar el valor de `ProjectName` si lo desea.

    ```bash
    aws cloudformation deploy \
      --template-file cloudformation.yaml \
      --stack-name DocManPro-Stack \
      --parameter-overrides ProjectName=DocManPro \
      --capabilities CAPABILITY_IAM
    ```

4.  Espere a que la creación de la pila finalice. Esto puede tardar varios minutos, especialmente la creación del dominio de OpenSearch. Puede monitorear el progreso en la consola de AWS CloudFormation.

### 2. Configuración del Frontend

Una vez que la pila se haya creado correctamente, necesita obtener la URL del API Gateway para configurar el frontend.

1.  Vaya a la consola de AWS CloudFormation, seleccione la pila `DocManPro-Stack` y vaya a la pestaña **"Outputs"** (Salidas).
2.  Copie el valor de la clave `ApiGatewayEndpointUrl`.
3.  Abra el archivo `frontend/script.js` en su editor de código.
4.  Reemplace las URLs de marcador de posición con la URL que copió. Asegúrese de añadir los paths correctos (`/generate-url` y `/search`):

    ```javascript
    // Ejemplo de cómo deberían quedar las URLs
    const API_GENERATE_URL = 'https://<ID-API>.execute-api.<REGION>.amazonaws.com/prod/generate-url';
    const API_SEARCH_URL = 'https://<ID-API>.execute-api.<REGION>.amazonaws.com/prod/search';
    ```

### 3. Uso del Prototipo

1.  Abra el archivo `frontend/index.html` en su navegador web.
2.  **Para cargar un documento:**
    -   Haga clic en "Choose File" y seleccione un archivo de imagen (JPG, PNG).
    -   Haga clic en "Cargar y Procesar".
3.  **Para buscar documentos:**
    -   Escriba un término de búsqueda en el campo de búsqueda.
    -   Haga clic en "Buscar". Los resultados aparecerán debajo.
