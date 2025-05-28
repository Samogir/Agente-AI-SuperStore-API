# Agente-AI-SuperStore-API
Agente de inteligencia artificial utilizando una API para correr el modelo LLM.
## Descripción 
Este proyecto se realizó con el fin de poder comparar el desempeño de un agente AI corriendo de manera local contra este que corre utilizando una llave API.
## Procedimiento
### Obtener los datos
Para la adquisición de los datos recurrí a los archivos .csv encontrados [aquí](https://github.com/joselquin/SuperStore_sales?tab=readme-ov-file).
La estructura de las tablas es de la siguiente manera:

La tabla Productos tiene las siguientes columnas: Product_ID, Category, Sub_Category, Product_Name

La tabla clientes tiene las siguientes columnas: Customer_ID, Customer_Name, Segment, Country, City, State, Postal_Code, Region

La tabla Ordenes tiene las siguientes columnas: Order_ID, Order_Date, Ship_Date, Ship_Mode, Customer_ID, City, Product_ID, Sales, Quantity, Discount, Profit, Return

### Creación de entorno virtual.
Para la creación del entorno virtual primero debemos crear una carpeta, en la cual estará nuestro proyecto, una vez creada la carpeta entramos en ella y abrimos un "command window" dentro de ella y utilizaremos los siguietnes comandos:

-Creación del entorno virtual:
python -m venv venv

Activación del entorno virtual:
./venv/Scripts/activate

Después se instalarán los requirements en el entorno virtual para poder realizar el trabajo.
pip install -r .\requirements.txt

Para desactivar(lo utilizaremos cuando terminemos de usar el agente):
deactivate

### Creación de archivo .env
Se debe crear un archivo ".env" que contenga la llave de la apy, el archivo debe contener lo siguiente: 

GOOGLE_API_KEY="TU_CLAVE_API_DE_GEMINI_AQUI"

Este archivo se puede crear directamente desde el editor de código.

### Correr el agente. 
Para correr nuestro agente virtual utilizaremos el comando directamente desde el command window python agent_with_pandas_gemini.py y allí mismo nos mostrará la interface para interactuar con nuestro agente y comenzar a hacerle las preguntas sobre la base de datos.
