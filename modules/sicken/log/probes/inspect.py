from inspect import stack, currentframe

class Inspect:
    def caller(self, depth):
        i=stack()[depth]
        resp={"filename":str(i.filename),
              "function": str(i.function),
              "line_number":str(i.lineno)}
        return resp