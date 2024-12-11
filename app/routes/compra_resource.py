from flask import Blueprint, request
from marshmallow import ValidationError

from app.mapping import CompraSchema, ResponseSchema
from app.services import CompraService, ResponseBuilder

compra = Blueprint('compra', __name__)
service = CompraService()
compra_schema = CompraSchema()
response_schema = ResponseSchema()

@compra.route('/compras', methods=['GET'])
def all():
    response_builder = ResponseBuilder()
    try:
        data = compra_schema.dump(service.get_all(), many=True)
        response_builder.add_message("Compras found").add_status_code(200).add_data(data)
        return response_schema.dump(response_builder.build()), 200
    except Exception as e:
        response_builder.add_message("Error fetching compras").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@compra.route('/compras/<int:id>', methods=['GET'])
def one(id):
    response_builder = ResponseBuilder()
    try:
        data = service.get_by_id(id)
        if data:
            serialized_data = compra_schema.dump(data)
            response_builder.add_message("Compra found").add_status_code(200).add_data(serialized_data)
            return response_schema.dump(response_builder.build()), 200
        else:
            response_builder.add_message("Compra not found").add_status_code(404).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 404
    except Exception as e:
        response_builder.add_message("Error fetching compra").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@compra.route('/compras', methods=['POST'])
def create():
    response_builder = ResponseBuilder()
    try:
        compra = compra_schema.load(request.json)
        data = compra_schema.dump(service.create(compra))
        response_builder.add_message("Compra created").add_status_code(201).add_data(data)
        return response_schema.dump(response_builder.build()), 201
    except ValidationError as err:
        response_builder.add_message("Validation error").add_status_code(422).add_data(err.messages)
        return response_schema.dump(response_builder.build()), 422
    except Exception as e:
        response_builder.add_message("Error creating compra").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@compra.route('/compras/<int:id>', methods=['PUT'])
def update(id):
    response_builder = ResponseBuilder()
    try:
        compra = compra_schema.load(request.json)
        data = compra_schema.dump(service.update(id, compra))
        response_builder.add_message("Compra updated").add_status_code(200).add_data(data)
        return response_schema.dump(response_builder.build()), 200
    except ValidationError as err:
        response_builder.add_message("Validation error").add_status_code(422).add_data(err.messages)
        return response_schema.dump(response_builder.build()), 422
    except Exception as e:
        response_builder.add_message("Error updating compra").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@compra.route('/compras/<int:id>', methods=['DELETE'])
def delete(id):
    response_builder = ResponseBuilder()
    try:
        if service.delete(id):
            response_builder.add_message("Compra deleted").add_status_code(200).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 200
        else:
            response_builder.add_message("Compra not found").add_status_code(404).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 404
    except Exception as e:
        response_builder.add_message("Error deleting compra").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500
