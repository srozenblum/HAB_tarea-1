import argparse
import os

import gseapy as gp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def leer_genes(genes_input_txt):
    """
    Lee un txt con con los genes y los devuelve como una lista.
    """

    with open(genes_input_txt, "r") as f:
        contenido = f.read().strip()

    lista_genes = [g.strip() for g in contenido.split(",")]

    return lista_genes


def ejecutar_analisis_funcional(lista_genes, lista_dbs, output_file="resultados.csv"):
    """
    Ejecuta el análisis de sobrerrepresentación (con p-valor = 0.05)
    y guarda resultados en output_file.
    """

    # Ejecutar análisis de sobrerrepresentación
    enr = gp.enrichr(
        gene_list=lista_genes,
        gene_sets=lista_dbs,
        organism='Human',
        cutoff=0.05
    )

    # Guardar todos los resultados
    output_path = os.path.join("results", output_file)

    enr.results.to_csv(output_path, index=False)
    print(f"Resultados guardados en results/{output_file}.")

    # Mostrar resumen
    print(enr.results[['Gene_set', 'Term', 'Adjusted P-value', 'Genes']].head(10))

    return enr

def limpiar_texto(text, max_palabras=3):
    """
    Limpia el texto para mejorar la visibilidad del gráfico.
    """

    # Eliminar el código (GO:xxxx)
    text = text.split("(")[0].strip()
    # Quedarse solo con las primeras N palabras
    palabras = text.split()
    if len(palabras) > max_palabras:
        text = " ".join(palabras[:max_palabras])
    else:
        text = " ".join(palabras)
    return text

def graficar(enr, n_resultados=10):
    """
    Gráfico de barras simple con los n_resultados por valor P ajustado.
    """

    df = enr.results.copy()
    if df.empty:
        print("⚠️ No hay términos para graficar.")
        return

    # Tomar los n_resultados ordenados por valor P ajustado
    df = df.sort_values("Adjusted P-value").head(n_resultados)

    # Revertir el orden para que el más significativo quede arriba
    df = df.iloc[::-1]

    # Formatear etiquetas
    df["Term_clean"] = df["Term"].apply(limpiar_texto)

    # Tamaño dinámico
    altura = 0.6 * len(df)
    plt.figure(figsize=(10, altura))

    # Gráficar
    plt.barh(df["Term_clean"], -np.log10(df["Adjusted P-value"]), color="#1976D2")
    plt.xlabel("-log10(Adjusted P-value)", fontsize=12)
    plt.title("Enfermedades y procesos biológicos más representados", fontsize=14, pad=15)
    plt.yticks(fontsize=10)
    plt.xticks(fontsize=10)
    plt.tight_layout()

    # Guardar gráfica en /results
    output_path = os.path.join("results", "grafica_resultados.png")
    plt.savefig(output_path)


def main():
    parser = argparse.ArgumentParser(description="Análisis funcional sencillo para los genes contenidos en genes_input.txt.")
    parser.add_argument("--input", required=True, help="Ruta al archivo de entrada con una lista de genes")
    parser.add_argument("--output", required=True, help="Ruta al archivo de salida para guardar los resultados")
    parser.add_argument("--graficar", action="store_true", help="Mostrar los resultados en un gráfico de barras")
    args = parser.parse_args()

    # Leer archivo de genes
    genes = leer_genes(args.input)

    # Definir lista de bases de datos
    databases = ['GO_Biological_Process_2021', 'KEGG_2021_Human', 'Reactome_2022']

    # Mostrar dataframe de pandas completo
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', None)

    # Ejecutar el análisis
    enr = ejecutar_analisis_funcional(genes, databases, output_file=args.output)

    if args.graficar:
        graficar(enr)

if __name__ == "__main__":
    main()