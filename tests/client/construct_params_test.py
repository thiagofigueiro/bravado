from mock import patch
import pytest

from bravado_core.exception import SwaggerMappingError
from bravado_core.operation import Operation

from bravado.client import CallableOperation
from bravado.client import construct_params


@patch('bravado.client.marshal_param')
def test_simple(mock_marshal_param, minimal_swagger_spec, getPetById_spec,
                request_dict):
    request_dict['url'] = '/pet/{petId}'
    op = CallableOperation(Operation.from_spec(
        minimal_swagger_spec, '/pet/{petId}', 'get', getPetById_spec))
    construct_params(op, request_dict, op_kwargs={'petId': 34})
    assert 1 == mock_marshal_param.call_count


@patch('bravado.client.marshal_param')
def test_no_params(mock_marshal_param, minimal_swagger_spec, request_dict):
    get_op = minimal_swagger_spec.spec_dict['paths']['/pet/{petId}']['get']
    del get_op['parameters'][0]
    op = CallableOperation(Operation.from_spec(
        minimal_swagger_spec, '/pet/{petId}', 'get', {}))
    construct_params(op, request_dict, op_kwargs={})
    assert 0 == mock_marshal_param.call_count
    assert 0 == len(request_dict)


def test_extra_parameter_error(minimal_swagger_spec, request_dict):
    op = CallableOperation(Operation.from_spec(
        minimal_swagger_spec, '/pet/{petId}', 'get', {}))
    with pytest.raises(SwaggerMappingError) as excinfo:
        construct_params(op, request_dict, op_kwargs={'extra_param': 'bar'})
    assert 'does not have parameter' in str(excinfo.value)


def test_required_parameter_missing(
        minimal_swagger_spec, getPetById_spec, request_dict):
    request_dict['url'] = '/pet/{petId}'
    op = CallableOperation(Operation.from_spec(
        minimal_swagger_spec, '/pet/{petId}', 'get', getPetById_spec))
    with pytest.raises(SwaggerMappingError) as excinfo:
        construct_params(op, request_dict, op_kwargs={})
    assert 'required parameter' in str(excinfo.value)


@patch('bravado.client.marshal_param')
def test_non_required_parameter_with_default_used(
        mock_marshal_param, minimal_swagger_spec, getPetById_spec,
        request_dict):

    del getPetById_spec['parameters'][0]['required']
    getPetById_spec['parameters'][0]['default'] = 99
    request_dict['url'] = '/pet/{petId}'
    op = CallableOperation(Operation.from_spec(
        minimal_swagger_spec, '/pet/{petId}', 'get', getPetById_spec))
    construct_params(op, request_dict, op_kwargs={})
    assert 1 == mock_marshal_param.call_count
