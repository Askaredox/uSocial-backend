import json
import datetime
import urllib3
import boto3
import os


def obtenerDatosPais(data,event):
    translate = boto3.client(service_name='translate',region_name='us-east-2', use_ssl=True)
    result = translate.translate_text(Text=event['Pais'], SourceLanguageCode= 'auto', TargetLanguageCode='en')
    if result.get('TranslatedText') in data:
        return data.get(result.get('TranslatedText'))
    else:    
        return 'no hay, no existe'

def lambda_handler(event, context):
    # TODO implement https://fherherand.github.io/covid-19-data-update/timeseries.json.
    http = urllib3.PoolManager()
    r = http.request('GET', 'https://fherherand.github.io/covid-19-data-update/timeseries.json')
    data = json.loads(r.data)
    valor=''
   
    valor=obtenerDatosPais(data,event)
    if(event['Info_Tipo']==1):
        valor=filtrarFecha(valor,event)
        if not valor == 'no disponible':
            valor=obtenerCasos(valor,event)
    else:
        valor=obtenerGrafica(valor,event)
   
   
   
       
    return {
        'statusCode': 200,
        'body': str(valor)#json.dumps(result.get('TranslatedText'))
    }
   

   
def obtenerCasos(obj,event):
    if event['Tipo']==1: #confirmados
        return {'confimados':obj['confirmed']}
    elif event['Tipo']==2: #recuperados
        return {'recuperados':obj['recovered']}
    elif event['Tipo']==3:#muertes
        return {'muertes':obj['deaths']}
    else: #todos
        return {'confimados':obj['confirmed'],'recuperados': obj['recovered'],'muertes': obj['deaths']}
           
def filtrarFecha(data,event):
    fecha=[]
    h=[]
    if "hoy" in event['Fecha'].lower():
        fecha= event['Fecha'].split("(")
        for x in data:
            if x['date'] == fecha[1].replace(")",""):
                return x
    else:
        for x in data:
            if x['date'] == event['Fecha']:
                return x
    return 'no disponible'
   
def obtenerGrafica(data,event):
    ret=[]
    fechas = event['Rango'].replace(' ','').split('a')
    inicio= fechas[0].split('-')
    final= fechas[1].split('-')
   
    fI= datetime.datetime(int(inicio[0]),int(inicio[1]),int(inicio[2]))
    fF= datetime.datetime(int(final[0]),int(final[1]),int(final[2]))
   
    for registro in data:
        actual= registro['date'].replace(' ','').split('-')
        fA= datetime.datetime(int(actual[0]),int(actual[1]),int(actual[2]))
       
        if fA>=fI and fA<=fF:
            total= int(registro['confirmed'])+int(registro['recovered'])+int(registro['deaths'])
            ret.append({'Tiempo':registro['date'],'Total':total})
    return ret  