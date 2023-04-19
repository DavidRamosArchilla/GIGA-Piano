import urllib.request
import zipfile
import os

import random
from random import sample

import pandas as pd

random.seed(10)
RUTA_DATASET = './Dataset'
LISTA_COMPOSITORES = [['Johann Sebastian Bach'], ['Sergei Rachmaninoff']]
nombres_zip = ['midis_barroco.zip', 'midis_vanguardias.zip']
url = "https://storage.googleapis.com/magentadata/datasets/maestro/v3.0.0/maestro-v3.0.0-midi.zip"

nombre_archivo = os.path.basename(url)
ruta_archivo = os.path.join(RUTA_DATASET, nombre_archivo)

if not os.path.exists(RUTA_DATASET):
    os.makedirs(RUTA_DATASET)
urllib.request.urlretrieve(url, ruta_archivo)

with zipfile.ZipFile(ruta_archivo, 'r') as zip_ref:
    zip_ref.extractall(RUTA_DATASET)


def comprimir_archivos_en_zip(lista_archivos, nombre_zip):
    with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as archivo_zip:
        for archivo in lista_archivos:
            nombre_base = os.path.basename(archivo)
            archivo_zip.write(archivo, nombre_base)


def obtener_lista_ficheros(compositores, tam_lista, lista_elementos_eliminar=None):
    df = pd.read_csv(RUTA_DATASET + '/maestro-v3.0.0/maestro-v3.0.0.csv')
    ficheros_obras_compositores = df[df.canonical_composer.isin(
        compositores)]['midi_filename']
    if lista_elementos_eliminar is not None:
        ficheros_obras_compositores = ficheros_obras_compositores.drop(
            lista_elementos_eliminar).values
    else:
        ficheros_obras_compositores = ficheros_obras_compositores.values
    ficheros_obras_compositores = RUTA_DATASET + \
        '/maestro-v3.0.0/' + ficheros_obras_compositores
    ficheros_obras_compositores = sample(
        ficheros_obras_compositores.tolist(), tam_lista)
    return ficheros_obras_compositores


for nombre_zip, compositores_estilo in zip(nombres_zip, LISTA_COMPOSITORES):
    ficheros_obras_compositores = obtener_lista_ficheros(
        compositores_estilo, 50)
    comprimir_archivos_en_zip(ficheros_obras_compositores, nombre_zip)
