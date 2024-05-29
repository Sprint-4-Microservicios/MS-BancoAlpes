from django.conf import settings
from tarjetas.forms import  TarjetaForm
from .models import Tarjeta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from tarjetas.utils.authentication import jwt_required
from pymongo import MongoClient
from bson.objectid import ObjectId
import json


def TarjetaList(request):
    client = MongoClient('mongodb://banco_alpes:banco_alpes@10.128.0.59:27017')
    db = client.tarjetas_db
    tarjetas_collection = db['tarjetas']
    tarjetas_data = tarjetas_collection.find({})
    tarjetas = [{
            'id': str(tarjeta['_id']),  
            'tipo': tarjeta.get('tipo', ''),
            'puntaje': int(tarjeta.get('puntaje', 0))
        } for tarjeta in tarjetas_data]
    client.close()
    return render(request, 'Tarjeta/tarjetas.html', {'tarjeta_list': tarjetas})


@jwt_required
def TarjetaCreate(request):
    if request.user_role != 'admin':
        return HttpResponse('No tienes permisos para crear tarjetas', status=403)
    else:
        client = MongoClient('mongodb://banco_alpes:banco_alpes@10.128.0.59:27017')
        db = client.tarjetas_db
        tarjetas_collection = db['tarjetas']
        if request.method == 'POST':
            tarjeta_data = {
                'tipo': request.POST.get('tipo'),
                'puntaje': request.POST.get('puntaje')
            }
            result = tarjetas_collection.insert_one(tarjeta_data)
            if result.acknowledged:
                messages.add_message(request, messages.SUCCESS, 'Tarjeta creada exitosamente')
                return HttpResponseRedirect(reverse('tarjetaCreate'))
            else:
                messages.add_message(request, messages.ERROR, 'Error al crear la tarjeta')
        client.close()
        return render(request, 'Tarjeta/tarjetaCreate.html')

@jwt_required
def TarjetaUpdate(request, id):
    if request.user_role != 'admin':
        return HttpResponse('No tienes permisos para actualizar tarjetas', status=403)
    else:
        client = MongoClient('mongodb://banco_alpes:banco_alpes@10.128.0.59:27017')
        db = client.tarjetas_db
        tarjetas_collection = db['tarjetas']
        tarjeta = tarjetas_collection.find_one({'_id': ObjectId(id)})
        if request.method == 'POST':
            update_data = {
                'tipo': request.POST.get('tipo'),
                'puntaje': request.POST.get('puntaje')
            }
            result = tarjetas_collection.update_one({'_id': ObjectId(id)}, {'$set': update_data})
            client.close()
            if result.modified_count >= 0:
                messages.success(request, 'Tarjeta actualizada exitosamente')
                return HttpResponseRedirect(reverse('tarjetaList'))
            else:
                messages.error(request, 'Error al actualizar la tarjeta')
        else:
            form = {
                'tipo': tarjeta.get('tipo', ''),
                'puntaje': int(tarjeta.get('puntaje', 0))
            }
            client.close()
            return render(request, 'Tarjeta/tarjetaUpdate.html', {'form': form, 'tarjeta_id': id})


def getTarjetaList(request):
    if request.method == 'GET':
        client = MongoClient('mongodb://banco_alpes:banco_alpes@10.128.0.59:27017')
        db = client.tarjetas_db
        tarjetas_collection = db['tarjetas']
        tarjetas_data = tarjetas_collection.find({})
        tarjetas = [{
            'id': str(tarjeta['_id']), 
            'tipo': tarjeta.get('tipo', ''),
            'puntaje': int(tarjeta.get('puntaje', 0))
        } for tarjeta in tarjetas_data]

        client.close()
        return JsonResponse(tarjetas, safe=False)
    

@jwt_required
def deleteTarjeta(request, id):
    if request.method == 'POST':
        if request.user_role != 'admin':
            return HttpResponse('No tienes permisos para eliminar tarjetas', status=403)    
        else:
            client = MongoClient('mongodb://banco_alpes:banco_alpes@10.128.0.59:27017')
            try:
                db = client.tarjetas_db
                tarjetas_collection = db['tarjetas']
                try:
                    object_id = ObjectId(id)
                except:
                    return HttpResponse('ID inválido', status=400)
                
                result = tarjetas_collection.delete_one({'_id': object_id})
                if result.deleted_count > 0:
                    return HttpResponseRedirect(reverse('tarjetaList'))
                else:
                    return HttpResponse('No se pudo eliminar la tarjeta', status=404)
            finally:
                client.close()
    else:
        return HttpResponse('Método no permitido', status=405)