"""
Script: analisis_funcional.py

Descripción:
    Ejecuta un análisis de sobrerrepresentación génica (Over-Representation Analysis, ORA)
    usando la herramienta Enrichr de GSEApy. Permite analizar cualquier lista de genes
    humanos en formato HUGO contra bases de datos como GO, KEGG o Reactome, generando
    una tabla de resultados y una visualización de las categorías más significativas.

Entradas:
    input_genes (str): ruta a un archivo de texto con los genes separados por comas
                       o por líneas (símbolos HUGO).
    output_dir (str): directorio donde se guardarán los resultados.
    databases (list[str], opcional): bases de datos a usar (por defecto GO, KEGG, Reactome).

Salidas:
    resultados_ORA.csv — tabla con categorías enriquecidas y p-valores ajustados.
    grafica_ORA.png — gráfico de barras con las categorías más significativas.
"""

import argparse
import os

import gseapy as gp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def leer_genes(input_genes: str) -> list[str]:
    """
    Lee un archivo con genes (separados por comas o saltos de línea) y devuelve una lista.
    """
    if not os.path.exists(input_genes):
        raise FileNotFoundError(f"No se encontró el archivo de entrada: {input_genes}")

    with open(input_genes, "r") as f:
        contenido = f.read().strip()

    # Aceptar formato separado por comas o líneas
    lista_genes = [g.strip().upper() for g in contenido.replace(",", "\n").splitlines() if g.strip()]
    print(f"✅ {len(lista_genes)} genes leídos desde {os.path.relpath(input_genes)}")
    return lista_genes

def ejecutar_ora(
    input_genes: str,
    output_dir: str,
    databases: list[str] = None
) -> pd.DataFrame:
    """
    Ejecuta un análisis de sobrerrepresentación génica (ORA) y guarda resultados y gráficos.

    Parámetros:
        input_genes (str): archivo con los genes (separados por comas o líneas).
        output_dir (str): directorio donde guardar los resultados.
        databases (list[str], opcional): bases de datos a usar.

    Retorna:
        pd.DataFrame: tabla completa con los resultados del análisis.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Leer genes
    genes = leer_genes(input_genes)

    # Bases de datos por defecto
    if databases is None:
        databases = ["GO_Biological_Process_2021", "KEGG_2021_Human", "Reactome_2022"]

    print(f"🔍 Ejecutando análisis funcional ORA en {len(genes)} genes...")
    enr = gp.enrichr(
        gene_list=genes,
        gene_sets=databases,
        organism="Human",
        cutoff=0.05,
    )

    df = enr.results
    if df.empty:
        print("⚠️ No se encontraron términos significativos.")
        return df

    # Guardar resultados
    output_csv = os.path.join(output_dir, "enrichment_results.csv")
    df.to_csv(output_csv, index=False)
    print(f"✅ Resultados guardados en {os.path.relpath(output_csv)}")

    # Graficar top resultados
    graficar_resultados(df, output_dir, 10)
    return df


def limpiar_texto(text: str, max_palabras: int = 3) -> str:
    """
    Limpia texto de etiquetas GO y reduce longitud para el gráfico.
    """
    text = text.split("(")[0].strip()
    palabras = text.split()
    return " ".join(palabras[:max_palabras])


def graficar_resultados(df: pd.DataFrame, output_dir: str, n_resultados: int = 10) -> None:
    """
    Genera un gráfico de barras de los n_resultados más significativos.
    """
    df = df.sort_values("Adjusted P-value").head(n_resultados)
    df = df.iloc[::-1].copy()
    df["Term_clean"] = df["Term"].apply(limpiar_texto)

    plt.figure(figsize=(10, 0.6 * len(df)))
    plt.barh(df["Term_clean"], -np.log10(df["Adjusted P-value"]), color="#1976D2")
    plt.xlabel("-log10(Adjusted P-value)", fontsize=12)
    plt.title("Categorías más representadas", fontsize=14, pad=15)
    plt.tight_layout()

    output_png = os.path.join(output_dir, "enrichment_plot.png")
    plt.savefig(output_png)
    plt.close()
    print(f"📊 Gráfico guardado en {os.path.relpath(output_png)}")


# === Ejecución directa ===
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Análisis funcional genérico (ORA).")
    parser.add_argument("--input", default="data/genes_input.txt", help="Archivo con genes de entrada (txt con comas o líneas).")
    parser.add_argument("--output", default="results", help="Directorio de salida.")
    parser.add_argument("--databases", nargs="+", default=["GO_Biological_Process_2021", "KEGG_2021_Human", "Reactome_2022"],
                        help="Bases de datos a usar para el análisis (separadas por espacio).")
    parser.add_argument("--graficar", action="store_true",
                        help="Generar gráfica de barras.")
    args = parser.parse_args()

    ejecutar_ora(input_genes=args.input, output_dir=args.output, databases=args.databases)

    # Leer archivo de genes
    genes = leer_genes(args.input)

    # Mostrar dataframe de pandas completo
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', None)

    # Ejecutar el análisis
    enr = ejecutar_ora(input_genes=args.input, output_dir=args.output, databases=args.databases)

    if args.graficar:
        graficar_resultados(df=enr, output_dir=args.output)