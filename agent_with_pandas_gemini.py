# agent_with_pandas_gemini.py
import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI # Importar para Gemini
import os
import getpass # Para ingresar la clave API de forma segura si no está como variable de entorno
from dotenv import load_dotenv # Para cargar variables de entorno desde .env

# Importar funciones de data_processing_gemini.py
from data_processing_gemini import load_all_dataframes, get_column_names_for_prefix, PRODUCTS_FILE, ORDERS_FILE, CUSTOMERS_FILE

def configure_google_api_key():
    """Configura la clave API de Google, pidiéndola si no está en el entorno."""
    load_dotenv() # Carga variables desde un archivo .env si existe
    if "GOOGLE_API_KEY" not in os.environ:
        print("Clave API de Google no encontrada en las variables de entorno.")
        api_key = getpass.getpass("Por favor, ingresa tu GOOGLE_API_KEY: ")
        os.environ["GOOGLE_API_KEY"] = api_key
    else:
        print("Clave API de Google encontrada en las variables de entorno.")
    
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("No se pudo configurar la GOOGLE_API_KEY. El agente no puede continuar.")


def main():
    # Configurar la clave API al inicio
    try:
        configure_google_api_key()
    except ValueError as e:
        print(e)
        return

    # --- Configuración del LLM con Gemini ---
    # Modelos populares: "gemini-1.0-pro", "gemini-1.5-flash-latest", "gemini-1.5-pro-latest"
    # "gemini-1.5-flash-latest" es rápido y bueno para muchas tareas.
    LLM_MODEL_NAME = "gemini-1.5-flash-latest" 
    try:
        llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME, temperature=0, convert_system_message_to_human=False)
        print(f"--- Iniciando Agente IA con Pandas y Gemini (Modelo: {LLM_MODEL_NAME}) ---")
    except Exception as e:
        print(f"Error al inicializar el modelo Gemini '{LLM_MODEL_NAME}': {e}")
        print("Asegúrate de que tu GOOGLE_API_KEY esté configurada correctamente y tengas acceso al modelo.")
        return

    all_data = load_all_dataframes()
    if not all_data or \
       'productos' not in all_data or \
       'ordenes' not in all_data or \
       'clientes' not in all_data:
        print("ERROR CRÍTICO: No se pudieron cargar todos los DataFrames. Saliendo.")
        return

    df_productos = all_data['productos']
    df_ordenes = all_data['ordenes']
    df_clientes = all_data['clientes']
    
    column_description_for_prefix = get_column_names_for_prefix(all_data)

    # El prefix que hemos refinado debería funcionar bien con Gemini también
    agent_prefix = f"""
Eres un agente experto en análisis de datos con Pandas. Tu tarea es responder a la PREGUNTA ACTUAL DEL USUARIO generando y ejecutando código Python usando la herramienta `python_repl_ast`.

**Formato Estricto para Acciones:**
Cuando decidas usar la herramienta `python_repl_ast`, DEBES usar el siguiente formato EXACTO:
Action: python_repl_ast
Action Input: [TU CÓDIGO PYTHON AQUÍ. El código debe ser completo y ejecutable. Usa `print()` en tu código para que el resultado de una operación clave sea la Observación.]

**Información de los DataFrames Disponibles (df1: productos, df2: órdenes, df3: clientes):**
{column_description_for_prefix}

**Proceso de Pensamiento y Respuesta (¡MUY IMPORTANTE!):**
1.  Analiza la PREGUNTA ACTUAL DEL USUARIO. No te desvíes.
2.  Planifica los Pasos: Decide qué información necesitas y de qué DataFrame(s) (`df1`, `df2`, `df3`).
3.  Ejecuta Código (Acción): Genera UNA acción Pandas lógica a la vez.
4.  Observa el Resultado: La salida de tu código (la Observación) es la información recuperada.
5.  Decide y Concluye (¡CLAVE!):
    * Si la Observación contiene la respuesta directa o la pieza final de información que necesitas para responder a la PREGUNTA ACTUAL DEL USUARIO, ¡DEBES CONCLUIR! Tu siguiente paso NO debe ser otra `Action: python_repl_ast`. En su lugar, debes proporcionar la "Final Answer" al usuario.
    * Ejemplo: Si la pregunta es "¿Nombre del cliente X?" y tu código produce la Observación "Nombre Apellido", entonces: `Final Answer: El nombre del cliente X es Nombre Apellido.`
    * Si necesitas más información (ej. obtuviste un ID y ahora necesitas el nombre), entonces sí, realiza otra `Action: python_repl_ast`.
6.  Respuesta Final: Cuando tengas la respuesta, formúlala en lenguaje natural.

**Consideraciones de Código Pandas:**
- `df1` (productos): Para nombres de productos (`Product_Name`) usando `Product_ID`.
- `df2` (órdenes): Para ventas, transacciones. Columnas: `Order_ID`, `Product_ID`, `Customer_ID`, `City` (envío), `Sales`, `Quantity`, `Profit`, `Return`. Las columnas numéricas relevantes (`Sales`, `Quantity`, `Discount`, `Profit`, `Return`) ya son del tipo correcto.
    - Para "producto con más pérdidas por devoluciones" (pérdida = `Sales` de ítems con `Return == 1`):
        a. `df_returned = df2[df2['Return'] == 1]`
        b. `sales_lost_per_product = df_returned.groupby('Product_ID')['Sales'].sum()`
        c. `top_product_id_lost = sales_lost_per_product.idxmax()`
        d. `max_sales_lost = sales_lost_per_product.max()`
        e. `top_product_name = df1.loc[df1['Product_ID'] == top_product_id_lost, 'Product_Name'].iloc[0]`
        f. Con `top_product_name` y `max_sales_lost`, da la "Final Answer".
- `df3` (clientes): Para `Customer_Name` usando `Customer_ID`.

Ahora, responde la PREGUNTA ACTUAL DEL USUARIO.
"""

    try:
        print("Inicializando Pandas DataFrame Agent con Gemini...")
        agent_executor = create_pandas_dataframe_agent(
            llm, # Modelo Gemini
            [df_productos, df_ordenes, df_clientes], # df1, df2, df3
            prefix=agent_prefix,
            agent_executor_kwargs={
                "handle_parsing_errors":True,
            },
            verbose=True,
            allow_dangerous_code=True, 
            max_iterations=10,
        )
        print("¡Agente Pandas con Gemini listo!")
    except Exception as e:
        print(f"Error inicializando el agente Pandas con Gemini: {e}")
        return

    print("\nPuedes empezar a hacer preguntas analíticas sobre tus datos usando Gemini.")
    print("Escribe 'salir' o 'q' para terminar la conversación.")

    while True:
        user_question = input("\nTú: ")
        if user_question.lower() in ['salir', 'q']:
            print("Agente: ¡Hasta luego!")
            break
        if not user_question.strip():
            continue

        print("\nAgente (Gemini) pensando y analizando datos...")
        try:
            response = agent_executor.invoke({"input": user_question})
            print(f"\nAgente: {response['output']}")
        except Exception as e:
            print(f"  ERROR al procesar la pregunta con el Agente Pandas (Gemini): {e}")
            import traceback
            traceback.print_exc()
        print("\n----------------------------------------------------")

if __name__ == "__main__":
    # Asegurarse de que los archivos CSV existen
    if not all(os.path.exists(f) for f in [PRODUCTS_FILE, ORDERS_FILE, CUSTOMERS_FILE]):
        print(f"ERROR: Uno o más archivos CSV ({PRODUCTS_FILE}, {ORDERS_FILE}, {CUSTOMERS_FILE}) no se encontraron.")
        print("Asegúrate de que estén en el mismo directorio que los scripts.")
    else:
        main()
        