import pytest
import werkzeug
import requests
from thumbp import thumbp

good_item_id = 'b3039064282a263cad6e57e76ad9caa8'
thumbp.es_base = 'http://localhost:9200/testindex'


class MockResult:
    def json(self):
        return {
            'hits': {
                'hits': [{
                    'fields': {
                        'id': 'b3039064282a263cad6e57e76ad9caa8',
                        'object': 'http://object/url'
                    }
                }]
            }
        }


class TestThumb:
    def test_es_url_is_correct(self, monkeypatch):
        correct_es_url = "http://localhost:9200/testindex/_search?q=id:%s" \
                         "&fields=id,object" % good_item_id
        def mockget(url):
            assert url == correct_es_url
            return True
        monkeypatch.setattr(requests, 'get', mockget)
        thumbp.elasticsearch_result(good_item_id)


class TestValidId:
    def test_valid_id_returns_valid_id(self):
        """32-character string of a-f and 0-9 is returned as valid string"""
        assert thumbp.valid_id(good_item_id) == good_item_id

    def test_valid_id_raises_exception(self):
        with pytest.raises(thumbp.Forbidden):
            thumbp.valid_id('x')
