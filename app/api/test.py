from app.api import bp
from app.api import helpers
from flask.views import MethodView

class TestAPI(MethodView):
    def get(self, test_id):
        return "TestAPI"

helpers.register_api(TestAPI, 'test_api', '/test/', pk='test_id')
