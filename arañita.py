import httpx
import asyncio
from collections import deque
from bs4 import BeautifulSoup
import pandas as pd

"""aca estaran los datos que se recuperend de las rDNS"""
fila:deque = deque()

"""aca estaran contenidos todos los datos ya refinados"""
contenedor:dict = {"ip":[], "hostname":[], "location":[], "mainContent":[], "title":[], "h1":[], "owern":[]}

"""funcion asyncrona la cual investiga si el hostname tiene un contenido"""
async def investigar():
    linea = None
    length:int = len(fila)
    while(length > 0):
        linea:dict = fila.popleft()
        if linea.get("hostname") != None:
            result:dict = {}
            async with httpx.AsyncClient() as client:
                try:
                    busqueda = await client.get(f'https://{linea.get("hostname")}')
                    if busqueda.headers["content-type"] == "text/html; charset=UTF-8":
                        soup = BeautifulSoup(busqueda.text, 'html.parser')
                        print("se pudo hacer una coneccion")
                        result["h1"] = soup.find('h1')
                        result["mainContent"] = soup.find('main')
                        result["title"] = soup.find('title')
                    else:
                        result["mainContent"].append(busqueda.json())
                except:
                    print("la ip no maneja coneccion https, intentandolo con el protocolo http")
                    try:
                        busqueda = await client.get(f'http://{linea.get("hostname")}')
                        print("se pudo hacer una coneccion")
                        if busqueda.headers["content-type"] == "text/html; charset=UTF-8":
                            soup = BeautifulSoup(busqueda.text, 'html.parser')
                            result["h1"] = soup.find('h1')
                            result["mainContent"] = soup.find('main')
                            result["title"] = soup.find('title')
                        else:
                            result["mainContent"].append(busqueda.json())
                    except:
                        print("la ip no maneja ningun procolo asociado a la web")
                linea.update(result)
        contenedor["ip"].append(linea.get("ip"))
        contenedor["hostname"].append(linea.get("hostname"))
        contenedor["location"].append(f'{linea.get("country")} {linea.get("region")} {linea.get("city")}')
        contenedor["owern"].append(linea.get("org"))
        contenedor["title"].append(linea.get("title"))
        contenedor["mainContent"].append(linea.get("mainContent"))
        contenedor["h1"].append(linea.get("mainContent"))
        length = len(fila)

"""aca se pregunta a una api de Reverse Donain servecise, para conocer informacion sobre la ip"""
async def rDNS(number):
    result = {"Yes":False}
    async with httpx.AsyncClient() as client:
        try:
            busqueda = await client.get(f'https://ipinfo.io/{number}/json')
            if busqueda.status_code == 200:
                result["Yes"] = True
            result.update(busqueda.json())
        except:
            print("upp error")
    return result

"""aca se pregunta que rango de busqueda de las ip"""
async def search():
    primera:int = int(input("dijite el rango mas pequeño"))
    segunda:int = int(input("dijite el rango mas grande"))
    tercera:int = int(input("dijite el rango mas pequeño"))
    cuarta:int = int(input("dijite el tango mas grande"))
    print(f'buscando de 186.86.{primera}.{cuarta} a 186.86.{segunda}.{tercera}')
    for i in range(primera,segunda):
        for j in range(tercera, cuarta):
            print(f'buscando 186.86.{i}.{j}')
            info = await rDNS(f'186.86.{i}.{j}')
            if(info["Yes"]):
                fila.append(info)


"""Aca se manda a llamar todas las funciones en orden"""
async def main():
    await search()
    await investigar()
    df = pd.DataFrame(contenedor)
    print("generando archivos de comas")
    df.to_csv("datosEstadistica3.csv", index=False) 

if __name__ == "__main__":
    asyncio.run(main())