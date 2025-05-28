# data_processing_gemini.py
import os
import pandas as pd

# --- Configuración de Archivos ---
PRODUCTS_FILE = 'productos.csv'
ORDERS_FILE = 'ordenes.csv'
CUSTOMERS_FILE = 'clientes.csv'

def load_all_dataframes():
    """Carga todos los DataFrames relevantes desde los archivos CSV y asegura tipos numéricos."""
    dataframes = {}
    print("Cargando archivos CSV...")
    try:
        # Productos
        if os.path.exists(PRODUCTS_FILE):
            dataframes['productos'] = pd.read_csv(PRODUCTS_FILE)
            print(f"  - '{PRODUCTS_FILE}' cargado con {len(dataframes['productos'])} filas.")
        else:
            print(f"  - ERROR: '{PRODUCTS_FILE}' no encontrado.")
            return None

        # Órdenes
        if os.path.exists(ORDERS_FILE):
            dataframes['ordenes'] = pd.read_csv(ORDERS_FILE)
            df_o = dataframes['ordenes'] # Alias corto
            # Convertir columnas de fecha
            for date_col in ['Order_Date', 'Ship_Date']:
                if date_col in df_o.columns:
                    df_o[date_col] = pd.to_datetime(df_o[date_col], errors='coerce')
            
            # Asegurar tipos numéricos para columnas clave de órdenes
            for num_col in ['Sales', 'Quantity', 'Discount', 'Profit', 'Return']: # 'Return' también es numérica
                if num_col in df_o.columns:
                    # Intentar convertir, si falla por valores no convertibles, se imprimiría un error
                    # pero es mejor asegurarse que los datos sean limpios.
                    try:
                        df_o[num_col] = pd.to_numeric(df_o[num_col])
                    except ValueError as ve:
                        print(f"Advertencia: Problema al convertir la columna '{num_col}' a numérica: {ve}. Intentando con 'coerce'.")
                        df_o[num_col] = pd.to_numeric(df_o[num_col], errors='coerce').fillna(0)
            
            print(f"  - '{ORDERS_FILE}' cargado con {len(df_o)} filas (tipos numéricos y de fecha procesados).")
        else:
            print(f"  - ERROR: '{ORDERS_FILE}' no encontrado.")
            return None

        # Clientes
        if os.path.exists(CUSTOMERS_FILE):
            dataframes['clientes'] = pd.read_csv(CUSTOMERS_FILE)
            print(f"  - '{CUSTOMERS_FILE}' cargado con {len(dataframes['clientes'])} filas.")
        else:
            print(f"  - ERROR: '{CUSTOMERS_FILE}' no encontrado.")
            return None
            
        print("Carga de CSVs finalizada.")
        return dataframes
    except FileNotFoundError as e:
        print(f"  - ERROR CRÍTICO: No se encontró el archivo {e.filename}. Verifica la ruta y nombre.")
        return None
    except Exception as e:
        print(f"  - ERROR CRÍTICO: Ocurrió un error al cargar los datos CSV: {e}")
        return None

def get_column_names_for_prefix(dataframes):
    """Genera una descripción de columnas para el prefix del agente Pandas."""
    if not dataframes:
        return "No se pudo generar la descripción de columnas: DataFrames no disponibles."
    prefix_parts = []
    if 'productos' in dataframes and not dataframes['productos'].empty:
        prefix_parts.append(f"- `df1` (productos): Columnas: {', '.join(dataframes['productos'].columns.tolist())}")
    if 'ordenes' in dataframes and not dataframes['ordenes'].empty:
        prefix_parts.append(f"- `df2` (órdenes): Columnas: {', '.join(dataframes['ordenes'].columns.tolist())}")
    if 'clientes' in dataframes and not dataframes['clientes'].empty:
        prefix_parts.append(f"- `df3` (clientes): Columnas: {', '.join(dataframes['clientes'].columns.tolist())}")
    return "\n".join(prefix_parts)

if __name__ == "__main__":
    print("--- Probando la carga de DataFrames y la generación de descripción de columnas (Versión Gemini) ---")
    all_data = load_all_dataframes()
    if all_data:
        column_summary = get_column_names_for_prefix(all_data)
        print("\n--- Descripción de Columnas para el Agente Pandas ---")
        print(column_summary)
        print("----------------------------------------------------")

        if 'ordenes' in all_data and not all_data['ordenes'].empty:
            print("\nTipos de datos en df_ordenes después de la conversión:")
            # Mostrar solo las columnas numéricas clave y 'Return'
            cols_to_check = [col for col in ['Sales', 'Quantity', 'Discount', 'Profit', 'Return'] if col in all_data['ordenes'].columns]
            if cols_to_check:
                print(all_data['ordenes'][cols_to_check].info())
            else:
                print("No se encontraron columnas numéricas clave para mostrar info.")
    else:
        print("Fallo en la carga inicial de datos.")